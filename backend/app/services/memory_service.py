"""Memory service for personalization logic."""
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from app.db.models import MemoryProfile, User, Recommendation, InvestigationSession, InvestigationEvent
from app.core.logging import get_logger
import json

logger = get_logger(__name__)


class MemoryService:
    """Service for managing user memory profiles and personalization."""

    def __init__(self, db: Session):
        self.db = db

    def get_or_create_memory_profile(self, user_id: int) -> MemoryProfile:
        """Get or create memory profile for user."""
        profile = self.db.query(MemoryProfile).filter(
            MemoryProfile.user_id == user_id
        ).first()

        if not profile:
            # Create default profile based on user role
            user = self.db.query(User).filter(User.id == user_id).first()
            default_prefs = self._get_default_preferences(user.role if user else "SRE")

            profile = MemoryProfile(
                user_id=user_id,
                preferences=default_prefs,
                patterns=[],
                shortcuts=[],
                success_map={},
            )
            self.db.add(profile)
            self.db.commit()
            self.db.refresh(profile)

        return profile

    def _get_default_preferences(self, role: str) -> Dict[str, Any]:
        """Get default preferences based on role."""
        defaults = {
            "SRE": {
                "action_style": "conservative",
                "noise_tolerance": "low",
                "focus_areas": ["infra", "latency"],
            },
            "Backend": {
                "action_style": "moderate",
                "noise_tolerance": "medium",
                "focus_areas": ["infra", "errors"],
            },
            "ML": {
                "action_style": "moderate",
                "noise_tolerance": "medium",
                "focus_areas": ["quality", "latency"],
            },
            "Product": {
                "action_style": "conservative",
                "noise_tolerance": "high",
                "focus_areas": ["quality"],
            },
        }
        return defaults.get(role, defaults["SRE"])

    def generate_incident_signature(
        self,
        services: List[str],
        endpoint: Optional[str],
        symptom_type: str,
        error_code: Optional[str],
        deploy_present: bool,
    ) -> str:
        """Generate incident signature for pattern matching."""
        # Normalize services
        services_str = ",".join(sorted(services))
        endpoint_str = endpoint or "unknown"
        error_code_str = error_code or "none"
        deploy_str = "deploy" if deploy_present else "no_deploy"

        signature = f"{services_str}|{endpoint_str}|{symptom_type}|{error_code_str}|{deploy_str}"
        return signature

    def get_preferred_steps(
        self, user_id: int, incident_signature: str
    ) -> List[str]:
        """Get preferred steps for incident signature."""
        profile = self.get_or_create_memory_profile(user_id)
        success_map = profile.success_map or {}

        # Look up preferred steps for this signature
        preferred = success_map.get(incident_signature, {}).get("steps", [])
        return preferred

    def record_step_success(
        self,
        user_id: int,
        incident_signature: str,
        step_id: str,
    ):
        """Record successful step execution for an incident signature."""
        profile = self.get_or_create_memory_profile(user_id)
        success_map = profile.success_map or {}

        if incident_signature not in success_map:
            success_map[incident_signature] = {"steps": [], "count": 0}

        signature_data = success_map[incident_signature]

        # Add step if not already present
        if step_id not in signature_data["steps"]:
            signature_data["steps"].append(step_id)

        signature_data["count"] = signature_data.get("count", 0) + 1

        profile.success_map = success_map
        self.db.commit()

    def record_recommendation_acceptance(
        self,
        user_id: int,
        recommendation_id: int,
        recommendation_type: str,
    ):
        """Record recommendation acceptance to update preferences."""
        profile = self.get_or_create_memory_profile(user_id)
        preferences = profile.preferences or {}

        # Increase weight for this recommendation type
        type_weights = preferences.get("type_weights", {})
        type_weights[recommendation_type] = type_weights.get(recommendation_type, 0) + 1
        preferences["type_weights"] = type_weights

        profile.preferences = preferences
        self.db.commit()

    def record_recommendation_rejection(
        self,
        user_id: int,
        recommendation_id: int,
        recommendation_type: str,
        reason: Optional[str] = None,
    ):
        """Record recommendation rejection."""
        profile = self.get_or_create_memory_profile(user_id)
        preferences = profile.preferences or {}

        # Decrease weight for this recommendation type
        type_weights = preferences.get("type_weights", {})
        type_weights[recommendation_type] = max(0, type_weights.get(recommendation_type, 0) - 1)
        preferences["type_weights"] = type_weights

        # Store rejection reason if provided
        rejections = preferences.get("rejections", [])
        rejections.append({
            "type": recommendation_type,
            "reason": reason,
            "timestamp": str(self.db.query(User).filter(User.id == user_id).first().created_at),
        })
        preferences["rejections"] = rejections[-10:]  # Keep last 10

        profile.preferences = preferences
        self.db.commit()

    def update_preferences(
        self,
        user_id: int,
        preferences: Dict[str, Any],
    ):
        """Update user preferences."""
        profile = self.get_or_create_memory_profile(user_id)
        current_prefs = profile.preferences or {}
        current_prefs.update(preferences)
        profile.preferences = current_prefs
        self.db.commit()

    def update_shortcuts(
        self,
        user_id: int,
        shortcuts: List[Dict[str, Any]],
    ):
        """Update user shortcuts."""
        profile = self.get_or_create_memory_profile(user_id)
        profile.shortcuts = shortcuts
        self.db.commit()

    def add_pattern(
        self,
        user_id: int,
        pattern: Dict[str, Any],
    ):
        """Add learned pattern."""
        profile = self.get_or_create_memory_profile(user_id)
        patterns = profile.patterns or []
        patterns.append(pattern)
        profile.patterns = patterns[-20:]  # Keep last 20 patterns
        self.db.commit()
