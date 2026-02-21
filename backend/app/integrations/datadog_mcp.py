"""Datadog HTTP API integration."""
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import httpx

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)

DD_BASE_URL = f"https://api.{settings.datadog_site or 'datadoghq.com'}"

def _dd_headers() -> Dict[str, str]:
    return {
        "DD-API-KEY": settings.datadog_api_key or "",
        "DD-APPLICATION-KEY": settings.datadog_app_key or "",
        "Content-Type": "application/json",
    }


class DatadogMCPClient:
    """Real Datadog HTTP API client with mock fallback."""

    def __init__(self):
        self.mode = settings.dd_mode
        self._client = httpx.AsyncClient(timeout=15.0)

    async def _live_get(self, path: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        url = f"{DD_BASE_URL}{path}"
        try:
            resp = await self._client.get(url, headers=_dd_headers(), params=params or {})
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            logger.error(f"Datadog GET {path} failed: {e}")
            return {}

    async def _live_post(self, path: str, body: Dict[str, Any]) -> Dict[str, Any]:
        url = f"{DD_BASE_URL}{path}"
        try:
            resp = await self._client.post(url, headers=_dd_headers(), json=body)
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            logger.error(f"Datadog POST {path} failed: {e}")
            return {}

    async def _mock_call(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        from app.integrations.mock_data.generator import generate_mock_response
        return await generate_mock_response(tool_name, arguments)

    async def get_active_monitors(
        self, time_window: int = 3600, tags: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        if self.mode != "live":
            result = await self._mock_call("get_active_monitors", {"time_window": time_window, "tags": tags or []})
            return result.get("monitors", [])

        params = {"with_downtimes": "false", "monitor_tags": "service:demo-service"}
        data = await self._live_get("/api/v1/monitor", params)
        if isinstance(data, list):
            return [
                {
                    "id": str(m.get("id", "")),
                    "name": m.get("name", ""),
                    "query": m.get("query", ""),
                    "severity": "critical" if m.get("overall_state") == "Alert" else "warning",
                    "status": m.get("overall_state", "Unknown"),
                    "tags": m.get("tags", []),
                }
                for m in data
            ]
        return []

    async def get_monitor_details(self, monitor_id: str) -> Dict[str, Any]:
        if self.mode != "live":
            result = await self._mock_call("get_monitor_details", {"monitor_id": monitor_id})
            return result.get("monitor", {})

        data = await self._live_get(f"/api/v1/monitor/{monitor_id}")
        if data:
            return {
                "id": str(data.get("id", "")),
                "name": data.get("name", f"Monitor {monitor_id}"),
                "query": data.get("query", ""),
                "severity": "critical" if data.get("overall_state") == "Alert" else "warning",
                "tags": data.get("tags", []),
            }
        return {"id": monitor_id, "name": f"Monitor {monitor_id}", "severity": "warning", "tags": []}

    async def query_metrics(
        self,
        query: str,
        from_ts: Optional[int] = None,
        to_ts: Optional[int] = None,
    ) -> Dict[str, Any]:
        if from_ts is None:
            from_ts = int((datetime.now() - timedelta(hours=1)).timestamp())
        if to_ts is None:
            to_ts = int(datetime.now().timestamp())

        if self.mode != "live":
            result = await self._mock_call("query_metrics", {"query": query, "from_ts": from_ts, "to_ts": to_ts})
            return result.get("metrics", [])

        params = {"query": query, "from": from_ts, "to": to_ts}
        data = await self._live_get("/api/v1/query", params)
        return data.get("series", [])

    async def search_logs(
        self,
        query: str,
        from_ts: Optional[int] = None,
        to_ts: Optional[int] = None,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        if from_ts is None:
            from_ts = int((datetime.now() - timedelta(hours=1)).timestamp())
        if to_ts is None:
            to_ts = int(datetime.now().timestamp())

        if self.mode != "live":
            result = await self._mock_call("search_logs", {"query": query, "from_ts": from_ts, "to_ts": to_ts, "limit": limit})
            return result.get("logs", [])

        body = {
            "filter": {
                "query": query,
                "from": datetime.fromtimestamp(from_ts).strftime("%Y-%m-%dT%H:%M:%SZ"),
                "to": datetime.fromtimestamp(to_ts).strftime("%Y-%m-%dT%H:%M:%SZ"),
            },
            "page": {"limit": limit},
        }
        data = await self._live_post("/api/v2/logs/events/search", body)
        logs = data.get("data", [])
        return [
            {
                "id": log.get("id", ""),
                "message": log.get("attributes", {}).get("message", ""),
                "level": log.get("attributes", {}).get("status", "info"),
                "service": log.get("attributes", {}).get("service", ""),
                "timestamp": log.get("attributes", {}).get("timestamp", ""),
            }
            for log in logs
        ]

    async def fetch_traces(
        self,
        service: Optional[str] = None,
        resource: Optional[str] = None,
        from_ts: Optional[int] = None,
        to_ts: Optional[int] = None,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        if from_ts is None:
            from_ts = int((datetime.now() - timedelta(hours=1)).timestamp())
        if to_ts is None:
            to_ts = int(datetime.now().timestamp())

        if self.mode != "live":
            result = await self._mock_call("fetch_traces", {"service": service, "resource": resource, "from_ts": from_ts, "to_ts": to_ts, "limit": limit})
            return result.get("traces", [])

        params = {
            "filter[from]": datetime.fromtimestamp(from_ts).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "filter[to]": datetime.fromtimestamp(to_ts).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "page[limit]": min(limit, 1000),
        }
        if service:
            params["filter[service]"] = service
        data = await self._live_get("/api/v2/apm/traces", params)
        traces = data.get("data", [])
        return [
            {
                "trace_id": t.get("id", ""),
                "service": t.get("attributes", {}).get("service", service or ""),
                "resource": t.get("attributes", {}).get("resource_name", ""),
                "duration": t.get("attributes", {}).get("duration", 0),
                "status": t.get("attributes", {}).get("status", "ok"),
            }
            for t in traces
        ]

    async def get_service_dependencies(
        self,
        service: str,
        from_ts: Optional[int] = None,
        to_ts: Optional[int] = None,
    ) -> Dict[str, Any]:
        if self.mode != "live":
            result = await self._mock_call("get_service_dependencies", {"service": service, "from_ts": from_ts, "to_ts": to_ts})
            return result.get("dependencies", {})
        return {}

    async def get_deploy_markers(
        self,
        from_ts: Optional[int] = None,
        to_ts: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        if from_ts is None:
            from_ts = int((datetime.now() - timedelta(hours=1)).timestamp())
        if to_ts is None:
            to_ts = int(datetime.now().timestamp())

        if self.mode != "live":
            result = await self._mock_call("get_deploy_markers", {"from_ts": from_ts, "to_ts": to_ts})
            return result.get("markers", [])

        params = {
            "start": from_ts,
            "end": to_ts,
            "tags": "deployment",
        }
        data = await self._live_get("/api/v1/events", params)
        events = data.get("events", [])
        return [
            {
                "id": str(e.get("id", "")),
                "title": e.get("title", ""),
                "timestamp": e.get("date_happened", 0),
                "tags": e.get("tags", []),
            }
            for e in events
        ]


_datadog_client: Optional[DatadogMCPClient] = None


def get_datadog_client() -> DatadogMCPClient:
    global _datadog_client
    if _datadog_client is None:
        _datadog_client = DatadogMCPClient()
    return _datadog_client
