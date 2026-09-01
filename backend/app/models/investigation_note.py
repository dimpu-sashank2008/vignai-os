from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base

class InvestigationNote(Base):
    __tablename__ = "investigation_notes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    complaint_id = Column(Integer, ForeignKey("complaints.id"), nullable=False, index=True)
    author_user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    author_role = Column(String(50), nullable=False) # faculty, management
    author_email = Column(String(255), nullable=False)
    note_type = Column(String(50), default="INTERNAL", nullable=False) # INTERNAL, ACTION, INVESTIGATION, ESCALATION, STUDENT_QUERY
    content = Column(Text, nullable=False)
    is_visible_to_student = Column(Boolean, default=False, nullable=False) # Internal notes are strictly False
    created_at = Column(DateTime, default=func.now(), nullable=False)

    complaint = relationship("Complaint", back_populates="investigation_notes")
    author = relationship("User", foreign_keys=[author_user_id])
