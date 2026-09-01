"""
Pydantic Schemas for VignaiAction (Phase 10).
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


class ActionPriorityEvidence(BaseModel):
    urgency: float
    impact: float
    evidence_strength: float
    relevance: float
    signals: List[Dict[str, Any]] = Field(default_factory=list)
    why_first: List[str] = Field(default_factory=list)
    conclusion: Optional[str] = None


class ActionPayload(BaseModel):
    label: str
    url: str
    action_type: str
    description: Optional[str] = None


class VignaiActionResponse(BaseModel):
    id: int
    action_type: str
    priority: str
    priority_score: float
    title: str
    summary: str
    role: str
    target_user_id: Optional[int] = None
    target_department: Optional[str] = None
    source_insight_id: Optional[int] = None
    source_domain: str
    evidence: Dict[str, Any]
    recommended_action: Dict[str, Any]
    target_route: str
    ask_vignai_query: Optional[str] = None
    status: str
    created_at: datetime
    expires_at: Optional[datetime] = None
    deduplication_key: str

    model_config = ConfigDict(from_attributes=True)


class ActionDailySummaryResponse(BaseModel):
    role: str
    greeting: str
    total_priorities: int
    top_priority_title: Optional[str] = None
    highlights: List[str] = Field(default_factory=list)
    actions: List[VignaiActionResponse] = Field(default_factory=list)


class ActionStatusUpdate(BaseModel):
    status: str  # SEEN, IN_PROGRESS, COMPLETED, DISMISSED
