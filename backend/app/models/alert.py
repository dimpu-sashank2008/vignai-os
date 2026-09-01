from sqlalchemy import Column, Integer, String, Text, DateTime, JSON
from sqlalchemy.sql import func
from app.database import Base

class VignaiAlert(Base):
    __tablename__ = "vignai_alerts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    alert_type = Column(String(50), default="PRIORITY_REVIEW", nullable=False) # PRIORITY_REVIEW, ANOMALY_BURST, RECURRING_DEFECT
    severity = Column(String(50), default="HIGH", nullable=False) # CRITICAL, HIGH, MEDIUM
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    case_group_id = Column(String(100), nullable=True, index=True)
    case_id = Column(String(50), nullable=True, index=True)
    department = Column(String(100), nullable=True, index=True)
    location = Column(String(255), nullable=True)
    status = Column(String(50), default="NEW", nullable=False, index=True) # NEW, ACKNOWLEDGED, RESOLVED, DISMISSED
    reason_data = Column(JSON, nullable=False) # Structured deterministic signals
    created_at = Column(DateTime, default=func.now(), nullable=False)
    acknowledged_at = Column(DateTime, nullable=True)
    resolved_at = Column(DateTime, nullable=True)
    dismissed_at = Column(DateTime, nullable=True)
