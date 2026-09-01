from sqlalchemy import Column, Integer, String, Text, Float, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base

class ComplaintAIAnalysis(Base):
    __tablename__ = "complaint_ai_analyses"

    id = Column(Integer, primary_key=True, autoincrement=True)
    complaint_id = Column(Integer, ForeignKey("complaints.id"), unique=True, nullable=False, index=True)
    category = Column(String(100), nullable=True)
    subcategory = Column(String(100), nullable=True)
    issue_summary = Column(String(255), nullable=True)
    location = Column(String(255), nullable=True)
    duration = Column(String(255), nullable=True)
    impact = Column(Text, nullable=True)
    suggested_priority = Column(String(50), nullable=True)
    priority_reason = Column(Text, nullable=True)
    confidence = Column(Float, nullable=True)
    processing_status = Column(String(50), default="PENDING", nullable=False) # PENDING, PROCESSING, COMPLETED, FAILED
    provider = Column(String(50), default="gemini", nullable=False)
    model = Column(String(100), nullable=True)
    error_message = Column(Text, nullable=True)

    # Phase 3: Intelligent Routing Intelligence Fields
    department = Column(String(100), nullable=True)
    suggested_route_type = Column(String(50), nullable=True) # DEPARTMENT_AND_MANAGEMENT, MANAGEMENT_ONLY, AUTHORIZED_GRIEVANCE, CAMPUS_OPERATIONS, OTHER
    sensitivity = Column(String(50), default="NORMAL", nullable=False) # NORMAL, SENSITIVE, HIGH_SENSITIVITY
    routing_reason = Column(Text, nullable=True)

    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)

    complaint = relationship("Complaint", back_populates="ai_analysis")
