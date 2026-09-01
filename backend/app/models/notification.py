from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base

class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    is_read = Column(Boolean, default=False, nullable=False)
    notification_type = Column(String(50), default="GENERAL", nullable=True)
    target_route = Column(String(255), nullable=True)
    target_entity_type = Column(String(50), nullable=True)
    target_entity_id = Column(String(100), nullable=True)
    target_anchor = Column(String(100), nullable=True)
    target_query = Column(String(255), nullable=True)
    source_action_id = Column(Integer, nullable=True)
    source_insight_id = Column(Integer, nullable=True)
    source_alert_id = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=func.now(), nullable=False)

    user = relationship("User", back_populates="notifications")
