#!/bin/bash
# run_tests.sh — Run all AIDog tests (backend + frontend)
# Usage: ./run_tests.sh [--backend-only] [--frontend-only] [-v]
set -e

ROOT="$(cd "$(dirname "$0")" && pwd)"
BACKEND="$ROOT/backend"
FRONTEND="$ROOT/frontend"

RUN_BACKEND=true
RUN_FRONTEND=true
VERBOSE=""

for arg in "$@"; do
  case $arg in
    --backend-only)  RUN_FRONTEND=false ;;
    --frontend-only) RUN_BACKEND=false ;;
    -v|--verbose)    VERBOSE="-v" ;;
  esac
done

PASS=0
FAIL=0

print_header() {
  echo ""
  echo "════════════════════════════════════════"
  echo "  $1"
  echo "════════════════════════════════════════"
}

# ── Backend ────────────────────────────────────────────────────────────────────
if $RUN_BACKEND; then
  print_header "BACKEND TESTS (pytest)"
  cd "$BACKEND"

  # Activate venv if it exists
  if [ -d "venv" ]; then
    source venv/bin/activate
  fi

  # Install test dependencies if needed
  pip install pytest pytest-asyncio httpx --quiet 2>/dev/null || true

  # Set test env vars
  export DD_MODE=mock
  export DATABASE_URL="sqlite:///:memory:"
  export SECRET_KEY="test-secret-key-for-pytest"
  export DATADOG_SITE="datadoghq.com"
  export DATADOG_API_KEY="test"
  export DATADOG_APP_KEY="test"
  export MINIMAX_API_KEY="${MINIMAX_API_KEY:-test-key}"

  if python -m pytest tests/ $VERBOSE \
      --tb=short \
      --asyncio-mode=auto \
      -q 2>&1; then
    echo "✓ Backend tests passed"
    PASS=$((PASS + 1))
  else
    echo "✗ Backend tests FAILED"
    FAIL=$((FAIL + 1))
  fi
fi

# ── Frontend ───────────────────────────────────────────────────────────────────
if $RUN_FRONTEND; then
  print_header "FRONTEND TESTS (jest)"
  cd "$FRONTEND"

  # Install deps if node_modules is missing or jest not present
  if [ ! -f "node_modules/.bin/jest" ]; then
    echo "Installing frontend test dependencies..."
    npm install --silent
  fi

  if npm run test:ci 2>&1; then
    echo "✓ Frontend tests passed"
    PASS=$((PASS + 1))
  else
    echo "✗ Frontend tests FAILED"
    FAIL=$((FAIL + 1))
  fi
fi

# ── Summary ────────────────────────────────────────────────────────────────────
print_header "RESULTS"
echo "  Passed suites: $PASS"
echo "  Failed suites: $FAIL"
echo ""

if [ $FAIL -gt 0 ]; then
  exit 1
fi
exit 0
