from sqlalchemy import Column, Integer, String, DateTime, Float, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base


# Assessment type constants
ASSESSMENT_QUIZ = "QUIZ"
ASSESSMENT_MID_EXAM = "MID_EXAM"
ASSESSMENT_LAB_EXAM = "LAB_EXAM"
ASSESSMENT_FINAL_EXAM = "FINAL_EXAM"
ASSESSMENT_ASSIGNMENT_EVAL = "ASSIGNMENT_EVAL"

ASSESSMENT_TYPES = [
    ASSESSMENT_QUIZ,
    ASSESSMENT_MID_EXAM,
    ASSESSMENT_LAB_EXAM,
    ASSESSMENT_FINAL_EXAM,
    ASSESSMENT_ASSIGNMENT_EVAL,
]


class Assessment(Base):
    __tablename__ = "assessments"

    id = Column(Integer, primary_key=True, autoincrement=True)
    subject_id = Column(Integer, ForeignKey("academic_subjects.id"), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    assessment_type = Column(String(50), nullable=False, default=ASSESSMENT_QUIZ)
    scheduled_at = Column(DateTime, nullable=True)
    max_marks = Column(Float, nullable=False, default=100.0)
    duration_minutes = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=func.now())

    # Relationships
    subject = relationship("AcademicSubject", back_populates="assessments")
    results = relationship("AssessmentResult", back_populates="assessment", cascade="all, delete-orphan")


class AssessmentResult(Base):
    __tablename__ = "assessment_results"

    id = Column(Integer, primary_key=True, autoincrement=True)
    assessment_id = Column(Integer, ForeignKey("assessments.id"), nullable=False, index=True)
    student_id = Column(Integer, ForeignKey("student_profiles.id"), nullable=False, index=True)
    marks = Column(Float, nullable=False, default=0.0)
    submitted_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=func.now())

    # Relationships
    assessment = relationship("Assessment", back_populates="results")
    student = relationship("StudentProfile")
