"""GuidedStepsAgent - generates next investigation steps."""
from typing import Dict, Any, Optional
from app.agents.base import BaseAgent
from app.schemas.agents import GuidedStepsOutput


class GuidedStepsAgent(BaseAgent[GuidedStepsOutput]):
    """Agent that generates guided investigation steps."""

    def get_system_prompt(self) -> str:
        return """You are an investigation guide agent that suggests the next best steps for investigating an incident.

Given an incident envelope, memory profile, and telemetry summary, generate 3-7 actionable investigation steps.
Each step should:
- Have a clear title and description
- Specify the action type (query_metrics, search_logs, fetch_traces, etc.)
- Include action parameters
- Provide rationale for why this step is useful
- Have a priority (1-10, higher is more important)

Consider the user's learned patterns and preferences when suggesting steps.

Output must be valid JSON matching the schema."""

    def get_output_schema(self):
        return GuidedStepsOutput

    async def generate_steps(
        self,
        incident_envelope: Dict[str, Any],
        memory_profile: Dict[str, Any],
        telemetry_summary: Dict[str, Any],
    ) -> GuidedStepsOutput:
        """Generate guided investigation steps."""
        context = {
            "incident": incident_envelope,
            "memory_profile": memory_profile,
            "telemetry_summary": telemetry_summary,
        }

        prompt = """Generate 3-7 guided investigation steps for this incident.
Each step should include:
- id: Unique identifier
- title: Short title
- description: What this step does
- action_type: Type of action (query_metrics, search_logs, fetch_traces, get_service_dependencies, etc.)
- action_params: Parameters for the action (as dict)
- rationale: Why this step is useful
- priority: 1-10 (higher = more important)

Consider the user's preferences and learned patterns from memory_profile.

Return JSON with steps (list) and reasoning (string)."""

        return await self.execute(prompt, context)
