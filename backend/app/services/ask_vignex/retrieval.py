"""
Deterministic Database Retrieval Layer for Ask VIGNEX (Phase 4C).
Queries only minimal, verified SQLite records matching the classified operational intent.
"""

import logging
from datetime import datetime, timedelta
from collections import defaultdict
from sqlalchemy.orm import Session
from app.models.complaint import Complaint
from app.models.emerging_pattern import EmergingPattern
from app.services.ask_vignex.schemas import (
    IntentClassificationResult,
    RetrievalContext,
)

logger = logging.getLogger(__name__)

class AskVignexRetrievalService:
    """Retrieves targeted database records and aggregations for verified context construction."""

    def retrieve_context(
        self,
        intent_res: IntentClassificationResult,
        db: Session,
        conversation_context: list[dict] | None = None,
    ) -> RetrievalContext:
        intent = intent_res.intent

        # Safety & Policy Short-circuits
        if intent == "PRIVACY_REFUSAL":
            return RetrievalContext(
                data_window="N/A",
                special_safety_flag="PRIVACY_ATTEMPT",
                is_sufficient_data=False,
            )

        if intent == "ALLEGATION_NEUTRALITY":
            return RetrievalContext(
                data_window="All active records",
                special_safety_flag="ALLEGATION_TRUTH_ATTEMPT",
                is_sufficient_data=True,
            )

        if intent == "UNSUPPORTED":
            return RetrievalContext(
                data_window="N/A",
                special_safety_flag="UNKNOWN_DATA",
                is_sufficient_data=False,
            )

        # -------------------------------------------------------------
        # 1. CONTEXTUAL FOLLOW-UP DRILLDOWN
        # -------------------------------------------------------------
        if intent == "CONTEXTUAL_FOLLOW_UP" and conversation_context:
            target_idx = intent_res.follow_up_target_index or 0
            last_turn = conversation_context[-1]
            last_cases = last_turn.get("supporting_case_ids", [])
            last_findings = last_turn.get("key_findings", [])

            # Target case or pattern from previous turn
            target_case_id = last_cases[target_idx] if target_idx < len(last_cases) else (last_cases[0] if last_cases else None)

            if target_case_id:
                target_complaint = db.query(Complaint).filter(Complaint.case_id == target_case_id).first()
                if target_complaint:
                    # Find related complaints at same location or category
                    related = db.query(Complaint).filter(
                        (Complaint.location == target_complaint.location) |
                        (Complaint.category == target_complaint.category)
                    ).limit(6).all()

                    supporting_cases_data = [
                        {
                            "case_id": c.case_id,
                            "title": c.ai_analysis.issue_summary if c.ai_analysis and c.ai_analysis.issue_summary else (c.title or c.description[:50]),
                            "category": c.category,
                            "location": c.location,
                            "priority": c.priority,
                            "status": c.status,
                        }
                        for c in related
                    ]

                    return RetrievalContext(
                        data_window="Last 30 days",
                        case_count=len(related),
                        open_cases_count=sum(1 for c in related if c.status.upper() not in ["RESOLVED", "CLOSED"]),
                        locations=[target_complaint.location or "Campus"],
                        categories=[target_complaint.category or "General"],
                        departments=[target_complaint.ai_analysis.department if target_complaint.ai_analysis and target_complaint.ai_analysis.department else "General"],
                        trend="RISING",
                        supporting_cases=supporting_cases_data,
                        supporting_case_ids=[c["case_id"] for c in supporting_cases_data],
                    )

        # -------------------------------------------------------------
        # 2. CAMPUS OVERVIEW / EMERGING ISSUES
        # -------------------------------------------------------------
        if intent == "CAMPUS_OVERVIEW":
            all_complaints = db.query(Complaint).all()
            patterns = db.query(EmergingPattern).filter(EmergingPattern.status == "ACTIVE").order_by(EmergingPattern.severity.desc()).all()

            pattern_data = [
                {
                    "id": p.id,
                    "title": p.title,
                    "description": p.description,
                    "severity": p.severity,
                    "case_count": p.case_count,
                    "trend": p.trend,
                    "affected_estimate": p.affected_estimate,
                    "location": p.primary_location,
                    "department": p.primary_department,
                    "evidence_case_ids": p.evidence_case_ids if isinstance(p.evidence_case_ids, list) else [],
                }
                for p in patterns[:4]
            ]

            evidence_ids = []
            for p in patterns[:3]:
                if isinstance(p.evidence_case_ids, list):
                    evidence_ids.extend(p.evidence_case_ids[:2])

            evidence_complaints = db.query(Complaint).filter(Complaint.case_id.in_(evidence_ids)).all()
            supporting_cases_data = [
                {
                    "case_id": c.case_id,
                    "title": c.ai_analysis.issue_summary if c.ai_analysis and c.ai_analysis.issue_summary else (c.title or c.description[:50]),
                    "category": c.category,
                    "location": c.location,
                    "priority": c.priority,
                    "status": c.status,
                }
                for c in evidence_complaints
            ]

            open_count = sum(1 for c in all_complaints if c.status.upper() not in ["RESOLVED", "CLOSED"])

            return RetrievalContext(
                data_window="Last 30 days",
                case_count=len(all_complaints),
                open_cases_count=open_count,
                resolved_cases_count=len(all_complaints) - open_count,
                locations=list(set(c.location for c in all_complaints if c.location))[:5],
                categories=list(set(c.category for c in all_complaints if c.category))[:5],
                trend="RISING" if len(patterns) > 2 else "STABLE",
                patterns=pattern_data,
                supporting_cases=supporting_cases_data,
                supporting_case_ids=[c["case_id"] for c in supporting_cases_data],
            )

        # -------------------------------------------------------------
        # 3. DEPARTMENT ANALYSIS (e.g. "Which department has the most unresolved cases?")
        # -------------------------------------------------------------
        if intent == "DEPARTMENT_ANALYSIS":
            open_complaints = db.query(Complaint).filter(Complaint.status.notin_(["RESOLVED", "CLOSED"])).all()

            dept_counts = defaultdict(int)
            dept_cases = defaultdict(list)

            for c in open_complaints:
                dept = (c.ai_analysis.department if c.ai_analysis and c.ai_analysis.department else "General").strip()
                dept_counts[dept] += 1
                dept_cases[dept].append(c)

            # Sort by unresolved count
            sorted_depts = sorted(dept_counts.items(), key=lambda x: x[1], reverse=True)
            top_dept_name = sorted_depts[0][0] if sorted_depts else "General"
            top_dept_cases = dept_cases[top_dept_name][:5]

            supporting_cases_data = [
                {
                    "case_id": c.case_id,
                    "title": c.ai_analysis.issue_summary if c.ai_analysis and c.ai_analysis.issue_summary else (c.title or c.description[:50]),
                    "category": c.category,
                    "location": c.location,
                    "priority": c.priority,
                    "status": c.status,
                }
                for c in top_dept_cases
            ]

            return RetrievalContext(
                data_window="All active records",
                case_count=len(open_complaints),
                open_cases_count=len(open_complaints),
                departments=[d for d, _ in sorted_depts],
                department_aggregates=dict(sorted_depts),
                trend="RISING",
                supporting_cases=supporting_cases_data,
                supporting_case_ids=[c["case_id"] for c in supporting_cases_data],
            )

        # -------------------------------------------------------------
        # 4. LOCATION ANALYSIS (e.g. "Why is Block A becoming a risk?")
        # -------------------------------------------------------------
        if intent == "LOCATION_ANALYSIS" and intent_res.location:
            loc_str = intent_res.location
            loc_complaints = db.query(Complaint).filter(
                Complaint.location.ilike(f"%{loc_str}%")
            ).order_by(Complaint.created_at.desc()).all()

            matched_patterns = db.query(EmergingPattern).filter(
                (EmergingPattern.primary_location.ilike(f"%{loc_str}%")) |
                (EmergingPattern.title.ilike(f"%{loc_str}%"))
            ).all()

            pattern_data = [
                {
                    "id": p.id,
                    "title": p.title,
                    "description": p.description,
                    "severity": p.severity,
                    "case_count": p.case_count,
                    "trend": p.trend,
                    "affected_estimate": p.affected_estimate,
                }
                for p in matched_patterns
            ]

            supporting_cases_data = [
                {
                    "case_id": c.case_id,
                    "title": c.ai_analysis.issue_summary if c.ai_analysis and c.ai_analysis.issue_summary else (c.title or c.description[:50]),
                    "category": c.category,
                    "location": c.location,
                    "priority": c.priority,
                    "status": c.status,
                }
                for c in loc_complaints[:5]
            ]

            open_count = sum(1 for c in loc_complaints if c.status.upper() not in ["RESOLVED", "CLOSED"])

            return RetrievalContext(
                data_window="Last 30 days",
                case_count=len(loc_complaints),
                open_cases_count=open_count,
                resolved_cases_count=len(loc_complaints) - open_count,
                locations=[loc_str],
                categories=list(set(c.category for c in loc_complaints if c.category)),
                departments=list(set(c.ai_analysis.department for c in loc_complaints if c.ai_analysis and c.ai_analysis.department)),
                trend="RISING" if open_count > 2 else "STABLE",
                patterns=pattern_data,
                supporting_cases=supporting_cases_data,
                supporting_case_ids=[c["case_id"] for c in supporting_cases_data],
            )

        # -------------------------------------------------------------
        # 5. CATEGORY ANALYSIS (e.g. "Show transport-related cases")
        # -------------------------------------------------------------
        if intent == "CATEGORY_ANALYSIS":
            cat_str = intent_res.category or "Transport"
            cat_complaints = db.query(Complaint).filter(
                (Complaint.category.ilike(f"%{cat_str}%")) |
                (Complaint.description.ilike(f"%{cat_str}%"))
            ).order_by(Complaint.created_at.desc()).all()

            open_count = sum(1 for c in cat_complaints if c.status.upper() not in ["RESOLVED", "CLOSED"])

            supporting_cases_data = [
                {
                    "case_id": c.case_id,
                    "title": c.ai_analysis.issue_summary if c.ai_analysis and c.ai_analysis.issue_summary else (c.title or c.description[:50]),
                    "category": c.category,
                    "location": c.location,
                    "priority": c.priority,
                    "status": c.status,
                }
                for c in cat_complaints[:5]
            ]

            return RetrievalContext(
                data_window="Last 30 days",
                case_count=len(cat_complaints),
                open_cases_count=open_count,
                resolved_cases_count=len(cat_complaints) - open_count,
                categories=[cat_str],
                locations=list(set(c.location for c in cat_complaints if c.location)),
                departments=list(set(c.ai_analysis.department for c in cat_complaints if c.ai_analysis and c.ai_analysis.department)),
                trend="RISING" if open_count > 1 else "STABLE",
                supporting_cases=supporting_cases_data,
                supporting_case_ids=[c["case_id"] for c in supporting_cases_data],
            )

        # -------------------------------------------------------------
        # 6. RECURRING ANALYSIS & TIME COMPARISON
        # -------------------------------------------------------------
        all_cases = db.query(Complaint).order_by(Complaint.created_at.desc()).limit(8).all()
        supporting_cases_data = [
            {
                "case_id": c.case_id,
                "title": c.ai_analysis.issue_summary if c.ai_analysis and c.ai_analysis.issue_summary else (c.title or c.description[:50]),
                "category": c.category,
                "location": c.location,
                "priority": c.priority,
                "status": c.status,
            }
            for c in all_cases
        ]

        patterns = db.query(EmergingPattern).filter(EmergingPattern.status == "ACTIVE").all()
        pattern_data = [
            {
                "id": p.id,
                "title": p.title,
                "description": p.description,
                "severity": p.severity,
                "case_count": p.case_count,
                "trend": p.trend,
            }
            for p in patterns[:3]
        ]

        return RetrievalContext(
            data_window="Last 7 days" if intent_res.time_window == "7d" else "Last 30 days",
            case_count=len(all_cases),
            open_cases_count=sum(1 for c in all_cases if c.status.upper() not in ["RESOLVED", "CLOSED"]),
            trend="RISING",
            patterns=pattern_data,
            supporting_cases=supporting_cases_data,
            supporting_case_ids=[c["case_id"] for c in supporting_cases_data],
        )


retrieval_service = AskVignexRetrievalService()
