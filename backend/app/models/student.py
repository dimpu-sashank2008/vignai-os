from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base

class StudentProfile(Base):
    __tablename__ = "student_profiles"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    enrollment_number = Column(String(50), unique=True, nullable=True)
    year_of_study = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=func.now())

    user = relationship("User", back_populates="student_profile")
