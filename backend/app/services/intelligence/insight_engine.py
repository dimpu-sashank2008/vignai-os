"""
Centralized Cross-Domain Insight Engine for VIGNAI OS (Phase 9).
Collects signals across Academics, Career Intelligence, Complaints, Proactive Alerts,
and VIIT Institutional Context to generate deterministic, evidence-grounded insights.
"""

import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.user import User
from app.models.student import StudentProfile
from app.models.academic_subject import AcademicSubject
from app.models.academic_enrollment import StudentSubjectEnrollment
from app.models.attendance_record import AttendanceRecord
from app.models.assessment import Assessment, AssessmentResult
from app.models.complaint import Complaint
from app.models.alert import VignaiAlert
from app.models.career import CareerProfile, CareerSkill, Opportunity
from app.models.insight import VignaiInsight
from app.models.notification import Notification

from app.services.intelligence.grouping_service import GroupingService
from app.services.intelligence.alert_service import VignaiAlertService
from app.services.intelligence.academic_service import academic_service
from app.services.career.career_fit_service import career_strength_analyzer, personalized_ranking_engine, eligibility_engine
from app.services.career.domain_taxonomy import CAREER_DOMAINS

logger = logging.getLogger(__name__)


class InsightEngine:
    """
    Centralized cross-domain intelligence engine.
    Detects cross-domain patterns deterministically, attaches evidence,
    and manages insight lifecycles and notifications without LLM score synthesis.
    """

    def __init__(self):
        self.alert_service = VignaiAlertService()
        self.grouping_service = GroupingService()

    def sync_all_insights(self, db: Session) -> None:
        """Runs periodic or triggered full synchronization across all domains and active users."""
        users = db.query(User).filter(User.is_active == True).all()
        for u in users:
            try:
                if u.role == "student":
                    self.evaluate_student_insights(db, u)
                elif u.role == "faculty":
                    self.evaluate_faculty_insights(db, u)
                elif u.role in ["management", "admin"]:
                    self.evaluate_management_insights(db, u)
            except Exception as e:
                logger.error(f"Error syncing insights for user {u.id} ({u.role}): {e}", exc_info=True)

    # --------------------------------------------------------------------------
    # 1. STUDENT INSIGHTS (Rules A, B, C, F, and Cross-Domain)
    # --------------------------------------------------------------------------
    def evaluate_student_insights(self, db: Session, user: User) -> List[VignaiInsight]:
        """
        Evaluates student cross-domain signals (Academics, Career Strengths, Opportunities, Skill Gaps).
        Strict privacy: Only personal student records evaluated.
        """
        generated_insights: List[VignaiInsight] = []
        now = datetime.utcnow()
        student_prof = db.query(StudentProfile).filter(StudentProfile.user_id == user.id).first()
        career_prof = db.query(CareerProfile).filter(CareerProfile.student_id == user.id).first()

        # ----------------------------------------------------------------------
        # RULE A: Academic -> Career Alignment (CAREER_ALIGNMENT)
        # ----------------------------------------------------------------------
        try:
            domain_strengths = career_strength_analyzer.analyze_strengths(db, user)
            if domain_strengths:
                top_domain = domain_strengths[0]
                if top_domain["alignment_score"] >= 60.0:
                    d_name = top_domain["domain_name"]
                    d_score = int(top_domain["alignment_score"])
                    
                    signals = [
                        {
                            "domain": "CAREER",
                            "metric": f"{d_name} Alignment Score",
                            "value": f"{d_score}% (Strong Fit)",
                            "source": "Career Strength Analyzer",
                        }
                    ]
                    for s in top_domain.get("relevant_subjects", [])[:2]:
                        signals.append({
                            "domain": "ACADEMICS",
                            "metric": f"{s['code']} {s['name']}",
                            "value": f"{int(s['score'])}% Score",
                            "source": "Assessment Records",
                        })
                    for sk in top_domain.get("matched_skills", [])[:3]:
                        signals.append({
                            "domain": "CAREER",
                            "metric": f"Verified Skill: {sk}",
                            "value": "Verified",
                            "source": "Verified Career Profile",
                        })

                    dedup_key = f"CAREER_ALIGNMENT|{user.id}|{top_domain['domain_id']}"
                    ins = self._upsert_insight(
                        db=db,
                        dedup_key=dedup_key,
                        insight_type="CAREER_ALIGNMENT",
                        severity="INFO",
                        title=f"Strong Career Alignment: {d_name}",
                        summary=f"Your verified profile and academic strengths show a strong {d_score}% alignment with {d_name}.",
                        role="student",
                        target_user_id=user.id,
                        source_domains=["ACADEMICS", "CAREER"],
                        evidence={
                            "signals": signals,
                            "details": {
                                "domain_id": top_domain["domain_id"],
                                "domain_name": d_name,
                                "alignment_score": d_score,
                                "summary_phrase": top_domain.get("summary_phrase", ""),
                            },
                            "conclusion": f"Observed coursework performance and technical competencies indicate strong alignment with {d_name}.",
                        },
                        recommended_action={
                            "label": "Explore Career Fit",
                            "url": "/student/career#strengths",
                            "action_type": "VIEW_CAREER",
                            "description": "Review your domain breakdown and matched industry roles.",
                        },
                        expires_at=now + timedelta(days=30),
                    )
                    generated_insights.append(ins)
        except Exception as e:
            logger.error(f"Rule A evaluation error for user {user.id}: {e}")

        # ----------------------------------------------------------------------
        # RULE B: Academic Risk (ACADEMIC_RISK)
        # ----------------------------------------------------------------------
        try:
            if student_prof:
                att_summary = academic_service.get_student_attendance(db, student_prof)
                for subj in att_summary.get("subjects", []):
                    code = subj.get("code")
                    pct = subj.get("percentage", 100.0)
                    trend = subj.get("trend")
                    
                    is_declining = trend and trend.get("direction") == "DECLINING"
                    is_low_att = pct < 75.0
                    
                    if is_low_att or is_declining:
                        severity = "HIGH" if pct < 65.0 else "MEDIUM"
                        signals = [
                            {
                                "domain": "ACADEMICS",
                                "metric": f"{code} Attendance Percentage",
                                "value": f"{pct}%",
                                "source": "VIIT Attendance Logs",
                            }
                        ]
                        if trend:
                            signals.append({
                                "domain": "ACADEMICS",
                                "metric": f"{code} Attendance Trajectory",
                                "value": f"Declining ({trend.get('from_pct')}% -> {trend.get('to_pct')}%)",
                                "source": "14-Session Window Calculation",
                            })

                        dedup_key = f"ACADEMIC_RISK|{user.id}|{code}|attendance_risk"
                        ins = self._upsert_insight(
                            db=db,
                            dedup_key=dedup_key,
                            insight_type="ACADEMIC_RISK",
                            severity=severity,
                            title=f"Academic Signal: Declining Attendance in {code}",
                            summary=f"VIGNAI detected a declining attendance trajectory in {code} ({subj.get('name')}) currently at {pct}%.",
                            role="student",
                            target_user_id=user.id,
                            source_domains=["ACADEMICS"],
                            evidence={
                                "signals": signals,
                                "details": {
                                    "subject_code": code,
                                    "subject_name": subj.get("name"),
                                    "attendance_pct": pct,
                                    "trend": trend,
                                },
                                "conclusion": f"Attendance is within the { 'Detention Warning (<65%)' if pct < 65.0 else 'Condonation Range (65-74.9%)' } threshold.",
                            },
                            recommended_action={
                                "label": "Review Attendance Logs",
                                "url": "/student/academics#attendance",
                                "action_type": "VIEW_ACADEMIC",
                                "description": f"Review recorded sessions and attend upcoming classes to satisfy 75% SEE eligibility.",
                            },
                            expires_at=now + timedelta(days=14),
                            notify=(severity == "HIGH"),
                        )
                        generated_insights.append(ins)
        except Exception as e:
            logger.error(f"Rule B evaluation error for user {user.id}: {e}")

        # ----------------------------------------------------------------------
        # RULE C & F & MULTI-DOMAIN (CROSS_DOMAIN, CAREER_OPPORTUNITY, PREVENTIVE_ACTION)
        # ----------------------------------------------------------------------
        try:
            recommendations = personalized_ranking_engine.get_recommendations(db, user)
            if recommendations:
                top_rec = recommendations[0]
                opp = top_rec["opportunity"]
                fit_score = int(top_rec["personalized_profile_fit"])
                eligibility = top_rec["eligibility"]
                days_left = top_rec.get("days_remaining", 10)
                is_closing = top_rec.get("is_closing_soon", False) or (days_left is not None and days_left <= 3)

                # Special Multi-Domain: High Fit + Eligible + Closing Soon
                if is_closing and eligibility.get("is_eligible", False) and fit_score >= 70:
                    signals = [
                        {
                            "domain": "CAREER",
                            "metric": f"{opp.title} Profile Fit",
                            "value": f"{fit_score}% Personalized Fit",
                            "source": "Personalized Recommendation Engine",
                        },
                        {
                            "domain": "CAREER",
                            "metric": "Eligibility Status",
                            "value": "ELIGIBLE",
                            "source": "Academic Eligibility Engine",
                        },
                        {
                            "domain": "CAREER",
                            "metric": "Application Deadline",
                            "value": f"{days_left} day(s) remaining",
                            "source": "Opportunity Intake System",
                        },
                    ]
                    for sk in top_rec.get("matched_skills", [])[:2]:
                        signals.append({
                            "domain": "CAREER",
                            "metric": f"Matched Skill: {sk}",
                            "value": "Verified",
                            "source": "Student Career Profile",
                        })

                    dedup_key = f"CROSS_DOMAIN|{user.id}|{opp.id}|closing_soon"
                    ins = self._upsert_insight(
                        db=db,
                        dedup_key=dedup_key,
                        insight_type="CROSS_DOMAIN",
                        severity="HIGH",
                        title=f"High-Fit Opportunity Closing Soon: {opp.title}",
                        summary=f"A high-fit verified opportunity ({opp.title} at {getattr(opp, 'organization', 'Partner Organization')}) matching your strengths is closing in {days_left} day(s).",
                        role="student",
                        target_user_id=user.id,
                        source_domains=["CAREER", "ACADEMICS"],
                        evidence={
                            "signals": signals,
                            "details": {
                                "opportunity_id": opp.id,
                                "opportunity_title": opp.title,
                                "company": getattr(opp, 'organization', 'Partner Organization'),
                                "fit_score": fit_score,
                                "days_remaining": days_left,
                                "why_recommended": top_rec.get("why_recommended"),
                            },
                            "conclusion": f"Your verified skills and academic record yield a {fit_score}% fit for this closing listing.",
                        },
                        recommended_action={
                            "label": "Review Opportunity",
                            "url": f"/student/career#opportunity-{opp.id}",
                            "action_type": "VIEW_OPPORTUNITY",
                            "description": "Inspect eligibility details, match score breakdown, and submit application before deadline.",
                        },
                        expires_at=now + timedelta(days=max(days_left, 1)),
                        notify=True,
                    )
                    generated_insights.append(ins)

                # Skill Gap / Preventive Action
                missing_skills = top_rec.get("missing_skills", [])
                if missing_skills and fit_score >= 60:
                    top_gap = missing_skills[0]
                    signals = [
                        {
                            "domain": "CAREER",
                            "metric": f"Target Opportunity Requirement: {top_gap}",
                            "value": f"Required by {opp.title}",
                            "source": "Opportunity Skill Requirements",
                        },
                        {
                            "domain": "CAREER",
                            "metric": "Student Profile Competency",
                            "value": "Missing in Verified Profile",
                            "source": "Verified Skills Registry",
                        },
                    ]
                    dedup_key = f"CAREER_SKILL_GAP|{user.id}|{top_gap.lower()}"
                    ins = self._upsert_insight(
                        db=db,
                        dedup_key=dedup_key,
                        insight_type="PREVENTIVE_ACTION",
                        severity="MEDIUM",
                        title=f"High-Demand Skill Recommendation: {top_gap}",
                        summary=f"Several high-alignment opportunities in your target field require {top_gap}, which is not currently present in your verified profile.",
                        role="student",
                        target_user_id=user.id,
                        source_domains=["CAREER"],
                        evidence={
                            "signals": signals,
                            "details": {
                                "missing_skill": top_gap,
                                "target_opportunity": opp.title,
                                "related_domain": top_rec.get("primary_domain"),
                            },
                            "conclusion": f"Adding practical competencies in {top_gap} can expand eligibility for high-fit roles.",
                        },
                        recommended_action={
                            "label": "View Skill Gap Diagnostics",
                            "url": "/student/career#skill-gaps",
                            "action_type": "VIEW_SKILL_GAPS",
                            "description": f"Explore learning resources and small project ideas for {top_gap}.",
                        },
                        expires_at=now + timedelta(days=21),
                    )
                    generated_insights.append(ins)
        except Exception as e:
            logger.error(f"Rule C/F evaluation error for user {user.id}: {e}")

        # Check for expired/resolved insights for student
        self._expire_stale_student_insights(db, user.id)

        # Return only active (NEW, SEEN) insights sorted by severity
        return self._get_active_insights_for_role(db, role="student", user_id=user.id)

    # --------------------------------------------------------------------------
    # 2. FACULTY INSIGHTS (Department Complaints & Authorized Academics)
    # --------------------------------------------------------------------------
    def evaluate_faculty_insights(self, db: Session, user: User) -> List[VignaiInsight]:
        """
        Evaluates faculty department-level patterns and academic trends within authorized scope.
        Never exposes private student resumes or protected complaint identities.
        """
        generated_insights: List[VignaiInsight] = []
        now = datetime.utcnow()
        dept_code = "CSE"
        if hasattr(user, "department") and getattr(user, "department", None):
            dept_code = user.department.code or "CSE"

        try:
            # Sync proactive alerts first
            self.alert_service.evaluate_and_sync_alerts(db)

            # Department complaint clusters
            dept_alerts = db.query(VignaiAlert).filter(
                VignaiAlert.department == dept_code,
                VignaiAlert.status.in_(["NEW", "ACKNOWLEDGED"])
            ).all()

            for alt in dept_alerts:
                signals = [
                    {
                        "domain": "COMPLAINTS",
                        "metric": f"{alt.department} Priority Alert",
                        "value": f"{alt.severity} Severity",
                        "source": "Proactive Priority Alert Engine",
                    },
                    {
                        "domain": "COMPLAINTS",
                        "metric": "Affected Location",
                        "value": alt.location or "Department Facilities",
                        "source": "Complaint Spatial Clustering",
                    },
                ]
                for s in alt.reason_data.get("signals", [])[:3]:
                    signals.append({
                        "domain": "CAMPUS_INTELLIGENCE",
                        "metric": "Clustering Signal",
                        "value": s,
                        "source": "Incident Aggregator",
                    })

                dedup_key = f"FACULTY_CAMPUS_PATTERN|{dept_code}|{alt.id}"
                ins = self._upsert_insight(
                    db=db,
                    dedup_key=dedup_key,
                    insight_type="CAMPUS_PATTERN",
                    severity=alt.severity,
                    title=f"Department Issue Cluster: {alt.title}",
                    summary=f"{alt.title} in {alt.location} requires review by {dept_code} departmental team.",
                    role="faculty",
                    target_department=dept_code,
                    source_domains=["COMPLAINTS", "CAMPUS_INTELLIGENCE"],
                    evidence={
                        "signals": signals,
                        "details": {
                            "alert_id": alt.id,
                            "case_group_id": alt.case_group_id,
                            "location": alt.location,
                            "department": dept_code,
                        },
                        "conclusion": f"Concentrated incident frequency observed in {alt.location}.",
                    },
                    recommended_action={
                        "label": "Investigate Cluster",
                        "url": f"/faculty/cases?alert={alt.id}",
                        "action_type": "VIEW_CASES",
                        "description": "Inspect anonymous incident logs and assign technical resolution team.",
                    },
                    expires_at=now + timedelta(days=7),
                    notify=(alt.severity in ["HIGH", "CRITICAL"]),
                )
                generated_insights.append(ins)
        except Exception as e:
            logger.error(f"Faculty insight evaluation error for user {user.id}: {e}")

        return self._get_active_insights_for_role(db, role="faculty", department=dept_code)

    # --------------------------------------------------------------------------
    # 3. MANAGEMENT INSIGHTS (Campus-Wide Patterns & What-If Recommendations)
    # --------------------------------------------------------------------------
    def evaluate_management_insights(self, db: Session, user: User) -> List[VignaiInsight]:
        """
        Evaluates campus-wide patterns, high-priority issues, and What-If recommendations.
        Strict privacy: No student PII exposed.
        """
        generated_insights: List[VignaiInsight] = []
        now = datetime.utcnow()

        try:
            # Sync proactive alerts
            self.alert_service.evaluate_and_sync_alerts(db)

            # Campus-wide alerts
            alerts = db.query(VignaiAlert).filter(
                VignaiAlert.status.in_(["NEW", "ACKNOWLEDGED"])
            ).order_by(VignaiAlert.created_at.desc()).all()

            for alt in alerts:
                is_urgent = alt.severity in ["HIGH", "CRITICAL"]
                signals = [
                    {
                        "domain": "CAMPUS_INTELLIGENCE",
                        "metric": f"{alt.location} Incident Cluster",
                        "value": f"{alt.severity} Severity",
                        "source": "Spatial Hotspot Detector",
                    },
                    {
                        "domain": "COMPLAINTS",
                        "metric": "Cluster Priority",
                        "value": alt.reason_data.get("priority", "HIGH"),
                        "source": "Incident Aggregation Queue",
                    },
                ]
                for s in alt.reason_data.get("signals", [])[:3]:
                    signals.append({
                        "domain": "CAMPUS_INTELLIGENCE",
                        "metric": "Operational Metric",
                        "value": s,
                        "source": "Telemetry Context",
                    })

                # Rule E: Complaint -> What-If Deep Link for High/Critical
                action_url = f"/management/what-if?location={alt.location or 'Campus'}" if is_urgent else "/management/campus-issues"
                action_label = "Run What-If Analysis" if is_urgent else "View Incident Cluster"

                dedup_key = f"MGMT_CAMPUS_PATTERN|{alt.id}"
                ins = self._upsert_insight(
                    db=db,
                    dedup_key=dedup_key,
                    insight_type="CAMPUS_PATTERN" if not is_urgent else "COMPLAINT_PATTERN",
                    severity=alt.severity,
                    title=f"Campus Pattern: {alt.title}",
                    summary=f"{alt.title} is showing concentrated incident density in {alt.location or 'campus facilities'}.",
                    role="management",
                    source_domains=["CAMPUS_INTELLIGENCE", "COMPLAINTS"],
                    evidence={
                        "signals": signals,
                        "details": {
                            "alert_id": alt.id,
                            "case_group_id": alt.case_group_id,
                            "location": alt.location,
                            "severity": alt.severity,
                            "recommended_simulation": f"Simulate impact if {alt.title} persists for 3 days",
                        },
                        "conclusion": f"Operational escalation threshold reached for {alt.location or 'campus'}.",
                    },
                    recommended_action={
                        "label": action_label,
                        "url": action_url,
                        "action_type": "RUN_WHAT_IF" if is_urgent else "VIEW_CASES",
                        "description": "Model escalation trajectory and evaluate preventive resource allocation.",
                    },
                    expires_at=now + timedelta(days=7),
                    notify=is_urgent,
                )
                generated_insights.append(ins)
        except Exception as e:
            logger.error(f"Management insight evaluation error: {e}")

        return self._get_active_insights_for_role(db, role="management")

    # --------------------------------------------------------------------------
    # 4. LIFECYCLE & STATE TRANSITIONS
    # --------------------------------------------------------------------------
    def mark_seen(self, db: Session, insight_id: int, user: User) -> VignaiInsight:
        """Transitions insight from NEW to SEEN."""
        ins = self._get_accessible_insight(db, insight_id, user)
        if ins.status == "NEW":
            ins.status = "SEEN"
            db.commit()
            db.refresh(ins)
        return ins

    def mark_actioned(self, db: Session, insight_id: int, user: User) -> VignaiInsight:
        """Transitions insight to ACTIONED."""
        ins = self._get_accessible_insight(db, insight_id, user)
        ins.status = "ACTIONED"
        db.commit()
        db.refresh(ins)
        return ins

    def mark_dismissed(self, db: Session, insight_id: int, user: User) -> VignaiInsight:
        """Transitions insight to DISMISSED."""
        ins = self._get_accessible_insight(db, insight_id, user)
        ins.status = "DISMISSED"
        db.commit()
        db.refresh(ins)
        return ins

    # --------------------------------------------------------------------------
    # 5. INTERNAL HELPERS & RESILIENCE
    # --------------------------------------------------------------------------
    def _upsert_insight(
        self,
        db: Session,
        dedup_key: str,
        insight_type: str,
        severity: str,
        title: str,
        summary: str,
        role: str,
        source_domains: List[str],
        evidence: Dict[str, Any],
        recommended_action: Dict[str, Any],
        target_user_id: Optional[int] = None,
        target_department: Optional[str] = None,
        expires_at: Optional[datetime] = None,
        notify: bool = False,
    ) -> VignaiInsight:
        """Creates or updates an insight without duplicating active entries."""
        existing = db.query(VignaiInsight).filter(
            VignaiInsight.deduplication_key == dedup_key
        ).first()

        if existing:
            # Update data while preserving dismissed status if still dismissed
            if existing.status != "DISMISSED":
                existing.severity = severity
                existing.title = title
                existing.summary = summary
                existing.evidence = evidence
                existing.recommended_action = recommended_action
                existing.expires_at = expires_at
                existing.updated_at = datetime.utcnow()
                db.commit()
                db.refresh(existing)
            return existing

        # Create new insight
        new_ins = VignaiInsight(
            insight_type=insight_type,
            severity=severity,
            title=title,
            summary=summary,
            role=role,
            target_user_id=target_user_id,
            target_department=target_department,
            status="NEW",
            source_domains=source_domains,
            evidence=evidence,
            recommended_action=recommended_action,
            deduplication_key=dedup_key,
            expires_at=expires_at,
        )
        db.add(new_ins)
        db.commit()
        db.refresh(new_ins)

        # High-value notification integration (deduplicated)
        if notify and severity in ["HIGH", "CRITICAL"]:
            self._dispatch_insight_notification(db, new_ins)

        return new_ins

    def _dispatch_insight_notification(self, db: Session, insight: VignaiInsight) -> None:
        """Creates a high-value notification for urgent insights without spamming."""
        try:
            target_user_ids: List[int] = []
            if insight.target_user_id:
                target_user_ids.append(insight.target_user_id)
            elif insight.role == "faculty" and insight.target_department:
                faculty_users = db.query(User).filter(
                    User.role == "faculty",
                    User.is_active == True,
                ).all()
                target_user_ids = [f.id for f in faculty_users if getattr(getattr(f, "department", None), "code", "CSE") == insight.target_department]
            elif insight.role in ["management", "admin"]:
                mgmt_users = db.query(User).filter(User.role.in_(["management", "admin"])).all()
                target_user_ids = [m.id for m in mgmt_users]

            rec_action = insight.recommended_action or {}
            raw_url = rec_action.get("url") or f"/{insight.role}"
            target_route = raw_url
            anchor = None
            query = None
            if "#" in target_route:
                target_route, anchor = target_route.split("#", 1)
            if "?" in target_route:
                target_route, query = target_route.split("?", 1)

            for u_id in target_user_ids:
                # Check for existing unread notification with identical title
                existing_notif = db.query(Notification).filter(
                    Notification.user_id == u_id,
                    Notification.title == insight.title,
                    Notification.is_read == False,
                ).first()
                if not existing_notif:
                    notif = Notification(
                        user_id=u_id,
                        title=insight.title,
                        message=insight.summary,
                        is_read=False,
                        notification_type="INSIGHT",
                        target_route=target_route,
                        target_entity_type="INSIGHT",
                        target_entity_id=str(insight.id),
                        target_anchor=anchor or f"insight-{insight.id}",
                        target_query=query,
                        source_insight_id=insight.id,
                    )
                    db.add(notif)
            db.commit()
        except Exception as e:
            logger.error(f"Error dispatching insight notification: {e}")

    def _expire_stale_student_insights(self, db: Session, user_id: int) -> None:
        """Marks insights EXPIRED when conditions no longer exist or expiration date passed."""
        now = datetime.utcnow()
        expired_q = db.query(VignaiInsight).filter(
            VignaiInsight.target_user_id == user_id,
            VignaiInsight.status.in_(["NEW", "SEEN"]),
            VignaiInsight.expires_at != None,
            VignaiInsight.expires_at < now,
        )
        expired_q.update({"status": "EXPIRED"})
        db.commit()

    def _get_active_insights_for_role(
        self,
        db: Session,
        role: str,
        user_id: Optional[int] = None,
        department: Optional[str] = None,
    ) -> List[VignaiInsight]:
        """Retrieves active (NEW, SEEN) insights with deterministic severity ranking."""
        query = db.query(VignaiInsight).filter(
            VignaiInsight.role == role,
            VignaiInsight.status.in_(["NEW", "SEEN"]),
        )
        if user_id:
            query = query.filter(VignaiInsight.target_user_id == user_id)
        if department:
            query = query.filter(VignaiInsight.target_department == department)

        insights = query.all()

        # Severity ranking order: CRITICAL > HIGH > MEDIUM > INFO
        severity_order = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "INFO": 3}
        insights.sort(key=lambda x: (severity_order.get(x.severity, 4), -(x.created_at.timestamp() if x.created_at else 0)))
        return insights

    def _get_accessible_insight(self, db: Session, insight_id: int, user: User) -> VignaiInsight:
        """Enforces strict RBAC on insight access."""
        ins = db.query(VignaiInsight).filter(VignaiInsight.id == insight_id).first()
        if not ins:
            from fastapi import HTTPException, status
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Insight not found.")

        # RBAC Check
        if user.role == "student" and ins.target_user_id != user.id:
            from fastapi import HTTPException, status
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied to this insight.")

        return ins


insight_engine = InsightEngine()
