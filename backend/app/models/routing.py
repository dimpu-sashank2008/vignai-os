from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base

class ComplaintRouting(Base):
    __tablename__ = "complaint_routings"

    id = Column(Integer, primary_key=True, autoincrement=True)
    complaint_id = Column(Integer, ForeignKey("complaints.id"), nullable=False, index=True)
    recipient_type = Column(String(50), nullable=False) # DEPARTMENT, MANAGEMENT, GRIEVANCE_AUTHORITY, SECURITY, OPERATIONS, FACULTY
    recipient_user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=True)
    department_code = Column(String(50), nullable=True)
    role = Column(String(50), nullable=False) # faculty, management, grievance_officer, admin
    assignment_status = Column(String(50), default="ASSIGNED", nullable=False) # SUGGESTED, ASSIGNED, ACCEPTED, REJECTED, COMPLETED
    is_primary = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)

    complaint = relationship("Complaint", back_populates="routings")
    recipient_user = relationship("User", foreign_keys=[recipient_user_id])
    department = relationship("Department", foreign_keys=[department_id])
