"""AgentCore Investigation Runner.

Orchestrates the full incident investigation pipeline:
  1. Create AgentCore working-memory session
  2. Fetch telemetry from Datadog (stored in session memory as each arrives)
  3. Run Toto forecast on key metric series
  4. Run IncidentSummarizerAgent (with memory context)
  5. Run HypothesisRankerAgent
  6. Run GuidedStepsAgent (personalized via SQLite MemoryProfile + AgentCore session)
  7. Run RecommendationDesignerAgent
  8. Log each step as a session event (powers /agent-trace endpoint)
  9. Close session and return full result

Minimax is the LLM inside every agent. AgentCore provides:
  - Working memory (ephemeral, per-session)
  - Tool catalog context (injected into agent prompts)
"""
import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from app.agentcore.memory import AgentCoreMemoryClient, get_memory_client
from app.agentcore.gateway import get_gateway_client
from app.integrations.datadog_mcp import get_datadog_client
from app.integrations.toto_forecaster import get_toto_forecaster
from app.agents.incident_summarizer import IncidentSummarizerAgent
from app.agents.hypothesis_ranker import HypothesisRankerAgent
from app.agents.guided_steps import GuidedStepsAgent
from app.agents.recommendation_designer import RecommendationDesignerAgent

logger = logging.getLogger(__name__)


def _safe_dump(obj) -> dict:
    """Convert an agent Pydantic output to a JSON-safe dict.

    round-trips through json.dumps(default=str) to sanitise PydanticUndefined
    values that can appear when an agent's fallback model_construct() is called.
    """
    import json

    try:
        raw = obj.model_dump()
    except Exception:
        raw = {}
    return json.loads(json.dumps(raw, default=str))


class InvestigationRunner:
    """Runs the full investigation pipeline for a single incident."""

    def __init__(self):
        self.memory: AgentCoreMemoryClient = get_memory_client()
        self.gateway = get_gateway_client()
        self.datadog = get_datadog_client()
        self.toto = get_toto_forecaster()

    # ------------------------------------------------------------------
    # Public entry point
    # ------------------------------------------------------------------

    async def run(
        self,
        incident_id: int,
        incident: Any,          # SQLAlchemy Incident model instance
        user_id: int,
        memory_profile: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Run the full investigation and return a structured result dict.

        The returned dict contains:
            session_id, envelope, hypotheses, guided_steps, recommendations,
            toto_forecasts, events (agent-trace log)
        """
        session_id = self.memory.create_session(incident_id, user_id)
        tool_defs = self.gateway.get_tool_definitions()

        self._log_event(session_id, "runner_start", {
            "incident_id": incident_id,
            "tools_registered": len(tool_defs),
        })

        services = incident.services or []

        # ── Step 1: Fetch telemetry ──────────────────────────────────────
        self._log_event(session_id, "tool_call", {
            "agent": "Datadog",
            "action": "get_active_monitors",
            "status": "running",
        })
        monitors = await self._safe(
            self.datadog.get_active_monitors(time_window=3600), []
        )
        self.memory.store(session_id, "current_incident", {
            "id": incident_id,
            "title": incident.title,
            "severity": incident.severity,
            "services": services,
        })
        self._log_event(session_id, "tool_call", {
            "agent": "Datadog",
            "action": "get_active_monitors",
            "status": "complete",
            "result_count": len(monitors),
        })

        self._log_event(session_id, "tool_call", {
            "agent": "Datadog",
            "action": "query_metrics",
            "status": "running",
        })
        service_filter = services[0] if services else "demo-service"
        metrics = await self._safe(
            self.datadog.query_metrics(
                query=f"sum:demo.http.requests.count{{service:{service_filter}}}.as_rate()"
            ),
            [],
        )
        self.memory.store(session_id, "last_tool_output", {"type": "metrics", "count": len(metrics)})
        self._log_event(session_id, "tool_call", {
            "agent": "Datadog",
            "action": "query_metrics",
            "status": "complete",
            "result_count": len(metrics),
        })

        self._log_event(session_id, "tool_call", {
            "agent": "Datadog",
            "action": "search_logs",
            "status": "running",
        })
        logs = await self._safe(
            self.datadog.search_logs(
                query=f"service:{service_filter}", limit=50
            ),
            [],
        )
        self._log_event(session_id, "tool_call", {
            "agent": "Datadog",
            "action": "search_logs",
            "status": "complete",
            "result_count": len(logs),
        })

        self._log_event(session_id, "tool_call", {
            "agent": "Datadog",
            "action": "fetch_traces",
            "status": "running",
        })
        traces = await self._safe(
            self.datadog.fetch_traces(service=service_filter, limit=50), []
        )
        self._log_event(session_id, "tool_call", {
            "agent": "Datadog",
            "action": "fetch_traces",
            "status": "complete",
            "result_count": len(traces),
        })

        telemetry_bundle = {
            "monitors": monitors,
            "metrics": metrics,
            "logs": logs,
            "traces": traces,
        }
        self.memory.store(session_id, "checked_items", ["monitors", "metrics", "logs", "traces"])

        # ── Step 2: Toto forecast ────────────────────────────────────────
        self._log_event(session_id, "tool_call", {
            "agent": "Toto",
            "action": "toto_forecast",
            "status": "running",
        })
        toto_forecasts = []
        if isinstance(metrics, list) and metrics:
            first_series = metrics[0]
            points = first_series.get("pointlist", [])
            if len(points) >= 10:
                values = [p[1] for p in points if p[1] is not None]
                fc = self.toto.forecast(
                    values=values,
                    interval_seconds=60,
                    series_name=first_series.get("metric", "request_rate"),
                )
                if fc:
                    toto_forecasts.append(fc.model_dump())
                    self.memory.store(session_id, "toto_anomaly_score", fc.anomaly_score)

        self._log_event(session_id, "tool_call", {
            "agent": "Toto",
            "action": "toto_forecast",
            "status": "complete",
            "forecasts": len(toto_forecasts),
        })

        # ── Step 3: IncidentSummarizerAgent ──────────────────────────────
        self._log_event(session_id, "agent_call", {
            "agent": "IncidentSummarizer",
            "action": "summarize",
            "status": "running",
        })
        try:
            summarizer = IncidentSummarizerAgent()
            envelope_obj = await summarizer.summarize(telemetry_bundle)
            envelope = _safe_dump(envelope_obj)
        except Exception as exc:
            logger.error(f"IncidentSummarizerAgent failed: {exc}")
            envelope = {
                "title": incident.title,
                "description": f"Incident affecting {', '.join(services)}",
                "started_at": incident.started_at.isoformat(),
                "affected_services": services,
                "blast_radius": "Unknown",
                "severity": incident.severity,
                "primary_symptom": "Unknown",
            }
        self.memory.store(session_id, "current_incident", {
            **self.memory.retrieve(session_id).get("current_incident", {}),
            "envelope": envelope,
        })
        self._log_event(session_id, "agent_call", {
            "agent": "IncidentSummarizer",
            "action": "summarize",
            "status": "complete",
            "severity": envelope.get("severity"),
        })

        # ── Step 4: HypothesisRankerAgent ────────────────────────────────
        self._log_event(session_id, "agent_call", {
            "agent": "HypothesisRanker",
            "action": "rank_hypotheses",
            "status": "running",
        })
        patterns = memory_profile.get("patterns", [])
        try:
            ranker = HypothesisRankerAgent()
            hypotheses_output = await ranker.rank_hypotheses(
                telemetry_evidence=telemetry_bundle,
                known_patterns=patterns[:5],
            )
            hyp_list = hypotheses_output.hypotheses or []
            hypotheses = [_safe_dump(h) for h in hyp_list]
        except Exception as exc:
            logger.error(f"HypothesisRankerAgent failed: {exc}")
            hypotheses = []
        self.memory.store(session_id, "open_hypotheses", hypotheses[:3])
        self._log_event(session_id, "agent_call", {
            "agent": "HypothesisRanker",
            "action": "rank_hypotheses",
            "status": "complete",
            "hypotheses_count": len(hypotheses),
        })

        # ── Step 5: GuidedStepsAgent ─────────────────────────────────────
        self._log_event(session_id, "agent_call", {
            "agent": "GuidedSteps",
            "action": "generate_steps",
            "status": "running",
        })
        try:
            steps_agent = GuidedStepsAgent()
            steps_output = await steps_agent.generate_steps(
                incident_envelope=envelope,
                memory_profile=memory_profile.get("preferences", {}),
                telemetry_summary={
                    "monitors_count": len(monitors),
                    "logs_count": len(logs),
                    "traces_count": len(traces),
                    "top_hypotheses": [h.get("title") or h.get("description", "") for h in hypotheses[:3]],
                    "learned_patterns": [p.get("description", "") for p in memory_profile.get("patterns", [])[:3]],
                },
            )
            steps_list = steps_output.steps or []
            guided_steps = [_safe_dump(s) for s in steps_list]
        except Exception as exc:
            logger.error(f"GuidedStepsAgent failed: {exc}")
            guided_steps = []
        investigation_graph = [
            {"step": s.get("id"), "title": s.get("title")} for s in guided_steps
        ]
        self.memory.store(session_id, "investigation_graph", investigation_graph)
        self._log_event(session_id, "agent_call", {
            "agent": "GuidedSteps",
            "action": "generate_steps",
            "status": "complete",
            "steps_count": len(guided_steps),
        })

        # ── Step 6: RecommendationDesignerAgent ──────────────────────────
        self._log_event(session_id, "agent_call", {
            "agent": "RecommendationDesigner",
            "action": "design_recommendations",
            "status": "running",
        })
        try:
            rec_agent = RecommendationDesignerAgent()
            # Pass lean hypothesis context (drop verbose evidence lists)
            def _slim_hyp(h: dict) -> dict:
                return {
                    "id": h.get("id", ""),
                    "title": h.get("title") or h.get("description", "")[:80],
                    "description": h.get("description", "")[:200],
                    "confidence": h.get("confidence", 50),
                }
            hyp_context = [_slim_hyp(h) for h in hypotheses[:3]] if hypotheses else [
                {"id": "h0", "title": envelope.get("primary_symptom", "Service degradation"),
                 "description": envelope.get("description", ""), "confidence": 70}
            ]
            rec_output = await rec_agent.design_recommendations(
                hypotheses=hyp_context,
                user_preferences={
                    **memory_profile.get("preferences", {}),
                    "incident_severity": envelope.get("severity", "warning"),
                    "affected_services": envelope.get("affected_services", services),
                },
            )
            rec_list = rec_output.recommendations or []
            recommendations = [_safe_dump(r) for r in rec_list[:5]]
        except Exception as exc:
            logger.error(f"RecommendationDesignerAgent failed: {exc}")
            recommendations = []
        self._log_event(session_id, "agent_call", {
            "agent": "RecommendationDesigner",
            "action": "design_recommendations",
            "status": "complete",
            "recommendations_count": len(recommendations),
        })

        # ── Step 7: Save learned pattern to memory profile ───────────────
        try:
            from app.db.session import SessionLocal
            from app.services.memory_service import MemoryService as _MemSvc
            top_hypothesis = (hypotheses[0].get("title") or hypotheses[0].get("description", "")) if hypotheses else ""
            top_recommendation = recommendations[0].get("title", "") if recommendations else ""
            pattern = {
                "description": (
                    f"Investigated {envelope.get('severity','unknown')} incident "
                    f"affecting {', '.join(services) if services else 'unknown service'}. "
                    f"{'Top hypothesis: ' + top_hypothesis + '. ' if top_hypothesis else ''}"
                    f"{'Recommended: ' + top_recommendation if top_recommendation else ''}"
                ).strip(),
                "services": services,
                "severity": envelope.get("severity", "unknown"),
                "primary_symptom": envelope.get("primary_symptom", ""),
                "top_recommendation": top_recommendation,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
            _db = SessionLocal()
            try:
                _mem = _MemSvc(_db)
                _mem.add_pattern(user_id=user_id, pattern=pattern)
            finally:
                _db.close()
        except Exception as exc:
            logger.warning(f"Failed to save learned pattern: {exc}")

        # ── Step 8: Finalise ─────────────────────────────────────────────
        self._log_event(session_id, "runner_complete", {
            "incident_id": incident_id,
            "hypotheses": len(hypotheses),
            "guided_steps": len(guided_steps),
            "recommendations": len(recommendations),
            "toto_forecasts": len(toto_forecasts),
        })
        self.memory.close_session(session_id)

        return {
            "session_id": session_id,
            "envelope": envelope,
            "evidence": telemetry_bundle,
            "hypotheses": hypotheses,
            "guided_steps": guided_steps,
            "recommendations": recommendations,
            "toto_forecasts": toto_forecasts,
            "events": self.memory.get_events(session_id),
        }

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _log_event(self, session_id: str, kind: str, payload: Dict[str, Any]) -> None:
        """Append a timestamped event to the session event log."""
        payload["timestamp"] = datetime.now(timezone.utc).isoformat()
        self.memory.store(session_id, f"_event_{kind}_{payload['timestamp']}", payload)
        # Also append to the events list directly
        mem = self.memory.retrieve(session_id)
        events = mem.get("events", [])
        events.append({"kind": kind, **payload})
        # Directly update the fallback store (store() would overwrite the key)
        from app.agentcore.memory import _fallback_sessions
        if session_id in _fallback_sessions:
            _fallback_sessions[session_id]["events"] = events

    @staticmethod
    async def _safe(coro, default):
        """Await a coroutine and return default on exception."""
        try:
            return await coro
        except Exception as exc:
            logger.warning(f"Runner tool call failed: {exc}")
            return default
