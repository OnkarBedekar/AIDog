"""Tests for AWS Bedrock AgentCore integration."""
import sys
import types
import pytest
from unittest.mock import MagicMock, patch, AsyncMock


# ── Mock bedrock-agentcore SDK ─────────────────────────────────────────────────

def _install_agentcore_mock():
    """Install a minimal stub of the bedrock-agentcore SDK."""
    pkg = types.ModuleType("bedrock_agentcore")
    mem_pkg = types.ModuleType("bedrock_agentcore.memory")
    const_pkg = types.ModuleType("bedrock_agentcore.memory.constants")

    class _MockSession:
        def __init__(self):
            self._turns = []

        def add_turns(self, messages):
            self._turns.extend(messages)

        def list_turns(self):
            return self._turns

        def search_memories(self, query, max_results=5):
            return [str(t) for t in self._turns[:max_results]]

    class _MockMemorySessionManager:
        def __init__(self, memory_id, region_name):
            self.memory_id = memory_id
            self.region_name = region_name
            self._sessions = {}

        def create_memory_session(self, actor_id, session_id):
            if session_id not in self._sessions:
                self._sessions[session_id] = _MockSession()
            return self._sessions[session_id]

    class _ConversationalMessage:
        def __init__(self, content, role):
            self.content = content
            self.role = role

        def __str__(self):
            return self.content

    class _MessageRole:
        USER = "user"
        ASSISTANT = "assistant"

    mem_pkg.MemorySessionManager = _MockMemorySessionManager
    const_pkg.ConversationalMessage = _ConversationalMessage
    const_pkg.MessageRole = _MessageRole

    sys.modules["bedrock_agentcore"] = pkg
    sys.modules["bedrock_agentcore.memory"] = mem_pkg
    sys.modules["bedrock_agentcore.memory.constants"] = const_pkg


_install_agentcore_mock()


# ── Fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture(autouse=True)
def reset_memory_singleton():
    """Reset the module-level memory client singleton between tests."""
    import app.agentcore.memory as mem_mod
    mem_mod._memory_client = None
    mem_mod._fallback_sessions.clear()
    yield
    mem_mod._memory_client = None
    mem_mod._fallback_sessions.clear()


@pytest.fixture(autouse=True)
def reset_gateway_singleton():
    import app.agentcore.gateway as gw_mod
    gw_mod._gateway_client = None
    yield
    gw_mod._gateway_client = None


# ── Memory tests ──────────────────────────────────────────────────────────────

def test_memory_client_creates_session():
    from app.agentcore.memory import AgentCoreMemoryClient

    client = AgentCoreMemoryClient()
    session_id = client.create_session(incident_id=1, user_id=42)
    assert "incident-1" in session_id
    assert "user-42" in session_id


def test_memory_client_store_and_retrieve():
    from app.agentcore.memory import AgentCoreMemoryClient

    client = AgentCoreMemoryClient()
    sid = client.create_session(1, 1)
    client.store(sid, "open_hypotheses", [{"id": "h1", "confidence": 80}])
    mem = client.retrieve(sid)
    assert mem["open_hypotheses"][0]["id"] == "h1"


def test_memory_client_search_fallback():
    from app.agentcore.memory import AgentCoreMemoryClient

    client = AgentCoreMemoryClient()
    sid = client.create_session(1, 1)
    client.store(sid, "current_incident", {"title": "High error rate on payments"})
    results = client.search(sid, "payments")
    assert len(results) >= 1
    assert any("payments" in r.lower() for r in results)


def test_memory_client_close_session():
    from app.agentcore.memory import AgentCoreMemoryClient

    client = AgentCoreMemoryClient()
    sid = client.create_session(1, 1)
    client.close_session(sid)
    mem = client.retrieve(sid)
    assert "closed_at" in mem


def test_memory_client_singleton():
    from app.agentcore.memory import get_memory_client

    a = get_memory_client()
    b = get_memory_client()
    assert a is b


# ── Gateway tests ─────────────────────────────────────────────────────────────

def test_gateway_client_tool_definitions():
    from app.agentcore.gateway import AgentCoreGatewayClient

    client = AgentCoreGatewayClient()
    tools = client.get_tool_definitions()
    assert len(tools) >= 7
    names = [t["name"] for t in tools]
    assert "query_metrics" in names
    assert "search_logs" in names
    assert "toto_forecast" in names
    assert "generate_test_plan" in names
    assert "run_tests" in names


def test_gateway_register_tools_skips_without_config():
    from app.agentcore.gateway import AgentCoreGatewayClient

    client = AgentCoreGatewayClient()
    # With no AWS config, should return False but not raise
    result = client.register_tools()
    assert result is False


def test_gateway_singleton():
    from app.agentcore.gateway import get_gateway_client

    a = get_gateway_client()
    b = get_gateway_client()
    assert a is b


# ── Runner tests ──────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_runner_run_returns_required_keys(client, auth_headers):
    """Integration: /api/incidents/{id} uses InvestigationRunner and returns envelope."""
    # First create an incident
    resp = client.post(
        "/api/incidents/from-monitor",
        params={"monitor_id": "test-monitor-1"},
        headers={"Authorization": auth_headers["Authorization"]},
    )
    assert resp.status_code == 200
    incident_id = resp.json()["id"]

    # Now fetch the incident detail (triggers InvestigationRunner)
    resp2 = client.get(
        f"/api/incidents/{incident_id}",
        headers={"Authorization": auth_headers["Authorization"]},
    )
    assert resp2.status_code == 200
    body = resp2.json()
    assert "envelope" in body
    assert "guided_steps" in body
    assert "evidence" in body
    assert "recommendations" in body


@pytest.mark.asyncio
async def test_forecast_endpoint_returns_200(client, auth_headers):
    """GET /api/incidents/{id}/forecast returns correct structure."""
    resp = client.post(
        "/api/incidents/from-monitor",
        params={"monitor_id": "test-monitor-forecast"},
        headers={"Authorization": auth_headers["Authorization"]},
    )
    incident_id = resp.json()["id"]

    resp2 = client.get(
        f"/api/incidents/{incident_id}/forecast",
        headers={"Authorization": auth_headers["Authorization"]},
    )
    assert resp2.status_code == 200
    body = resp2.json()
    assert "incident_id" in body
    assert "forecasts" in body
    assert isinstance(body["forecasts"], list)


@pytest.mark.asyncio
async def test_agent_trace_endpoint_returns_200(client, auth_headers):
    """GET /api/incidents/{id}/agent-trace returns correct structure."""
    resp = client.post(
        "/api/incidents/from-monitor",
        params={"monitor_id": "test-monitor-trace"},
        headers={"Authorization": auth_headers["Authorization"]},
    )
    incident_id = resp.json()["id"]

    resp2 = client.get(
        f"/api/incidents/{incident_id}/agent-trace",
        headers={"Authorization": auth_headers["Authorization"]},
    )
    assert resp2.status_code == 200
    body = resp2.json()
    assert "events" in body
    assert isinstance(body["events"], list)
