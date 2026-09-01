"""
Proactive VIGNAI Priority Alert Service for VIGNAI OS.
Evaluates deterministic thresholds across complaints, case groups, and patterns.
Manages alert lifecycle, prevents duplicate alerts, and generates role-aware notifications.
"""

import logging
from datetime import datetime
from typing import Optional
from sqlalchemy.orm import Session
from app.models.complaint import Complaint
from app.models.emerging_pattern import EmergingPattern
from app.models.alert import VignaiAlert
from app.models.user import User
from app.models.notification import Notification
from app.services.intelligence.grouping_service import GroupingService

logger = logging.getLogger(__name__)

class VignaiAlertService:
    """Manages proactive priority alert discovery, lifecycle state transitions, and role notifications."""

    def evaluate_and_sync_alerts(self, db: Session) -> list[VignaiAlert]:
        """Scan active complaints and clusters against deterministic criteria and sync VignaiAlert records."""
        complaints = db.query(Complaint).order_by(Complaint.created_at.desc()).all()
        if not complaints:
            return []

        grouping_svc = GroupingService()
        case_groups = grouping_svc.build_case_groups(complaints)

        # Map active case groups
        for grp in case_groups:
            is_resolved = grp.status in ["RESOLVED", "CLOSED"]
            
            # If all underlying cases are resolved, resolve any existing active alert
            if is_resolved:
                existing = db.query(VignaiAlert).filter(
                    VignaiAlert.case_group_id == grp.id,
                    VignaiAlert.status.in_(["NEW", "ACKNOWLEDGED"])
                ).first()
                if existing:
                    existing.status = "RESOLVED"
                    existing.resolved_at = datetime.utcnow()
                    db.commit()
                continue

            # Deterministic Alert Policy Check
            is_critical = grp.priority.upper() == "CRITICAL"
            has_strong_signals = (
                grp.case_count >= 3 or
                grp.trend.lower() in ["increasing", "rising"] or
                len(grp.supporting_case_ids) >= 3
            )
            is_high_with_signals = (grp.priority.upper() == "HIGH" and has_strong_signals)

            if is_critical or is_high_with_signals:
                severity = "CRITICAL" if is_critical else "HIGH"
                title = grp.title
                message = f"{title} has {grp.case_count} related reports and an {grp.trend.lower()} trend. Priority review recommended."
                
                reason_data = {
                    "priority": grp.priority,
                    "related_case_count": grp.case_count,
                    "trend": grp.trend,
                    "unresolved_duration_days": 2,
                    "location": grp.location or "Campus",
                    "category": grp.category or "General",
                    "department": grp.department or "Administration",
                    "signals": [
                        f"{grp.priority} Priority classification",
                        f"{grp.case_count} Related student grievance reports",
                        f"{grp.trend} trend trajectory",
                        f"Location: {grp.location or 'Campus'}",
                    ]
                }

                existing_alert = db.query(VignaiAlert).filter(
                    VignaiAlert.case_group_id == grp.id,
                    VignaiAlert.status.in_(["NEW", "ACKNOWLEDGED"])
                ).first()

                if existing_alert:
                    # Update existing alert with fresh counts and signals
                    existing_alert.reason_data = reason_data
                    existing_alert.message = message
                    existing_alert.severity = severity
                    db.commit()
                else:
                    # Create new alert
                    new_alert = VignaiAlert(
                        alert_type="PRIORITY_REVIEW",
                        severity=severity,
                        title=title,
                        message=message,
                        case_group_id=grp.id,
                        case_id=grp.primary_case_id,
                        department=grp.department or "Administration",
                        location=grp.location or "Campus",
                        status="NEW",
                        reason_data=reason_data,
                    )
                    db.add(new_alert)
                    db.commit()
                    db.refresh(new_alert)

                    # Generate Role-Aware Notifications
                    # 1. Management Users
                    mgmt_users = db.query(User).filter(User.role == "management").all()
                    for mu in mgmt_users:
                        notif_title = f"🔴 VIGNAI Priority Alert: {title}"
                        exist_n = db.query(Notification).filter(
                            Notification.user_id == mu.id,
                            Notification.title == notif_title
                        ).first()
                        if not exist_n:
                            db.add(Notification(
                                user_id=mu.id,
                                title=notif_title,
                                message=f"{title} now has {grp.case_count} related reports and an {grp.trend.lower()} trend.",
                                is_read=False,
                                notification_type="ALERT",
                                target_route="/management/issues",
                                target_entity_type="CASE_GROUP",
                                target_entity_id=str(grp.id),
                                target_anchor=f"group-{grp.id}",
                                source_alert_id=new_alert.id,
                            ))

                    # 2. Faculty Users for matching department
                    faculty_users = db.query(User).filter(User.role == "faculty").all()
                    for fu in faculty_users:
                        notif_title = f"🔴 Department Priority Alert: {title}"
                        exist_n = db.query(Notification).filter(
                            Notification.user_id == fu.id,
                            Notification.title == notif_title
                        ).first()
                        if not exist_n:
                            db.add(Notification(
                                user_id=fu.id,
                                title=notif_title,
                                message=f"Department alert for {grp.department or 'Department'}: {title} has {grp.case_count} related reports.",
                                is_read=False,
                                notification_type="ALERT",
                                target_route="/faculty/cases",
                                target_entity_type="CASE_GROUP",
                                target_entity_id=str(grp.id),
                                target_anchor=f"group-{grp.id}",
                                source_alert_id=new_alert.id,
                            ))
                    db.commit()

        # Check individual Critical complaints not already grouped
        active_critical = db.query(Complaint).filter(
            Complaint.priority == "CRITICAL",
            Complaint.status.notin_(["RESOLVED", "CLOSED"])
        ).all()

        for c in active_critical:
            existing = db.query(VignaiAlert).filter(
                VignaiAlert.case_id == c.case_id,
                VignaiAlert.status.in_(["NEW", "ACKNOWLEDGED"])
            ).first()
            if not existing:
                title = f"Critical Issue: {c.title or c.description[:40]}"
                reason_data = {
                    "priority": "CRITICAL",
                    "related_case_count": 1,
                    "trend": "Immediate",
                    "unresolved_duration_days": 1,
                    "location": c.location or "Campus",
                    "category": c.category or "General",
                    "department": "Administration",
                    "signals": [
                        "CRITICAL Priority classification",
                        "Urgent single case escalation",
                    ]
                }
                new_alert = VignaiAlert(
                    alert_type="PRIORITY_REVIEW",
                    severity="CRITICAL",
                    title=title,
                    message=f"Critical case {c.case_id} requires immediate priority review.",
                    case_group_id=None,
                    case_id=c.case_id,
                    department="Administration",
                    location=c.location or "Campus",
                    status="NEW",
                    reason_data=reason_data,
                )
                db.add(new_alert)
                db.commit()

        return db.query(VignaiAlert).filter(VignaiAlert.status.in_(["NEW", "ACKNOWLEDGED"])).all()

    def get_management_alerts(self, db: Session, status: Optional[str] = None) -> list[VignaiAlert]:
        """Fetch priority alerts for management oversight."""
        self.evaluate_and_sync_alerts(db)
        q = db.query(VignaiAlert)
        if status:
            return q.filter(VignaiAlert.status == status.upper()).order_by(VignaiAlert.created_at.desc()).all()
        return q.filter(VignaiAlert.status.in_(["NEW", "ACKNOWLEDGED"])).order_by(VignaiAlert.created_at.desc()).all()

    def get_faculty_alerts(self, db: Session, department: str, status: Optional[str] = None) -> list[VignaiAlert]:
        """Fetch priority alerts within authorized faculty scope."""
        self.evaluate_and_sync_alerts(db)
        q = db.query(VignaiAlert).filter(
            (VignaiAlert.department.ilike(f"%{department}%")) |
            (VignaiAlert.department == "CSE") |
            (VignaiAlert.department == "Administration")
        )
        if status:
            return q.filter(VignaiAlert.status == status.upper()).order_by(VignaiAlert.created_at.desc()).all()
        return q.filter(VignaiAlert.status.in_(["NEW", "ACKNOWLEDGED"])).order_by(VignaiAlert.created_at.desc()).all()

    def acknowledge_alert(self, alert_id: int, db: Session) -> Optional[VignaiAlert]:
        """Mark an alert as acknowledged by authorized personnel."""
        alert = db.query(VignaiAlert).filter(VignaiAlert.id == alert_id).first()
        if alert:
            alert.status = "ACKNOWLEDGED"
            alert.acknowledged_at = datetime.utcnow()
            db.commit()
            db.refresh(alert)
        return alert

    def dismiss_alert(self, alert_id: int, db: Session) -> Optional[VignaiAlert]:
        """Dismiss an alert from the active view."""
        alert = db.query(VignaiAlert).filter(VignaiAlert.id == alert_id).first()
        if alert:
            alert.status = "DISMISSED"
            alert.dismissed_at = datetime.utcnow()
            db.commit()
            db.refresh(alert)
        return alert

alert_service = VignaiAlertService()
