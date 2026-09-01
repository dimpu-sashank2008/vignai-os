"""
Pydantic schemas for RelatedCaseGroup and grouping explainability (Phase 4 / Intelligence Correction).
Enforces strict student privacy, structured explainability signals, and non-destructive case representation.
"""

from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime
from typing import Any

class GroupExplainabilitySignal(BaseModel):
    name: str
    weight: str
    evidence: str

class GroupUnderlyingCase(BaseModel):
    id: int
    case_id: str
    title: str | None = None
    description: str
    location: str | None = None
    category: str | None = None
    status: str
    priority: str
    identity_protected: bool
    reporter_visibility: str
    reporter_email: str | None = None
    evidence_count: int = 0
    department: str | None = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class RelatedCaseGroupResponse(BaseModel):
    id: str
    group_key: str
    title: str
    description: str
    category: str
    location: str | None = None
    department: str | None = None
    priority: str  # CRITICAL, HIGH, MEDIUM, LOW
    case_count: int
    trend: str  # Increasing, Stable, Resolving
    status: str  # Composite or primary status
    primary_case_id: str
    supporting_case_ids: list[str]
    explainability_signals: list[GroupExplainabilitySignal] = Field(default_factory=list)
    grouping_label: str = "POTENTIALLY RELATED"
    ai_assisted_priority: bool = True
    priority_reason: str = "Derived from member case severities and report volume."
    created_at: datetime
    updated_at: datetime

class RelatedCaseGroupDetailResponse(RelatedCaseGroupResponse):
    cases: list[GroupUnderlyingCase] = Field(default_factory=list)
