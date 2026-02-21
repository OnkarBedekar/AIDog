"""BehaviorMinerAgent - analyzes user events to extract patterns."""
from typing import Dict, Any, Optional
from app.agents.base import BaseAgent
from app.schemas.agents import BehaviorMinerOutput, Pattern, PreferenceAdjustment


class BehaviorMinerAgent(BaseAgent[BehaviorMinerOutput]):
    """Agent that mines user behavior patterns from events."""

    def get_system_prompt(self) -> str:
        return """You are a behavior analysis agent that identifies patterns in user investigation behavior.
Analyze user events, investigation sessions, and accepted/rejected recommendations to extract:
1. Recurring investigation patterns (e.g., "user always checks traces before logs")
2. Preference adjustments (e.g., "user prefers conservative recommendations")
3. Success patterns (e.g., "user's preferred steps for latency incidents")

Output must be valid JSON matching the schema."""

    def get_output_schema(self):
        return BehaviorMinerOutput

    async def analyze(
        self,
        user_events: list,
        recent_sessions: list,
        accepted_recommendations: list,
        rejected_recommendations: list,
    ) -> BehaviorMinerOutput:
        """Analyze user behavior and return patterns."""
        context = {
            "user_events": user_events,
            "recent_sessions": recent_sessions,
            "accepted_recommendations": accepted_recommendations,
            "rejected_recommendations": rejected_recommendations,
        }

        prompt = """Analyze the user's investigation behavior and extract:
1. Patterns: Recurring investigation sequences or preferences
2. Preference adjustments: Changes in user preferences based on actions
3. Summary: Brief summary of key behavioral insights

Return JSON with patterns (list of Pattern objects), preference_adjustments (list), and summary (string)."""

        return await self.execute(prompt, context)
