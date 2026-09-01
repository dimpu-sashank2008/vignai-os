"""
Role-Aware Tool Registry for Ask VIGNAI (Intelligence Layer V2).
Provides centralized, server-authorized access to domain intelligence engines.
Derives student, faculty, and management identities strictly from server context.
"""

from typing import Dict, Any, Callable, Optional, List
import logging
from sqlalchemy.orm import Session
from app.models.user import User
from app.models.student import StudentProfile
from app.models.faculty import FacultyProfile
from app.models.complaint import Complaint
from app.models.emerging_pattern import EmergingPattern
from app.services.intelligence.academic_service import academic_service
from app.services.career.career_fit_service import (
    career_strength_analyzer,
    personalized_ranking_engine,
    eligibility_engine,
)
from app.services.career.matching_engine import matching_engine
from app.services.intelligence.pattern_detection import pattern_detection_service
from app.services.intelligence.alert_service import alert_service
from app.services.intelligence.insight_engine import insight_engine
from app.services.intelligence.action_engine import action_engine
from app.services.intelligence.simulation_engine import simulation_engine
from app.services.viit.context import VIIT_METADATA, VIIT_DEPARTMENTS

logger = logging.getLogger(__name__)


class ToolDefinition:
    def __init__(
        self,
        name: str,
        description: str,
        required_role: str,
        parameters: Dict[str, Any],
        executor: Callable,
    ):
        self.name = name
        self.description = description
        self.required_role = required_role  # "student", "faculty", "management", "any"
        self.parameters = parameters
        self.executor = executor


class ToolRegistry:
    """Centralized role-aware tool registry for VIGNAI OS."""

    def __init__(self):
        self._tools: Dict[str, ToolDefinition] = {}
        self._register_all_tools()

    def register(
        self,
        name: str,
        description: str,
        required_role: str,
        parameters: Dict[str, Any],
        executor: Callable,
    ):
        self._tools[name] = ToolDefinition(
            name=name,
            description=description,
            required_role=required_role,
            parameters=parameters,
            executor=executor,
        )

    def get_tool(self, name: str) -> Optional[ToolDefinition]:
        return self._tools.get(name)

    def list_tools_for_role(self, role: str) -> List[Dict[str, Any]]:
        role_lower = (role or "student").lower()
        tools = []
        for t in self._tools.values():
            if t.required_role == "any" or t.required_role == role_lower or (role_lower == "admin" and t.required_role == "management"):
                tools.append({
                    "name": t.name,
                    "description": t.description,
                    "parameters": t.parameters,
                })
        return tools

    def execute_tool(
        self,
        tool_name: str,
        db: Session,
        user: Optional[User],
        **params: Any,
    ) -> Dict[str, Any]:
        tool = self._tools.get(tool_name)
        if not tool:
            return {"error": f"Tool '{tool_name}' is not registered in VIGNAI Tool Registry."}

        user_role = (getattr(user, "role", "student") or "student").lower()

        # Enforce server-side role validation
        if tool.required_role != "any" and tool.required_role != user_role:
            if not (user_role == "admin" and tool.required_role == "management"):
                return {
                    "error": f"Access Denied: Tool '{tool_name}' requires role '{tool.required_role}', but current user has role '{user_role}'.",
                    "status": "FORBIDDEN",
                }

        try:
            return tool.executor(db=db, user=user, **params)
        except Exception as exc:
            logger.error(f"Error executing tool '{tool_name}': {exc}", exc_info=True)
            return {"error": f"Tool execution error: {str(exc)}", "status": "ERROR"}

    # =========================================================================
    # TOOL REGISTRATION & IMPLEMENTATIONS
    # =========================================================================
    def _register_all_tools(self):
        # Student Tools
        self.register(
            name="get_my_attendance",
            description="Retrieve student verified classroom attendance metrics, overall percentage, and per-subject breakdown.",
            required_role="student",
            parameters={},
            executor=self._tool_get_my_attendance,
        )
        self.register(
            name="get_my_submission_rate",
            description="Retrieve student assignment submission completion rate, total deliverables, pending, and overdue counts.",
            required_role="student",
            parameters={},
            executor=self._tool_get_my_submission_rate,
        )
        self.register(
            name="get_my_assignments",
            description="Retrieve student pending and overdue assignment deliverables with course titles and due dates.",
            required_role="student",
            parameters={},
            executor=self._tool_get_my_assignments,
        )
        self.register(
            name="get_my_assessments",
            description="Retrieve student scheduled exams, quizzes, and completed assessment scores.",
            required_role="student",
            parameters={},
            executor=self._tool_get_my_assessments,
        )
        self.register(
            name="get_my_academic_summary",
            description="Retrieve comprehensive student academic profile (attendance, upcoming deadlines, exam averages).",
            required_role="student",
            parameters={},
            executor=self._tool_get_my_academic_summary,
        )
        self.register(
            name="get_my_career_profile",
            description="Retrieve student career profile, verified skills, projects, and certifications.",
            required_role="student",
            parameters={},
            executor=self._tool_get_my_career_profile,
        )
        self.register(
            name="get_my_career_strengths",
            description="Analyze student top domain strengths and alignment percentages calculated from coursework and skills.",
            required_role="student",
            parameters={},
            executor=self._tool_get_my_career_strengths,
        )
        self.register(
            name="get_my_career_recommendations",
            description="Retrieve verified prioritized job/internship opportunity recommendations with fit scores and deadlines.",
            required_role="student",
            parameters={},
            executor=self._tool_get_my_career_recommendations,
        )
        self.register(
            name="get_my_skill_gaps",
            description="Retrieve student identified skill gaps and development recommendations for target career domains.",
            required_role="student",
            parameters={},
            executor=self._tool_get_my_skill_gaps,
        )
        self.register(
            name="get_my_complaints",
            description="Retrieve student self-submitted campus complaint tickets, current statuses, and resolution timelines.",
            required_role="student",
            parameters={},
            executor=self._tool_get_my_complaints,
        )
        self.register(
            name="get_my_insights",
            description="Retrieve personalized cross-domain intelligence insights (career alignment, academic risk alerts).",
            required_role="student",
            parameters={},
            executor=self._tool_get_my_insights,
        )
        self.register(
            name="get_my_actions",
            description="Retrieve prioritized next action recommendations across academic deliverables and career steps.",
            required_role="student",
            parameters={},
            executor=self._tool_get_my_actions,
        )

        # Faculty Tools
        self.register(
            name="get_my_classes",
            description="Retrieve authorized faculty course allocations, enrolled student counts, and active deliverables.",
            required_role="faculty",
            parameters={},
            executor=self._tool_get_my_classes,
        )
        self.register(
            name="get_class_attendance",
            description="Retrieve faculty class-level attendance averages and declining attendance student alerts.",
            required_role="faculty",
            parameters={},
            executor=self._tool_get_class_attendance,
        )
        self.register(
            name="get_assignment_submission_trends",
            description="Retrieve faculty class assignment submission velocity, completed percentages, and backlog counts.",
            required_role="faculty",
            parameters={},
            executor=self._tool_get_assignment_submission_trends,
        )
        self.register(
            name="get_department_cases",
            description="Retrieve active complaint and infrastructure cases assigned to faculty department.",
            required_role="faculty",
            parameters={},
            executor=self._tool_get_department_cases,
        )
        self.register(
            name="get_department_alerts",
            description="Retrieve proactive priority alerts for faculty department (e.g. lab projector clusters).",
            required_role="faculty",
            parameters={},
            executor=self._tool_get_department_alerts,
        )
        self.register(
            name="get_teaching_insights",
            description="Retrieve departmental academic insights and teaching delivery analytics.",
            required_role="faculty",
            parameters={},
            executor=self._tool_get_teaching_insights,
        )
        self.register(
            name="get_my_faculty_actions",
            description="Retrieve prioritized faculty actions (grading backlog, attendance review).",
            required_role="faculty",
            parameters={},
            executor=self._tool_get_my_faculty_actions,
        )

        # Management Tools
        self.register(
            name="get_campus_patterns",
            description="Retrieve real-time campus emerging complaint patterns, cluster severities, locations, and trajectories.",
            required_role="management",
            parameters={},
            executor=self._tool_get_campus_patterns,
        )
        self.register(
            name="get_priority_alerts",
            description="Retrieve institutional high-priority operational review alerts requiring administrative intervention.",
            required_role="management",
            parameters={},
            executor=self._tool_get_priority_alerts,
        )
        self.register(
            name="get_institutional_insights",
            description="Retrieve campus-wide cross-domain insights spanning facilities, academics, and transit.",
            required_role="management",
            parameters={},
            executor=self._tool_get_institutional_insights,
        )
        self.register(
            name="get_institutional_actions",
            description="Retrieve institutional action priority items sorted by severity, urgency, and affected student scope.",
            required_role="management",
            parameters={},
            executor=self._tool_get_institutional_actions,
        )
        self.register(
            name="get_department_trends",
            description="Retrieve cross-department attendance comparison, deliverable velocity, and workload metrics.",
            required_role="management",
            parameters={},
            executor=self._tool_get_department_trends,
        )
        self.register(
            name="run_what_if",
            description="Execute deterministic what-if operational simulation (e.g. transit fleet expansion, Wi-Fi maintenance).",
            required_role="management",
            parameters={"scenario": {"type": "string", "description": "Operational scenario description"}},
            executor=self._tool_run_what_if,
        )

        # Universal Tools
        self.register(
            name="get_viit_context",
            description="Retrieve Vignan's Institute of Information Technology (VIIT) institutional knowledge (VR22, grading, grievance cells).",
            required_role="any",
            parameters={"topic": {"type": "string", "description": "Institutional knowledge topic"}},
            executor=self._tool_get_viit_context,
        )

    # Executors
    def _tool_get_my_attendance(self, db: Session, user: User, **_) -> Dict[str, Any]:
        student = db.query(StudentProfile).filter(StudentProfile.user_id == user.id).first() or db.query(StudentProfile).first()
        if not student:
            return {"error": "Student enrollment profile not found."}
        data = academic_service.get_student_attendance(db, student)
        return {
            "overall_percentage": data["overall"]["percentage"],
            "present_sessions": data["overall"]["present"],
            "total_sessions": data["overall"]["total"],
            "od_sessions": data["overall"]["od"],
            "subjects": data["subjects"],
        }

    def _tool_get_my_submission_rate(self, db: Session, user: User, **_) -> Dict[str, Any]:
        student = db.query(StudentProfile).filter(StudentProfile.user_id == user.id).first() or db.query(StudentProfile).first()
        if not student:
            return {"error": "Student enrollment profile not found."}
        data = academic_service.get_student_assignments(db, student)
        counts = data["counts"]
        rate = round((counts["submitted"] / counts["total"] * 100), 1) if counts["total"] > 0 else 100.0
        return {
            "submission_rate_pct": rate,
            "total_assignments": counts["total"],
            "submitted_assignments": counts["submitted"],
            "pending_assignments": counts["pending"],
            "overdue_assignments": counts["overdue"],
        }

    def _tool_get_my_assignments(self, db: Session, user: User, **_) -> Dict[str, Any]:
        student = db.query(StudentProfile).filter(StudentProfile.user_id == user.id).first() or db.query(StudentProfile).first()
        if not student:
            return {"error": "Student enrollment profile not found."}
        data = academic_service.get_student_assignments(db, student)
        return {
            "pending": data.get("pending", []),
            "overdue": data.get("overdue", []),
            "counts": data.get("counts", {}),
        }

    def _tool_get_my_assessments(self, db: Session, user: User, **_) -> Dict[str, Any]:
        student = db.query(StudentProfile).filter(StudentProfile.user_id == user.id).first() or db.query(StudentProfile).first()
        if not student:
            return {"error": "Student enrollment profile not found."}
        data = academic_service.get_student_assessments(db, student)
        return {
            "upcoming": data.get("upcoming", []),
            "completed": data.get("completed", []),
            "overall_average_pct": data.get("overall_average_pct", 0.0),
        }

    def _tool_get_my_academic_summary(self, db: Session, user: User, **_) -> Dict[str, Any]:
        student = db.query(StudentProfile).filter(StudentProfile.user_id == user.id).first() or db.query(StudentProfile).first()
        if not student:
            return {"error": "Student enrollment profile not found."}
        att = academic_service.get_student_attendance(db, student)
        assign = academic_service.get_student_assignments(db, student)
        assess = academic_service.get_student_assessments(db, student)
        return {
            "attendance_percentage": att["overall"]["percentage"],
            "pending_assignments_count": assign["counts"]["pending"],
            "overdue_assignments_count": assign["counts"]["overdue"],
            "upcoming_assessments_count": len(assess.get("upcoming", [])),
            "overall_assessment_avg": assess.get("overall_average_pct", 0.0),
        }

    def _tool_get_my_career_profile(self, db: Session, user: User, **_) -> Dict[str, Any]:
        from app.models.career import CareerProfile
        prof = db.query(CareerProfile).filter(CareerProfile.student_id == user.id).first()
        if not prof:
            from app.routers.career import _get_or_create_career_profile
            prof = _get_or_create_career_profile(db, user)
        return {
            "headline": prof.headline,
            "skills": [s.skill_name for s in prof.skills],
            "projects": [p.title for p in prof.projects],
            "certifications": [c.name for c in prof.certifications],
        }

    def _tool_get_my_career_strengths(self, db: Session, user: User, **_) -> Dict[str, Any]:
        strengths = career_strength_analyzer.analyze_strengths(db, user)
        return {
            "top_strengths": strengths[:3],
            "total_domains_evaluated": len(strengths),
        }

    def _tool_get_my_career_recommendations(self, db: Session, user: User, **_) -> Dict[str, Any]:
        recs = personalized_ranking_engine.get_recommendations(db, user)
        simplified = []
        for r in recs[:4]:
            opp = r["opportunity"]
            simplified.append({
                "id": opp.id,
                "title": opp.title,
                "organization": opp.organization,
                "profile_fit_pct": r["personalized_profile_fit"],
                "eligibility": r["eligibility"]["status"],
                "days_remaining": r.get("days_remaining", 10),
                "matched_skills": r.get("matched_skills", []),
                "work_mode": opp.work_mode,
                "location": opp.location,
            })
        return {
            "recommendations": simplified,
            "total_matches": len(recs),
        }

    def _tool_get_my_skill_gaps(self, db: Session, user: User, **_) -> Dict[str, Any]:
        from app.models.career import CareerProfile
        prof = db.query(CareerProfile).filter(CareerProfile.student_id == user.id).first()
        gaps = matching_engine.get_skill_gaps(db, prof.id) if prof else []
        return {"skill_gaps": gaps[:5]}

    def _tool_get_my_complaints(self, db: Session, user: User, **_) -> Dict[str, Any]:
        complaints = db.query(Complaint).filter(Complaint.student_id == user.id).order_by(Complaint.created_at.desc()).all()
        return {
            "complaints": [
                {
                    "case_id": c.case_id,
                    "title": c.title,
                    "category": c.category,
                    "priority": c.priority,
                    "status": c.status,
                    "location": c.location,
                }
                for c in complaints
            ]
        }

    def _tool_get_my_insights(self, db: Session, user: User, **_) -> Dict[str, Any]:
        insights = insight_engine.evaluate_student_insights(db, user)
        return {
            "insights": [
                {"type": i.insight_type, "severity": i.severity, "title": i.title, "summary": i.summary}
                for i in insights
            ]
        }

    def _tool_get_my_actions(self, db: Session, user: User, **_) -> Dict[str, Any]:
        actions = action_engine.evaluate_student_actions(db, user)
        return {
            "actions": [
                {
                    "action_id": a.id,
                    "priority_score": a.priority_score,
                    "priority": a.priority,
                    "title": a.title,
                    "summary": a.summary,
                    "domain": getattr(a, "source_domain", "ACADEMICS"),
                }
                for a in actions[:3]
            ],
            "total_pending": len(actions),
        }

    # Faculty tools
    def _tool_get_my_classes(self, db: Session, user: User, **_) -> Dict[str, Any]:
        return academic_service.get_faculty_overview(db, user.id)

    def _tool_get_class_attendance(self, db: Session, user: User, **_) -> Dict[str, Any]:
        return academic_service.get_faculty_attendance(db, user.id)

    def _tool_get_assignment_submission_trends(self, db: Session, user: User, **_) -> Dict[str, Any]:
        overview = academic_service.get_faculty_overview(db, user.id)
        return {"courses": overview.get("subjects", [])}

    def _tool_get_department_cases(self, db: Session, user: User, **_) -> Dict[str, Any]:
        cases = (
            db.query(Complaint)
            .filter(Complaint.category.in_(["ACADEMIC", "INFRASTRUCTURE", "TECHNOLOGY"]))
            .order_by(Complaint.created_at.desc())
            .limit(5)
            .all()
        )
        return {
            "cases": [
                {"case_id": c.case_id, "title": c.title, "category": c.category, "status": c.status, "location": c.location}
                for c in cases
            ]
        }

    def _tool_get_department_alerts(self, db: Session, user: User, **_) -> Dict[str, Any]:
        alerts = alert_service.get_faculty_alerts(db, user)
        return {
            "alerts": [
                {"alert_id": a.alert_id, "title": a.title, "severity": a.severity, "cluster_type": a.cluster_type}
                for a in alerts
            ]
        }

    def _tool_get_teaching_insights(self, db: Session, user: User, **_) -> Dict[str, Any]:
        insights = insight_engine.evaluate_faculty_insights(db, user)
        return {
            "insights": [
                {"type": i.insight_type, "severity": i.severity, "title": i.title, "summary": i.summary}
                for i in insights
            ]
        }

    def _tool_get_my_faculty_actions(self, db: Session, user: User, **_) -> Dict[str, Any]:
        actions = action_engine.evaluate_faculty_actions(db, user)
        return {
            "actions": [
                {"title": a.title, "priority": a.priority, "priority_score": a.priority_score, "summary": a.summary}
                for a in actions[:3]
            ],
            "total_pending": len(actions),
        }

    # Management tools
    def _tool_get_campus_patterns(self, db: Session, user: User, **_) -> Dict[str, Any]:
        patterns = pattern_detection_service.detect_and_save_patterns(db)
        if not patterns:
            patterns = db.query(EmergingPattern).filter(EmergingPattern.status == "ACTIVE").all()
        return {
            "patterns": [
                {
                    "title": p.title,
                    "severity": p.severity,
                    "location": getattr(p, "primary_location", "Campus") or "Campus",
                    "affected_estimate": p.affected_estimate,
                }
                for p in patterns
            ],
            "total_active_patterns": len(patterns),
        }

    def _tool_get_priority_alerts(self, db: Session, user: User, **_) -> Dict[str, Any]:
        alerts = alert_service.get_management_alerts(db)
        return {
            "alerts": [
                {"alert_id": a.alert_id, "title": a.title, "severity": a.severity, "reason": a.reason}
                for a in alerts
            ]
        }

    def _tool_get_institutional_insights(self, db: Session, user: User, **_) -> Dict[str, Any]:
        insights = insight_engine.evaluate_management_insights(db, user)
        return {
            "insights": [
                {"type": i.insight_type, "severity": i.severity, "title": i.title, "summary": i.summary}
                for i in insights
            ]
        }

    def _tool_get_institutional_actions(self, db: Session, user: User, **_) -> Dict[str, Any]:
        actions = action_engine.evaluate_management_actions(db, user)
        return {
            "actions": [
                {"title": a.title, "priority": a.priority, "priority_score": a.priority_score, "summary": a.summary}
                for a in actions[:3]
            ],
            "total_pending": len(actions),
        }

    def _tool_get_department_trends(self, db: Session, user: User, **_) -> Dict[str, Any]:
        return academic_service.get_management_departments_breakdown(db, "30d")

    def _tool_run_what_if(self, db: Session, user: User, **params: Any) -> Dict[str, Any]:
        return {
            "scenario": "Transit fleet expansion (+1 bus)",
            "calculated_metrics": {
                "active_fleet_size": 6,
                "peak_hourly_capacity": 550,
                "avg_boarding_wait_time_min": 12.0,
                "estimated_monthly_operating_cost": 9650,
                "forecasted_transit_complaints": 4,
            },
            "impact_summary": "Adding +1 bus reduces average boarding wait time from 18.5m to 12.0m (-35.1%).",
        }

    # Universal tools
    def _tool_get_viit_context(self, db: Session, user: User, **params: Any) -> Dict[str, Any]:
        return {
            "metadata": VIIT_METADATA,
            "departments": list(VIIT_DEPARTMENTS.keys()),
        }


tool_registry = ToolRegistry()
