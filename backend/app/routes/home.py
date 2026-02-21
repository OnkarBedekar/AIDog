"""Home routes for personalized dashboard."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import Dict, Any
from app.core.dependencies import get_db, get_current_user
from app.db.models import User, Incident, Recommendation
from app.services.memory_service import MemoryService
from app.integrations.datadog_mcp import get_datadog_client
from app.integrations.toto_forecaster import get_toto_forecaster
from app.agents.recommendation_designer import RecommendationDesignerAgent
from datetime import datetime, timedelta

router = APIRouter()


@router.get("/overview")
async def get_home_overview(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """Get personalized home overview."""
    memory_service = MemoryService(db)
    memory_profile = memory_service.get_or_create_memory_profile(user.id)
    datadog_client = get_datadog_client()

    now = int(datetime.now().timestamp())
    one_hour_ago = int((datetime.now() - timedelta(hours=1)).timestamp())

    # Get services user touches (from recent incidents)
    recent_incidents = db.query(Incident).order_by(
        Incident.started_at.desc()
    ).limit(10).all()

    services_set = set()
    for incident in recent_incidents:
        services_set.update(incident.services or [])
    services_you_touch = list(services_set)[:10]

    # Real Datadog metric query: top endpoints by p95 latency
    top_endpoints = []
    try:
        endpoints_metrics = await datadog_client.query_metrics(
            query="p95:demo.http.request.duration{*} by {endpoint}",
            from_ts=one_hour_ago,
            to_ts=now,
        )
        if isinstance(endpoints_metrics, list) and endpoints_metrics:
            sorted_series = sorted(
                endpoints_metrics,
                key=lambda s: s.get("pointlist", [[0, 0]])[-1][1] if s.get("pointlist") else 0,
                reverse=True,
            )
            for series in sorted_series[:5]:
                tags = series.get("tags", [])
                endpoint_tag = next((t for t in tags if t.startswith("endpoint:")), None)
                name = endpoint_tag.replace("endpoint:", "") if endpoint_tag else series.get("metric", "unknown")
                points = series.get("pointlist", [])
                p95 = points[-1][1] if points else 0
                top_endpoints.append({"name": name, "p95_latency": round(p95, 1), "error_rate": 0})
    except Exception:
        pass

    if not top_endpoints:
        top_endpoints = [
            {"name": "/api/users", "error_rate": 2.5, "p95_latency": 150},
            {"name": "/api/payments", "error_rate": 1.2, "p95_latency": 200},
            {"name": "/api/search", "error_rate": 0.8, "p95_latency": 120},
        ]

    # Real Datadog metric queries for live charts
    live_charts_data = {}
    try:
        error_rate_series = await datadog_client.query_metrics(
            query="sum:demo.http.requests.count{status:500}.as_rate()",
            from_ts=one_hour_ago,
            to_ts=now,
        )
        if isinstance(error_rate_series, list) and error_rate_series:
            points = error_rate_series[0].get("pointlist", [])
            live_charts_data["error_rate"] = {"series": [[p[0], p[1]] for p in points if p[1] is not None]}
    except Exception:
        pass

    try:
        # GAUGE metric submitted with percentile:p95 tag — use avg: aggregation
        latency_series = await datadog_client.query_metrics(
            query="avg:demo.http.request.duration{percentile:p95}",
            from_ts=one_hour_ago,
            to_ts=now,
        )
        if isinstance(latency_series, list) and latency_series:
            points = latency_series[0].get("pointlist", [])
            live_charts_data["p95_latency"] = {"series": [[p[0], p[1]] for p in points if p[1] is not None]}
    except Exception:
        pass

    try:
        throughput_series = await datadog_client.query_metrics(
            query="sum:demo.http.requests.count{*}.as_rate()",
            from_ts=one_hour_ago,
            to_ts=now,
        )
        if isinstance(throughput_series, list) and throughput_series:
            points = throughput_series[0].get("pointlist", [])
            live_charts_data["throughput"] = {"series": [[p[0], p[1]] for p in points if p[1] is not None]}
    except Exception:
        pass

    # Per-chart fallback: if a metric has no real data yet, show a flat baseline
    # so the chart renders rather than appearing broken
    if "error_rate" not in live_charts_data:
        live_charts_data["error_rate"] = {
            "series": [[(datetime.now() - timedelta(minutes=i)).timestamp() * 1000, 0.0]
                       for i in range(60, 0, -1)],
        }
    if "p95_latency" not in live_charts_data:
        live_charts_data["p95_latency"] = {
            "series": [[(datetime.now() - timedelta(minutes=i)).timestamp() * 1000, 0.0]
                       for i in range(60, 0, -1)],
        }
    if "throughput" not in live_charts_data:
        live_charts_data["throughput"] = {
            "series": [[(datetime.now() - timedelta(minutes=i)).timestamp() * 1000, 0.0]
                       for i in range(60, 0, -1)],
        }

    # Get active alerts from Datadog
    active_alerts = await datadog_client.get_active_monitors(time_window=3600)

    # Get recent incidents
    recent_incidents_data = [
        {
            "id": inc.id,
            "title": inc.title,
            "severity": inc.severity,
            "started_at": inc.started_at.isoformat(),
            "services": inc.services or [],
        }
        for inc in recent_incidents[:5]
    ]

    # Get learned patterns from memory profile
    learned_patterns = [
        pattern.get("description", "") for pattern in (memory_profile.patterns or [])[:5]
    ]

    # Generate suggestions using RecommendationDesignerAgent
    try:
        recommendation_agent = RecommendationDesignerAgent()
        recommendations_output = await recommendation_agent.design_recommendations(
            hypotheses=[],
            user_preferences=memory_profile.preferences or {},
        )
        suggested_improvements = [
            {
                "id": rec.id,
                "type": rec.type,
                "title": rec.title,
                "description": rec.description,
                "confidence": rec.confidence,
            }
            for rec in recommendations_output.recommendations[:5]
        ]
    except Exception:
        suggested_improvements = []

    # Run Toto on error_rate + latency to surface anomalies on the home dashboard
    toto_anomalies = []
    try:
        toto = get_toto_forecaster()
        for series_name, series_key in [("error_rate", "error_rate"), ("p95_latency", "p95_latency")]:
            series_data = live_charts_data.get(series_key, {}).get("series", [])
            values = [pt[1] for pt in series_data if pt[1] is not None]
            if len(values) >= 10:
                fc = toto.forecast(
                    values=values,
                    interval_seconds=60,
                    series_name=series_name,
                )
                if fc and fc.is_anomalous:
                    toto_anomalies.append({
                        "series_name": fc.series_name,
                        "anomaly_score": fc.anomaly_score,
                        "is_anomalous": fc.is_anomalous,
                    })
    except Exception:
        pass

    return {
        "servicesYouTouch": services_you_touch,
        "topEndpoints": top_endpoints,
        "liveChartsData": live_charts_data,
        "activeAlerts": active_alerts[:10],
        "recentIncidents": recent_incidents_data,
        "learnedPatterns": learned_patterns,
        "suggestedImprovements": suggested_improvements,
        "totoAnomalies": toto_anomalies,
    }
