"""
VignaiInsight Model for VIGNAI OS — Phase 9 (Cross-Domain Intelligence & Proactive Insight Engine).
Persists structured, evidence-grounded insights spanning Academics, Career, Complaints, and Operations.
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, JSON, ForeignKey, Index
from sqlalchemy.sql import func
from app.database import Base


class VignaiInsight(Base):
    __tablename__ = "vignai_insights"

    id = Column(Integer, primary_key=True, autoincrement=True)
    insight_type = Column(String(50), nullable=False, index=True)
    # Types: ACADEMIC_RISK, CAREER_ALIGNMENT, CAREER_OPPORTUNITY, CAMPUS_PATTERN,
    #        COMPLAINT_PATTERN, CROSS_DOMAIN, PREVENTIVE_ACTION, TREND_CHANGE

    severity = Column(String(20), nullable=False, default="INFO", index=True)
    # Severities: INFO, MEDIUM, HIGH, CRITICAL

    title = Column(String(255), nullable=False)
    summary = Column(Text, nullable=False)
    role = Column(String(50), nullable=False, index=True)  # student, faculty, management, admin

    target_user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    target_department = Column(String(100), nullable=True, index=True)

    status = Column(String(50), nullable=False, default="NEW", index=True)
    # Statuses: NEW, SEEN, ACTIONED, DISMISSED, EXPIRED

    source_domains = Column(JSON, nullable=False)
    # List of domain names, e.g. ["ACADEMICS", "CAREER"]

    evidence = Column(JSON, nullable=False)
    # Structured evidence: {"signals": [{"domain": "...", "metric": "...", "value": "...", "source": "..."}], "details": {...}, "conclusion": "..."}

    recommended_action = Column(JSON, nullable=False)
    # Action payload: {"label": "...", "url": "...", "action_type": "...", "description": "..."}

    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    expires_at = Column(DateTime, nullable=True)

    deduplication_key = Column(String(255), nullable=False, unique=True, index=True)

    __table_args__ = (
        Index("ix_vignai_insights_role_status", "role", "status"),
        Index("ix_vignai_insights_user_status", "target_user_id", "status"),
    )
