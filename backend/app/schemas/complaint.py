from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime
from app.schemas.evidence import EvidenceResponse
from app.schemas.ai_analysis import ComplaintAIAnalysisResponse

class ComplaintCreateRequest(BaseModel):
    description: str = Field(..., min_length=5, description="Natural language problem description")
    location: str | None = Field(None, max_length=255, description="Building, room, block, or area")
    category: str | None = Field(None, max_length=100, description="Optional category")
    subcategory: str | None = Field(None, max_length=100, description="Optional subcategory")
    identity_protected: bool = Field(False, description="Flag indicating if identity is protected from the assigned handler")

class ComplaintResponse(BaseModel):
    id: int
    case_id: str
    student_id: int
    title: str | None = None
    description: str
    location: str | None = None
    category: str | None = None
    status: str
    priority: str
    identity_protected: bool
    created_at: datetime
    updated_at: datetime
    evidences: list[EvidenceResponse] = []
    ai_analysis: ComplaintAIAnalysisResponse | None = None

    model_config = ConfigDict(from_attributes=True)

class ComplaintSummaryResponse(BaseModel):
    total: int
    open: int
    under_review: int
    in_progress: int
    resolved: int
    closed: int

class TaxonomyCategoryItem(BaseModel):
    key: str
    label: str
    subcategories: list[str]

class TaxonomyResponse(BaseModel):
    categories: list[TaxonomyCategoryItem]
    taxonomy_map: dict[str, list[str]]

