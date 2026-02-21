"""FastAPI application entry point."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.core.config import settings
from app.core.logging import setup_logging
from app.db.session import init_db

# Setup logging
setup_logging("INFO" if settings.app_env == "prod" else "DEBUG")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup
    init_db()
    # Pre-warm Toto in a background thread (downloads model if not cached)
    try:
        from app.integrations.toto_forecaster import prewarm_toto
        prewarm_toto()
    except Exception:
        pass
    yield
    # Shutdown
    pass


app = FastAPI(
    title="Datadog Copilot API",
    description="Personalized Datadog Copilot Backend",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],  # Frontend URLs
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok", "env": settings.app_env}


# Import routes
from app.routes import auth, home, incidents, recommendations, tests, memory

app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(home.router, prefix="/api/home", tags=["home"])
app.include_router(incidents.router, prefix="/api/incidents", tags=["incidents"])
app.include_router(recommendations.router, prefix="/api/recommendations", tags=["recommendations"])
app.include_router(tests.router, prefix="/api/tests", tags=["tests"])
app.include_router(memory.router, prefix="/api/memory", tags=["memory"])
