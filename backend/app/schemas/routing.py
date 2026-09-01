from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime

class ComplaintRoutingResponse(BaseModel):
    id: int
    complaint_id: int
    recipient_type: str
    recipient_user_id: int | None = None
    department_id: int | None = None
    department_code: str | None = None
    role: str
    assignment_status: str
    is_primary: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class RoutingAuditResponse(BaseModel):
    id: int
    complaint_id: int
    ai_suggested_route: str
    policy_validation_result: str
    final_route: str
    decision_by: str
    decision_reason: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class InvestigationNoteCreatePayload(BaseModel):
    note_type: str = Field("INTERNAL", description="INTERNAL, ACTION, INVESTIGATION, ESCALATION, STUDENT_QUERY")
    content: str = Field(..., min_length=2, description="Content of the investigation note")

class InvestigationNoteResponse(BaseModel):
    id: int
    complaint_id: int
    author_user_id: int
    author_role: str
    author_email: str
    note_type: str
    content: str
    is_visible_to_student: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class FacultyCaseActionPayload(BaseModel):
    action: str = Field(..., description="ACCEPT, STATUS_UPDATE, ESCALATE, REQUEST_INFO")
    status: str | None = None
    note: str | None = None
    escalation_reason: str | None = None
