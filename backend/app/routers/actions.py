"""
Action Intelligence Router for VIGNAI OS (Phase 10).
Serves role-scoped prioritized actions and manages lifecycle transitions.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.schemas.action import VignaiActionResponse, ActionDailySummaryResponse, ActionStatusUpdate
from app.services.intelligence.action_engine import action_engine

router = APIRouter(tags=["Action Intelligence"])


@router.get("/student/actions", response_model=List[VignaiActionResponse])
def get_student_actions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Returns prioritized recommended actions for the authenticated student."""
    if current_user.role != "student":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Student action center is exclusively accessible to students.",
        )
    return action_engine.evaluate_student_actions(db, current_user)


@router.get("/student/actions/daily-summary", response_model=ActionDailySummaryResponse)
def get_student_daily_summary(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Returns daily priority briefing for the student."""
    if current_user.role != "student":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access restricted.")
    return action_engine.get_daily_summary(db, current_user)


@router.get("/faculty/actions", response_model=List[VignaiActionResponse])
def get_faculty_actions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Returns department issue priorities and instructional improvement actions."""
    if current_user.role not in ["faculty", "management", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access restricted to authorized faculty members.",
        )
    return action_engine.evaluate_faculty_actions(db, current_user)


@router.get("/faculty/actions/daily-summary", response_model=ActionDailySummaryResponse)
def get_faculty_daily_summary(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Returns daily priority briefing for faculty."""
    if current_user.role not in ["faculty", "management", "admin"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access restricted.")
    return action_engine.get_daily_summary(db, current_user)


@router.get("/management/actions", response_model=List[VignaiActionResponse])
def get_management_actions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Returns institutional priorities and What-If recommendations."""
    if current_user.role not in ["management", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Management action center requires executive clearance.",
        )
    return action_engine.evaluate_management_actions(db, current_user)


@router.get("/management/actions/daily-summary", response_model=ActionDailySummaryResponse)
def get_management_daily_summary(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Returns daily priority briefing for management."""
    if current_user.role not in ["management", "admin"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access restricted.")
    return action_engine.get_daily_summary(db, current_user)


@router.post("/actions/{action_id}/seen", response_model=VignaiActionResponse)
def mark_action_seen(
    action_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Marks action as seen."""
    return action_engine.mark_seen(db, action_id, current_user)


@router.post("/actions/{action_id}/in-progress", response_model=VignaiActionResponse)
def mark_action_in_progress(
    action_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Marks action as in progress."""
    return action_engine.mark_in_progress(db, action_id, current_user)


@router.post("/actions/{action_id}/complete", response_model=VignaiActionResponse)
def mark_action_completed(
    action_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Marks action as completed."""
    return action_engine.mark_completed(db, action_id, current_user)


@router.post("/actions/{action_id}/dismiss", response_model=VignaiActionResponse)
def mark_action_dismissed(
    action_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Dismisses an action."""
    return action_engine.mark_dismissed(db, action_id, current_user)
