from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base

class Complaint(Base):
    __tablename__ = "complaints"

    id = Column(Integer, primary_key=True, autoincrement=True)
    case_id = Column(String(20), unique=True, nullable=False, index=True)
    student_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    title = Column(String(255), nullable=True)
    description = Column(Text, nullable=False)
    location = Column(String(255), nullable=True)
    category = Column(String(100), nullable=True)
    status = Column(String(50), default="SUBMITTED", nullable=False, index=True)
    priority = Column(String(50), default="MEDIUM", nullable=False)
    identity_protected = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)

    student = relationship("User", back_populates="complaints")
    evidences = relationship("Evidence", back_populates="complaint", cascade="all, delete-orphan", order_by="Evidence.created_at.desc()")
    ai_analysis = relationship("ComplaintAIAnalysis", uselist=False, back_populates="complaint", cascade="all, delete-orphan")
    routings = relationship("ComplaintRouting", back_populates="complaint", cascade="all, delete-orphan", order_by="ComplaintRouting.created_at.asc()")
    routing_audits = relationship("RoutingAudit", back_populates="complaint", cascade="all, delete-orphan", order_by="RoutingAudit.created_at.desc()")
    investigation_notes = relationship("InvestigationNote", back_populates="complaint", cascade="all, delete-orphan", order_by="InvestigationNote.created_at.asc()")
