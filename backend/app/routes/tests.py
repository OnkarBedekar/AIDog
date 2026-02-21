"""Test routes."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Dict, Any
from app.core.dependencies import get_db, get_current_user
from app.db.models import User, Recommendation
from app.schemas.api import GenerateTestRequest, GenerateTestResponse, RunTestRequest, RunTestResponse, TestResultsResponse
from app.integrations.testsprite import get_testsprite_client
from app.agents.test_plan import TestPlanAgent

router = APIRouter()


@router.post("/generate", response_model=GenerateTestResponse)
async def generate_test_plan(
    request: GenerateTestRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> GenerateTestResponse:
    """Generate test plan for a recommendation."""
    recommendation = db.query(Recommendation).filter(
        Recommendation.id == request.recommendation_id,
        Recommendation.user_id == user.id,
    ).first()

    if not recommendation:
        raise HTTPException(status_code=404, detail="Recommendation not found")

    # Generate test plan using agent
    try:
        test_agent = TestPlanAgent()
        test_output = await test_agent.generate_test_plan(
            recommendation=recommendation.content or {},
            incident_type=recommendation.type,
            telemetry_signature={},
        )
        plan_dict = test_output.plan.model_dump()
    except Exception as e:
        # Fallback plan
        plan_dict = {
            "name": f"Test plan for recommendation {request.recommendation_id}",
            "description": "Generated test plan",
            "steps": [],
            "validation_criteria": "Check if recommendation improves metrics",
            "failure_interpretation": "Test failures indicate recommendation may not be effective",
        }

    # Create test plan in TestSprite
    testsprite_client = get_testsprite_client()
    testsprite_plan = await testsprite_client.create_test_plan(
        name=plan_dict["name"],
        steps_json=plan_dict,
    )

    return GenerateTestResponse(plan=testsprite_plan)


@router.post("/run", response_model=RunTestResponse)
async def run_test_plan(
    request: RunTestRequest,
    user: User = Depends(get_current_user),
) -> RunTestResponse:
    """Run a test plan."""
    testsprite_client = get_testsprite_client()
    run_result = await testsprite_client.run_test_plan(request.plan_id)

    return RunTestResponse(run_id=run_result["id"])


@router.get("/runs/{run_id}", response_model=TestResultsResponse)
async def get_test_results(
    run_id: str,
    user: User = Depends(get_current_user),
) -> TestResultsResponse:
    """Get test run results."""
    testsprite_client = get_testsprite_client()
    results = await testsprite_client.get_test_results(run_id)

    return TestResultsResponse(
        id=results["id"],
        status=results["status"],
        passed=results.get("passed", False),
        total_tests=results.get("total_tests", 0),
        passed_tests=results.get("passed_tests", 0),
        failed_tests=results.get("failed_tests", 0),
        artifacts=results.get("artifacts", []),
    )
