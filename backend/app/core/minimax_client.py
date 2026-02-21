"""Minimax LLM client — uses the Anthropic-compatible MiniMax API.

Endpoint: https://api.minimax.io/anthropic
Auth:     MINIMAX_API_KEY (same key, passed as ANTHROPIC_API_KEY to SDK)
Model:    MiniMax-M2.5-highspeed (100 tps, 204k context)

All agents call chat_json() / generate_text() — no changes needed in agent code.
"""
import json
from typing import Optional, Dict, Any, List
import anthropic
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)

_MINIMAX_BASE_URL = "https://api.minimax.io/anthropic"
_MODEL = "MiniMax-M2.5-highspeed"


class MinimaxClient:
    """Minimax client using the Anthropic-compatible endpoint."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        temperature: Optional[float] = None,
    ):
        self.api_key = api_key or settings.minimax_api_key
        self.model = _MODEL
        self.temperature = max(0.01, min(0.99, temperature or settings.minimax_temperature))
        self._client = anthropic.Anthropic(
            base_url=_MINIMAX_BASE_URL,
            api_key=self.api_key,
        ) if self.api_key else None

    def _get_text(self, resp) -> str:
        """Extract text from response, skipping ThinkingBlock."""
        for block in resp.content:
            if hasattr(block, "text"):
                return block.text
        return ""

    async def chat_json(
        self,
        messages: List[Dict[str, str]],
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Chat completion returning parsed JSON dict — used by all agents."""
        if not self._client:
            raise ValueError("MINIMAX_API_KEY not configured")

        sys = (system_prompt or "") + "\n\nRespond with valid JSON only. No markdown, no prose outside JSON."
        temp = max(0.01, min(0.99, temperature or self.temperature))

        api_messages = []
        for m in messages:
            role = m.get("role", "user")
            if role not in ("user", "assistant"):
                role = "user"
            api_messages.append({"role": role, "content": m.get("content", "")})

        resp = self._client.messages.create(
            model=self.model,
            max_tokens=max_tokens or 2000,
            temperature=temp,
            system=sys,
            messages=api_messages,
        )

        text = self._get_text(resp).strip()

        # Strip markdown fences if present
        if text.startswith("```"):
            parts = text.split("```")
            text = parts[1] if len(parts) > 1 else text
            if text.startswith("json"):
                text = text[4:]
            text = text.strip()

        try:
            return json.loads(text)
        except json.JSONDecodeError:
            # Try to extract first JSON object
            start = text.find("{")
            end = text.rfind("}") + 1
            if start >= 0 and end > start:
                try:
                    return json.loads(text[start:end])
                except json.JSONDecodeError:
                    pass
            logger.error(f"Failed to parse JSON from Minimax: {text[:300]}")
            raise ValueError(f"No valid JSON in Minimax response: {text[:200]}")

    async def generate_text(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = None,
    ) -> str:
        if not self._client:
            raise ValueError("MINIMAX_API_KEY not configured")
        temp = max(0.01, min(0.99, temperature or self.temperature))
        resp = self._client.messages.create(
            model=self.model,
            max_tokens=1000,
            temperature=temp,
            system=system_prompt or "You are a helpful assistant.",
            messages=[{"role": "user", "content": prompt}],
        )
        return self._get_text(resp)


# Global singleton
_minimax_client: Optional[MinimaxClient] = None


def get_minimax_client() -> MinimaxClient:
    """Get or create Minimax client instance."""
    global _minimax_client
    if _minimax_client is None:
        _minimax_client = MinimaxClient()
    return _minimax_client
