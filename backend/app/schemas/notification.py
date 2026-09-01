from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional

class NotificationResponse(BaseModel):
    id: int
    user_id: int
    title: str
    message: str
    is_read: bool
    notification_type: Optional[str] = "GENERAL"
    target_route: Optional[str] = None
    target_entity_type: Optional[str] = None
    target_entity_id: Optional[str] = None
    target_anchor: Optional[str] = None
    target_query: Optional[str] = None
    source_action_id: Optional[int] = None
    source_insight_id: Optional[int] = None
    source_alert_id: Optional[int] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
