# AIDog — Personalized, Predictive, Verified Observability Copilot

AIDog is an AI-powered incident investigation platform that combines real-time Datadog telemetry, Toto time-series forecasting, Minimax LLM agents, and AWS Bedrock AgentCore to help on-call engineers investigate and resolve incidents faster — and personalize to each engineer over time.

---

## Architecture Overview

```
┌──────────────────────────────────────────────────────────────────┐
│                     Frontend  (Next.js 14)                        │
│   Home Dashboard · Incident Room (7 tabs) · Personalization Studio│
└───────────────────────────┬──────────────────────────────────────┘
                            │  REST + JWT
┌───────────────────────────▼──────────────────────────────────────┐
│                      Backend  (FastAPI)                           │
│                                                                   │
│  ┌────────────────┐  ┌──────────────────┐  ┌──────────────────┐  │
│  │  6 Minimax LLM │  │  Toto Forecaster │  │  AgentCore       │  │
│  │     Agents     │  │  (anomaly score) │  │  Memory+Gateway  │  │
│  └───────┬────────┘  └────────┬─────────┘  └────────┬─────────┘  │
│          └───────────────────┼──────────────────────┘           │
│                    ┌─────────▼──────────┐                        │
│                    │  Integrations      │                        │
│                    │  Datadog · TestSprite · AWS Bedrock         │
│                    └────────────────────┘                        │
│                                                                   │
│  SQLite (MemoryProfile, Incidents)  ·  AgentCore (session memory) │
└──────────────────────────────────────────────────────────────────┘
                            │
┌───────────────────────────▼──────────────────────────────────────┐
│                   Demo Service  (port 8001)                       │
│   Synthetic traffic generator → Datadog metrics + APM traces     │
└──────────────────────────────────────────────────────────────────┘
```

---

## Components

| Component | Tech | What it does |
|-----------|------|-------------|
| **Frontend** | Next.js 14, TypeScript, TailwindCSS, Recharts | Incident Room with 7 tabs, live charts, command palette (`Cmd+K`), personalization studio |
| **Backend** | FastAPI, SQLAlchemy, Pydantic | REST API, JWT auth, investigation pipeline, all agent orchestration |
| **IncidentSummarizer** | Minimax LLM | Reads raw telemetry → produces incident envelope (title, severity, blast radius, primary symptom) |
| **HypothesisRanker** | Minimax LLM | Ranks root-cause hypotheses with confidence scores using telemetry + user patterns |
| **GuidedSteps** | Minimax LLM | Generates 3–7 prioritized investigation steps tailored to the user's role and working memory |
| **RecommendationDesigner** | Minimax LLM | Produces monitor tuning, dashboard, SLO, and shortcut recommendations |
| **BehaviorMiner** | Minimax LLM | Learns from accept/reject actions → updates preference weights and pattern signatures |
| **TestPlan** | Minimax LLM | Generates TestSprite test plans to verify accepted fixes |
| **Toto Forecaster** | `toto-ts`, HuggingFace | Datadog's open-weights time-series model. Forecasts next 60 points + computes anomaly score 0–100 |
| **AgentCore** | AWS Bedrock | Per-session ephemeral working memory (current incident context, tool outputs, open hypotheses) + tool catalog Gateway |
| **Datadog MCP** | httpx | Read-only HTTP client for monitors, metrics, logs, APM traces. Falls back to deterministic mock data |
| **TestSprite** | httpx | Generates and executes test plans. Mock or live mode |
| **Demo Service** | FastAPI, ddtrace | Sends `demo.http.requests.count` + `demo.http.request.duration` to Datadog with realistic error/latency patterns |
| **SQLite MemoryProfile** | SQLAlchemy | Durable per-user store: preferences, patterns, shortcuts, success_map |

---

## Project Structure

```
AIDog/
├── backend/
│   ├── app/
│   │   ├── main.py                 # FastAPI entry point, lifespan, CORS
│   │   ├── core/
│   │   │   ├── config.py           # All settings read from .env
│   │   │   ├── dependencies.py     # get_db, get_current_user
│   │   │   └── minimax_client.py   # Minimax LLM wrapper
│   │   ├── db/
│   │   │   ├── models.py           # User, Incident, Recommendation, MemoryProfile, InvestigationSession
│   │   │   ├── session.py          # DB session factory
│   │   │   └── seed.py             # Seeds 4 demo users (SRE, Backend, ML, Product)
│   │   ├── agents/
│   │   │   ├── base.py             # BaseAgent: async LLM runner + Pydantic validation + fallback
│   │   │   ├── incident_summarizer.py
│   │   │   ├── hypothesis_ranker.py
│   │   │   ├── guided_steps.py
│   │   │   ├── recommendation_designer.py
│   │   │   ├── behavior_miner.py
│   │   │   └── test_plan.py
│   │   ├── schemas/
│   │   │   ├── api.py              # Request/response Pydantic models
│   │   │   ├── agents.py           # Agent output schemas
│   │   │   └── toto.py             # TotoForecast schema
│   │   ├── integrations/
│   │   │   ├── datadog_mcp.py      # Datadog HTTP client (live + mock)
│   │   │   ├── toto_forecaster.py  # Toto time-series model (lazy-loaded singleton)
│   │   │   └── testsprite.py       # TestSprite client (mock or live)
│   │   ├── routes/
│   │   │   ├── auth.py             # /api/auth/{signup,login,me}
│   │   │   ├── home.py             # /api/home/overview
│   │   │   ├── incidents.py        # /api/incidents + /forecast + /agent-trace
│   │   │   ├── recommendations.py  # /api/recommendations
│   │   │   ├── tests.py            # /api/tests
│   │   │   └── memory.py           # /api/memory
│   │   ├── services/
│   │   │   ├── investigation_service.py  # Session + event tracking
│   │   │   └── memory_service.py         # MemoryProfile CRUD
│   │   └── agentcore/
│   │       ├── memory.py           # AgentCoreMemoryClient (AWS or in-process fallback)
│   │       ├── gateway.py          # AgentCoreGatewayClient + TOOL_OPENAPI_SPEC (7 tools)
│   │       └── runner.py           # InvestigationRunner — orchestrates the full 6-agent pipeline
│   ├── tests/
│   │   ├── conftest.py             # Fixtures: test client, DB, auth headers
│   │   ├── test_api.py             # Full API integration tests
│   │   ├── test_agentcore.py       # AgentCore memory + gateway + runner tests
│   │   ├── test_toto.py            # Toto forecaster unit tests
│   │   ├── test_datadog.py         # Datadog mock-mode tests
│   │   └── test_setup.py           # DB + import smoke tests
│   ├── agentcore_deploy.py         # One-time AWS AgentCore provisioning script
│   ├── pyproject.toml
│   └── .env
│
├── frontend/
│   ├── src/
│   │   ├── app/                    # Next.js App Router pages
│   │   │   ├── home/               # Personalized dashboard
│   │   │   ├── incidents/[id]/     # Incident Room
│   │   │   └── studio/             # Personalization Studio
│   │   ├── components/
│   │   │   ├── IncidentRoom.tsx    # 7-tab incident detail view
│   │   │   ├── ForecastPanel.tsx   # Toto anomaly chart (Recharts ComposedChart)
│   │   │   ├── AgentTracePanel.tsx # AgentCore session event timeline
│   │   │   ├── HomeOverview.tsx    # Dashboard cards
│   │   │   ├── EvidenceView.tsx    # Traces, logs, metrics display
│   │   │   └── CommandMenu.tsx     # Cmd+K command palette
│   │   └── lib/
│   │       ├── api.ts              # ApiClient with JWT auth
│   │       └── auth.ts             # Token management
│   └── __tests__/
│       └── components/
│           ├── ForecastPanel.test.tsx
│           └── AgentTracePanel.test.tsx
│
├── demo-service/
│   ├── main.py                     # FastAPI with /api/users, /api/payments, /api/search
│   ├── traffic.py                  # Generates continuous synthetic traffic
│   ├── setup_monitors.py           # Creates Datadog monitors for demo endpoints
│   └── start.sh                    # Starts service with ddtrace APM
│
├── docker-compose.yml              # PostgreSQL 15 + Redis 7
└── run_tests.sh                    # Unified backend + frontend test runner
```

---

## Quick Start — Mock Mode (No API Keys Required)

Mock mode runs the full application with deterministic fake Datadog data.

### 1. Backend

```bash
cd backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate

# Install dependencies
pip install -e ".[dev]"

# Create .env
cat > .env << 'EOF'
APP_ENV=dev
DATABASE_URL=sqlite:///./app.db
DD_MODE=mock
DATADOG_SITE=datadoghq.com
DATADOG_API_KEY=mock
DATADOG_APP_KEY=mock
MINIMAX_API_KEY=your-minimax-key-here
MINIMAX_MODEL=abab5.5-chat
MINIMAX_TEMPERATURE=0.3
TESTSPRITE_API_KEY=mock
TESTSPRITE_MODE=mock
SECRET_KEY=change-me-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440
EOF

# Start backend
uvicorn app.main:app --reload --port 8000
```

Backend: `http://localhost:8000` · API docs: `http://localhost:8000/docs`

### 2. Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend: `http://localhost:3000`

### 3. Sign up and explore

Open `http://localhost:3000`, create an account, and start investigating. Four demo incidents are pre-loaded.

---

## Live Mode Setup

### Backend `.env` — full configuration

```bash
# App
APP_ENV=dev
DATABASE_URL=sqlite:///./app.db          # or postgresql+psycopg2://...

# Datadog (set DD_MODE=live to use real telemetry)
DD_MODE=live
DATADOG_SITE=datadoghq.com
DATADOG_API_KEY=<your-datadog-api-key>
DATADOG_APP_KEY=<your-datadog-app-key>

# Minimax (required — powers all 6 agents)
MINIMAX_API_KEY=<your-minimax-api-key>
MINIMAX_MODEL=abab5.5-chat
MINIMAX_TEMPERATURE=0.3

# TestSprite (set TESTSPRITE_MODE=live for real test execution)
TESTSPRITE_API_KEY=<your-testsprite-api-key>
TESTSPRITE_MODE=live                     # or mock

# AWS Bedrock AgentCore (optional — falls back to in-process memory if not set)
AWS_REGION=us-east-2
AGENTCORE_MEMORY_ID=<from agentcore_deploy.py>
AGENTCORE_GATEWAY_ID=<from agentcore_deploy.py>

# Auth
SECRET_KEY=change-me-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440
```

### Provision AWS AgentCore (one-time)

Requires an IAM user with `bedrock-agentcore:*` and `iam:PassRole` permissions on the gateway role.

```bash
cd backend
source venv/bin/activate
pip install boto3

# First time: creates Memory + Gateway + tool target
AWS_PROFILE=<your-profile> python3 agentcore_deploy.py \
  --region us-east-2 \
  --role-arn arn:aws:iam::<account-id>:role/AIDogAgentCoreGatewayRole

# Copy the printed IDs into .env:
#   AGENTCORE_MEMORY_ID=...
#   AGENTCORE_GATEWAY_ID=...
```

### Start the Demo Service (optional — generates live Datadog metrics)

```bash
cd demo-service
pip install -r requirements.txt
DD_AGENT_HOST=localhost bash start.sh
```

Emits `demo.http.requests.count` and `demo.http.request.duration` to Datadog tagged by endpoint and status code.

### Pre-download the Toto model (optional — ~605 MB, enables anomaly forecasting)

```bash
pip install toto-ts
python3 -c "from toto.model.toto import Toto; Toto.from_pretrained('Datadog/Toto-Open-Base-1.0')"
```

The model loads lazily on first forecast request and pre-warms in a background thread at startup. If not installed, `/forecast` endpoints gracefully return empty results.

---

## All Commands

### Backend

| Command | What it does |
|---------|-------------|
| `uvicorn app.main:app --reload --port 8000` | Start dev server with hot reload |
| `uvicorn app.main:app --port 8000` | Start server without hot reload |
| `pip install -e ".[dev]"` | Install all Python dependencies |
| `python3 agentcore_deploy.py --region us-east-2 --role-arn <arn>` | Provision AWS AgentCore (run once) |
| `python3 -m pytest tests/ -v` | Run all backend tests |
| `python3 -m pytest tests/test_api.py -v` | Run API integration tests only |
| `python3 -m pytest tests/test_toto.py -v` | Run Toto forecasting tests only |
| `python3 -m pytest tests/test_agentcore.py -v` | Run AgentCore tests only |

### Frontend

| Command | What it does |
|---------|-------------|
| `npm run dev` | Start Next.js dev server on port 3000 |
| `npm run build` | Production build |
| `npm run start` | Start production server (requires build) |
| `npm run lint` | Run ESLint |
| `npm test` | Run Jest tests in watch mode |
| `npm run test:ci` | Run Jest tests once — for CI |

### Full Test Suite

| Command | What it does |
|---------|-------------|
| `./run_tests.sh` | Run all backend (pytest) + frontend (Jest) tests |
| `./run_tests.sh --backend-only` | Backend tests only |
| `./run_tests.sh --frontend-only` | Frontend tests only |
| `./run_tests.sh -v` | All tests with verbose output |

### Docker (PostgreSQL + Redis)

| Command | What it does |
|---------|-------------|
| `docker-compose up -d` | Start PostgreSQL on port 5432 and Redis on port 6379 |
| `docker-compose down` | Stop containers |
| `docker-compose down -v` | Stop containers and delete volumes |

---

## API Endpoints

| Method | Endpoint | What it does |
|--------|----------|-------------|
| `POST` | `/api/auth/signup` | Create a new account |
| `POST` | `/api/auth/login` | Get JWT token |
| `GET` | `/api/auth/me` | Current user info |
| `GET` | `/api/home/overview` | Personalized dashboard: services, endpoints, alerts, patterns, Toto anomalies |
| `GET` | `/api/incidents` | List all incidents |
| `POST` | `/api/incidents/from-monitor` | Create incident from a Datadog monitor ID |
| `GET` | `/api/incidents/{id}` | Full incident detail — runs the 6-agent investigation pipeline |
| `POST` | `/api/incidents/{id}/steps/{step_id}/execute` | Execute a guided investigation step |
| `GET` | `/api/incidents/{id}/forecast` | Toto anomaly forecast for the incident's key metrics |
| `GET` | `/api/incidents/{id}/agent-trace` | AgentCore session event timeline for this investigation |
| `GET` | `/api/recommendations` | List recommendations for the current user |
| `POST` | `/api/recommendations/{id}/accept` | Accept a recommendation (triggers test plan generation) |
| `POST` | `/api/recommendations/{id}/reject` | Reject a recommendation |
| `GET` | `/api/recommendations/{id}/export` | Get the export payload (Datadog monitor JSON, dashboard JSON, etc.) |
| `POST` | `/api/tests/generate` | Generate a TestSprite test plan from a recommendation |
| `POST` | `/api/tests/run/{plan_id}` | Execute a test plan |
| `GET` | `/api/tests/runs/{run_id}` | Get test run results |
| `GET` | `/api/memory/profile` | Get the current user's full memory profile |
| `PUT` | `/api/memory/preferences` | Update investigation preferences |
| `POST` | `/api/memory/shortcuts` | Add or update a shortcut |
| `GET` | `/health` | Health check — returns `{"status": "ok"}` |

---

## Investigation Pipeline

When `GET /api/incidents/{id}` is called, `InvestigationRunner` executes this sequence:

```
1. Create AgentCore Memory session
2. Fetch telemetry from Datadog
   ├── get_active_monitors()    → stored in session memory
   ├── query_metrics()          → stored in session memory
   ├── search_logs()            → stored in session memory
   └── fetch_traces()           → stored in session memory
3. Toto forecast on first metric series → anomaly_score stored in session memory
4. IncidentSummarizerAgent    → incident envelope (title, severity, blast_radius, primary_symptom)
5. HypothesisRankerAgent      → ranked hypotheses with confidence scores
6. GuidedStepsAgent           → 3–7 personalized next steps (uses working memory + user preferences)
7. RecommendationDesignerAgent → concrete recommendations (monitor/dashboard/SLO/shortcut)
8. Close AgentCore session, persist agentcore_session_id to DB
9. Return: envelope, evidence, hypotheses, guided_steps, recommendations, toto_forecasts, events
```

---

## The 6 Agents

All agents use Minimax (`abab5.5-chat`, temperature 0.3) with Pydantic schema validation and graceful fallbacks.

| Agent | Input | Output |
|-------|-------|--------|
| **IncidentSummarizer** | Telemetry bundle (monitors + metrics + logs + traces) | `IncidentEnvelope`: title, severity, blast_radius, primary_symptom, affected_services |
| **HypothesisRanker** | Telemetry + known user patterns | `HypothesisRanking`: list of hypotheses with confidence (0–100) and evidence pointers |
| **GuidedSteps** | Incident envelope + AgentCore working memory + user preferences | `GuidedStepsPlan`: 3–7 steps with title, rationale, action type, estimated minutes |
| **RecommendationDesigner** | Top 3 hypotheses + user preferences | `RecommendationPlan`: up to 5 recommendations of type monitor_tune / dashboard / slo / shortcut / hypothesis |
| **BehaviorMiner** | User actions (accept/reject/execute events) | Updated `preferences` dict and new `pattern` entries for MemoryProfile |
| **TestPlan** | Accepted recommendation | TestSprite-compatible test plan JSON |

---

## Toto Forecasting

| Property | Value |
|----------|-------|
| Model | `Datadog/Toto-Open-Base-1.0` |
| Size | ~605 MB (Apache 2.0) |
| Input | Last 512 data points of a metric series (z-score normalized) |
| Output | 60-point forecast: `predicted_median`, `lower_bound` (p10), `upper_bound` (p90) |
| Anomaly score | 0–100. Computed from how much the last 5 actual values exceed `upper_bound`. Score > 70 = anomalous |
| Loading | Lazy-loaded on first call, pre-warmed in background thread at startup |

---

## Memory & Personalization

| Layer | Storage | Lifetime | What's stored |
|-------|---------|----------|---------------|
| **SQLite MemoryProfile** | Local DB | Permanent, per-user | `preferences` (verbosity, auto-run), `patterns` (recurring incident signatures), `shortcuts` (saved queries), `success_map` (what worked per incident type) |
| **AWS AgentCore Memory** | AWS Bedrock | Ephemeral, per-session | Current incident context, tool outputs, open hypotheses, investigation graph |

The **Personalization Studio** (`/studio`) lets users view and edit their profile, reorder shortcuts via drag-and-drop, review learned patterns, and export the full profile as JSON.

---

## Troubleshooting

**`ModuleNotFoundError` when starting backend**
```bash
cd backend && source venv/bin/activate && pip install -e ".[dev]"
```

**`No module named pytest`**
```bash
# Use the venv Python explicitly
backend/venv/bin/python -m pytest tests/ -v
```

**Frontend fails to start**
```bash
cd frontend && rm -rf node_modules && npm install && npm run dev
```

**Toto model not found / forecast returns empty**
```bash
pip install toto-ts
python3 -c "from toto.model.toto import Toto; Toto.from_pretrained('Datadog/Toto-Open-Base-1.0')"
```

**AgentCore `AccessDeniedException`**
- Ensure the IAM user has `bedrock-agentcore:*` permissions
- Ensure `iam:PassRole` is granted on the gateway role
- Verify `AWS_PROFILE` is set: `AWS_PROFILE=<profile> python3 agentcore_deploy.py ...`
- Without AWS config, AgentCore falls back to an in-process dict (full functionality, no AWS cost)

**Datadog live mode returns empty data**
- Set `DD_MODE=live` in `.env`
- Verify `DATADOG_API_KEY` and `DATADOG_APP_KEY` are valid
- Start the demo service to generate metrics: `cd demo-service && bash start.sh`

**Port already in use**
```bash
# Backend on a different port
uvicorn app.main:app --reload --port 8001

# Frontend on a different port
npm run dev -- --port 3001
```
