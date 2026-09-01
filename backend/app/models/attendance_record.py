from sqlalchemy import Column, Integer, String, Date, DateTime, ForeignKey, Index
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base


# Attendance status constants
ATTENDANCE_PRESENT = "PRESENT"
ATTENDANCE_ABSENT = "ABSENT"
ATTENDANCE_OD = "OD"          # On Duty
ATTENDANCE_OTHER = "OTHER"

ATTENDANCE_STATUSES = [ATTENDANCE_PRESENT, ATTENDANCE_ABSENT, ATTENDANCE_OD, ATTENDANCE_OTHER]


class AttendanceRecord(Base):
    __tablename__ = "attendance_records"

    id = Column(Integer, primary_key=True, autoincrement=True)
    student_id = Column(Integer, ForeignKey("student_profiles.id"), nullable=False, index=True)
    subject_id = Column(Integer, ForeignKey("academic_subjects.id"), nullable=False, index=True)
    date = Column(Date, nullable=False)
    status = Column(String(20), nullable=False, default=ATTENDANCE_PRESENT)
    created_at = Column(DateTime, default=func.now())

    __table_args__ = (
        Index("ix_attendance_student_subject_date", "student_id", "subject_id", "date"),
    )

    # Relationships
    student = relationship("StudentProfile")
    subject = relationship("AcademicSubject", back_populates="attendance_records")
