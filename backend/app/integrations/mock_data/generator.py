"""Mock data generator for Datadog operations."""
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import random
import json


# Incident scenarios
INCIDENT_SCENARIOS = {
    "db_latency_spike": {
        "services": ["user-service", "payment-service", "database"],
        "symptom": "High p95 latency",
        "error_code": "TIMEOUT",
        "deploy_present": True,
    },
    "ai_quality_drift": {
        "services": ["llm-service", "retrieval-service", "embedding-service"],
        "symptom": "Quality degradation",
        "error_code": "RETRIEVAL_MISMATCH",
        "deploy_present": False,
    },
}


async def generate_mock_response(
    tool_name: str, arguments: Dict[str, Any]
) -> Dict[str, Any]:
    """Generate mock response based on tool name and arguments."""
    if tool_name == "get_active_monitors":
        return {"monitors": _generate_monitors(arguments)}
    elif tool_name == "get_monitor_details":
        return {"monitor": _generate_monitor_details(arguments.get("monitor_id"))}
    elif tool_name == "query_metrics":
        return {"metrics": _generate_metrics(arguments)}
    elif tool_name == "search_logs":
        return {"logs": _generate_logs(arguments)}
    elif tool_name == "fetch_traces":
        return {"traces": _generate_traces(arguments)}
    elif tool_name == "get_service_dependencies":
        return {"dependencies": _generate_dependencies(arguments)}
    elif tool_name == "get_deploy_markers":
        return {"markers": _generate_deploy_markers(arguments)}
    else:
        return {"error": f"Unknown tool: {tool_name}"}


def _generate_monitors(arguments: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Generate mock monitors."""
    monitors = [
        {
            "id": "mon_001",
            "name": "High Error Rate - user-service",
            "type": "metric alert",
            "query": "sum:http.errors{service:user-service}",
            "status": "alert",
            "severity": "critical",
            "tags": ["service:user-service", "env:production"],
            "created_at": (datetime.now() - timedelta(hours=2)).isoformat(),
        },
        {
            "id": "mon_002",
            "name": "P95 Latency Spike - payment-service",
            "type": "metric alert",
            "query": "p95:http.request.duration{service:payment-service}",
            "status": "alert",
            "severity": "warning",
            "tags": ["service:payment-service", "env:production"],
            "created_at": (datetime.now() - timedelta(minutes=30)).isoformat(),
        },
        {
            "id": "mon_003",
            "name": "Database Connection Pool Exhausted",
            "type": "metric alert",
            "query": "avg:db.connections.active{service:database}",
            "status": "alert",
            "severity": "critical",
            "tags": ["service:database", "env:production"],
            "created_at": (datetime.now() - timedelta(hours=1)).isoformat(),
        },
        {
            "id": "mon_004",
            "name": "LLM Quality Score Drop",
            "type": "metric alert",
            "query": "avg:llm.quality_score{service:llm-service}",
            "status": "alert",
            "severity": "warning",
            "tags": ["service:llm-service", "env:production"],
            "created_at": (datetime.now() - timedelta(minutes=45)).isoformat(),
        },
    ]

    # Filter by tags if provided
    tags = arguments.get("tags", [])
    if tags:
        monitors = [
            m
            for m in monitors
            if any(tag in str(m.get("tags", [])) for tag in tags)
        ]

    return monitors


def _generate_monitor_details(monitor_id: str) -> Dict[str, Any]:
    """Generate detailed monitor information."""
    base_monitor = {
        "id": monitor_id,
        "name": f"Monitor {monitor_id}",
        "type": "metric alert",
        "query": "sum:http.errors{service:user-service}",
        "status": "alert",
        "severity": "critical",
        "message": "Monitor is currently alerting",
        "thresholds": {"critical": 10, "warning": 5},
        "current_value": 15.5,
        "tags": ["service:user-service", "env:production"],
        "created_at": (datetime.now() - timedelta(hours=2)).isoformat(),
        "updated_at": datetime.now().isoformat(),
    }

    return base_monitor


def _generate_metrics(arguments: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Generate mock metrics data as a list of series (Datadog format)."""
    query = arguments.get("query", "")
    from_ts = arguments.get("from_ts", int((datetime.now() - timedelta(hours=1)).timestamp()))
    to_ts = arguments.get("to_ts", int(datetime.now().timestamp()))

    # Generate time series with realistic variation keyed to wall-clock time
    # so data changes between API calls (charts actually move)
    seed_offset = int(datetime.now().timestamp()) // 60  # changes every minute
    pointlist = []
    current_ts = from_ts
    step = 0
    while current_ts <= to_ts:
        noise = random.uniform(-0.05, 0.05)
        if "latency" in query.lower() or "duration" in query.lower():
            base = 150 if current_ts < to_ts - 1800 else 350
            value = base * (1 + noise) + (seed_offset % 50)
        elif "error" in query.lower() or "500" in query:
            base = 0.5 if current_ts < to_ts - 1800 else 8.0
            value = base * (1 + noise) + (seed_offset % 3) * 0.1
        else:
            value = 1000 + (seed_offset % 200) + random.uniform(-20, 20)
        pointlist.append([current_ts * 1000, round(value, 3)])  # ms timestamps
        current_ts += 60
        step += 1

    metric_name = query.split("{")[0].lstrip("sum:p95:avg:").strip() if query else "metric"
    return [
        {
            "metric": metric_name,
            "pointlist": pointlist,
            "tags": ["service:demo-service", "env:production"],
        }
    ]


def _generate_logs(arguments: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Generate mock log entries."""
    query = arguments.get("query", "")
    limit = arguments.get("limit", 100)
    from_ts = arguments.get("from_ts", int((datetime.now() - timedelta(hours=1)).timestamp()))

    logs = []
    for i in range(min(limit, 50)):  # Cap at 50 for demo
        log_time = from_ts + (i * 60)
        logs.append({
            "id": f"log_{i:06d}",
            "timestamp": log_time * 1000,  # milliseconds
            "message": f"ERROR: Request failed with timeout after 5s",
            "level": "error" if i % 3 == 0 else "info",
            "service": "user-service",
            "tags": ["env:production", "service:user-service"],
            "attributes": {
                "http.status_code": 500 if i % 3 == 0 else 200,
                "http.method": "POST",
                "http.url": "/api/users",
            },
        })

    return logs


def _generate_traces(arguments: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Generate mock trace data."""
    service = arguments.get("service", "user-service")
    limit = arguments.get("limit", 100)
    from_ts = arguments.get("from_ts", int((datetime.now() - timedelta(hours=1)).timestamp()))

    traces = []
    for i in range(min(limit, 20)):  # Cap at 20 for demo
        trace_time = from_ts + (i * 180)  # Every 3 minutes
        traces.append({
            "trace_id": f"trace_{i:012d}",
            "span_id": f"span_{i:012d}",
            "service": service,
            "resource": "/api/users",
            "operation": "http.request",
            "start": trace_time * 1000000,  # microseconds
            "duration": random.randint(100000, 5000000),  # 100ms to 5s
            "error": i % 5 == 0,  # 20% error rate
            "tags": {
                "env": "production",
                "service": service,
                "http.method": "POST",
                "http.status_code": 500 if i % 5 == 0 else 200,
            },
        })

    return traces


def _generate_dependencies(arguments: Dict[str, Any]) -> Dict[str, Any]:
    """Generate service dependency graph."""
    service = arguments.get("service", "user-service")

    dependencies = {
        "service": service,
        "dependencies": [
            {
                "service": "database",
                "type": "database",
                "calls": 150,
                "errors": 5,
            },
            {
                "service": "auth-service",
                "type": "http",
                "calls": 80,
                "errors": 2,
            },
        ],
        "dependents": [
            {
                "service": "api-gateway",
                "type": "http",
                "calls": 200,
                "errors": 10,
            },
        ],
    }

    return dependencies


def _generate_deploy_markers(arguments: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Generate deployment markers."""
    from_ts = arguments.get("from_ts", int((datetime.now() - timedelta(hours=1)).timestamp()))
    to_ts = arguments.get("to_ts", int(datetime.now().timestamp()))

    markers = [
        {
            "id": "deploy_001",
            "service": "user-service",
            "version": "v1.2.3",
            "timestamp": (from_ts + 1800) * 1000,  # 30 minutes ago
            "environment": "production",
            "deployed_by": "ci/cd",
        },
        {
            "id": "deploy_002",
            "service": "payment-service",
            "version": "v2.1.0",
            "timestamp": (from_ts + 3600) * 1000,  # 1 hour ago
            "environment": "production",
            "deployed_by": "ci/cd",
        },
    ]

    # Filter by time range
    markers = [
        m
        for m in markers
        if from_ts * 1000 <= m["timestamp"] <= to_ts * 1000
    ]

    return markers
