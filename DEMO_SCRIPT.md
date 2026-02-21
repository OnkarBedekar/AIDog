# AIDog — Judge Demo Script

> **Time target:** 5–7 minutes
> **One-line pitch:** AIDog is an AI copilot that pulls live Datadog telemetry, runs a 4-agent LLM pipeline powered by Minimax, and delivers a full incident diagnosis — ranked hypotheses, personalized investigation steps, and actionable recommendations — in one click.

---

## 0. Before You Start (Setup Checks)

Make sure these are running:
- **Demo service** on `:8001` — the fake microservice that generates real Datadog metrics
- **Backend** on `:8000` — FastAPI + AgentCore + all agents
- **Frontend** on `:3000` — Next.js UI

Confirm live data is flowing:
```
curl http://localhost:8001/health
# → {"status": "ok", "service": "demo-service", "version": "1.0.0"}
```

To spike errors before the demo (creates a visible incident):
```
curl http://localhost:8001/inject-errors?count=15
# Injects 30 synthetic 500s (15 on /api/users + 15 on /api/payments)
# Flushes immediately to Datadog
```

---

## 1. Opening Hook (30 seconds)

> "The average time to detect and triage a production incident is 23 minutes. Engineers are context-switching between monitors, logs, trace explorers, and dashboards — all manually.
>
> AIDog collapses that into a single click. It doesn't just alert you — it investigates alongside you."

---

## 2. The Demo Service → Datadog Pipeline (45 seconds)

**Point at the demo service code or the Datadog dashboard.**

> "We have a real microservice running — three endpoints: `/api/users`, `/api/payments`, `/api/search`. It's not mocked. Every 10 seconds, it batches and ships two real metrics directly to Datadog's v2 Series API:"

- **`demo.http.requests.count`** — request count per endpoint per status (COUNT type)
- **`demo.http.request.duration`** — p95 latency in ms per endpoint (GAUGE type)

> "We set up 3 real Datadog monitors watching this service:"

| Monitor | Condition |
|---------|-----------|
| High Error Rate | Error rate > 5% |
| P95 Latency Spike | p95 latency > 500ms |
| Service Down | Request rate < 1 req/s |

> "The demo service also has an `/inject-errors` endpoint — right now we've spiked it, so Datadog already knows something is wrong."

---

## 3. Click "Detect Live Incident" (30 seconds)

**Navigate to `/home`. Click the "Detect Live Incident" button.**

> "One click. The backend hits Datadog's REST APIs — monitors, metrics, logs, and APM traces — all in parallel. The IncidentSummarizerAgent reads the raw telemetry and synthesizes it into a structured incident envelope. An incident row is created in the database with `source: datadog_live`, and we're navigated straight into the investigation room."

---

## 4. The Agent Pipeline — What Just Happened (90 seconds)

**Switch to the "Memory" tab to show the Agent Trace.**

> "Behind that single click, 4 specialized agents fired sequentially. Let me walk you through exactly what each one did."

### Step 1 — Datadog Tool Calls (real HTTP, not mocked)

The runner called 4 Datadog APIs in order:

| Tool | Datadog Endpoint | What it fetched |
|------|-----------------|-----------------|
| `get_active_monitors` | `GET /api/v1/monitor` | All monitors in Alert/Warn state |
| `query_metrics` | `GET /api/v1/query` | `sum:demo.http.requests.count{service:demo-service}.as_rate()` — last 1 hour |
| `search_logs` | `POST /api/v2/logs/events/search` | Last 50 logs from `service:demo-service` |
| `fetch_traces` | `GET /api/v2/apm/traces` | Last 50 APM traces filtered by service |

> "Every single one of these is a real Datadog API call. The result — monitors, metrics, logs, traces — is bundled and stored in an AgentCore working-memory session."

### Step 2 — Toto Forecast

> "Before any LLM runs, we pass the raw metric time series into Toto — Datadog's open-weights foundation model for time-series forecasting. `Datadog/Toto-Open-Base-1.0`. It runs 64-sample inference on 512 data points, z-score normalized. It outputs a predicted median, 10th/90th percentile bounds, and an **anomaly score from 0–100**. Anything above 70 is flagged as anomalous. This is not a threshold rule — it's a learned model."

### Step 3 — IncidentSummarizerAgent (Minimax)

> "Agent 1: IncidentSummarizerAgent. It receives the full telemetry bundle — monitors, metrics, logs, traces — and returns a structured incident envelope: title, description, affected services, blast radius, severity, primary symptom, and initial root-cause hypothesis. All powered by Minimax."

### Step 4 — HypothesisRankerAgent (Minimax)

> "Agent 2: HypothesisRankerAgent. It receives the telemetry evidence plus any patterns the user has learned from previous investigations. It generates 3–5 ranked hypotheses, each with a confidence score and evidence pointers — which specific metrics, logs, or traces support this hypothesis."

### Step 5 — GuidedStepsAgent (Minimax, personalized)

> "Agent 3: GuidedStepsAgent. This is where personalization kicks in. It receives the incident envelope, the top hypotheses, AND the user's memory profile — their past learned patterns, their role preferences. It generates 3–7 prioritized investigation steps, each specifying an action type like `query_metrics`, `search_logs`, or `fetch_traces`, with the exact parameters. Steps for an SRE look different than steps for a backend engineer."

### Step 6 — RecommendationDesignerAgent (Minimax)

> "Agent 4: RecommendationDesignerAgent. It takes the top hypotheses and user preferences and designs concrete, exportable recommendations: monitor threshold tuning, new dashboard panels, SLO definitions, or reusable investigation shortcuts. Each one comes with an export payload JSON and an optional CLI snippet."

---

## 5. Minimax LLM — Under the Hood (20 seconds)

> "Every agent is powered by **MiniMax-M2.5-highspeed** — 100 tokens/second, 204k context window. We access it through its Anthropic-compatible API endpoint, so the Anthropic SDK drives it. Every agent call returns validated JSON, parsed against a Pydantic schema. If Minimax returns malformed output, the agent falls back gracefully so the pipeline never crashes."

---

## 6. Walk the Tabs (60 seconds)

**Click through the tabs in IncidentRoom:**

### Overview Tab
> "The incident envelope from IncidentSummarizerAgent — title, description, primary symptom, blast radius, severity. Structured output, not freeform text."

### Evidence Tab
> "Raw Datadog telemetry — monitors, metrics, logs, traces — exactly as returned by the 4 API calls. Engineers can inspect the raw signal."

### Forecast Tab *(click it — lazy loaded)*
> "Toto forecast loads on demand. You see the historical metric, the predicted median going forward, and the confidence band. The anomaly score — say 84 — tells you this is statistically anomalous, not just above a static threshold."

### Guided Steps Tab
> "Personalized investigation steps from GuidedStepsAgent. Each step has an action type and parameters — so you can literally click Execute and it runs the Datadog query for you. The steps are ordered by priority and shaped by this user's learned patterns from past investigations."

### Recommendations Tab
> "Concrete outputs from RecommendationDesignerAgent: adjust monitor thresholds, create a new dashboard, define an SLO. Each has a confidence score and an exportable JSON payload. This isn't advice — it's a diff you can apply."

---

## 7. TestSprite — Validate the Fix (30 seconds)

**Click the Tests tab.**

> "Once you've identified and remediated the incident, you want to verify the fix didn't break anything. We integrated TestSprite — it generates and runs a test plan against our service. The TestSpriteClient creates a named test plan with steps, executes it, and polls for results. In live mode with an API key, these run as real browser or API tests. The results land right here in the Tests tab — pass/fail, total tests, artifacts."

---

## 8. Memory & Personalization (20 seconds)

> "After every investigation, AIDog writes a new learned pattern to the user's memory profile: what service broke, what severity, what was the top hypothesis, what was the top recommendation. Next time a similar incident fires, HypothesisRanker and GuidedSteps both read those patterns and give you more targeted output. The system gets smarter the more you use it."

---

## 9. AWS Bedrock AgentCore (15 seconds)

> "The entire pipeline runs inside an AgentCore session. We register 7 tools in AgentCore's tool catalog via an OpenAPI 3.0 spec — query_metrics, search_logs, fetch_traces, get_active_monitors, get_deploy_markers, toto_forecast, generate_test_plan. The session tracks every tool call and agent event as a timestamped log — that's what powers the agent trace view. When the pipeline completes, the session closes."

---

## 10. Closing (20 seconds)

> "To summarize what happened in those few seconds:
>
> — 4 real Datadog APIs were called
> — Toto ran actual time-series inference on live metric data
> — 4 LLM agents fired sequentially using Minimax
> — The user got ranked hypotheses, personalized steps, and exportable recommendations
> — TestSprite validated the service post-remediation
> — A new pattern was written to the user's memory profile for future incidents
>
> That's AIDog."

---

## Quick Reference — Key Technical Facts

| Component | Detail |
|-----------|--------|
| LLM | MiniMax-M2.5-highspeed · 100 tps · 204k context · via Anthropic SDK |
| Agents | IncidentSummarizer → HypothesisRanker → GuidedSteps → RecommendationDesigner |
| Datadog tools | get_active_monitors, query_metrics, search_logs, fetch_traces, get_deploy_markers |
| Datadog APIs | v1/monitor · v1/query · v2/logs/events/search · v2/apm/traces · v1/events |
| Datadog metrics sent | demo.http.requests.count (COUNT) · demo.http.request.duration (GAUGE p95) every 10s |
| Toto model | Datadog/Toto-Open-Base-1.0 · 512-point context · 64 samples · anomaly score 0–100 |
| Anomaly threshold | Score > 70 = anomalous |
| AgentCore | Session memory + 7-tool OpenAPI catalog · every step logged |
| TestSprite | create_test_plan → run_test_plan → get_test_results |
| Personalization | MemoryProfile: patterns + preferences injected into agents 3 & 4 |
| Demo service | 3 endpoints · 5% error rate on /api/users · 10% latency spikes on /api/payments |
| Error injection | `curl localhost:8001/inject-errors?count=15` |
