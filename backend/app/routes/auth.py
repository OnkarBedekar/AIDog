"""Authentication routes."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from jose import jwt
from datetime import datetime, timedelta
from typing import Dict
import bcrypt
from app.core.dependencies import get_db, get_current_user
from app.core.config import settings
from app.db.models import User
from app.schemas.api import SignupRequest, LoginRequest, LoginResponse, UserResponse
from app.services.memory_service import MemoryService

router = APIRouter()


def _hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def _verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode(), hashed.encode())


def create_access_token(user_id: int) -> str:
    """Create JWT access token."""
    expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
    to_encode = {"sub": str(user_id), "exp": expire}
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
    return encoded_jwt


@router.post("/signup", response_model=LoginResponse)
async def signup(request: SignupRequest, db: Session = Depends(get_db)):
    """Signup endpoint - creates new user with password."""
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == request.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists",
        )

    # Hash password
    password_hash = _hash_password(request.password)

    # Create user
    user = User(
        email=request.email,
        role=request.role,
        password_hash=password_hash,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    # Create memory profile
    memory_service = MemoryService(db)
    memory_service.get_or_create_memory_profile(user.id)

    # Generate token
    token = create_access_token(user.id)

    return LoginResponse(
        token=token,
        user={
            "id": user.id,
            "email": user.email,
            "role": user.role,
            "created_at": user.created_at.isoformat(),
        },
    )


@router.post("/login", response_model=LoginResponse)
async def login(request: LoginRequest, db: Session = Depends(get_db)):
    """Login endpoint - authenticates user with email and password."""
    # Find user by email
    user = db.query(User).filter(User.email == request.email).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    # Verify password
    if not _verify_password(request.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    # Generate token
    token = create_access_token(user.id)

    return LoginResponse(
        token=token,
        user={
            "id": user.id,
            "email": user.email,
            "role": user.role,
            "created_at": user.created_at.isoformat(),
        },
    )


@router.get("/me")
async def get_me(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get current user and memory profile."""
    memory_service = MemoryService(db)
    memory_profile = memory_service.get_or_create_memory_profile(user.id)

    return {
        "user": {
            "id": user.id,
            "email": user.email,
            "role": user.role,
            "created_at": user.created_at.isoformat(),
        },
        "memoryProfile": {
            "preferences": memory_profile.preferences or {},
            "patterns": memory_profile.patterns or [],
            "shortcuts": memory_profile.shortcuts or [],
            "success_map": memory_profile.success_map or {},
        },
    }
