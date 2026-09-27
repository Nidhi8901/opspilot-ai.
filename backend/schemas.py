from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field


class ServiceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    environment: str
    status: str
    cpu: int
    memory: int
    created_at: datetime


class IncidentCreate(BaseModel):
    service_id: int
    title: str = Field(min_length=5, max_length=200)
    severity: Literal["low", "medium", "high", "critical"]
    status: Literal["open", "investigating", "monitoring", "resolved"] = "investigating"
    summary: str = Field(min_length=10, max_length=1000)
    evidence: list[str] = Field(default_factory=list)
    recent_deployment: Optional[str] = None


class IncidentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    service_id: int
    title: str
    severity: str
    status: str
    detected_at: datetime
    summary: str
    evidence: list[str]
    recent_deployment: Optional[str] = None


class DeploymentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    service_id: int
    version: str
    status: str
    deployed_at: datetime


class RunbookResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    problem_type: str
    description: str
    keywords: list[str]
    content: str
    created_at: datetime


class AIAnalysisResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    incident_id: int
    runbook_id: Optional[int] = None
    runbook_title: Optional[str] = None
    runbook_similarity: Optional[float] = None
    model_id: str
    summary: str
    probable_cause: str
    impact: str
    recommended_actions: list[str]
    rollback_consideration: str
    confidence_percent: int
    input_tokens: int
    output_tokens: int
    total_tokens: int
    latency_ms: int
    created_at: datetime
