"""
Deterministic Routing Policy Engine for VIGNEX (Phase 3).

CRITICAL SECURITY PRINCIPLE:
The LLM is NOT the authorization system.
The LLM may recommend routing, but this deterministic backend policy engine
makes the binding routing and access control decisions.
"""

from typing import Any
from app.models.complaint import Complaint
from app.models.ai_analysis import ComplaintAIAnalysis
from app.config.categories import normalize_category_name
from app.services.ai.policy.rules import CONFIGURED_DEPARTMENTS

class RoutingDecision:
    def __init__(
        self,
        ai_suggested_route: str,
        policy_validation_result: str,
        final_route: str,
        decision_reason: str,
        primary_recipients: list[dict[str, Any]],
        secondary_oversight: list[dict[str, Any]],
        restricted_recipients: list[str],
    ):
        self.ai_suggested_route = ai_suggested_route
        self.policy_validation_result = policy_validation_result
        self.final_route = final_route
        self.decision_reason = decision_reason
        self.primary_recipients = primary_recipients
        self.secondary_oversight = secondary_oversight
        self.restricted_recipients = restricted_recipients

def evaluate_routing_policy(complaint: Complaint, ai_analysis: ComplaintAIAnalysis | None = None) -> RoutingDecision:
    """Evaluate deterministic routing rules against a complaint and its AI recommendation.
    Enforces that high-sensitivity cases are restricted, operational cases route to facilities/IT/transit,
    and only departmental academic/infrastructure issues route to faculty.
    """
    raw_category = complaint.category or (ai_analysis.category if ai_analysis else "") or ""
    category = normalize_category_name(raw_category)
    subcategory = (ai_analysis.subcategory if ai_analysis else "") or ""
    subcategory_lower = subcategory.lower()
    description = complaint.description.lower()
    ai_route_type = (ai_analysis.suggested_route_type if ai_analysis else "DEPARTMENT_AND_MANAGEMENT") or "DEPARTMENT_AND_MANAGEMENT"
    ai_dept = (ai_analysis.department if ai_analysis else None) or "CSE"
    sensitivity = (ai_analysis.sensitivity if ai_analysis else "NORMAL") or "NORMAL"

    ai_suggested_route = f"{ai_dept} ({ai_route_type})"

    # Rule 1: High Sensitivity / Faculty Conduct Allegation / Harassment
    # MUST be strictly isolated to Authorized Grievance Authority + Management Oversight.
    # Subject faculty MUST NEVER receive the complaint.
    is_conduct_grievance = (
        sensitivity == "HIGH_SENSITIVITY" or
        ai_route_type == "AUTHORIZED_GRIEVANCE" or
        category == "SENSITIVE_GRIEVANCE" or
        "faculty conduct" in subcategory_lower or
        any(k in description for k in ["conduct", "inappropriate", "harass", "misconduct", "assault", "retaliat"])
    )

    if is_conduct_grievance:
        return RoutingDecision(
            ai_suggested_route=ai_suggested_route,
            policy_validation_result="RESTRICTED_OVERRIDE",
            final_route="Authorized Grievance Authority + Management Oversight",
            decision_reason="High-sensitivity conduct allegation isolated from departmental faculty to protect confidentiality and prevent conflicts of interest.",
            primary_recipients=[
                {
                    "recipient_type": "GRIEVANCE_AUTHORITY",
                    "department_code": "Student Affairs",
                    "role": "grievance_officer",
                    "is_primary": True,
                }
            ],
            secondary_oversight=[
                {
                    "recipient_type": "MANAGEMENT",
                    "department_code": "Administration",
                    "role": "management",
                    "is_primary": False,
                }
            ],
            restricted_recipients=["SUBJECT_FACULTY", "DEPARTMENT_FACULTY"],
        )

    # Rule 2: Transport Authority
    if subcategory_lower == "transport" or ai_dept == "Transport" or any(k in description for k in ["bus", "shuttle", "transit", "bus stop"]):
        return RoutingDecision(
            ai_suggested_route=ai_suggested_route,
            policy_validation_result="VALIDATED",
            final_route="Campus Transport Authority + Management Oversight",
            decision_reason="Campus transit schedule/route issue routed to Transport coordinator.",
            primary_recipients=[
                {
                    "recipient_type": "DEPARTMENT",
                    "department_code": "Transport",
                    "role": "management",
                    "is_primary": True,
                }
            ],
            secondary_oversight=[
                {
                    "recipient_type": "MANAGEMENT",
                    "department_code": "Administration",
                    "role": "management",
                    "is_primary": False,
                }
            ],
            restricted_recipients=[],
        )

    # Rule 3: Hostel Administration
    if subcategory_lower == "hostel" or ai_dept == "Hostel" or any(k in description for k in ["hostel", "dorm", "warden", "mess"]):
        return RoutingDecision(
            ai_suggested_route=ai_suggested_route,
            policy_validation_result="VALIDATED",
            final_route="Hostel Administration + Management Oversight",
            decision_reason="Hostel residential facility issue routed to Hostel Warden & Administration.",
            primary_recipients=[
                {
                    "recipient_type": "DEPARTMENT",
                    "department_code": "Hostel",
                    "role": "faculty",
                    "is_primary": True,
                }
            ],
            secondary_oversight=[
                {
                    "recipient_type": "MANAGEMENT",
                    "department_code": "Administration",
                    "role": "management",
                    "is_primary": False,
                }
            ],
            restricted_recipients=[],
        )

    # Rule 4: Examination Authority
    if "exam" in subcategory_lower or subcategory_lower == "timetable" or "timetable" in description or ai_dept == "Examinations":
        return RoutingDecision(
            ai_suggested_route=ai_suggested_route,
            policy_validation_result="VALIDATED",
            final_route="Examinations Authority + Management Oversight",
            decision_reason="Academic examination clash/scheduling issue routed to Examination Cell.",
            primary_recipients=[
                {
                    "recipient_type": "DEPARTMENT",
                    "department_code": "Examinations",
                    "role": "faculty",
                    "is_primary": True,
                }
            ],
            secondary_oversight=[
                {
                    "recipient_type": "MANAGEMENT",
                    "department_code": "Administration",
                    "role": "management",
                    "is_primary": False,
                }
            ],
            restricted_recipients=[],
        )

    # Rule 5: Technology / Network Operations
    if category == "TECHNOLOGY" or subcategory_lower in ["wi-fi / network", "erp / portal", "computer system", "software / access"] or ai_dept == "IT" or any(k in description for k in ["wi-fi", "wifi", "eduroam", "network drop", "portal"]):
        return RoutingDecision(
            ai_suggested_route=ai_suggested_route,
            policy_validation_result="VALIDATED",
            final_route="Campus Operations (IT) + Management Oversight",
            decision_reason="Campus technology and network infrastructure issue routed to IT operations team.",
            primary_recipients=[
                {
                    "recipient_type": "OPERATIONS",
                    "department_code": "IT",
                    "role": "management",
                    "is_primary": True,
                }
            ],
            secondary_oversight=[
                {
                    "recipient_type": "MANAGEMENT",
                    "department_code": "Administration",
                    "role": "management",
                    "is_primary": False,
                }
            ],
            restricted_recipients=[],
        )

    # Rule 6: Campus Operations / Facilities / Cleanliness / Security / Campus Maintenance
    if category == "CAMPUS_OPERATIONS" or subcategory_lower in ["cleanliness", "security", "campus maintenance", "electrical"] or ai_route_type == "CAMPUS_OPERATIONS":
        dept_code = "Security" if (subcategory_lower == "security" or "security" in description or "guard" in description) else "Maintenance"
        return RoutingDecision(
            ai_suggested_route=ai_suggested_route,
            policy_validation_result="VALIDATED",
            final_route=f"Campus Operations ({dept_code}) + Management Oversight",
            decision_reason=f"Campus facilities & operations issue routed to central {dept_code} team.",
            primary_recipients=[
                {
                    "recipient_type": "OPERATIONS",
                    "department_code": dept_code,
                    "role": "management",
                    "is_primary": True,
                }
            ],
            secondary_oversight=[
                {
                    "recipient_type": "MANAGEMENT",
                    "department_code": "Administration",
                    "role": "management",
                    "is_primary": False,
                }
            ],
            restricted_recipients=[],
        )

    # Rule 7: Student Services / Administration
    if category == "STUDENT_SERVICES" or subcategory_lower in ["scholarships", "certificates", "administration", "student affairs"]:
        return RoutingDecision(
            ai_suggested_route=ai_suggested_route,
            policy_validation_result="VALIDATED",
            final_route="Student Services & Affairs + Management Oversight",
            decision_reason="Student administrative services request routed to Student Affairs.",
            primary_recipients=[
                {
                    "recipient_type": "DEPARTMENT",
                    "department_code": "Student Affairs",
                    "role": "faculty",
                    "is_primary": True,
                }
            ],
            secondary_oversight=[
                {
                    "recipient_type": "MANAGEMENT",
                    "department_code": "Administration",
                    "role": "management",
                    "is_primary": False,
                }
            ],
            restricted_recipients=[],
        )

    # Rule 8: Department-Specific Laboratory / Classroom / Academic Instruction Issue
    # Route to matching academic Department Faculty + Management Oversight
    matched_dept = ai_dept if ai_dept in CONFIGURED_DEPARTMENTS else "CSE"
    # Default to CSE if lab mentioned without explicit other department
    if category == "INFRASTRUCTURE" and matched_dept not in ["ECE", "EEE", "Mechanical", "Civil", "IT"]:
        matched_dept = "CSE"

    return RoutingDecision(
        ai_suggested_route=ai_suggested_route,
        policy_validation_result="VALIDATED",
        final_route=f"{matched_dept} Department + Management Oversight",
        decision_reason=f"Department-specific {category or 'academic'} facility issue assigned to {matched_dept} faculty coordinators.",
        primary_recipients=[
            {
                "recipient_type": "DEPARTMENT",
                "department_code": matched_dept,
                "role": "faculty",
                "is_primary": True,
            }
        ],
        secondary_oversight=[
            {
                "recipient_type": "MANAGEMENT",
                "department_code": "Administration",
                "role": "management",
                "is_primary": False,
            }
        ],
        restricted_recipients=[],
    )
