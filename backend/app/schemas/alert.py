from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime
from typing import Any, Optional

class AlertReasonData(BaseModel):
    priority: str = "NORMAL"
    related_case_count: int = 0
    trend: str = "STABLE"
    unresolved_duration_days: int = 0
    location: Optional[str] = None
    category: Optional[str] = None
    department: Optional[str] = None
    signals: list[str] = Field(default_factory=list)

class VignaiAlertResponse(BaseModel):
    id: int
    alert_type: str
    severity: str
    title: str
    message: str
    case_group_id: Optional[str] = None
    case_id: Optional[str] = None
    department: Optional[str] = None
    location: Optional[str] = None
    status: str
    reason_data: AlertReasonData
    target_route: str
    created_at: datetime
    acknowledged_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None
    dismissed_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

class AlertActionResponse(BaseModel):
    id: int
    status: str
    message: str
    updated_at: Optional[datetime] = None
