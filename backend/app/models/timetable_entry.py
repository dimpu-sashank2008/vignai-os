from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base


DAY_OF_WEEK = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]


class TimetableEntry(Base):
    __tablename__ = "timetable_entries"

    id = Column(Integer, primary_key=True, autoincrement=True)
    subject_id = Column(Integer, ForeignKey("academic_subjects.id"), nullable=False, index=True)
    day_of_week = Column(String(20), nullable=False)   # e.g. "Monday"
    start_time = Column(String(10), nullable=False)     # e.g. "09:00"
    end_time = Column(String(10), nullable=False)       # e.g. "10:00"
    room = Column(String(50), nullable=True)
    created_at = Column(DateTime, default=func.now())

    # Relationships
    subject = relationship("AcademicSubject", back_populates="timetable_entries")
