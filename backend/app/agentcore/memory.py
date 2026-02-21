"""AWS Bedrock AgentCore Memory client.

Provides per-session ephemeral working memory for investigation sessions.
This is NOT the durable MemoryProfile (which stays in SQLite). This is
short-lived, session-scoped context: current hypotheses, tool outputs,
investigation graph, etc.

Falls back to an in-memory dict when AWS_REGION is not configured.
"""
import json
import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from app.core.config import settings

logger = logging.getLogger(__name__)

# In-process fallback when AWS is unavailable
_fallback_sessions: Dict[str, Dict[str, Any]] = {}


class AgentCoreMemoryClient:
    """Wraps bedrock_agentcore MemorySessionManager for per-session working memory."""

    def __init__(self):
        self._manager = None
        self._use_aws = bool(
            settings.aws_region and settings.agentcore_memory_id
        )
        if self._use_aws:
            try:
                from bedrock_agentcore.memory import MemorySessionManager

                self._manager = MemorySessionManager(
                    memory_id=settings.agentcore_memory_id,
                    region_name=settings.aws_region,
                )
                logger.info("AgentCore Memory client initialized (AWS mode).")
            except Exception as exc:
                logger.warning(
                    f"AgentCore Memory init failed, using in-process fallback: {exc}"
                )
                self._use_aws = False
        else:
            logger.info("AgentCore Memory using in-process fallback (no AWS config).")

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def create_session(self, incident_id: int, user_id: int) -> str:
        """Create a new working-memory session for an incident investigation.

        Returns the session_id string.
        """
        session_id = f"incident-{incident_id}-user-{user_id}-{int(datetime.now(timezone.utc).timestamp())}"

        if self._use_aws and self._manager:
            try:
                self._manager.create_memory_session(
                    actor_id=f"user-{user_id}",
                    session_id=session_id,
                )
                logger.debug(f"AgentCore session created: {session_id}")
            except Exception as exc:
                logger.warning(f"AgentCore create_session failed: {exc}")
                self._use_aws = False

        # Always initialise the fallback entry (used when AWS unavailable)
        _fallback_sessions[session_id] = {
            "current_incident": None,
            "checked_items": [],
            "last_tool_output": None,
            "open_hypotheses": [],
            "investigation_graph": [],
            "events": [],
        }
        return session_id

    def store(self, session_id: str, key: str, value: Any) -> None:
        """Store a key-value pair in the session working memory."""
        serialized = json.dumps(value, default=str)

        if self._use_aws and self._manager:
            try:
                from bedrock_agentcore.memory.constants import (
                    ConversationalMessage,
                    MessageRole,
                )

                session = self._manager.create_memory_session(
                    actor_id="system",
                    session_id=session_id,
                )
                session.add_turns(
                    messages=[
                        ConversationalMessage(
                            f"[MEMORY_UPDATE] {key}",
                            MessageRole.USER,
                        ),
                        ConversationalMessage(
                            serialized,
                            MessageRole.ASSISTANT,
                        ),
                    ]
                )
            except Exception as exc:
                logger.warning(f"AgentCore store failed: {exc}")

        # Always update in-process fallback
        if session_id in _fallback_sessions:
            _fallback_sessions[session_id][key] = value
            _fallback_sessions[session_id]["events"].append(
                {
                    "kind": "memory_update",
                    "key": key,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                }
            )

    def retrieve(self, session_id: str) -> Dict[str, Any]:
        """Return the full session working memory dict."""
        return _fallback_sessions.get(session_id, {})

    def search(self, session_id: str, query: str, max_results: int = 5) -> List[str]:
        """Semantic search over session memories.

        Uses AgentCore's semantic search when available; otherwise does a
        simple substring scan over the in-process fallback.
        """
        if self._use_aws and self._manager:
            try:
                from bedrock_agentcore.memory.constants import ConversationalMessage, MessageRole

                session = self._manager.create_memory_session(
                    actor_id="system",
                    session_id=session_id,
                )
                results = session.search_memories(query=query, max_results=max_results)
                return [str(r) for r in results]
            except Exception as exc:
                logger.warning(f"AgentCore search failed: {exc}")

        # Fallback: simple substring scan
        mem = _fallback_sessions.get(session_id, {})
        matches = []
        for key, val in mem.items():
            if key == "events":
                continue
            text = json.dumps(val, default=str)
            if query.lower() in text.lower():
                matches.append(f"{key}: {text[:200]}")
        return matches[:max_results]

    def close_session(self, session_id: str) -> None:
        """Finalise and clean up the session."""
        # Keep the fallback entry in memory for the lifetime of the process
        # (so agent-trace endpoint can still return it). Mark as closed.
        if session_id in _fallback_sessions:
            _fallback_sessions[session_id]["closed_at"] = datetime.now(timezone.utc).isoformat()
        logger.debug(f"AgentCore session closed: {session_id}")

    def get_events(self, session_id: str) -> List[Dict[str, Any]]:
        """Return the ordered event log for a session (used by agent-trace endpoint)."""
        return _fallback_sessions.get(session_id, {}).get("events", [])


# Module-level singleton
_memory_client: Optional[AgentCoreMemoryClient] = None


def get_memory_client() -> AgentCoreMemoryClient:
    """Return the shared AgentCoreMemoryClient instance."""
    global _memory_client
    if _memory_client is None:
        _memory_client = AgentCoreMemoryClient()
    return _memory_client
