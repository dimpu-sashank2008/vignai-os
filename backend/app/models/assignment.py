from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Index
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base


# Assignment status constants
ASSIGNMENT_PENDING = "PENDING"
ASSIGNMENT_SUBMITTED = "SUBMITTED"
ASSIGNMENT_COMPLETED = "COMPLETED"
ASSIGNMENT_OVERDUE = "OVERDUE"

ASSIGNMENT_STATUSES = [
    ASSIGNMENT_PENDING,
    ASSIGNMENT_SUBMITTED,
    ASSIGNMENT_COMPLETED,
    ASSIGNMENT_OVERDUE,
]


class Assignment(Base):
    __tablename__ = "assignments"

    id = Column(Integer, primary_key=True, autoincrement=True)
    subject_id = Column(Integer, ForeignKey("academic_subjects.id"), nullable=False, index=True)
    student_id = Column(Integer, ForeignKey("student_profiles.id"), nullable=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(String(1000), nullable=True)
    due_at = Column(DateTime, nullable=False)
    status = Column(String(20), nullable=False, default=ASSIGNMENT_PENDING)
    submitted_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=func.now())

    __table_args__ = (
        Index("ix_assignment_student_due", "student_id", "due_at"),
    )

    # Relationships
    subject = relationship("AcademicSubject", back_populates="assignments")
    student = relationship("StudentProfile")
