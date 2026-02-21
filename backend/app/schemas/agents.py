"""Pydantic schemas for agent outputs."""
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime


# BehaviorMinerAgent schemas
class Pattern(BaseModel):
    """Learned pattern."""
    description: str
    confidence: int = Field(ge=0, le=100)
    frequency: int = 0
    last_seen: Optional[str] = None


class PreferenceAdjustment(BaseModel):
    """Preference adjustment."""
    key: str
    value: Any
    reason: str


class BehaviorMinerOutput(BaseModel):
    """Output from BehaviorMinerAgent."""
    patterns: List[Pattern]
    preference_adjustments: List[PreferenceAdjustment]
    summary: str


# IncidentSummarizerAgent schemas
class IncidentEnvelope(BaseModel):
    """Incident summary envelope."""
    title: str
    description: str
    started_at: str
    affected_services: List[str]
    blast_radius: str  # e.g., "3 services, 15% of traffic"
    severity: str
    primary_symptom: str
    root_cause_hypothesis: Optional[str] = None


# GuidedStepsAgent schemas
class GuidedStep(BaseModel):
    """Guided investigation step."""
    id: str
    title: str
    description: str
    action_type: str  # query_metrics, search_logs, fetch_traces, etc.
    action_params: Dict[str, Any] = {}
    rationale: str
    priority: int = Field(ge=1, le=10, default=5)


class GuidedStepsOutput(BaseModel):
    """Output from GuidedStepsAgent."""
    steps: List[GuidedStep]
    reasoning: str


# HypothesisRankerAgent schemas
class EvidencePointer(BaseModel):
    """Pointer to evidence."""
    type: str  # metric, log, trace
    source: str
    key_findings: List[str]


class Hypothesis(BaseModel):
    """Ranked hypothesis."""
    id: str
    title: Optional[str] = None
    description: str
    confidence: int = Field(ge=0, le=100)
    evidence: List[EvidencePointer] = []
    reasoning: str


class HypothesisRankerOutput(BaseModel):
    """Output from HypothesisRankerAgent."""
    hypotheses: List[Hypothesis]
    summary: str


# RecommendationDesignerAgent schemas
class ExportPayload(BaseModel):
    """Export payload for recommendation."""
    type: str  # monitor_tune, dashboard, slo, shortcut
    payload: Dict[str, Any]
    cli_snippet: Optional[str] = None


class RecommendationProposal(BaseModel):
    """Recommendation proposal."""
    id: str
    type: str  # monitor_tune, dashboard, slo, shortcut, hypothesis
    title: str
    description: str
    confidence: int = Field(ge=0, le=100)
    export_payload: Optional[ExportPayload] = None
    rationale: str


class RecommendationDesignerOutput(BaseModel):
    """Output from RecommendationDesignerAgent."""
    recommendations: List[RecommendationProposal]
    summary: str


# TestPlanAgent schemas
class TestStep(BaseModel):
    """Test step."""
    name: str
    description: str
    type: str  # http_request, metric_check, log_search, etc.
    params: Dict[str, Any] = {}
    expected_result: str


class TestPlan(BaseModel):
    """Test plan."""
    name: str
    description: str
    steps: List[TestStep] = []
    validation_criteria: Any = ""
    failure_interpretation: Any = ""


class TestPlanOutput(BaseModel):
    """Output from TestPlanAgent."""
    plan: Optional[TestPlan] = None
    rationale: str = ""
