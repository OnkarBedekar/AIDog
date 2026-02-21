"""Memory routes."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import Dict, Any
from app.core.dependencies import get_db, get_current_user
from app.db.models import User
from app.schemas.api import MemoryProfileResponse, UpdatePreferencesRequest, ReorderShortcutsRequest, PatternFeedbackRequest
from app.services.memory_service import MemoryService

router = APIRouter()


@router.get("/profile", response_model=MemoryProfileResponse)
async def get_memory_profile(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> MemoryProfileResponse:
    """Get memory profile."""
    memory_service = MemoryService(db)
    memory_profile = memory_service.get_or_create_memory_profile(user.id)

    return MemoryProfileResponse(
        preferences=memory_profile.preferences or {},
        patterns=memory_profile.patterns or [],
        shortcuts=memory_profile.shortcuts or [],
        success_map=memory_profile.success_map or {},
    )


@router.post("/preferences")
async def update_preferences(
    request: UpdatePreferencesRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """Update user preferences."""
    memory_service = MemoryService(db)
    memory_service.update_preferences(user.id, request.preferences)

    return {"status": "updated"}


@router.post("/shortcuts/reorder")
async def reorder_shortcuts(
    request: ReorderShortcutsRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """Reorder user shortcuts."""
    memory_service = MemoryService(db)
    memory_service.update_shortcuts(user.id, request.shortcuts)

    return {"status": "updated"}


@router.post("/patterns/feedback")
async def pattern_feedback(
    request: PatternFeedbackRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """Provide feedback on a pattern."""
    memory_service = MemoryService(db)
    memory_profile = memory_service.get_or_create_memory_profile(user.id)

    # Update pattern feedback
    patterns = memory_profile.patterns or []
    for pattern in patterns:
        if pattern.get("id") == request.pattern_id:
            pattern["feedback"] = request.feedback
            break

    memory_profile.patterns = patterns
    db.commit()

    return {"status": "updated"}
