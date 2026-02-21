"""RecommendationDesignerAgent - creates actionable recommendations."""
from typing import Dict, Any, List
from app.agents.base import BaseAgent
from app.schemas.agents import RecommendationDesignerOutput


class RecommendationDesignerAgent(BaseAgent[RecommendationDesignerOutput]):
    """Agent that designs actionable recommendations."""

    def get_system_prompt(self) -> str:
        return """You are a recommendation designer agent that creates actionable proposals based on hypotheses and user preferences.

Generate recommendations for:
- Monitor tuning (threshold adjustments, query improvements)
- Dashboard creation (new correlation panels)
- SLO definitions (new service level objectives)
- Shortcut templates (reusable investigation shortcuts)
- Hypothesis validation (ways to test hypotheses)

Each recommendation must include:
- Type (monitor_tune, dashboard, slo, shortcut, hypothesis)
- Title and description
- Confidence score (0-100)
- Export payload (JSON that can be applied)
- CLI snippet (optional, for applying the change)
- Rationale

Consider user preferences (conservative vs aggressive, noise tolerance, focus areas).

Output must be valid JSON matching the schema."""

    def get_output_schema(self):
        return RecommendationDesignerOutput

    async def design_recommendations(
        self,
        hypotheses: List[Dict[str, Any]],
        user_preferences: Dict[str, Any],
    ) -> RecommendationDesignerOutput:
        """Design recommendations based on hypotheses and preferences."""
        context = {
            "hypotheses": hypotheses,
            "user_preferences": user_preferences,
        }

        prompt = """Generate actionable recommendations based on the hypotheses and user preferences.
Each recommendation should include:
- id: Unique identifier
- type: monitor_tune, dashboard, slo, shortcut, or hypothesis
- title: Short title
- description: What this recommendation does
- confidence: 0-100 score
- export_payload: JSON payload with type and payload fields, plus optional cli_snippet
- rationale: Why this recommendation is valuable

Consider user preferences for action style and focus areas.

Return JSON with recommendations (list) and summary (string)."""

        return await self.execute(prompt, context, max_tokens=4000)
