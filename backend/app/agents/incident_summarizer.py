"""IncidentSummarizerAgent - summarizes telemetry into incident envelope."""
from typing import Dict, Any
from app.agents.base import BaseAgent
from app.schemas.agents import IncidentEnvelope


class IncidentSummarizerAgent(BaseAgent[IncidentEnvelope]):
    """Agent that summarizes telemetry into incident envelope."""

    def get_system_prompt(self) -> str:
        return """You are an incident analysis agent that processes telemetry data (metrics, logs, traces, monitors)
to create a structured incident envelope.

Extract:
- What happened (title, description)
- When it started
- Where (affected services)
- Blast radius (impact estimate)
- Severity
- Primary symptom
- Initial root cause hypothesis

Output must be valid JSON matching the schema."""

    def get_output_schema(self):
        return IncidentEnvelope

    async def summarize(
        self,
        telemetry_bundle: Dict[str, Any],
    ) -> IncidentEnvelope:
        """Summarize telemetry bundle into incident envelope."""
        prompt = """Analyze the telemetry bundle and create an incident envelope with:
- title: Brief incident title
- description: What happened
- started_at: ISO timestamp
- affected_services: List of service names
- blast_radius: Impact estimate (e.g., "3 services, 15% of traffic")
- severity: critical, warning, or info
- primary_symptom: Main symptom observed
- root_cause_hypothesis: Initial hypothesis (optional)

Return JSON matching the IncidentEnvelope schema."""

        return await self.execute(prompt, {"telemetry": telemetry_bundle})
