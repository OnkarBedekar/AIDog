"""Recommendation routes."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from app.core.dependencies import get_db, get_current_user
from app.db.models import User, Recommendation
from app.schemas.api import RecommendationResponse, RecommendationExportResponse
from app.services.memory_service import MemoryService
from app.integrations.testsprite import get_testsprite_client
from app.agents.test_plan import TestPlanAgent

router = APIRouter()


@router.get("", response_model=List[RecommendationResponse])
async def list_recommendations(
    incident_id: Optional[int] = None,
    status: Optional[str] = None,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> List[RecommendationResponse]:
    """List recommendations with optional filters."""
    query = db.query(Recommendation).filter(Recommendation.user_id == user.id)

    if incident_id:
        query = query.filter(Recommendation.incident_id == incident_id)

    if status:
        query = query.filter(Recommendation.status == status)

    recommendations = query.order_by(Recommendation.created_at.desc()).limit(50).all()

    return [
        RecommendationResponse(
            id=rec.id,
            user_id=rec.user_id,
            incident_id=rec.incident_id,
            type=rec.type,
            content=rec.content,
            confidence=rec.confidence,
            status=rec.status,
            created_at=rec.created_at,
        )
        for rec in recommendations
    ]


@router.post("/{recommendation_id}/accept")
async def accept_recommendation(
    recommendation_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """Accept a recommendation."""
    recommendation = db.query(Recommendation).filter(
        Recommendation.id == recommendation_id,
        Recommendation.user_id == user.id,
    ).first()

    if not recommendation:
        raise HTTPException(status_code=404, detail="Recommendation not found")

    recommendation.status = "accepted"
    db.commit()

    # Update memory
    memory_service = MemoryService(db)
    memory_service.record_recommendation_acceptance(
        user_id=user.id,
        recommendation_id=recommendation_id,
        recommendation_type=recommendation.type,
    )

    # Auto-generate and run TestSprite test plan
    test_plan = None
    test_run = None
    test_results = None
    try:
        test_agent = TestPlanAgent()
        test_output = await test_agent.generate_test_plan(
            recommendation=recommendation.content or {},
            incident_type=recommendation.type or "general",
            telemetry_signature={},
        )
        plan_obj = getattr(test_output, "plan", None)
        if plan_obj is None:
            raise ValueError("TestPlanAgent returned no plan")
        plan_dict = plan_obj.model_dump() if hasattr(plan_obj, "model_dump") else dict(plan_obj)
        testsprite = get_testsprite_client()
        test_plan = await testsprite.create_test_plan(
            name=plan_dict.get("name", f"Test for recommendation {recommendation_id}"),
            steps_json=plan_dict,
        )
        test_run = await testsprite.run_test_plan(test_plan["id"])
        test_results = await testsprite.get_test_results(test_run["id"])
    except Exception as exc:
        test_results = {"error": str(exc), "status": "error"}

    return {
        "status": "accepted",
        "id": recommendation_id,
        "test_plan": test_plan,
        "test_run": test_run,
        "test_results": test_results,
    }


@router.post("/{recommendation_id}/reject")
async def reject_recommendation(
    recommendation_id: int,
    reason: Optional[str] = None,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """Reject a recommendation."""
    recommendation = db.query(Recommendation).filter(
        Recommendation.id == recommendation_id,
        Recommendation.user_id == user.id,
    ).first()

    if not recommendation:
        raise HTTPException(status_code=404, detail="Recommendation not found")

    recommendation.status = "rejected"
    db.commit()

    # Update memory
    memory_service = MemoryService(db)
    memory_service.record_recommendation_rejection(
        user_id=user.id,
        recommendation_id=recommendation_id,
        recommendation_type=recommendation.type,
        reason=reason,
    )

    return {"status": "rejected", "id": recommendation_id}


@router.get("/{recommendation_id}/export", response_model=RecommendationExportResponse)
async def export_recommendation(
    recommendation_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> RecommendationExportResponse:
    """Get export payload for a recommendation."""
    recommendation = db.query(Recommendation).filter(
        Recommendation.id == recommendation_id,
        Recommendation.user_id == user.id,
    ).first()

    if not recommendation:
        raise HTTPException(status_code=404, detail="Recommendation not found")

    # Extract export payload from content
    content = recommendation.content or {}
    export_payload = content.get("export_payload", {})

    payload = export_payload.get("payload", {})
    cli_snippet = export_payload.get("cli_snippet")

    return RecommendationExportResponse(
        payload=payload,
        cli_snippet=cli_snippet,
    )
