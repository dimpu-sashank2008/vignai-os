from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base

class RoutingAudit(Base):
    __tablename__ = "routing_audits"

    id = Column(Integer, primary_key=True, autoincrement=True)
    complaint_id = Column(Integer, ForeignKey("complaints.id"), nullable=False, index=True)
    ai_suggested_route = Column(String(255), nullable=False)
    policy_validation_result = Column(String(100), nullable=False) # VALIDATED, RESTRICTED_OVERRIDE, ESCALATED, MANAGEMENT_OVERRIDE
    final_route = Column(String(255), nullable=False)
    decision_by = Column(String(100), default="SYSTEM_POLICY_ENGINE", nullable=False)
    decision_reason = Column(Text, nullable=False)
    created_at = Column(DateTime, default=func.now(), nullable=False)

    complaint = relationship("Complaint", back_populates="routing_audits")
