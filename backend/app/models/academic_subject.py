from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Index
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base


class AcademicSubject(Base):
    __tablename__ = "academic_subjects"

    id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String(20), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=True)
    faculty_user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    credits = Column(Integer, default=3)
    is_active = Column(Boolean, default=True)
    data_source = Column(String(50), default="SYNTHETIC DEVELOPMENT DATA")
    created_at = Column(DateTime, default=func.now())

    # Relationships
    department = relationship("Department")
    faculty_user = relationship("User", foreign_keys=[faculty_user_id])
    enrollments = relationship("StudentSubjectEnrollment", back_populates="subject", cascade="all, delete-orphan")
    attendance_records = relationship("AttendanceRecord", back_populates="subject", cascade="all, delete-orphan")
    assessments = relationship("Assessment", back_populates="subject", cascade="all, delete-orphan")
    assignments = relationship("Assignment", back_populates="subject", cascade="all, delete-orphan")
    timetable_entries = relationship("TimetableEntry", back_populates="subject", cascade="all, delete-orphan")
