"""
VignaiAction Model for VIGNAI OS — Phase 10 (Action Intelligence: From Insights to Decisions).
Persists prioritized, evidence-backed actions for authenticated users across roles.
"""

from datetime import datetime
from sqlalchemy import Column, Integer, Float, String, Text, DateTime, JSON, ForeignKey, Index
from sqlalchemy.sql import func
from app.database import Base


class VignaiAction(Base):
    __tablename__ = "vignai_actions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    action_type = Column(String(50), nullable=False, index=True)
    # Types: ACADEMIC_ATTENDANCE, ACADEMIC_ASSESSMENT, ACADEMIC_ASSIGNMENT,
    #        CAREER_OPPORTUNITY, CAREER_SKILL_GAP, CAREER_EXPLORATION,
    #        CAMPUS_CLUSTER, TEACHING_IMPROVEMENT, WHAT_IF_SIMULATION, CROSS_DOMAIN

    priority = Column(String(20), nullable=False, default="MEDIUM", index=True)
    # Severities: CRITICAL, HIGH, MEDIUM, LOW

    priority_score = Column(Float, nullable=False, default=0.5)
    # Deterministic calculation: (Urgency * 0.35) + (Impact * 0.30) + (EvidenceStrength * 0.20) + (Relevance * 0.15)

    title = Column(String(255), nullable=False)
    summary = Column(Text, nullable=False)
    role = Column(String(50), nullable=False, index=True)  # student, faculty, management, admin

    target_user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    target_department = Column(String(100), nullable=True, index=True)
    source_insight_id = Column(Integer, ForeignKey("vignai_insights.id"), nullable=True, index=True)

    source_domain = Column(String(100), nullable=False, default="GENERAL")
    # ACADEMICS, CAREER, COMPLAINTS, CAMPUS_INTELLIGENCE, CROSS_DOMAIN

    evidence = Column(JSON, nullable=False)
    # Structured evidence: {"urgency": 0.9, "impact": 0.8, "evidence_strength": 0.95, "relevance": 1.0, "signals": [...], "why_first": [...], "conclusion": "..."}

    recommended_action = Column(JSON, nullable=False)
    # Action payload: {"label": "...", "url": "...", "action_type": "...", "description": "..."}

    target_route = Column(String(255), nullable=False)
    # Target URL for deep-linking: /student/academics#attendance, /student/career#opportunity-1, etc.

    ask_vignai_query = Column(String(255), nullable=True)
    # Pre-crafted query: "Why is CS204 attendance currently a priority for me?"

    status = Column(String(50), nullable=False, default="NEW", index=True)
    # Statuses: NEW, SEEN, IN_PROGRESS, COMPLETED, DISMISSED, EXPIRED

    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    expires_at = Column(DateTime, nullable=True)

    deduplication_key = Column(String(255), nullable=False, unique=True, index=True)

    __table_args__ = (
        Index("ix_vignai_actions_role_status", "role", "status"),
        Index("ix_vignai_actions_user_status", "target_user_id", "status"),
    )
