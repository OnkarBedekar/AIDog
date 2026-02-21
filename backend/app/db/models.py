"""SQLAlchemy database models."""
from sqlalchemy import Column, Integer, String, DateTime, Text, JSON, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
from typing import Optional

from app.db.session import Base


class User(Base):
    """User model."""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    role = Column(String, nullable=False)  # SRE, Backend, ML, Product
    password_hash = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    investigation_sessions = relationship("InvestigationSession", back_populates="user")
    recommendations = relationship("Recommendation", back_populates="user")
    memory_profile = relationship("MemoryProfile", back_populates="user", uselist=False)


class OrgConfig(Base):
    """Organization configuration."""
    __tablename__ = "org_configs"

    id = Column(Integer, primary_key=True, index=True)
    datadog_site = Column(String, nullable=True)
    default_time_window = Column(Integer, default=3600)  # seconds
    tags_of_interest = Column(JSON, default=list)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class InvestigationSession(Base):
    """Investigation session tracking."""
    __tablename__ = "investigation_sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    ended_at = Column(DateTime(timezone=True), nullable=True)
    context = Column(JSON, default=dict)

    # Relationships
    user = relationship("User", back_populates="investigation_sessions")
    events = relationship("InvestigationEvent", back_populates="session")


class InvestigationEvent(Base):
    """Individual investigation event."""
    __tablename__ = "investigation_events"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("investigation_sessions.id"), nullable=False)
    kind = Column(String, nullable=False)  # open_dashboard, run_query, click_trace, filter_logs, etc.
    payload = Column(JSON, default=dict)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    session = relationship("InvestigationSession", back_populates="events")


class Incident(Base):
    """Incident model."""
    __tablename__ = "incidents"

    id = Column(Integer, primary_key=True, index=True)
    source = Column(String, default="datadog")
    title = Column(String, nullable=False)
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    severity = Column(String, nullable=False)  # critical, warning, info
    services = Column(JSON, default=list)
    state = Column(String, default="open")  # open, investigating, resolved, closed
    monitor_id = Column(String, nullable=True)
    toto_forecasts = Column(JSON, default=list)   # List[TotoForecast] dicts
    agentcore_session_id = Column(String, nullable=True)  # AgentCore session for agent-trace

    # Relationships
    recommendations = relationship("Recommendation", back_populates="incident")


class Recommendation(Base):
    """Recommendation model."""
    __tablename__ = "recommendations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    incident_id = Column(Integer, ForeignKey("incidents.id"), nullable=True)
    type = Column(String, nullable=False)  # monitor_tune, dashboard, slo, shortcut, hypothesis
    content = Column(JSON, nullable=False)
    confidence = Column(Integer, default=0)  # 0-100
    status = Column(String, default="proposed")  # proposed, accepted, rejected
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="recommendations")
    incident = relationship("Incident", back_populates="recommendations")


class MemoryProfile(Base):
    """User memory profile for personalization."""
    __tablename__ = "memory_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    preferences = Column(JSON, default=dict)  # action_style, noise_tolerance, focus_areas
    patterns = Column(JSON, default=list)  # Learned patterns
    shortcuts = Column(JSON, default=list)  # User shortcuts
    success_map = Column(JSON, default=dict)  # incident_signature -> preferred_steps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="memory_profile")
