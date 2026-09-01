"""
Insights Router for VIGNAI OS (Phase 9).
Serves role-scoped, evidence-grounded insights and manages lifecycle transitions.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.schemas.insight import VignaiInsightResponse, InsightStatusUpdate
from app.services.intelligence.insight_engine import insight_engine

router = APIRouter(tags=["Cross-Domain Intelligence Insights"])


@router.get("/student/insights", response_model=List[VignaiInsightResponse])
def get_student_insights(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Returns evaluated cross-domain insights for the authenticated student."""
    if current_user.role != "student":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Student insights are exclusively accessible to students.",
        )
    return insight_engine.evaluate_student_insights(db, current_user)


@router.get("/faculty/insights", response_model=List[VignaiInsightResponse])
def get_faculty_insights(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Returns department complaint clusters and authorized academic insights."""
    if current_user.role not in ["faculty", "management", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access restricted to authorized faculty members.",
        )
    return insight_engine.evaluate_faculty_insights(db, current_user)


@router.get("/management/insights", response_model=List[VignaiInsightResponse])
def get_management_insights(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Returns campus-wide patterns, priority incident clusters, and What-If recommendations."""
    if current_user.role not in ["management", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Management insights require administrative clearance.",
        )
    return insight_engine.evaluate_management_insights(db, current_user)


@router.post("/insights/{insight_id}/seen", response_model=VignaiInsightResponse)
def mark_insight_seen(
    insight_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Marks an insight as seen."""
    return insight_engine.mark_seen(db, insight_id, current_user)


@router.post("/insights/{insight_id}/actioned", response_model=VignaiInsightResponse)
def mark_insight_actioned(
    insight_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Marks an insight as actioned."""
    return insight_engine.mark_actioned(db, insight_id, current_user)


@router.post("/insights/{insight_id}/dismiss", response_model=VignaiInsightResponse)
def mark_insight_dismissed(
    insight_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Dismisses an insight."""
    return insight_engine.mark_dismissed(db, insight_id, current_user)
