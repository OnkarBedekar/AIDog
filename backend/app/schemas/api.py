"""Pydantic schemas for API requests and responses."""
from pydantic import BaseModel, EmailStr
from typing import List, Dict, Any, Optional
from datetime import datetime


# Auth schemas
class SignupRequest(BaseModel):
    email: EmailStr
    password: str
    role: str  # SRE, Backend, ML, Product


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class LoginResponse(BaseModel):
    token: str
    user: Dict[str, Any]


class UserResponse(BaseModel):
    id: int
    email: str
    role: str
    created_at: datetime


# Home schemas
class HomeOverviewResponse(BaseModel):
    servicesYouTouch: List[str]
    topEndpoints: List[Dict[str, Any]]
    liveChartsData: Dict[str, Any]
    activeAlerts: List[Dict[str, Any]]
    recentIncidents: List[Dict[str, Any]]
    learnedPatterns: List[str]
    suggestedImprovements: List[Dict[str, Any]]


# Incident schemas
class IncidentResponse(BaseModel):
    id: int
    source: str
    title: str
    started_at: datetime
    severity: str
    services: List[str]
    state: str
    monitor_id: Optional[str] = None


class IncidentDetailResponse(BaseModel):
    incident: IncidentResponse
    envelope: Dict[str, Any]
    evidence: Dict[str, Any]
    guided_steps: List[Dict[str, Any]]
    recommendations: List[Dict[str, Any]]


class ExecuteStepRequest(BaseModel):
    step_id: str


class ExecuteStepResponse(BaseModel):
    result: Dict[str, Any]
    updated_investigation_graph: Dict[str, Any]
    next_steps_optional: Optional[List[Dict[str, Any]]] = None


# Recommendation schemas
class RecommendationResponse(BaseModel):
    id: int
    user_id: int
    incident_id: Optional[int]
    type: str
    content: Dict[str, Any]
    confidence: int
    status: str
    created_at: datetime


class RecommendationExportResponse(BaseModel):
    payload: Dict[str, Any]
    cli_snippet: Optional[str] = None


# Test schemas
class GenerateTestRequest(BaseModel):
    recommendation_id: int


class GenerateTestResponse(BaseModel):
    plan: Dict[str, Any]


class RunTestRequest(BaseModel):
    plan_id: str


class RunTestResponse(BaseModel):
    run_id: str


class TestResultsResponse(BaseModel):
    id: str
    status: str
    passed: bool
    total_tests: int
    passed_tests: int
    failed_tests: int
    artifacts: List[Dict[str, Any]]


# Memory schemas
class MemoryProfileResponse(BaseModel):
    preferences: Dict[str, Any]
    patterns: List[Dict[str, Any]]
    shortcuts: List[Dict[str, Any]]
    success_map: Dict[str, Any]


class UpdatePreferencesRequest(BaseModel):
    preferences: Dict[str, Any]


class ReorderShortcutsRequest(BaseModel):
    shortcuts: List[Dict[str, Any]]


class PatternFeedbackRequest(BaseModel):
    pattern_id: str
    feedback: str  # thumbs_up or thumbs_down
