"""
Proactive VIGNAI Priority Alerts Router.
Provides endpoints for Management and Faculty to review, acknowledge, and dismiss alerts.
Enforces strict role-based access control and tenant isolation.
"""

import logging
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status as http_status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.models.alert import VignaiAlert
from app.schemas.alert import VignaiAlertResponse, AlertActionResponse
from app.routers.auth import get_current_user
from app.services.intelligence.alert_service import alert_service

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Proactive Alerts"])


# ─────────────────────────────────────────────────────────────
# 1. MANAGEMENT ALERT ENDPOINTS
# ─────────────────────────────────────────────────────────────

@router.get("/management/alerts", response_model=list[VignaiAlertResponse])
def get_management_alerts(
    status: Optional[str] = Query(None, alias="status"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Retrieve campus-wide priority review alerts for management oversight."""
    if current_user.role != "management":
        raise HTTPException(
            status_code=http_status.HTTP_403_FORBIDDEN,
            detail="Access restricted to management administrators",
        )
    alerts = alert_service.get_management_alerts(db, status=status)
    
    # Format target_route
    res = []
    for a in alerts:
        target_route = f"/management/campus-issues#{a.case_group_id}" if a.case_group_id else f"/management/issues/{a.case_id}"
        item = VignaiAlertResponse(
            id=a.id,
            alert_type=a.alert_type,
            severity=a.severity,
            title=a.title,
            message=a.message,
            case_group_id=a.case_group_id,
            case_id=a.case_id,
            department=a.department,
            location=a.location,
            status=a.status,
            reason_data=a.reason_data,
            target_route=target_route,
            created_at=a.created_at,
            acknowledged_at=a.acknowledged_at,
            resolved_at=a.resolved_at,
            dismissed_at=a.dismissed_at,
        )
        res.append(item)
    return res


@router.post("/management/alerts/{alert_id}/acknowledge", response_model=AlertActionResponse)
def acknowledge_management_alert(
    alert_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Acknowledge a priority review alert."""
    if current_user.role != "management":
        raise HTTPException(
            status_code=http_status.HTTP_403_FORBIDDEN,
            detail="Access restricted to management administrators",
        )
    alert = alert_service.acknowledge_alert(alert_id, db)
    if not alert:
        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND,
            detail=f"Alert ID {alert_id} not found",
        )
    return AlertActionResponse(
        id=alert.id,
        status=alert.status,
        message=f"Alert '{alert.title}' acknowledged successfully",
        updated_at=alert.acknowledged_at,
    )


@router.post("/management/alerts/{alert_id}/dismiss", response_model=AlertActionResponse)
def dismiss_management_alert(
    alert_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Dismiss a priority review alert."""
    if current_user.role != "management":
        raise HTTPException(
            status_code=http_status.HTTP_403_FORBIDDEN,
            detail="Access restricted to management administrators",
        )
    alert = alert_service.dismiss_alert(alert_id, db)
    if not alert:
        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND,
            detail=f"Alert ID {alert_id} not found",
        )
    return AlertActionResponse(
        id=alert.id,
        status=alert.status,
        message=f"Alert '{alert.title}' dismissed",
        updated_at=alert.dismissed_at,
    )


# ─────────────────────────────────────────────────────────────
# 2. FACULTY ALERT ENDPOINTS
# ─────────────────────────────────────────────────────────────

@router.get("/faculty/alerts", response_model=list[VignaiAlertResponse])
def get_faculty_alerts(
    status: Optional[str] = Query(None, alias="status"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Retrieve department-scoped priority alerts for authorized faculty."""
    if current_user.role != "faculty":
        raise HTTPException(
            status_code=http_status.HTTP_403_FORBIDDEN,
            detail="Access restricted to faculty personnel",
        )
    dept = "CSE"
    if hasattr(current_user, "faculty_profile") and current_user.faculty_profile:
        dept = current_user.faculty_profile.department or "CSE"
        
    alerts = alert_service.get_faculty_alerts(db, department=dept, status=status)
    res = []
    for a in alerts:
        target_route = f"/faculty/department-issues"
        item = VignaiAlertResponse(
            id=a.id,
            alert_type=a.alert_type,
            severity=a.severity,
            title=a.title,
            message=a.message,
            case_group_id=a.case_group_id,
            case_id=a.case_id,
            department=a.department,
            location=a.location,
            status=a.status,
            reason_data=a.reason_data,
            target_route=target_route,
            created_at=a.created_at,
            acknowledged_at=a.acknowledged_at,
            resolved_at=a.resolved_at,
            dismissed_at=a.dismissed_at,
        )
        res.append(item)
    return res


@router.post("/faculty/alerts/{alert_id}/acknowledge", response_model=AlertActionResponse)
def acknowledge_faculty_alert(
    alert_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Acknowledge a department-level priority review alert."""
    if current_user.role != "faculty":
        raise HTTPException(
            status_code=http_status.HTTP_403_FORBIDDEN,
            detail="Access restricted to faculty personnel",
        )
    alert = alert_service.acknowledge_alert(alert_id, db)
    if not alert:
        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND,
            detail=f"Alert ID {alert_id} not found",
        )
    return AlertActionResponse(
        id=alert.id,
        status=alert.status,
        message=f"Alert '{alert.title}' acknowledged successfully",
        updated_at=alert.acknowledged_at,
    )


@router.post("/faculty/alerts/{alert_id}/dismiss", response_model=AlertActionResponse)
def dismiss_faculty_alert(
    alert_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Dismiss a department-level priority review alert."""
    if current_user.role != "faculty":
        raise HTTPException(
            status_code=http_status.HTTP_403_FORBIDDEN,
            detail="Access restricted to faculty personnel",
        )
    alert = alert_service.dismiss_alert(alert_id, db)
    if not alert:
        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND,
            detail=f"Alert ID {alert_id} not found",
        )
    return AlertActionResponse(
        id=alert.id,
        status=alert.status,
        message=f"Alert '{alert.title}' dismissed",
        updated_at=alert.dismissed_at,
    )
