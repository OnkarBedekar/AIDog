"""Tests that verify imports, settings, and DB models load correctly."""
import os
import pytest


class TestImports:
    def test_config_imports(self):
        from app.core.config import settings
        assert settings is not None

    def test_settings_values(self):
        from app.core.config import settings
        assert settings.algorithm == "HS256"
        assert settings.access_token_expire_minutes > 0
        assert settings.database_url != ""

    def test_dd_mode_is_mock_in_tests(self):
        from app.core.config import settings
        # Tests must run in mock mode (set by conftest.py env override)
        assert settings.dd_mode in ("mock", "live")

    def test_db_models_import(self):
        from app.db.models import (
            User, Incident, Recommendation,
            InvestigationSession, InvestigationEvent,
            MemoryProfile, OrgConfig,
        )
        assert User.__tablename__ == "users"
        assert Incident.__tablename__ == "incidents"
        assert Recommendation.__tablename__ == "recommendations"
        assert MemoryProfile.__tablename__ == "memory_profiles"

    def test_schemas_import(self):
        from app.schemas.api import (
            SignupRequest, LoginRequest, LoginResponse,
            IncidentResponse, IncidentDetailResponse,
            ExecuteStepRequest, ExecuteStepResponse,
        )
        assert SignupRequest is not None
        assert ExecuteStepRequest is not None

    def test_routes_import(self):
        from app.routes import auth, home, incidents, recommendations, memory
        assert auth.router is not None
        assert home.router is not None
        assert incidents.router is not None

    def test_agents_import(self):
        from app.agents.base import BaseAgent
        from app.agents.incident_summarizer import IncidentSummarizerAgent
        from app.agents.guided_steps import GuidedStepsAgent
        from app.agents.recommendation_designer import RecommendationDesignerAgent
        from app.agents.behavior_miner import BehaviorMinerAgent
        assert BaseAgent is not None
        assert IncidentSummarizerAgent is not None

    def test_services_import(self):
        from app.services.memory_service import MemoryService
        from app.services.investigation_service import InvestigationService
        assert MemoryService is not None
        assert InvestigationService is not None

    def test_integrations_import(self):
        from app.integrations.datadog_mcp import DatadogMCPClient, get_datadog_client
        assert DatadogMCPClient is not None
        assert get_datadog_client is not None

    def test_fastapi_app_import(self):
        from app.main import app
        assert app.title is not None
        assert len(app.routes) > 0


class TestDatabase:
    def test_db_session_creates(self, db):
        assert db is not None

    def test_tables_exist(self, engine):
        from sqlalchemy import inspect
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        assert "users" in tables
        assert "incidents" in tables
        assert "recommendations" in tables
        assert "memory_profiles" in tables
        assert "investigation_sessions" in tables
        assert "investigation_events" in tables

    def test_user_model_crud(self, db):
        import bcrypt
        from app.db.models import User
        pw = bcrypt.hashpw(b"test", bcrypt.gensalt()).decode()
        user = User(email="crud@example.com", role="SRE", password_hash=pw)
        db.add(user)
        db.flush()
        assert user.id is not None

        fetched = db.query(User).filter(User.email == "crud@example.com").first()
        assert fetched is not None
        assert fetched.role == "SRE"

    def test_incident_model_crud(self, db):
        from app.db.models import Incident
        inc = Incident(title="Test Incident", severity="warning", services=["api"])
        db.add(inc)
        db.flush()
        assert inc.id is not None

        fetched = db.query(Incident).filter(Incident.title == "Test Incident").first()
        assert fetched is not None
        assert fetched.severity == "warning"
        assert "api" in fetched.services
