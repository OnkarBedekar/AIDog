"""Incident routes."""
import asyncio
from datetime import datetime, timedelta
from typing import Any, Dict, List

from fastapi import APIRouter, Depends, HTTPException

from sqlalchemy.orm import Session

from app.core.dependencies import get_db, get_current_user
from app.db.models import User, Incident, Recommendation
from app.schemas.api import (
    IncidentResponse,
    IncidentDetailResponse,
    ExecuteStepRequest,
    ExecuteStepResponse,
)
from app.integrations.datadog_mcp import get_datadog_client
from app.integrations.toto_forecaster import get_toto_forecaster
from app.agentcore.runner import InvestigationRunner
from app.agentcore.memory import get_memory_client
from app.services.memory_service import MemoryService
from app.services.investigation_service import InvestigationService

router = APIRouter()


# ── Helpers ────────────────────────────────────────────────────────────────────

async def _run_toto_for_incident(incident_id: int, db_url: str) -> None:
    """Background task: run Toto forecast and persist results on the incident."""
    # We need our own DB session since this runs in a background task
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    from app.db.models import Incident as _Incident

    engine = create_engine(db_url, connect_args={"check_same_thread": False})
    Session = sessionmaker(bind=engine)
    session = Session()
    try:
        incident = session.query(_Incident).filter(_Incident.id == incident_id).first()
        if not incident:
            return

        datadog = get_datadog_client()
        toto = get_toto_forecaster()
        now = int(datetime.now().timestamp())
        two_hours_ago = int((datetime.now() - timedelta(hours=2)).timestamp())

        # Fetch two key metric series
        metric_queries = [
            ("error_rate", "sum:demo.http.requests.count{status:500}.as_rate()"),
            ("p95_latency", "p95:demo.http.request.duration{*}"),
        ]

        forecasts = []
        for series_name, query in metric_queries:
            try:
                series_list = await datadog.query_metrics(
                    query=query, from_ts=two_hours_ago, to_ts=now
                )
                if isinstance(series_list, list) and series_list:
                    points = series_list[0].get("pointlist", [])
                    values = [p[1] for p in points if p[1] is not None]
                    if len(values) >= 10:
                        fc = toto.forecast(
                            values=values,
                            interval_seconds=60,
                            series_name=series_name,
                            horizon=60,
                        )
                        if fc:
                            forecasts.append(fc.model_dump())
            except Exception:
                pass

        if forecasts:
            incident.toto_forecasts = forecasts
            session.commit()
    except Exception:
        pass
    finally:
        session.close()


# ── Routes ─────────────────────────────────────────────────────────────────────

@router.get("", response_model=List[IncidentResponse])
async def list_incidents(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> List[IncidentResponse]:
    """List all incidents."""
    incidents = db.query(Incident).order_by(Incident.started_at.desc()).limit(50).all()

    return [
        IncidentResponse(
            id=inc.id,
            source=inc.source,
            title=inc.title,
            started_at=inc.started_at,
            severity=inc.severity,
            services=inc.services or [],
            state=inc.state,
            monitor_id=inc.monitor_id,
        )
        for inc in incidents
    ]


@router.get("/{incident_id}", response_model=IncidentDetailResponse)
async def get_incident(
    incident_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> IncidentDetailResponse:
    """Get incident details — uses InvestigationRunner for full pipeline."""
    incident = db.query(Incident).filter(Incident.id == incident_id).first()

    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")

    memory_service = MemoryService(db)
    memory_profile = memory_service.get_or_create_memory_profile(user.id)
    profile_dict = {
        "preferences": memory_profile.preferences or {},
        "patterns": memory_profile.patterns or [],
        "shortcuts": memory_profile.shortcuts or [],
    }

    runner = InvestigationRunner()
    result = await runner.run(
        incident_id=incident_id,
        incident=incident,
        user_id=user.id,
        memory_profile=profile_dict,
    )

    # Persist AgentCore session_id for agent-trace endpoint
    if result.get("session_id") and not incident.agentcore_session_id:
        incident.agentcore_session_id = result["session_id"]
        db.commit()

    # Persist runner recommendations to DB (idempotent: only when none exist)
    db_recommendations = db.query(Recommendation).filter(
        Recommendation.incident_id == incident_id
    ).all()
    if not db_recommendations and result.get("recommendations"):
        for rec in result["recommendations"][:5]:
            db_rec = Recommendation(
                user_id=user.id,
                incident_id=incident_id,
                type=rec.get("type", "shortcut"),
                content=rec,
                confidence=rec.get("confidence", 50),
                status="pending",
            )
            db.add(db_rec)
        db.commit()
        db_recommendations = db.query(Recommendation).filter(
            Recommendation.incident_id == incident_id
        ).all()

    recommendations_data = [
        {
            "id": rec.id,
            "type": rec.type,
            "content": rec.content,
            "confidence": rec.confidence,
            "status": rec.status,
        }
        for rec in db_recommendations
    ]

    return IncidentDetailResponse(
        incident=IncidentResponse(
            id=incident.id,
            source=incident.source,
            title=incident.title,
            started_at=incident.started_at,
            severity=incident.severity,
            services=incident.services or [],
            state=incident.state,
            monitor_id=incident.monitor_id,
        ),
        envelope=result["envelope"],
        evidence=result["evidence"],
        guided_steps=result["guided_steps"],
        recommendations=recommendations_data,
    )


@router.get("/{incident_id}/forecast")
async def get_incident_forecast(
    incident_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """Return Toto forecasts stored on the incident.

    If not yet computed, runs them synchronously (takes ~10–30s on CPU).
    """
    incident = db.query(Incident).filter(Incident.id == incident_id).first()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")

    forecasts = incident.toto_forecasts or []

    # If not yet computed, run synchronously
    if not forecasts:
        datadog = get_datadog_client()
        toto = get_toto_forecaster()
        now = int(datetime.now().timestamp())
        two_hours_ago = int((datetime.now() - timedelta(hours=2)).timestamp())

        for series_name, query in [
            ("error_rate", "sum:demo.http.requests.count{status:500}.as_rate()"),
            ("p95_latency", "p95:demo.http.request.duration{*}"),
        ]:
            try:
                series_list = await datadog.query_metrics(
                    query=query, from_ts=two_hours_ago, to_ts=now
                )
                if isinstance(series_list, list) and series_list:
                    points = series_list[0].get("pointlist", [])
                    values = [p[1] for p in points if p[1] is not None]
                    if len(values) >= 10:
                        fc = toto.forecast(
                            values=values,
                            interval_seconds=60,
                            series_name=series_name,
                        )
                        if fc:
                            forecasts.append(fc.model_dump())
            except Exception:
                pass

        if forecasts:
            incident.toto_forecasts = forecasts
            db.commit()

    return {
        "incident_id": incident_id,
        "forecasts": forecasts,
        "computed_at": datetime.now().isoformat(),
    }


@router.get("/{incident_id}/agent-trace")
async def get_agent_trace(
    incident_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """Return the AgentCore session event trace for this incident's last investigation."""
    incident = db.query(Incident).filter(Incident.id == incident_id).first()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")

    session_id = incident.agentcore_session_id
    if not session_id:
        return {"incident_id": incident_id, "session_id": None, "events": []}

    memory_client = get_memory_client()
    events = memory_client.get_events(session_id)

    return {
        "incident_id": incident_id,
        "session_id": session_id,
        "events": events,
    }


@router.post("/detect")
async def detect_incident_from_metrics(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> IncidentResponse:
    """Fetch live Datadog metrics, detect anomaly, and create a real incident via Minimax."""
    from app.agents.incident_summarizer import IncidentSummarizerAgent

    datadog_client = get_datadog_client()
    now = int(datetime.now().timestamp())
    one_hour_ago = int((datetime.now() - timedelta(hours=1)).timestamp())

    # Fetch the three key metrics
    metrics_bundle: Dict[str, Any] = {}
    for name, query in [
        ("error_rate", "sum:demo.http.requests.count{status:500}.as_rate()"),
        ("latency_p95", "avg:demo.http.request.duration{percentile:p95}"),
        ("throughput", "sum:demo.http.requests.count{*}.as_rate()"),
    ]:
        try:
            series = await datadog_client.query_metrics(
                query=query, from_ts=one_hour_ago, to_ts=now
            )
            if isinstance(series, list) and series:
                points = series[0].get("pointlist", [])
                values = [p[1] for p in points if p[1] is not None]
                if values:
                    metrics_bundle[name] = {
                        "current": round(values[-1], 3),
                        "avg": round(sum(values) / len(values), 3),
                        "max": round(max(values), 3),
                        "data_points": len(values),
                        "recent_5": [round(v, 3) for v in values[-5:]],
                    }
        except Exception:
            pass

    monitors = await datadog_client.get_active_monitors(time_window=3600)

    # Compute anomaly context from real metric values
    anomalies_found = []
    error_rate = metrics_bundle.get("error_rate", {}).get("current", 0) or 0
    error_avg = metrics_bundle.get("error_rate", {}).get("avg", 0) or 0
    latency = metrics_bundle.get("latency_p95", {}).get("current", 0) or 0
    latency_avg = metrics_bundle.get("latency_p95", {}).get("avg", 0) or 0
    throughput = metrics_bundle.get("throughput", {}).get("current", 0) or 0

    if error_rate > max(error_avg * 2, 0.5):
        anomalies_found.append(f"error rate spiked to {error_rate:.2f}/s (avg {error_avg:.2f}/s)")
    if latency > max(latency_avg * 1.5, 300):
        anomalies_found.append(f"p95 latency at {latency:.0f}ms (avg {latency_avg:.0f}ms)")
    if not anomalies_found:
        anomalies_found.append(f"elevated error rate {error_rate:.2f}/s, p95 latency {latency:.0f}ms")

    # Feed real data + computed anomalies to Minimax for rich incident description
    telemetry_bundle = {
        "monitors": monitors,
        "live_metrics": metrics_bundle,
        "detected_anomalies": anomalies_found,
        "timestamp": datetime.now().isoformat(),
        "source_service": "demo-service",
        "instruction": (
            "Use the detected_anomalies list and live_metrics to write a specific, "
            "actionable incident title and description. Include exact metric values."
        ),
    }

    try:
        summarizer = IncidentSummarizerAgent()
        envelope = await summarizer.summarize(telemetry_bundle)
        title = envelope.title or f"Incident: {', '.join(anomalies_found[:1])}"
        severity = envelope.severity or ("critical" if error_rate > 5 or latency > 500 else "warning")
        services = envelope.affected_services or ["demo-service"]
    except Exception:
        severity = "critical" if error_rate > 5 or latency > 500 else "warning"
        title = f"demo-service: {', '.join(anomalies_found)}"
        services = ["demo-service"]

    incident = Incident(
        source="datadog_live",
        title=title,
        severity=severity,
        services=services,
        state="open",
        monitor_id=None,
    )
    db.add(incident)
    db.commit()
    db.refresh(incident)

    return IncidentResponse(
        id=incident.id,
        source=incident.source,
        title=incident.title,
        started_at=incident.started_at,
        severity=incident.severity,
        services=incident.services or [],
        state=incident.state,
        monitor_id=incident.monitor_id,
    )


@router.post("/from-monitor")
async def create_incident_from_monitor(
    monitor_id: str,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> IncidentResponse:
    """Create or attach incident from a Datadog monitor (legacy)."""
    return await detect_incident_from_metrics(user=user, db=db)


@router.post("/{incident_id}/steps/execute", response_model=ExecuteStepResponse)
async def execute_step(
    incident_id: int,
    request: ExecuteStepRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ExecuteStepResponse:
    """Execute a guided investigation step."""
    incident = db.query(Incident).filter(Incident.id == incident_id).first()

    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")

    investigation_service = InvestigationService(db)
    sessions = investigation_service.get_user_sessions(user.id, limit=1)
    session = (
        sessions[0]
        if sessions
        else investigation_service.create_session(user.id, {"incident_id": incident_id})
    )

    investigation_service.record_event(
        session_id=session.id,
        kind="execute_step",
        payload={"step_id": request.step_id},
    )

    datadog_client = get_datadog_client()
    result_data: Dict[str, Any] = {}
    action_type = getattr(request, "action_type", None) or "query_metrics"
    action_params = getattr(request, "action_params", None) or {}

    try:
        if action_type == "query_metrics":
            query = action_params.get(
                "query",
                f"sum:demo.http.requests.count{{service:{','.join(incident.services or ['demo-service'])}}}.as_rate()",
            )
            metrics = await datadog_client.query_metrics(query=query)
            result_data = {"metrics": metrics, "query": query}
        elif action_type == "search_logs":
            log_query = action_params.get(
                "query", f"service:{','.join(incident.services or ['demo-service'])}"
            )
            logs = await datadog_client.search_logs(query=log_query, limit=50)
            result_data = {"logs": logs[:20], "count": len(logs)}
        elif action_type == "fetch_traces":
            service = action_params.get("service") or (
                incident.services[0] if incident.services else None
            )
            traces = await datadog_client.fetch_traces(service=service, limit=50)
            result_data = {"traces": traces[:20], "count": len(traces)}
        else:
            result_data = {"message": f"Step '{action_type}' executed"}
    except Exception as exc:
        result_data = {"error": str(exc), "message": "Step execution encountered an error"}

    result = {
        "step_id": request.step_id,
        "status": "completed",
        "data": result_data,
    }

    events = investigation_service.get_session_events(session.id)
    investigation_graph = {
        "nodes": [{"id": f"event_{e.id}", "label": e.kind} for e in events],
        "edges": [
            {"from": f"event_{events[i].id}", "to": f"event_{events[i + 1].id}"}
            for i in range(len(events) - 1)
        ],
    }

    return ExecuteStepResponse(
        result=result,
        updated_investigation_graph=investigation_graph,
        next_steps_optional=None,
    )
