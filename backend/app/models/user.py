from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    roll_number = Column(String(50), unique=True, nullable=True, index=True)
    faculty_id = Column(String(50), unique=True, nullable=True, index=True)
    management_id = Column(String(50), unique=True, nullable=True, index=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(50), nullable=False)
    is_active = Column(Boolean, default=True)
    must_change_password = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=func.now())

    student_profile = relationship("StudentProfile", uselist=False, back_populates="user")
    faculty_profile = relationship("FacultyProfile", uselist=False, back_populates="user")
    complaints = relationship("Complaint", back_populates="student", cascade="all, delete-orphan", order_by="Complaint.created_at.desc()")
    notifications = relationship("Notification", back_populates="user", cascade="all, delete-orphan", order_by="Notification.created_at.desc()")
