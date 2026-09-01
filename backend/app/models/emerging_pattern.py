from sqlalchemy import Column, Integer, String, Text, Float, DateTime, JSON
from sqlalchemy.sql import func
from app.database import Base

class EmergingPattern(Base):
    __tablename__ = "emerging_patterns"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    pattern_type = Column(String(50), nullable=False) # LOCATION_CLUSTER, CATEGORY_BURST, RECURRING_DEFECT, CROSS_DEPT_RISK
    severity = Column(String(50), default="MEDIUM", nullable=False) # LOW, MEDIUM, HIGH, CRITICAL
    case_count = Column(Integer, default=1, nullable=False)
    affected_estimate = Column(String(100), default="Unknown", nullable=False)
    trend = Column(String(50), default="STABLE", nullable=False) # RISING, STABLE, RESOLVING
    evidence_case_ids = Column(JSON, nullable=False) # List of case IDs e.g. ["VX-104821", "VX-960050"]
    confidence = Column(Float, default=0.85, nullable=False)
    primary_department = Column(String(100), nullable=True)
    primary_location = Column(String(255), nullable=True)
    status = Column(String(50), default="ACTIVE", nullable=False) # ACTIVE, INVESTIGATING, RESOLVED, DISMISSED
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
