from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime
from app.schemas.evidence import EvidenceResponse
from app.schemas.ai_analysis import ComplaintAIAnalysisResponse
from app.schemas.routing import RoutingAuditResponse, InvestigationNoteResponse

class ReporterInfo(BaseModel):
    is_protected: bool
    visibility: str
    email: str | None = None
    enrollment_number: str | None = None
    year_of_study: int | None = None

class ManagementComplaintListResponse(BaseModel):
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
    evidence_count: int
    ai_analysis: ComplaintAIAnalysisResponse | None = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class ManagementComplaintDetailResponse(BaseModel):
    id: int
    case_id: str
    title: str | None = None
    description: str
    location: str | None = None
    category: str | None = None
    status: str
    priority: str
    identity_protected: bool
    reporter: ReporterInfo
    evidence_count: int
    evidences: list[EvidenceResponse] = []
    ai_analysis: ComplaintAIAnalysisResponse | None = None
    routing_audit: RoutingAuditResponse | None = None
    investigation_notes: list[InvestigationNoteResponse] = []
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class StatusUpdatePayload(BaseModel):
    status: str = Field(..., description="Target status: SUBMITTED, UNDER_REVIEW, IN_PROGRESS, RESOLVED, CLOSED")
    notes: str | None = Field(None, description="Optional administrative notes")

class ManagementSummaryResponse(BaseModel):
    total: int
    open: int
    under_review: int
    in_progress: int
    resolved: int
    closed: int
