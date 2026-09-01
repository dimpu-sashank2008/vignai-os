"""
Explainability Service for VIGNEX Intelligence (Phase 4B).
Generates transparent, evidence-backed "Why this insight?" rationales,
including supporting case counts, signals, factual interpretations, and explicit limitations.
"""

import logging
from sqlalchemy.orm import Session
from app.models.complaint import Complaint
from app.models.emerging_pattern import EmergingPattern
from app.schemas.intelligence import (
    WhyInsightResponse,
    WhyInsightSignal,
)

logger = logging.getLogger(__name__)

class ExplainabilityService:
    """Provides transparent evidence breakdowns for AI patterns, priorities, and health ratings."""

    def explain_insight(
        self,
        db: Session,
        insight_type: str,
        insight_id: str,
    ) -> WhyInsightResponse:
        type_upper = insight_type.upper()

        if type_upper == "PATTERN":
            pattern = db.query(EmergingPattern).filter(EmergingPattern.id == int(insight_id)).first()
            if not pattern:
                raise ValueError(f"Pattern with ID {insight_id} not found.")

            # Query supporting evidence complaints
            case_ids = pattern.evidence_case_ids if isinstance(pattern.evidence_case_ids, list) else []
            supporting_cases = db.query(Complaint).filter(Complaint.case_id.in_(case_ids)).all()

            locations = list(set(
                c.location or (c.ai_analysis.location if c.ai_analysis else None)
                for c in supporting_cases
                if (c.location or (c.ai_analysis and c.ai_analysis.location))
            ))
            categories = list(set(
                c.category or (c.ai_analysis.category if c.ai_analysis else None)
                for c in supporting_cases
                if (c.category or (c.ai_analysis and c.ai_analysis.category))
            ))
            departments = list(set(
                c.ai_analysis.department for c in supporting_cases if (c.ai_analysis and c.ai_analysis.department)
            ))

            signals = [
                WhyInsightSignal(
                    name="Evidence Density",
                    weight="High",
                    evidence=f"{pattern.case_count} corroborating student complaints across {len(locations)} physical zones.",
                ),
                WhyInsightSignal(
                    name="Spatial Concentration",
                    weight="High",
                    evidence=f"Concentrated primarily in {pattern.primary_location or 'Campus Facilities'}.",
                ),
                WhyInsightSignal(
                    name="Trend Trajectory",
                    weight="Medium",
                    evidence=f"Report velocity currently evaluated as {pattern.trend}.",
                ),
                WhyInsightSignal(
                    name="Impact Scope",
                    weight="High",
                    evidence=f"Estimated campus exposure: {pattern.affected_estimate}.",
                ),
            ]

            interpretation = (
                f"These signals indicate a recurring operational bottleneck in {pattern.primary_location or 'campus zones'}. "
                f"Multiple independent student reports corroborating defect symptoms demonstrate that this is a persistent "
                f"systemic cluster rather than an isolated one-off issue."
            )

            limitations = (
                "Underlying physical hardware failure or infrastructure cause is inferred from student report clustering "
                "and has not yet been physically verified by departmental technicians on site."
            )

            return WhyInsightResponse(
                insight_id=str(pattern.id),
                insight_type="PATTERN",
                title=pattern.title,
                supporting_case_count=pattern.case_count,
                supporting_case_ids=case_ids,
                locations=locations,
                categories=categories,
                departments=departments or [pattern.primary_department or "Administration"],
                data_window="Past 30 days active queue",
                signals=signals,
                interpretation=interpretation,
                limitations=limitations,
            )

        elif type_upper == "PRIORITY_CASE":
            complaint = db.query(Complaint).filter(Complaint.case_id == insight_id).first()
            if not complaint:
                raise ValueError(f"Case {insight_id} not found.")

            ai = complaint.ai_analysis
            dept = ai.department if (ai and ai.department) else "CSE"
            loc = complaint.location or (ai.location if ai else "Campus")
            cat = complaint.category or (ai.category if ai else "General")

            signals = [
                WhyInsightSignal(
                    name="Reported Priority Weight",
                    weight="High",
                    evidence=f"Severity classified as {complaint.priority} (AI Suggested: {ai.suggested_priority if ai else complaint.priority}).",
                ),
                WhyInsightSignal(
                    name="Academic / Operational Impact",
                    weight="High" if complaint.priority in ["HIGH", "CRITICAL"] else "Medium",
                    evidence=ai.impact if (ai and ai.impact) else "Standard departmental operational impact.",
                ),
                WhyInsightSignal(
                    name="Sensitivity Assessment",
                    weight="Critical" if (ai and ai.sensitivity == "HIGH_SENSITIVITY") else "Normal",
                    evidence=f"Sensitivity tagged as {ai.sensitivity if ai else 'NORMAL'}.",
                ),
            ]

            interpretation = (
                f"Case {complaint.case_id} was prioritized because of high academic/operational impact in {loc} "
                f"under the responsibility of the {dept} department."
            )

            limitations = (
                "Priority is calculated from reported student symptoms and NLP classification. "
                "Final urgency must be confirmed by assigned faculty or department heads."
            )

            return WhyInsightResponse(
                insight_id=complaint.case_id,
                insight_type="PRIORITY_CASE",
                title=ai.issue_summary if (ai and ai.issue_summary) else (complaint.title or complaint.description[:50]),
                supporting_case_count=1,
                supporting_case_ids=[complaint.case_id],
                locations=[loc] if loc else [],
                categories=[cat] if cat else [],
                departments=[dept],
                data_window="Case creation to present",
                signals=signals,
                interpretation=interpretation,
                limitations=limitations,
            )

        elif type_upper == "DOMAIN_HEALTH":
            domain = insight_id
            domain_mapping = {
                "Academics": ["academic", "laboratory", "examinations", "cse", "ece", "eee", "mech", "civil", "it"],
                "Infrastructure": ["infrastructure", "classroom", "maintenance", "electrical", "cleanliness"],
                "Transport": ["transport", "bus", "shuttle", "parking"],
                "Hostel": ["hostel", "dorm", "mess"],
                "Student Experience": ["wi-fi", "wifi", "network", "student affairs", "canteen", "library"],
                "Security": ["security", "guard", "gate", "grievance"],
            }
            keywords = domain_mapping.get(domain, [domain.lower()])

            complaints = db.query(Complaint).all()
            matched_cases = [
                c for c in complaints
                if any(kw in (c.category or "").lower() or kw in c.description.lower() or kw in ((c.ai_analysis.department if c.ai_analysis else "") or "").lower() for kw in keywords)
            ]
            open_cases = [c for c in matched_cases if c.status.upper() not in ["RESOLVED", "CLOSED"]]
            case_ids = [c.case_id for c in open_cases[:8]]

            signals = [
                WhyInsightSignal(
                    name="Domain Incident Volume",
                    weight="High",
                    evidence=f"{len(open_cases)} active unaddressed cases currently in queue.",
                ),
                WhyInsightSignal(
                    name="Critical Risk Ratio",
                    weight="High",
                    evidence=f"{sum(1 for c in open_cases if c.priority.upper() in ['HIGH', 'CRITICAL'])} high or critical severity cases.",
                ),
            ]

            interpretation = (
                f"Domain health for {domain} reflects the ratio of unresolved incidents and active cluster density "
                f"within the {domain} functional responsibility area."
            )

            limitations = "Health scoring evaluates complaint volume and severity only, not maintenance budget or scheduled downtime."

            return WhyInsightResponse(
                insight_id=domain,
                insight_type="DOMAIN_HEALTH",
                title=f"{domain} Domain Operational Health",
                supporting_case_count=len(open_cases),
                supporting_case_ids=case_ids,
                locations=list(set(c.location for c in open_cases if c.location))[:5],
                categories=list(set(c.category for c in open_cases if c.category))[:5],
                departments=[domain],
                data_window="Current active operational window",
                signals=signals,
                interpretation=interpretation,
                limitations=limitations,
            )

        else:
            raise ValueError(f"Unsupported insight type: {insight_type}")


explainability_service = ExplainabilityService()
