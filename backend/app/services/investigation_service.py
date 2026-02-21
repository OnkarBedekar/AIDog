"""Investigation service for tracking investigation sessions."""
from typing import Dict, Any, Optional, List
from sqlalchemy.orm import Session
from datetime import datetime
from app.db.models import InvestigationSession, InvestigationEvent, User
from app.core.logging import get_logger

logger = get_logger(__name__)


class InvestigationService:
    """Service for managing investigation sessions and events."""

    def __init__(self, db: Session):
        self.db = db

    def create_session(
        self,
        user_id: int,
        context: Optional[Dict[str, Any]] = None,
    ) -> InvestigationSession:
        """Create a new investigation session."""
        session = InvestigationSession(
            user_id=user_id,
            context=context or {},
        )
        self.db.add(session)
        self.db.commit()
        self.db.refresh(session)
        return session

    def end_session(self, session_id: int):
        """End an investigation session."""
        session = self.db.query(InvestigationSession).filter(
            InvestigationSession.id == session_id
        ).first()

        if session:
            session.ended_at = datetime.now()
            self.db.commit()

    def record_event(
        self,
        session_id: int,
        kind: str,
        payload: Optional[Dict[str, Any]] = None,
    ) -> InvestigationEvent:
        """Record an investigation event."""
        event = InvestigationEvent(
            session_id=session_id,
            kind=kind,
            payload=payload or {},
        )
        self.db.add(event)
        self.db.commit()
        self.db.refresh(event)
        return event

    def get_session_events(
        self,
        session_id: int,
    ) -> List[InvestigationEvent]:
        """Get all events for a session."""
        return self.db.query(InvestigationEvent).filter(
            InvestigationEvent.session_id == session_id
        ).order_by(InvestigationEvent.created_at).all()

    def get_user_sessions(
        self,
        user_id: int,
        limit: int = 10,
    ) -> List[InvestigationSession]:
        """Get recent investigation sessions for a user."""
        return self.db.query(InvestigationSession).filter(
            InvestigationSession.user_id == user_id
        ).order_by(InvestigationSession.started_at.desc()).limit(limit).all()

    def analyze_event_sequence(
        self,
        session_id: int,
    ) -> Dict[str, Any]:
        """Analyze event sequence to extract patterns."""
        events = self.get_session_events(session_id)

        # Extract sequence of event kinds
        sequence = [e.kind for e in events]

        # Count event types
        event_counts = {}
        for event in events:
            event_counts[event.kind] = event_counts.get(event.kind, 0) + 1

        return {
            "sequence": sequence,
            "event_counts": event_counts,
            "total_events": len(events),
            "duration_seconds": (
                (events[-1].created_at - events[0].created_at).total_seconds()
                if len(events) > 1
                else 0
            ),
        }
