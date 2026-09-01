from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime

class ComplaintAIAnalysisSchema(BaseModel):
    category: str = Field(..., description="Suggested campus category")
    subcategory: str | None = Field(None, description="Specific subcategory")
    issue_summary: str = Field(..., description="Concise summary of the problem")
    location: str | None = Field(None, description="Extracted location")
    duration: str | None = Field(None, description="Reported duration or occurrence timeline")
    impact: str | None = Field(None, description="Reported impact or affected scope")
    suggested_priority: str = Field("MEDIUM", description="Suggested priority: LOW, MEDIUM, HIGH, CRITICAL")
    priority_reason: str | None = Field(None, description="Reasoning for priority suggestion")
    confidence: float = Field(0.85, ge=0.0, le=1.0, description="Model categorization confidence")

    # Phase 3 Routing Analysis Fields
    department: str | None = Field(None, description="Recommended handling department from configured list")
    suggested_route_type: str | None = Field("DEPARTMENT_AND_MANAGEMENT", description="Suggested route type")
    sensitivity: str = Field("NORMAL", description="Sensitivity classification: NORMAL, SENSITIVE, HIGH_SENSITIVITY")
    routing_reason: str | None = Field(None, description="Justification for routing recommendation")

class ComplaintAIAnalysisResponse(BaseModel):
    id: int
    complaint_id: int
    category: str | None = None
    subcategory: str | None = None
    issue_summary: str | None = None
    location: str | None = None
    duration: str | None = None
    impact: str | None = None
    suggested_priority: str | None = None
    priority_reason: str | None = None
    confidence: float | None = None
    processing_status: str
    provider: str
    model: str | None = None
    error_message: str | None = None

    department: str | None = None
    suggested_route_type: str | None = None
    sensitivity: str = "NORMAL"
    routing_reason: str | None = None

    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class RelatedCaseSchema(BaseModel):
    case_id: str
    title: str | None = None
    category: str | None = None
    location: str | None = None
    status: str
    similarity_score: float
    reason: str
