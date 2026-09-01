"""
Pydantic Schemas for VignaiInsight (Phase 9).
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


class InsightSignal(BaseModel):
    domain: str
    metric: str
    value: str
    source: str


class InsightEvidence(BaseModel):
    signals: List[InsightSignal]
    details: Dict[str, Any] = Field(default_factory=dict)
    conclusion: Optional[str] = None


class InsightAction(BaseModel):
    label: str
    url: str
    action_type: str
    description: Optional[str] = None


class VignaiInsightResponse(BaseModel):
    id: int
    insight_type: str
    severity: str
    title: str
    summary: str
    role: str
    target_user_id: Optional[int] = None
    target_department: Optional[str] = None
    status: str
    source_domains: List[str]
    evidence: Dict[str, Any]
    recommended_action: Dict[str, Any]
    created_at: datetime
    expires_at: Optional[datetime] = None
    deduplication_key: str

    model_config = ConfigDict(from_attributes=True)


class InsightStatusUpdate(BaseModel):
    status: str  # SEEN, ACTIONED, DISMISSED
