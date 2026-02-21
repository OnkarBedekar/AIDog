"""TestPlanAgent - generates TestSprite test plans."""
from typing import Dict, Any
from app.agents.base import BaseAgent
from app.schemas.agents import TestPlanOutput


class TestPlanAgent(BaseAgent[TestPlanOutput]):
    """Agent that generates test plans for recommendations."""

    def get_system_prompt(self) -> str:
        return """You are a test plan generator agent that creates TestSprite test plans for validating recommendations.

Given a recommendation, incident type, and telemetry signature, generate a test plan with:
- Name and description
- Test steps (what to validate)
- Validation criteria (how to interpret results)
- Failure interpretation (what failures mean)

Test steps should be actionable and validate the recommendation's effectiveness.

Output must be valid JSON matching the schema."""

    def get_output_schema(self):
        return TestPlanOutput

    async def generate_test_plan(
        self,
        recommendation: Dict[str, Any],
        incident_type: str,
        telemetry_signature: Dict[str, Any],
    ) -> TestPlanOutput:
        """Generate test plan for a recommendation."""
        context = {
            "recommendation": recommendation,
            "incident_type": incident_type,
            "telemetry_signature": telemetry_signature,
        }

        prompt = """Generate a TestSprite test plan for validating this recommendation.
The plan should include:
- name: Test plan name
- description: What this test validates
- steps: List of test steps (name, description, type, params, expected_result)
- validation_criteria: How to interpret test results
- failure_interpretation: What test failures indicate

Return JSON with plan (TestPlan object) and rationale (string)."""

        return await self.execute(prompt, context, max_tokens=3000)
