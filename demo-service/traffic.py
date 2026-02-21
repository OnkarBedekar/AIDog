"""Background traffic generator for demo-service."""
import asyncio
import random
import time
import httpx
import threading

BASE_URL = "http://localhost:8001"
ENDPOINTS = [
    ("GET", "/api/users", None),
    ("POST", "/api/payments", {"amount": 100, "currency": "USD"}),
    ("GET", "/api/search?q=test", None),
    ("GET", "/api/search?q=product", None),
    ("GET", "/health", None),
]

async def send_request(client: httpx.AsyncClient, method: str, path: str, body=None):
    try:
        if method == "GET":
            await client.get(f"{BASE_URL}{path}", timeout=10.0)
        elif method == "POST":
            await client.post(f"{BASE_URL}{path}", json=body, timeout=10.0)
    except Exception:
        pass  # Errors are expected and tracked by the service itself

async def run_normal_traffic():
    """Generate ~20 req/s of normal traffic."""
    async with httpx.AsyncClient() as client:
        while True:
            tasks = []
            for _ in range(20):
                method, path, body = random.choice(ENDPOINTS)
                tasks.append(send_request(client, method, path, body))
            await asyncio.gather(*tasks)
            await asyncio.sleep(1.0)

async def run_error_bursts():
    """Inject error bursts every ~5 minutes."""
    while True:
        # Wait 5 minutes
        await asyncio.sleep(300)
        print("[traffic] Injecting error burst...")
        async with httpx.AsyncClient() as client:
            tasks = []
            for _ in range(50):
                # Hit endpoints that have higher error rates
                tasks.append(send_request(client, "GET", "/api/users", None))
                tasks.append(send_request(client, "POST", "/api/payments", {"amount": -1}))
            await asyncio.gather(*tasks)

async def run_latency_spikes():
    """Inject latency spikes periodically."""
    while True:
        await asyncio.sleep(120)
        print("[traffic] Triggering latency spike...")
        async with httpx.AsyncClient() as client:
            tasks = [send_request(client, "POST", "/api/payments", {"amount": 999}) for _ in range(20)]
            await asyncio.gather(*tasks)

async def main():
    print(f"[traffic] Starting traffic generator targeting {BASE_URL}")
    await asyncio.gather(
        run_normal_traffic(),
        run_error_bursts(),
        run_latency_spikes(),
    )

if __name__ == "__main__":
    asyncio.run(main())
