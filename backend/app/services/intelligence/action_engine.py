"""
Centralized Action Intelligence Engine for VIGNAI OS (Phase 10).
"From Insights to Decisions"
Orchestrates verified insights, academic signals, career fit, and incident clusters
into a prioritized, evidence-backed list of recommended user actions.
"""

import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session

from app.models.user import User
from app.models.student import StudentProfile
from app.models.academic_subject import AcademicSubject
from app.models.academic_enrollment import StudentSubjectEnrollment
from app.models.attendance_record import AttendanceRecord
from app.models.assessment import Assessment, AssessmentResult
from app.models.assignment import Assignment
from app.models.complaint import Complaint
from app.models.alert import VignaiAlert
from app.models.career import CareerProfile, CareerSkill, Opportunity
from app.models.insight import VignaiInsight
from app.models.action import VignaiAction
from app.models.notification import Notification

from app.services.intelligence.insight_engine import insight_engine
from app.services.intelligence.academic_service import academic_service
from app.services.career.career_fit_service import CareerStrengthAnalyzer, PersonalizedRecommendationEngine

logger = logging.getLogger(__name__)


class ActionEngine:
    """
    Deterministic Action Intelligence Orchestrator.
    Calculates Action Priority:
    PriorityScore = (Urgency * 0.35) + (Impact * 0.30) + (EvidenceStrength * 0.20) + (Relevance * 0.15)
    Normalized:
    CRITICAL: >= 0.85
    HIGH:     >= 0.65
    MEDIUM:   >= 0.40
    LOW:      < 0.40
    """

    def calculate_priority(
        self,
        urgency: float,
        impact: float,
        evidence_strength: float,
        relevance: float,
    ) -> tuple[str, float]:
        """Calculates deterministic priority score and label."""
        score = round((urgency * 0.35) + (impact * 0.30) + (evidence_strength * 0.20) + (relevance * 0.15), 3)
        if score >= 0.85:
            return "CRITICAL", score
        elif score >= 0.65:
            return "HIGH", score
        elif score >= 0.40:
            return "MEDIUM", score
        else:
            return "LOW", score

    # --------------------------------------------------------------------------
    # 1. STUDENT ACTION CENTER
    # --------------------------------------------------------------------------
    def evaluate_student_actions(self, db: Session, user: User) -> List[VignaiAction]:
        """
        Evaluates student actions from underlying insights and academic/career signals.
        Max 3-5 prioritized actions returned.
        """
        actions: List[VignaiAction] = []
        now = datetime.utcnow()

        # 1. Generate/sync underlying insights first
        insights = insight_engine.evaluate_student_insights(db, user)

        for ins in insights:
            try:
                action_item = self._map_insight_to_student_action(db, user, ins)
                if action_item:
                    actions.append(action_item)
            except Exception as e:
                logger.error(f"Error mapping insight {ins.id} to student action: {e}")

        # Check for expired actions where underlying conditions resolved
        self._expire_stale_actions(db, role="student", user_id=user.id)

        # Return active actions sorted by priority score
        return self._get_active_actions_for_role(db, role="student", user_id=user.id, max_items=5)

    def _map_insight_to_student_action(self, db: Session, user: User, ins: VignaiInsight) -> Optional[VignaiAction]:
        """Maps a student VignaiInsight into an actionable VignaiAction with deterministic priority."""
        now = datetime.utcnow()
        action_type = ins.insight_type
        target_route = ins.recommended_action.get("url", "/student/dashboard")
        signals = ins.evidence.get("signals", [])

        if ins.insight_type == "ACADEMIC_RISK":
            # Attendance Risk
            subj_code = ins.evidence.get("details", {}).get("subject_code", "Course")
            att_pct = ins.evidence.get("details", {}).get("attendance_pct", 70.0)
            is_critical = att_pct < 65.0

            urgency = 0.95 if is_critical else 0.80
            impact = 0.90 if is_critical else 0.75
            evidence_strength = 0.95
            relevance = 1.0

            priority_label, score = self.calculate_priority(urgency, impact, evidence_strength, relevance)
            why_first = [
                f"Attendance is at {att_pct}% ({'Detention warning' if is_critical else 'Condonation range'})",
                "Requires immediate attendance recovery to satisfy 75% SEE eligibility",
                "Continuous assessment window active",
            ]
            ask_query = f"Why is {subj_code} attendance currently a priority for me?"

            dedup_key = f"ACTION|student|{user.id}|academic|{subj_code}|attendance"
            return self._upsert_action(
                db=db,
                dedup_key=dedup_key,
                action_type="ACADEMIC_ATTENDANCE",
                priority=priority_label,
                priority_score=score,
                title=f"Review {subj_code} Attendance",
                summary=f"Attendance in {subj_code} is currently at {att_pct}%. Immediate attendance review recommended before examination cutoff.",
                role="student",
                target_user_id=user.id,
                source_insight_id=ins.id,
                source_domain="ACADEMICS",
                evidence={
                    "urgency": urgency,
                    "impact": impact,
                    "evidence_strength": evidence_strength,
                    "relevance": relevance,
                    "signals": signals,
                    "why_first": why_first,
                    "conclusion": f"VIGNAI recommends attending upcoming {subj_code} lectures to maintain academic eligibility.",
                },
                recommended_action={
                    "label": "Review Attendance Logs",
                    "url": target_route,
                    "action_type": "VIEW_ACADEMIC",
                    "description": "Inspect session breakdown and calculate minimum attendance required.",
                },
                target_route=target_route,
                ask_vignai_query=ask_query,
                expires_at=ins.expires_at or (now + timedelta(days=14)),
                notify=(priority_label in ["CRITICAL", "HIGH"]),
            )

        elif ins.insight_type in ["CROSS_DOMAIN", "CAREER_OPPORTUNITY"]:
            # Closing Opportunity
            opp_title = ins.evidence.get("details", {}).get("opportunity_title", "Opportunity")
            days_left = ins.evidence.get("details", {}).get("days_remaining", 3)
            fit_score = ins.evidence.get("details", {}).get("fit_score", 85)
            opp_id = ins.evidence.get("details", {}).get("opportunity_id", 1)

            urgency = 0.90 if (days_left is not None and days_left <= 2) else 0.75
            impact = 0.85
            evidence_strength = 0.90
            relevance = 0.95

            priority_label, score = self.calculate_priority(urgency, impact, evidence_strength, relevance)
            why_first = [
                f"Application deadline closing in {days_left} day(s)",
                f"Personalized Profile Fit: {fit_score}% (High Alignment)",
                "Academic and branch eligibility verified",
            ]
            ask_query = f"Why is the {opp_title} opportunity recommended for me to act on first?"

            opp_target_route = target_route if target_route.startswith("/student/career") else f"/student/career#opportunity-{opp_id}"

            dedup_key = f"ACTION|student|{user.id}|career|opp_{opp_id}"
            return self._upsert_action(
                db=db,
                dedup_key=dedup_key,
                action_type="CAREER_OPPORTUNITY",
                priority=priority_label,
                priority_score=score,
                title=f"Apply to {opp_title}",
                summary=f"High-fit verified opportunity closing in {days_left} day(s). Profile fit is {fit_score}%.",
                role="student",
                target_user_id=user.id,
                source_insight_id=ins.id,
                source_domain="CROSS_DOMAIN",
                evidence={
                    "urgency": urgency,
                    "impact": impact,
                    "evidence_strength": evidence_strength,
                    "relevance": relevance,
                    "signals": signals,
                    "why_first": why_first,
                    "conclusion": "High personalized fit and impending deadline make this a priority action.",
                },
                recommended_action={
                    "label": "Review Opportunity",
                    "url": opp_target_route,
                    "action_type": "VIEW_OPPORTUNITY",
                    "description": "Inspect match explanation and submit before application portal closes.",
                },
                target_route=opp_target_route,
                ask_vignai_query=ask_query,
                expires_at=ins.expires_at or (now + timedelta(days=max(days_left or 1, 1))),
                notify=(priority_label in ["CRITICAL", "HIGH"]),
            )

        elif ins.insight_type == "PREVENTIVE_ACTION":
            # Skill Gap
            missing_skill = ins.evidence.get("details", {}).get("missing_skill", "Technical Competency")
            urgency = 0.50
            impact = 0.70
            evidence_strength = 0.85
            relevance = 0.85

            priority_label, score = self.calculate_priority(urgency, impact, evidence_strength, relevance)
            why_first = [
                f"{missing_skill} is required by multiple high-fit opportunities in your domain",
                "Not currently verified in your student profile",
                "Non-punitive proactive learning suggestion",
            ]
            ask_query = f"Why should I focus on improving {missing_skill} skills?"

            dedup_key = f"ACTION|student|{user.id}|skill|{missing_skill.lower()}"
            return self._upsert_action(
                db=db,
                dedup_key=dedup_key,
                action_type="CAREER_SKILL_GAP",
                priority=priority_label,
                priority_score=score,
                title=f"Improve {missing_skill} Skills",
                summary=f"Technical skill {missing_skill} appears in multiple target roles. Strengthening this expands eligible opportunities.",
                role="student",
                target_user_id=user.id,
                source_insight_id=ins.id,
                source_domain="CAREER",
                evidence={
                    "urgency": urgency,
                    "impact": impact,
                    "evidence_strength": evidence_strength,
                    "relevance": relevance,
                    "signals": signals,
                    "why_first": why_first,
                    "conclusion": f"Building competence in {missing_skill} directly improves match scores.",
                },
                recommended_action={
                    "label": "View Skill Gap Diagnostics",
                    "url": target_route,
                    "action_type": "VIEW_SKILL_GAPS",
                    "description": f"Explore learning resources and mini-projects for {missing_skill}.",
                },
                target_route=target_route,
                ask_vignai_query=ask_query,
                expires_at=ins.expires_at or (now + timedelta(days=21)),
            )

        elif ins.insight_type == "CAREER_ALIGNMENT":
            # Domain Exploration
            domain_name = ins.evidence.get("details", {}).get("domain_name", "Field")
            align_score = ins.evidence.get("details", {}).get("alignment_score", 70)
            urgency = 0.30
            impact = 0.60
            evidence_strength = 0.80
            relevance = 0.80

            priority_label, score = self.calculate_priority(urgency, impact, evidence_strength, relevance)
            why_first = [
                f"Coursework and skills show {align_score}% alignment with {domain_name}",
                "Positive career trajectory indicator",
            ]
            ask_query = f"Why did VIGNAI suggest exploring {domain_name} as a career direction?"

            dedup_key = f"ACTION|student|{user.id}|career_align|{domain_name.lower()}"
            return self._upsert_action(
                db=db,
                dedup_key=dedup_key,
                action_type="CAREER_EXPLORATION",
                priority=priority_label,
                priority_score=score,
                title=f"Explore {domain_name} Fit",
                summary=f"Your profile reflects a solid {align_score}% alignment with {domain_name}. Explore matched job profiles and certifications.",
                role="student",
                target_user_id=user.id,
                source_insight_id=ins.id,
                source_domain="CAREER",
                evidence={
                    "urgency": urgency,
                    "impact": impact,
                    "evidence_strength": evidence_strength,
                    "relevance": relevance,
                    "signals": signals,
                    "why_first": why_first,
                    "conclusion": f"Observed academic strengths highlight positive alignment with {domain_name}.",
                },
                recommended_action={
                    "label": "Explore Career Strengths",
                    "url": target_route,
                    "action_type": "VIEW_CAREER",
                    "description": f"Review breakdown and matched roles for {domain_name}.",
                },
                target_route=target_route,
                ask_vignai_query=ask_query,
                expires_at=ins.expires_at or (now + timedelta(days=30)),
            )

        return None

    # --------------------------------------------------------------------------
    # 2. FACULTY ACTION CENTER (Department Priorities + Teaching Improvement)
    # --------------------------------------------------------------------------
    def evaluate_faculty_actions(self, db: Session, user: User) -> List[VignaiAction]:
        """
        Evaluates faculty department actions and non-punitive teaching improvement items.
        Strict privacy: No individual student PII or protected complaint identities.
        """
        actions: List[VignaiAction] = []
        now = datetime.utcnow()
        dept_code = "CSE"
        if hasattr(user, "department") and getattr(user, "department", None):
            dept_code = user.department.code or "CSE"

        # 1. Department Complaint Clusters
        dept_insights = insight_engine.evaluate_faculty_insights(db, user)
        for ins in dept_insights:
            try:
                is_urgent = ins.severity in ["HIGH", "CRITICAL"]
                urgency = 0.90 if is_urgent else 0.60
                impact = 0.85
                evidence_strength = 0.90
                relevance = 1.0

                priority_label, score = self.calculate_priority(urgency, impact, evidence_strength, relevance)
                signals = ins.evidence.get("signals", [])
                why_first = [
                    f"{ins.severity} priority department incident cluster",
                    f"Concentrated reports in {ins.evidence.get('details', {}).get('location', 'department')}",
                    "Requires assignment of technical resolution team",
                ]

                dedup_key = f"ACTION|faculty|{dept_code}|dept_alert_{ins.id}"
                act = self._upsert_action(
                    db=db,
                    dedup_key=dedup_key,
                    action_type="CAMPUS_CLUSTER",
                    priority=priority_label,
                    priority_score=score,
                    title=f"Review {ins.title}",
                    summary=f"Recurring incidents reported in {ins.evidence.get('details', {}).get('location', dept_code)}. Assign department coordinator.",
                    role="faculty",
                    target_department=dept_code,
                    source_insight_id=ins.id,
                    source_domain="COMPLAINTS",
                    evidence={
                        "urgency": urgency,
                        "impact": impact,
                        "evidence_strength": evidence_strength,
                        "relevance": relevance,
                        "signals": signals,
                        "why_first": why_first,
                        "conclusion": "Timely department triage prevents escalating student disruption.",
                    },
                    recommended_action={
                        "label": "Investigate Incident Queue",
                        "url": ins.recommended_action.get("url", "/faculty/cases"),
                        "action_type": "VIEW_CASES",
                        "description": "Inspect anonymous aggregated incident queue and delegate resolution.",
                    },
                    target_route=ins.recommended_action.get("url", "/faculty/cases"),
                    ask_vignai_query=f"Why is {ins.title} currently a departmental priority?",
                    expires_at=ins.expires_at or (now + timedelta(days=7)),
                    notify=is_urgent,
                )
                actions.append(act)
            except Exception as e:
                logger.error(f"Error mapping faculty insight {ins.id} to action: {e}")

        # 2. Teaching Improvement Actions (Non-Punitive)
        try:
            faculty_overview = academic_service.get_faculty_overview(db, user.id)
            for cls in faculty_overview.get("classes", []):
                s_id = cls.get("subject_id")
                s_code = cls.get("subject_code")
                s_name = cls.get("subject_name")
                att_pct = cls.get("attendance_percentage", 100.0)

                # Class Attendance Trend Alert
                if att_pct < 75.0:
                    urgency = 0.70
                    impact = 0.75
                    evidence_strength = 0.85
                    relevance = 0.90

                    priority_label, score = self.calculate_priority(urgency, impact, evidence_strength, relevance)
                    why_first = [
                        f"Overall class attendance in {s_code} is {att_pct}% (<75% threshold)",
                        "Non-punitive instructional support alert",
                        "Consider reviewing session pace or timing conflicts",
                    ]

                    dedup_key = f"ACTION|faculty|{user.id}|teaching|att_{s_id}"
                    act = self._upsert_action(
                        db=db,
                        dedup_key=dedup_key,
                        action_type="TEACHING_IMPROVEMENT",
                        priority=priority_label,
                        priority_score=score,
                        title=f"Review {s_code} Class Attendance",
                        summary=f"Average attendance for {s_code} ({s_name}) is currently {att_pct}%. Review class timeline and engagement.",
                        role="faculty",
                        target_user_id=user.id,
                        target_department=dept_code,
                        source_domain="ACADEMICS",
                        evidence={
                            "urgency": urgency,
                            "impact": impact,
                            "evidence_strength": evidence_strength,
                            "relevance": relevance,
                            "signals": [
                                {"domain": "ACADEMICS", "metric": f"{s_code} Class Average Attendance", "value": f"{att_pct}%", "source": "VIIT Class Roll"}
                            ],
                            "why_first": why_first,
                            "conclusion": f"Proactive attendance review supports student exam qualification in {s_code}.",
                        },
                        recommended_action={
                            "label": "Review Class Analytics",
                            "url": f"/faculty/academics/classes/{s_id}",
                            "action_type": "VIEW_CLASS",
                            "description": "Inspect attendance distribution and identify attendance trends.",
                        },
                        target_route=f"/faculty/academics/classes/{s_id}",
                        ask_vignai_query=f"What instructional insights does VIGNAI have for {s_code}?",
                        expires_at=now + timedelta(days=14),
                    )
                    actions.append(act)
        except Exception as e:
            logger.error(f"Error calculating faculty teaching improvement actions: {e}")

        # Expire stale faculty actions
        self._expire_stale_actions(db, role="faculty", department=dept_code)

        return self._get_active_actions_for_role(db, role="faculty", department=dept_code, max_items=5)

    # --------------------------------------------------------------------------
    # 3. MANAGEMENT ACTION CENTER (Institutional Priorities + What-If)
    # --------------------------------------------------------------------------
    def evaluate_management_actions(self, db: Session, user: User) -> List[VignaiAction]:
        """
        Evaluates campus-wide institutional actions and What-If recommendations.
        Strict privacy: Zero individual student PII.
        """
        actions: List[VignaiAction] = []
        now = datetime.utcnow()

        mgmt_insights = insight_engine.evaluate_management_insights(db, user)
        for ins in mgmt_insights:
            try:
                is_urgent = ins.severity in ["HIGH", "CRITICAL"]
                urgency = 0.95 if is_urgent else 0.65
                impact = 0.90
                evidence_strength = 0.90
                relevance = 1.0

                priority_label, score = self.calculate_priority(urgency, impact, evidence_strength, relevance)
                signals = ins.evidence.get("signals", [])
                loc = ins.evidence.get("details", {}).get("location", "Campus")
                why_first = [
                    f"{ins.severity} priority institutional issue",
                    f"Concentrated incident reports in {loc}",
                    "Recommended for preventive simulation and resource dispatch",
                ]

                # What-If integration
                has_what_if = is_urgent
                target_route = f"/management/what-if?location={loc}" if has_what_if else "/management"
                action_label = "Run What-If Analysis" if has_what_if else "View Cluster Details"

                dedup_key = f"ACTION|management|campus_cluster_{ins.id}"
                act = self._upsert_action(
                    db=db,
                    dedup_key=dedup_key,
                    action_type="WHAT_IF_SIMULATION" if has_what_if else "CAMPUS_CLUSTER",
                    priority=priority_label,
                    priority_score=score,
                    title=f"Review {ins.title}",
                    summary=f"{ins.title} in {loc} is showing elevated incident frequency. Evaluate resource allocation or model impact in What-If Lab.",
                    role="management",
                    source_insight_id=ins.id,
                    source_domain="CAMPUS_INTELLIGENCE",
                    evidence={
                        "urgency": urgency,
                        "impact": impact,
                        "evidence_strength": evidence_strength,
                        "relevance": relevance,
                        "signals": signals,
                        "why_first": why_first,
                        "conclusion": f"Simulating or addressing {ins.title} prevents campus-wide operational friction.",
                    },
                    recommended_action={
                        "label": action_label,
                        "url": target_route,
                        "action_type": "RUN_WHAT_IF" if has_what_if else "VIEW_CASES",
                        "description": "Model escalation trajectory and evaluate preventive resource allocation.",
                    },
                    target_route=target_route,
                    ask_vignai_query=f"Why is {ins.title} an institutional priority today?",
                    expires_at=ins.expires_at or (now + timedelta(days=7)),
                    notify=is_urgent,
                )
                actions.append(act)
            except Exception as e:
                logger.error(f"Error mapping management insight {ins.id} to action: {e}")

        # Expire stale management actions
        self._expire_stale_actions(db, role="management")

        return self._get_active_actions_for_role(db, role="management", max_items=5)

    # --------------------------------------------------------------------------
    # 4. DAILY ACTION SUMMARY
    # --------------------------------------------------------------------------
    def get_daily_summary(self, db: Session, user: User) -> Dict[str, Any]:
        """Generates role-specific daily action briefing with live counts."""
        role = user.role
        actions: List[VignaiAction] = []

        if role == "student":
            actions = self.evaluate_student_actions(db, user)
            greeting = "GOOD MORNING"
            highlights = []
            if actions:
                highlights.append(f"Top priority: {actions[0].title}")
                opp_acts = [a for a in actions if a.action_type == "CAREER_OPPORTUNITY"]
                if opp_acts:
                    highlights.append(f"Career: {len(opp_acts)} high-fit opportunity closes soon")
                skill_acts = [a for a in actions if a.action_type == "CAREER_SKILL_GAP"]
                if skill_acts:
                    highlights.append(f"Learning: {skill_acts[0].title}")
            else:
                highlights.append("All academic and career parameters are in steady standing.")

            return {
                "role": "student",
                "greeting": greeting,
                "total_priorities": len(actions),
                "top_priority_title": actions[0].title if actions else "Steady Standing",
                "highlights": highlights,
                "actions": actions,
            }

        elif role == "faculty":
            actions = self.evaluate_faculty_actions(db, user)
            greeting = "TODAY'S DEPARTMENT PRIORITIES"
            highlights = [f"{len(actions)} active departmental and instructional focus area(s)"]
            if actions:
                highlights.append(f"Primary focus: {actions[0].title}")

            return {
                "role": "faculty",
                "greeting": greeting,
                "total_priorities": len(actions),
                "top_priority_title": actions[0].title if actions else "Department Normal",
                "highlights": highlights,
                "actions": actions,
            }

        else:
            actions = self.evaluate_management_actions(db, user)
            greeting = "TODAY'S INSTITUTIONAL PRIORITIES"
            highlights = [f"{len(actions)} active institutional priority focus item(s)"]
            if actions:
                highlights.append(f"Primary operational focus: {actions[0].title}")

            return {
                "role": "management",
                "greeting": greeting,
                "total_priorities": len(actions),
                "top_priority_title": actions[0].title if actions else "Operations Nominal",
                "highlights": highlights,
                "actions": actions,
            }

    # --------------------------------------------------------------------------
    # 5. LIFECYCLE & STATE TRANSITIONS
    # --------------------------------------------------------------------------
    def mark_seen(self, db: Session, action_id: int, user: User) -> VignaiAction:
        """Transitions action from NEW to SEEN."""
        act = self._get_accessible_action(db, action_id, user)
        if act.status == "NEW":
            act.status = "SEEN"
            db.commit()
            db.refresh(act)
        return act

    def mark_in_progress(self, db: Session, action_id: int, user: User) -> VignaiAction:
        """Transitions action to IN_PROGRESS."""
        act = self._get_accessible_action(db, action_id, user)
        act.status = "IN_PROGRESS"
        db.commit()
        db.refresh(act)
        return act

    def mark_completed(self, db: Session, action_id: int, user: User) -> VignaiAction:
        """Transitions action to COMPLETED."""
        act = self._get_accessible_action(db, action_id, user)
        act.status = "COMPLETED"
        db.commit()
        db.refresh(act)
        return act

    def mark_dismissed(self, db: Session, action_id: int, user: User) -> VignaiAction:
        """Transitions action to DISMISSED."""
        act = self._get_accessible_action(db, action_id, user)
        act.status = "DISMISSED"
        db.commit()
        db.refresh(act)
        return act

    # --------------------------------------------------------------------------
    # 6. INTERNAL HELPERS & RESILIENCE
    # --------------------------------------------------------------------------
    def _upsert_action(
        self,
        db: Session,
        dedup_key: str,
        action_type: str,
        priority: str,
        priority_score: float,
        title: str,
        summary: str,
        role: str,
        source_domain: str,
        evidence: Dict[str, Any],
        recommended_action: Dict[str, Any],
        target_route: str,
        target_user_id: Optional[int] = None,
        target_department: Optional[str] = None,
        source_insight_id: Optional[int] = None,
        ask_vignai_query: Optional[str] = None,
        expires_at: Optional[datetime] = None,
        notify: bool = False,
    ) -> VignaiAction:
        """Creates or updates an action without duplicating active entries."""
        existing = db.query(VignaiAction).filter(
            VignaiAction.deduplication_key == dedup_key
        ).first()

        if existing:
            if existing.status not in ["DISMISSED", "COMPLETED"]:
                existing.priority = priority
                existing.priority_score = priority_score
                existing.title = title
                existing.summary = summary
                existing.evidence = evidence
                existing.recommended_action = recommended_action
                existing.target_route = target_route
                existing.ask_vignai_query = ask_vignai_query
                existing.expires_at = expires_at
                existing.updated_at = datetime.utcnow()
                db.commit()
                db.refresh(existing)
            return existing

        new_act = VignaiAction(
            action_type=action_type,
            priority=priority,
            priority_score=priority_score,
            title=title,
            summary=summary,
            role=role,
            target_user_id=target_user_id,
            target_department=target_department,
            source_insight_id=source_insight_id,
            source_domain=source_domain,
            evidence=evidence,
            recommended_action=recommended_action,
            target_route=target_route,
            ask_vignai_query=ask_vignai_query,
            status="NEW",
            deduplication_key=dedup_key,
            expires_at=expires_at,
        )
        db.add(new_act)
        db.commit()
        db.refresh(new_act)

        # Notification integration for critical/high priorities
        if notify and priority in ["CRITICAL", "HIGH"]:
            self._dispatch_action_notification(db, new_act)

        return new_act

    def _dispatch_action_notification(self, db: Session, action: VignaiAction) -> None:
        """Creates a high-value notification for urgent actions without spamming."""
        try:
            target_user_ids: List[int] = []
            if action.target_user_id:
                target_user_ids.append(action.target_user_id)
            elif action.role == "faculty" and action.target_department:
                faculty_users = db.query(User).filter(
                    User.role == "faculty",
                    User.is_active == True,
                ).all()
                target_user_ids = [f.id for f in faculty_users if getattr(getattr(f, "department", None), "code", "CSE") == action.target_department]
            elif action.role in ["management", "admin"]:
                mgmt_users = db.query(User).filter(User.role.in_(["management", "admin"])).all()
                target_user_ids = [m.id for m in mgmt_users]

            raw_url = action.target_route or f"/{action.role}"
            target_route = raw_url
            anchor = None
            query = None
            if "#" in target_route:
                target_route, anchor = target_route.split("#", 1)
            if "?" in target_route:
                target_route, query = target_route.split("?", 1)

            for u_id in target_user_ids:
                existing_notif = db.query(Notification).filter(
                    Notification.user_id == u_id,
                    Notification.title == action.title,
                    Notification.is_read == False,
                ).first()
                if not existing_notif:
                    notif = Notification(
                        user_id=u_id,
                        title=action.title,
                        message=action.summary,
                        is_read=False,
                        notification_type="ACTION",
                        target_route=target_route,
                        target_entity_type="ACTION",
                        target_entity_id=str(action.id),
                        target_anchor=anchor or f"action-{action.id}",
                        target_query=query,
                        source_action_id=action.id,
                        source_insight_id=action.source_insight_id,
                    )
                    db.add(notif)
            db.commit()
        except Exception as e:
            logger.error(f"Error dispatching action notification: {e}")

    def _expire_stale_actions(
        self,
        db: Session,
        role: str,
        user_id: Optional[int] = None,
        department: Optional[str] = None,
    ) -> None:
        """Marks actions EXPIRED when condition resolved or past deadline."""
        now = datetime.utcnow()
        query = db.query(VignaiAction).filter(
            VignaiAction.role == role,
            VignaiAction.status.in_(["NEW", "SEEN", "IN_PROGRESS"]),
        )
        if user_id:
            query = query.filter(VignaiAction.target_user_id == user_id)
        if department:
            query = query.filter(VignaiAction.target_department == department)

        active_actions = query.all()
        for act in active_actions:
            # 1. Past expiration date
            if act.expires_at and act.expires_at < now:
                act.status = "EXPIRED"
            # 2. Underlying insight resolved/expired
            elif act.source_insight_id:
                ins = db.query(VignaiInsight).filter(VignaiInsight.id == act.source_insight_id).first()
                if ins and ins.status in ["EXPIRED", "DISMISSED", "ACTIONED"]:
                    act.status = "EXPIRED"

        db.commit()

    def _get_active_actions_for_role(
        self,
        db: Session,
        role: str,
        user_id: Optional[int] = None,
        department: Optional[str] = None,
        max_items: int = 5,
    ) -> List[VignaiAction]:
        """Retrieves active (NEW, SEEN, IN_PROGRESS) actions sorted deterministically by priority score."""
        query = db.query(VignaiAction).filter(
            VignaiAction.role == role,
            VignaiAction.status.in_(["NEW", "SEEN", "IN_PROGRESS"]),
        )
        if user_id:
            query = query.filter(VignaiAction.target_user_id == user_id)
        if department:
            query = query.filter(VignaiAction.target_department == department)

        actions = query.all()

        # Priority ranking order: priority_score desc, created_at desc
        actions.sort(key=lambda x: (x.priority_score, x.created_at.timestamp() if x.created_at else 0), reverse=True)
        return actions[:max_items]

    def _get_accessible_action(self, db: Session, action_id: int, user: User) -> VignaiAction:
        """Enforces strict RBAC on action item access."""
        act = db.query(VignaiAction).filter(VignaiAction.id == action_id).first()
        if not act:
            from fastapi import HTTPException, status
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Action not found.")

        if user.role == "student" and act.target_user_id != user.id:
            from fastapi import HTTPException, status
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied to this action.")

        return act


action_engine = ActionEngine()
