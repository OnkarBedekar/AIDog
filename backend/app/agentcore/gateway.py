"""AWS Bedrock AgentCore Gateway client.

Registers Datadog + TestSprite + Toto as formal tool definitions in the
AgentCore Gateway.  The FastAPI backend acts as the implementation server;
Gateway provides the tool catalog for agent context injection and audit.

Tool calls are still executed directly via httpx (existing integrations).
The Gateway registration makes tools discoverable and auditable in AWS.

Falls back gracefully when AGENTCORE_GATEWAY_ID is not set.
"""
import json
import logging
from typing import Any, Dict, List, Optional

from app.core.config import settings

logger = logging.getLogger(__name__)

# OpenAPI 3.0 spec describing all tools exposed to AgentCore agents
TOOL_OPENAPI_SPEC = {
    "openapi": "3.0.3",
    "info": {
        "title": "AIDog Observability Tools",
        "version": "1.0.0",
        "description": "Datadog, Toto, and TestSprite tools for incident investigation.",
    },
    "paths": {
        "/tools/query_metrics": {
            "post": {
                "operationId": "query_metrics",
                "summary": "Query Datadog time-series metrics",
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "required": ["query"],
                                "properties": {
                                    "query": {"type": "string"},
                                    "from_ts": {"type": "integer"},
                                    "to_ts": {"type": "integer"},
                                },
                            }
                        }
                    },
                },
                "responses": {"200": {"description": "Metric time-series data"}},
            }
        },
        "/tools/search_logs": {
            "post": {
                "operationId": "search_logs",
                "summary": "Search Datadog logs",
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "required": ["query"],
                                "properties": {
                                    "query": {"type": "string"},
                                    "from_ts": {"type": "integer"},
                                    "to_ts": {"type": "integer"},
                                    "limit": {"type": "integer", "default": 50},
                                },
                            }
                        }
                    },
                },
                "responses": {"200": {"description": "Log events"}},
            }
        },
        "/tools/fetch_traces": {
            "post": {
                "operationId": "fetch_traces",
                "summary": "Fetch APM distributed traces",
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "service": {"type": "string"},
                                    "from_ts": {"type": "integer"},
                                    "to_ts": {"type": "integer"},
                                    "limit": {"type": "integer", "default": 50},
                                },
                            }
                        }
                    },
                },
                "responses": {"200": {"description": "APM traces"}},
            }
        },
        "/tools/get_active_monitors": {
            "post": {
                "operationId": "get_active_monitors",
                "summary": "Get active Datadog monitors",
                "requestBody": {
                    "required": False,
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "tags": {"type": "array", "items": {"type": "string"}},
                                    "time_window": {"type": "integer", "default": 3600},
                                },
                            }
                        }
                    },
                },
                "responses": {"200": {"description": "Active monitors"}},
            }
        },
        "/tools/toto_forecast": {
            "post": {
                "operationId": "toto_forecast",
                "summary": "Forecast metric anomalies using Toto",
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "required": ["series_name", "metric_values", "interval_seconds"],
                                "properties": {
                                    "series_name": {"type": "string"},
                                    "metric_values": {
                                        "type": "array",
                                        "items": {"type": "number"},
                                    },
                                    "interval_seconds": {"type": "integer"},
                                },
                            }
                        }
                    },
                },
                "responses": {"200": {"description": "Toto forecast with anomaly score"}},
            }
        },
        "/tools/generate_test_plan": {
            "post": {
                "operationId": "generate_test_plan",
                "summary": "Generate a TestSprite test plan from a recommendation",
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "required": ["recommendation"],
                                "properties": {
                                    "recommendation": {"type": "object"},
                                },
                            }
                        }
                    },
                },
                "responses": {"200": {"description": "Test plan ID"}},
            }
        },
        "/tools/run_tests": {
            "post": {
                "operationId": "run_tests",
                "summary": "Execute a TestSprite test plan",
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "required": ["plan_id"],
                                "properties": {
                                    "plan_id": {"type": "string"},
                                },
                            }
                        }
                    },
                },
                "responses": {"200": {"description": "Test run ID and status"}},
            }
        },
    },
}


class AgentCoreGatewayClient:
    """Registers and describes tools via AWS Bedrock AgentCore Gateway."""

    def __init__(self):
        self._gateway_id = settings.agentcore_gateway_id
        self._region = settings.aws_region
        self._registered = False
        self._use_aws = bool(self._gateway_id and self._region)

    def get_tool_definitions(self) -> List[Dict[str, Any]]:
        """Return a flat list of tool definitions for Minimax agent context injection.

        Each entry: {"name": str, "description": str, "parameters": dict}
        """
        tools = []
        for path, methods in TOOL_OPENAPI_SPEC["paths"].items():
            for _method, op in methods.items():
                schema = (
                    op.get("requestBody", {})
                    .get("content", {})
                    .get("application/json", {})
                    .get("schema", {})
                )
                tools.append(
                    {
                        "name": op["operationId"],
                        "description": op.get("summary", ""),
                        "parameters": schema,
                    }
                )
        return tools

    def register_tools(self) -> bool:
        """Idempotently register the tool OpenAPI spec with AWS AgentCore Gateway.

        Returns True on success, False if AWS is unavailable.
        Called once at startup (and by agentcore_deploy.py).
        """
        if not self._use_aws:
            logger.info("AgentCore Gateway: skipping registration (no AWS config).")
            return False

        if self._registered:
            return True

        try:
            import boto3

            client = boto3.client("bedrock-agentcore-control", region_name=self._region)
            client.create_mcp_gateway_target(
                gatewayId=self._gateway_id,
                targetName="aidog-observability-tools",
                targetType="openapi",
                payload=json.dumps(TOOL_OPENAPI_SPEC),
            )
            self._registered = True
            logger.info("AgentCore Gateway tools registered successfully.")
            return True
        except Exception as exc:
            # Target may already exist — that's fine
            if "already exists" in str(exc).lower() or "conflict" in str(exc).lower():
                self._registered = True
                logger.info("AgentCore Gateway tools already registered.")
                return True
            logger.warning(f"AgentCore Gateway registration failed: {exc}")
            return False


# Module-level singleton
_gateway_client: Optional[AgentCoreGatewayClient] = None


def get_gateway_client() -> AgentCoreGatewayClient:
    """Return the shared AgentCoreGatewayClient instance."""
    global _gateway_client
    if _gateway_client is None:
        _gateway_client = AgentCoreGatewayClient()
    return _gateway_client
