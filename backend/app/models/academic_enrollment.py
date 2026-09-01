from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base


class StudentSubjectEnrollment(Base):
    __tablename__ = "student_subject_enrollments"

    id = Column(Integer, primary_key=True, autoincrement=True)
    student_id = Column(Integer, ForeignKey("student_profiles.id"), nullable=False, index=True)
    subject_id = Column(Integer, ForeignKey("academic_subjects.id"), nullable=False, index=True)
    semester = Column(Integer, nullable=False, default=1)
    section = Column(String(10), nullable=True, default="A")
    academic_year = Column(String(20), nullable=True, default="2024-25")
    created_at = Column(DateTime, default=func.now())

    __table_args__ = (
        UniqueConstraint("student_id", "subject_id", name="uq_student_subject"),
    )

    # Relationships
    student = relationship("StudentProfile")
    subject = relationship("AcademicSubject", back_populates="enrollments")
