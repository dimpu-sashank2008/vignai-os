from datetime import datetime
from typing import Optional, List, Any, Dict
from pydantic import BaseModel, ConfigDict, Field
from app.schemas.career import OpportunityResponse, OpportunitySkillSchema


class CoordinatorIntakeRequest(BaseModel):
    announcement_text: str
    source_name: str = "VIIT Placement Coordinator"
    source_type: str = "AUTHORIZED_COORDINATOR"


class CoordinatorIntakeExtraction(BaseModel):
    title: str
    organization: str
    opportunity_type: str = "INTERNSHIP"
    description: str
    skills_required: List[str] = Field(default_factory=list)
    skills_preferred: List[str] = Field(default_factory=list)
    eligibility: str = "B.Tech All Branches"
    location: str = "Visakhapatnam"
    work_mode: str = "HYBRID"
    deadline_str: Optional[str] = None


class CoordinatorIntakeResponse(BaseModel):
    message: str
    opportunity: OpportunityResponse
    extracted_details: CoordinatorIntakeExtraction


class VerificationActionRequest(BaseModel):
    action: str # VERIFY, REJECT
    review_notes: Optional[str] = None


class OpportunitySourceResponse(BaseModel):
    id: int
    source_name: str
    source_type: str # INSTITUTION_CURATED, AUTHORIZED_COORDINATOR, APPROVED_API, PUBLIC_FEED
    status: str # HEALTHY, DEGRADED, OFFLINE
    last_checked: Optional[datetime] = None
    last_success: Optional[datetime] = None
    items_found: int = 0
    error_message: Optional[str] = None
    is_active: bool = True
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class SyncSourcesResponse(BaseModel):
    message: str
    total_sources_polled: int
    new_opportunities_ingested: int
    duplicates_skipped: int
    expired_count: int
    sources_health: List[OpportunitySourceResponse]
