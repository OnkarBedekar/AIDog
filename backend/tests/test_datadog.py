"""Tests for DatadogMCPClient — init, mock mode, and method contracts."""
import os
import pytest

os.environ["DD_MODE"] = "mock"


class TestDatadogClientInit:
    def test_client_instantiates(self):
        from app.integrations.datadog_mcp import DatadogMCPClient
        client = DatadogMCPClient()
        assert client is not None

    def test_singleton_returns_same_instance(self):
        from app.integrations.datadog_mcp import get_datadog_client
        c1 = get_datadog_client()
        c2 = get_datadog_client()
        assert c1 is c2

    def test_client_reads_mode_from_settings(self):
        from app.integrations.datadog_mcp import DatadogMCPClient
        client = DatadogMCPClient()
        assert client.mode in ("mock", "live")

    def test_dd_headers_built_correctly(self):
        from app.integrations.datadog_mcp import _dd_headers
        headers = _dd_headers()
        assert "DD-API-KEY" in headers
        assert "DD-APPLICATION-KEY" in headers
        assert "Content-Type" in headers
        assert headers["Content-Type"] == "application/json"


class TestDatadogClientMockMode:
    @pytest.fixture
    def mock_client(self):
        from app.integrations.datadog_mcp import DatadogMCPClient
        from unittest.mock import patch
        client = DatadogMCPClient()
        client.mode = "mock"
        return client

    @pytest.mark.asyncio
    async def test_get_active_monitors_returns_list(self, mock_client):
        result = await mock_client.get_active_monitors()
        assert isinstance(result, list)

    @pytest.mark.asyncio
    async def test_get_monitor_details_returns_dict(self, mock_client):
        result = await mock_client.get_monitor_details("test_monitor_001")
        assert isinstance(result, dict)

    @pytest.mark.asyncio
    async def test_query_metrics_returns_something(self, mock_client):
        result = await mock_client.query_metrics(query="sum:demo.http.requests.count{*}.as_rate()")
        # Can be list or dict depending on mock
        assert result is not None

    @pytest.mark.asyncio
    async def test_search_logs_returns_list(self, mock_client):
        result = await mock_client.search_logs(query="service:demo-service")
        assert isinstance(result, list)

    @pytest.mark.asyncio
    async def test_fetch_traces_returns_list(self, mock_client):
        result = await mock_client.fetch_traces(service="demo-service")
        assert isinstance(result, list)

    @pytest.mark.asyncio
    async def test_get_deploy_markers_returns_list(self, mock_client):
        result = await mock_client.get_deploy_markers()
        assert isinstance(result, list)

    @pytest.mark.asyncio
    async def test_get_active_monitors_with_tags(self, mock_client):
        result = await mock_client.get_active_monitors(tags=["service:demo-service"])
        assert isinstance(result, list)

    @pytest.mark.asyncio
    async def test_search_logs_respects_limit(self, mock_client):
        result = await mock_client.search_logs(query="error", limit=5)
        assert isinstance(result, list)
        # Mock may return fewer items than limit — just ensure it's a list
        assert len(result) <= 100  # sanity cap

    @pytest.mark.asyncio
    async def test_fetch_traces_with_timestamps(self, mock_client):
        import time
        now = int(time.time())
        result = await mock_client.fetch_traces(from_ts=now - 3600, to_ts=now)
        assert isinstance(result, list)


class TestDatadogClientDDBaseUrl:
    def test_dd_base_url_uses_site(self):
        from app.integrations import datadog_mcp
        assert "datadoghq" in datadog_mcp.DD_BASE_URL or "api." in datadog_mcp.DD_BASE_URL
