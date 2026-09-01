"""
SQLAlchemy Model for Saved What-If Lab Simulations (Phase 4D).
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, JSON, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class SavedSimulation(Base):
    __tablename__ = "simulations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    name = Column(String(255), nullable=False)
    scenario_type = Column(String(64), nullable=False, index=True) # TRANSPORT, INFRASTRUCTURE, MAINTENANCE, RESOURCE_ALLOCATION
    input_data = Column(JSON, nullable=False)
    result_data = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    user = relationship("User", backref="saved_simulations")
