"""Demo microservice — submits metrics directly to Datadog HTTP API (no agent needed)."""
import random
import time
import asyncio
import os
import threading
from collections import defaultdict
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import httpx
import uvicorn

DD_API_KEY = os.getenv("DATADOG_API_KEY", "")
DD_SITE    = os.getenv("DATADOG_SITE", "datadoghq.com")
DD_SERVICE = os.getenv("DD_SERVICE", "demo-service")
DD_ENV     = os.getenv("DD_ENV", "prod")

# ── Metrics buffer ────────────────────────────────────────────────────────────
_lock      = threading.Lock()
_counts: dict   = defaultdict(int)   # "endpoint|status" -> count
_durations: dict = defaultdict(list) # "endpoint|status" -> [ms, ...]

def track_request(endpoint: str, status: int, duration_ms: float):
    """Buffer a request metric for the next flush."""
    key = f"{endpoint}|{status}"
    with _lock:
        _counts[key] += 1
        _durations[key].append(duration_ms)

async def _flush_metrics():
    """Every 10 s: aggregate buffered metrics and POST to Datadog v2 API."""
    while True:
        await asyncio.sleep(10)
        if not DD_API_KEY:
            continue

        with _lock:
            counts    = dict(_counts);    _counts.clear()
            durations = {k: list(v) for k, v in _durations.items()}; _durations.clear()

        if not counts:
            continue

        ts = int(time.time())
        series = []
        for key, count in counts.items():
            endpoint, status = key.split("|", 1)
            tags = [f"endpoint:{endpoint}", f"status:{status}",
                    f"service:{DD_SERVICE}", f"env:{DD_ENV}"]

            series.append({
                "metric": "demo.http.requests.count",
                "points": [{"timestamp": ts, "value": count}],
                "type": 1,      # COUNT
                "tags": tags,
                "resources": [{"name": DD_SERVICE, "type": "host"}],
            })

            dlist = sorted(durations.get(key, []))
            if dlist:
                p95 = dlist[min(int(len(dlist) * 0.95), len(dlist) - 1)]
                series.append({
                    "metric": "demo.http.request.duration",
                    "points": [{"timestamp": ts, "value": p95}],
                    "type": 3,  # GAUGE  (p95 latency in ms)
                    "tags": tags + ["percentile:p95"],
                    "resources": [{"name": DD_SERVICE, "type": "host"}],
                })

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.post(
                    f"https://api.{DD_SITE}/api/v2/series",
                    json={"series": series},
                    headers={"DD-API-KEY": DD_API_KEY, "Content-Type": "application/json"},
                )
            if resp.status_code == 202:
                print(f"[metrics] flushed {len(series)} series → Datadog OK")
            else:
                print(f"[metrics] Datadog {resp.status_code}: {resp.text[:200]}")
        except Exception as exc:
            print(f"[metrics] flush error: {exc}")

# ── App ───────────────────────────────────────────────────────────────────────
app = FastAPI(title="Demo Service", version="1.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

@app.on_event("startup")
async def startup():
    asyncio.create_task(_flush_metrics())
    if DD_API_KEY:
        print(f"[metrics] Datadog direct-API enabled → api.{DD_SITE}")
    else:
        print("[metrics] DATADOG_API_KEY not set — metrics disabled")

# ── Endpoints ─────────────────────────────────────────────────────────────────
@app.get("/api/users")
async def get_users():
    start = time.time()
    if random.random() < 0.05:
        duration = (time.time() - start) * 1000
        track_request("/api/users", 500, duration)
        raise HTTPException(status_code=500, detail="Internal server error")
    await asyncio.sleep(random.uniform(0.02, 0.15))
    users = [{"id": i, "name": f"User {i}", "email": f"user{i}@example.com", "active": True}
             for i in range(1, random.randint(10, 50))]
    duration = (time.time() - start) * 1000
    track_request("/api/users", 200, duration)
    return {"users": users, "total": len(users)}

@app.post("/api/payments")
async def process_payment(payment: dict = None):
    start = time.time()
    if random.random() < 0.1:
        await asyncio.sleep(random.uniform(0.5, 2.0))
    else:
        await asyncio.sleep(random.uniform(0.05, 0.2))
    if random.random() < 0.03:
        duration = (time.time() - start) * 1000
        track_request("/api/payments", 500, duration)
        raise HTTPException(status_code=500, detail="Payment processing failed")
    duration = (time.time() - start) * 1000
    track_request("/api/payments", 200, duration)
    return {"transaction_id": f"txn_{random.randint(10000,99999)}", "status": "success",
            "amount": round(random.uniform(10, 500), 2)}

@app.get("/api/search")
async def search(q: str = "test"):
    start = time.time()
    base = random.gauss(0.08, 0.04)
    if random.random() < 0.05:
        base += random.uniform(0.3, 0.8)
    await asyncio.sleep(max(0.01, base))
    results = [{"id": i, "title": f"Result {i} for '{q}'", "score": random.uniform(0.5, 1.0)}
               for i in range(random.randint(0, 20))]
    duration = (time.time() - start) * 1000
    track_request("/api/search", 200, duration)
    return {"results": results, "total": len(results), "query": q}

@app.get("/health")
async def health():
    return {"status": "ok", "service": "demo-service", "version": "1.0.0"}


@app.get("/inject-errors")
async def inject_errors(count: int = 10):
    """Inject synthetic 500 errors to spike error rate in Datadog."""
    for _ in range(count):
        track_request("/api/users", 500, random.uniform(800, 2000))
        track_request("/api/payments", 500, random.uniform(1000, 3000))
    await _flush_metrics()
    return {"injected": count * 2, "status": "flushed to Datadog"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)
