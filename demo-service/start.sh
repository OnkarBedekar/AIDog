#!/bin/bash
set -e

echo "Starting demo-service..."

# Resolve python
PYTHON="${VIRTUAL_ENV:+$VIRTUAL_ENV/bin/python}"
if [ -z "$PYTHON" ] || [ ! -x "$PYTHON" ]; then
  PYTHON=$(command -v python3 2>/dev/null || command -v python)
fi

# Load Datadog credentials from backend .env (if present)
BACKEND_ENV="$(dirname "$0")/../backend/.env"
if [ -f "$BACKEND_ENV" ]; then
  while IFS='=' read -r key val; do
    [[ "$key" =~ ^(DATADOG_API_KEY|DATADOG_APP_KEY|DATADOG_SITE)$ ]] && export "$key"="$val"
  done < <(grep -E "^(DATADOG_API_KEY|DATADOG_APP_KEY|DATADOG_SITE)=" "$BACKEND_ENV")
  echo "Loaded Datadog keys from backend/.env"
fi

export DD_SERVICE=demo-service
export DD_ENV=prod
export DD_VERSION=1.0.0

# Start traffic generator in background
"$PYTHON" traffic.py &
TRAFFIC_PID=$!
echo "Traffic generator started (PID: $TRAFFIC_PID)"

cleanup() {
  echo "Stopping traffic generator..."
  kill $TRAFFIC_PID 2>/dev/null || true
}
trap cleanup EXIT INT TERM

echo "Starting demo-service on :8001 (metrics → Datadog direct API)"
"$PYTHON" -m uvicorn main:app --host 0.0.0.0 --port 8001 --reload
