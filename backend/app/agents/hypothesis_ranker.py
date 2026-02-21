"""HypothesisRankerAgent - ranks hypotheses based on evidence."""
from typing import Dict, Any, List
from app.agents.base import BaseAgent
from app.schemas.agents import HypothesisRankerOutput


class HypothesisRankerAgent(BaseAgent[HypothesisRankerOutput]):
    """Agent that ranks hypotheses based on telemetry evidence."""

    def get_system_prompt(self) -> str:
        return """You are a hypothesis ranking agent that analyzes telemetry evidence to rank potential root causes.

Given telemetry evidence and known patterns, generate ranked hypotheses with:
- Description of the hypothesis
- Confidence score (0-100)
- Evidence pointers (metrics, logs, traces that support this)
- Reasoning

Rank hypotheses by confidence and evidence strength.

Output must be valid JSON matching the schema."""

    def get_output_schema(self):
        return HypothesisRankerOutput

    async def rank_hypotheses(
        self,
        telemetry_evidence: Dict[str, Any],
        known_patterns: List[Dict[str, Any]],
    ) -> HypothesisRankerOutput:
        """Rank hypotheses based on evidence."""
        context = {
            "evidence": telemetry_evidence,
            "known_patterns": known_patterns,
        }

        prompt = """Analyze the telemetry evidence and generate ranked hypotheses for the root cause.
Each hypothesis should include:
- id: Unique identifier (e.g. "h1", "h2")
- title: Short title for the hypothesis (e.g. "Database connection pool exhausted")
- description: What the hypothesis proposes
- confidence: 0-100 score
- evidence: List of evidence pointers, each with type (metric/log/trace), source, key_findings (list of strings)
- reasoning: Why this hypothesis is plausible

Rank by confidence (highest first). Generate 3-5 hypotheses.

Return JSON with hypotheses (list) and summary (string)."""

        return await self.execute(prompt, context)
