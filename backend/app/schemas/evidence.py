from pydantic import BaseModel, ConfigDict
from datetime import datetime

class EvidenceResponse(BaseModel):
    id: int
    complaint_id: int
    file_name: str
    file_type: str
    file_size: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
