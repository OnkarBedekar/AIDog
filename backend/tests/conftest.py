"""Shared pytest fixtures for AIDog backend tests."""
import os
import uuid

# Set env vars BEFORE any app imports so pydantic-settings picks them up
os.environ["DD_MODE"] = "mock"
os.environ["DATADOG_SITE"] = "datadoghq.com"
os.environ["DATADOG_API_KEY"] = "test-api-key"
os.environ["DATADOG_APP_KEY"] = "test-app-key"
os.environ["DATABASE_URL"] = "sqlite:///:memory:"
os.environ["SECRET_KEY"] = "test-secret-key-for-pytest"
os.environ["MINIMAX_API_KEY"] = os.environ.get("MINIMAX_API_KEY", "test-minimax-key")

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.db.session import Base, get_db

SQLALCHEMY_TEST_URL = "sqlite:///:memory:"


@pytest.fixture(scope="session")
def engine():
    """Single in-memory SQLite engine shared across the test session."""
    eng = create_engine(
        SQLALCHEMY_TEST_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,  # All connections share the same in-memory DB
    )
    Base.metadata.create_all(bind=eng)
    yield eng
    eng.dispose()


@pytest.fixture(scope="function")
def db(engine):
    """Per-test DB session that rolls back uncommitted changes after each test."""
    TestSession = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = TestSession()
    try:
        yield session
    finally:
        session.rollback()
        session.close()


@pytest.fixture(scope="function")
def client(db):
    """TestClient with get_db overridden to use the test session."""
    def override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app, raise_server_exceptions=True) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def auth_headers(client):
    """Signup a unique test user per test and return Authorization headers."""
    email = f"testuser_{uuid.uuid4().hex[:8]}@example.com"
    resp = client.post(
        "/api/auth/signup",
        json={"email": email, "password": "testpass123", "role": "SRE"},
    )
    assert resp.status_code == 200, f"Signup failed: {resp.status_code} {resp.text}"
    token = resp.json().get("token", "")
    return {"Authorization": f"Bearer {token}", "_email": email}
