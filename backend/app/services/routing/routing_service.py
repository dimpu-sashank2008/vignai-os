"""
Routing Orchestrator Service for VIGNEX (Phase 3).
Applies deterministic routing policy, saves routing/audit records, and notifies assignees.
"""

import logging
from sqlalchemy.orm import Session
from app.models.complaint import Complaint
from app.models.ai_analysis import ComplaintAIAnalysis
from app.models.routing import ComplaintRouting
from app.models.routing_audit import RoutingAudit
from app.models.department import Department
from app.models.faculty import FacultyProfile
from app.models.user import User
from app.models.notification import Notification
from app.services.routing.routing_policy import evaluate_routing_policy, RoutingDecision

logger = logging.getLogger(__name__)

class RoutingService:
    """Manages complaint routing lifecycle, policy enforcement, and audit records."""

    def apply_routing(
        self,
        db: Session,
        complaint: Complaint,
        ai_analysis: ComplaintAIAnalysis | None = None,
    ) -> list[ComplaintRouting]:
        """Evaluate deterministic routing policy and persist routing & audit entries."""
        decision: RoutingDecision = evaluate_routing_policy(complaint, ai_analysis)

        # 1. Record Routing Audit Entry
        audit = RoutingAudit(
            complaint_id=complaint.id,
            ai_suggested_route=decision.ai_suggested_route,
            policy_validation_result=decision.policy_validation_result,
            final_route=decision.final_route,
            decision_by="SYSTEM_POLICY_ENGINE",
            decision_reason=decision.decision_reason,
        )
        db.add(audit)
        db.commit()

        # Remove any existing pending routings before applying new decision
        db.query(ComplaintRouting).filter(ComplaintRouting.complaint_id == complaint.id).delete()

        created_routings: list[ComplaintRouting] = []

        # 2. Process Primary Recipients
        for prim in decision.primary_recipients:
            dept_code = prim.get("department_code")
            dept_obj = None
            assigned_user_id = None

            if dept_code:
                # Find or match department
                dept_obj = db.query(Department).filter(
                    (Department.code == dept_code) |
                    (Department.name.ilike(f"%{dept_code}%")) |
                    (Department.code == "CS" if dept_code == "CSE" else False)
                ).first()

                # Find candidate faculty in that department
                if dept_obj and prim.get("role") == "faculty":
                    faculty_prof = db.query(FacultyProfile).filter(
                        FacultyProfile.department_id == dept_obj.id
                    ).first()
                    if faculty_prof:
                        assigned_user_id = faculty_prof.user_id

            routing_entry = ComplaintRouting(
                complaint_id=complaint.id,
                recipient_type=prim["recipient_type"],
                recipient_user_id=assigned_user_id,
                department_id=dept_obj.id if dept_obj else None,
                department_code=dept_code,
                role=prim["role"],
                assignment_status="ASSIGNED",
                is_primary=True,
            )
            db.add(routing_entry)
            created_routings.append(routing_entry)

            # Generate notification for assigned faculty member if applicable
            if assigned_user_id and "SUBJECT_FACULTY" not in decision.restricted_recipients:
                notif = Notification(
                    user_id=assigned_user_id,
                    title=f"New Case Assigned ({complaint.case_id})",
                    message=f"Case {complaint.case_id} has been routed to your department: {complaint.title or complaint.category}.",
                    notification_type="CASE",
                    target_route=f"/faculty/cases/{complaint.case_id}",
                    target_entity_type="CASE",
                    target_entity_id=complaint.case_id,
                    target_anchor=f"case-{complaint.case_id}",
                )
                db.add(notif)

        # 3. Process Secondary Oversight (Management)
        for sec in decision.secondary_oversight:
            routing_entry = ComplaintRouting(
                complaint_id=complaint.id,
                recipient_type=sec["recipient_type"],
                recipient_user_id=None,
                department_id=None,
                department_code=sec.get("department_code", "Administration"),
                role=sec["role"],
                assignment_status="ASSIGNED",
                is_primary=False,
            )
            db.add(routing_entry)
            created_routings.append(routing_entry)

        db.commit()
        logger.info(
            f"Routing applied for case {complaint.case_id}: "
            f"PolicyResult={decision.policy_validation_result}, FinalRoute={decision.final_route}"
        )
        return created_routings


routing_service = RoutingService()
