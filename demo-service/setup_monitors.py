"""Setup Datadog monitors for demo-service."""
import os
import sys
import httpx
import json

DATADOG_API_KEY = os.environ.get("DATADOG_API_KEY", "17b06505123b2b29ce2973deb131f02d")
DATADOG_APP_KEY = os.environ.get("DATADOG_APP_KEY", "ddaeebac-3fd1-4d11-9d4d-7c24cac0c189")
DATADOG_SITE = os.environ.get("DATADOG_SITE", "datadoghq.com")
BASE_URL = f"https://api.{DATADOG_SITE}/api/v1"

HEADERS = {
    "DD-API-KEY": DATADOG_API_KEY,
    "DD-APPLICATION-KEY": DATADOG_APP_KEY,
    "Content-Type": "application/json",
}

MONITORS = [
    {
        "name": "demo-service: High Error Rate",
        "type": "metric alert",
        "query": "sum(last_5m):sum:demo.http.requests.count{status:500} / sum:demo.http.requests.count{*} > 0.05",
        "message": "Error rate exceeded 5% on demo-service. @slack-alerts",
        "tags": ["service:demo-service", "env:prod", "severity:critical"],
        "options": {
            "thresholds": {"critical": 0.05, "warning": 0.02},
            "notify_no_data": False,
            "renotify_interval": 0,
        },
    },
    {
        "name": "demo-service: P95 Latency Spike",
        "type": "metric alert",
        "query": "avg(last_5m):p95:demo.http.request.duration{*} > 500",
        "message": "P95 latency exceeded 500ms on demo-service. @slack-alerts",
        "tags": ["service:demo-service", "env:prod", "severity:warning"],
        "options": {
            "thresholds": {"critical": 1000, "warning": 500},
            "notify_no_data": False,
            "renotify_interval": 0,
        },
    },
    {
        "name": "demo-service: Service Down",
        "type": "metric alert",
        "query": "min(last_2m):avg:demo.http.requests.count{*}.as_rate() < 1",
        "message": "demo-service appears to be down (request rate < 1/s). @slack-alerts",
        "tags": ["service:demo-service", "env:prod", "severity:critical"],
        "options": {
            "thresholds": {"critical": 1},
            "notify_no_data": True,
            "no_data_timeframe": 2,
            "renotify_interval": 0,
        },
    },
]

def create_monitor(client: httpx.Client, monitor: dict) -> dict:
    resp = client.post(f"{BASE_URL}/monitor", json=monitor, headers=HEADERS)
    resp.raise_for_status()
    return resp.json()

def main():
    print(f"Creating {len(MONITORS)} Datadog monitors...")
    with httpx.Client(timeout=30.0) as client:
        for monitor in MONITORS:
            try:
                result = create_monitor(client, monitor)
                print(f"  [OK] Created monitor '{monitor['name']}' (ID: {result.get('id')})")
            except httpx.HTTPStatusError as e:
                print(f"  [ERROR] Failed to create '{monitor['name']}': {e.response.text}")
            except Exception as e:
                print(f"  [ERROR] Failed to create '{monitor['name']}': {e}")
    print("Done.")

if __name__ == "__main__":
    main()
