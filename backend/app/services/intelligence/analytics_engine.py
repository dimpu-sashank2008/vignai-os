"""
Deterministic Campus Analytics and Intelligence Scoring Engine (Phase 4A).
Computes transparent scores, domain health, trend distributions, and prioritized queues
from the centralized database without fabricating numbers or hallucinating events.
"""

import logging
from datetime import datetime, timedelta
from collections import defaultdict
from sqlalchemy.orm import Session
from app.models.complaint import Complaint
from app.models.emerging_pattern import EmergingPattern
from app.models.ai_analysis import ComplaintAIAnalysis
from app.models.routing_audit import RoutingAudit
from app.models.investigation_note import InvestigationNote
from app.schemas.intelligence import (
    CampusIntelligenceSummary,
    AIPriorityItem,
    DomainHealthItem,
    CampusTrendAnalytics,
    AIActivityEvent,
)
from app.services.intelligence.pattern_detection import pattern_detection_service

logger = logging.getLogger(__name__)

class AnalyticsEngine:
    """Calculates transparent campus operational intelligence from database records."""

    def get_summary(self, db: Session) -> CampusIntelligenceSummary:
        """Compute top-level KPI metrics and transparent Campus Intelligence Score."""
        complaints = db.query(Complaint).all()
        total_cases = len(complaints)

        # Refresh or fetch active patterns
        patterns = db.query(EmergingPattern).filter(EmergingPattern.status == "ACTIVE").all()
        if not patterns and total_cases > 0:
            patterns = pattern_detection_service.detect_and_save_patterns(db)

        patterns_count = len(patterns)

        open_cases = [c for c in complaints if c.status.upper() not in ["RESOLVED", "CLOSED"]]
        critical_cases = sum(1 for c in open_cases if c.priority.upper() == "CRITICAL")
        high_cases = sum(1 for c in open_cases if c.priority.upper() == "HIGH")
        high_impact_risks = critical_cases + high_cases

        # Recommended actions = distinct patterns + high impact unaddressed issues
        recommended_actions_count = patterns_count + high_impact_risks

        # Transparent Intelligence Score Calculation (Base 100)
        score = 100
        critical_deduction = critical_cases * 8
        high_deduction = high_cases * 4
        pattern_deduction = patterns_count * 5
        open_deduction = min(len(open_cases) * 1, 15)

        total_deductions = critical_deduction + high_deduction + pattern_deduction + open_deduction
        calculated_score = max(25, min(98, score - total_deductions))

        if calculated_score >= 85:
            score_status = "OPTIMAL"
        elif calculated_score >= 70:
            score_status = "GOOD"
        elif calculated_score >= 50:
            score_status = "MODERATE"
        else:
            score_status = "CRITICAL"

        score_breakdown = {
            "base_score": 100,
            "critical_risk_deduction": -critical_deduction,
            "high_priority_deduction": -high_deduction,
            "active_pattern_deduction": -pattern_deduction,
            "unresolved_load_deduction": -open_deduction,
            "final_score": calculated_score,
        }

        return CampusIntelligenceSummary(
            total_cases=total_cases,
            open_cases_count=len(open_cases),
            emerging_patterns_count=patterns_count,
            high_impact_risks=high_impact_risks,
            recommended_actions_count=recommended_actions_count,
            campus_intelligence_score=calculated_score,
            score_status=score_status,
            score_breakdown=score_breakdown,
            is_sufficient_data=total_cases >= 3,
        )

    def get_ai_priorities(self, db: Session, limit: int = 10) -> list[AIPriorityItem]:
        """Rank non-resolved cases using a transparent deterministic multi-signal formula."""
        open_cases = db.query(Complaint).filter(
            Complaint.status.notin_(["RESOLVED", "CLOSED"])
        ).order_by(Complaint.created_at.desc()).all()

        patterns = db.query(EmergingPattern).filter(EmergingPattern.status == "ACTIVE").all()
        pattern_case_ids = set()
        for p in patterns:
            if isinstance(p.evidence_case_ids, list):
                pattern_case_ids.update(p.evidence_case_ids)

        ranked_items: list[AIPriorityItem] = []

        for c in open_cases:
            score = 0
            factors = []

            # 1. Base Priority Signal
            pri = c.priority.upper()
            if pri == "CRITICAL":
                score += 40
                factors.append("Critical Priority (+40)")
            elif pri == "HIGH":
                score += 25
                factors.append("High Priority (+25)")
            elif pri == "MEDIUM":
                score += 12
                factors.append("Medium Priority (+12)")
            else:
                score += 5
                factors.append("Low Priority (+5)")

            # 2. Recurrence / Cluster Signal
            if c.case_id in pattern_case_ids:
                score += 20
                factors.append("Part of Active Cluster (+20)")

            # 3. Sensitivity Signal
            ai = c.ai_analysis
            if ai and ai.sensitivity == "HIGH_SENSITIVITY":
                score += 20
                factors.append("High Sensitivity Grievance (+20)")
            elif ai and ai.sensitivity == "SENSITIVE":
                score += 10
                factors.append("Sensitive Issue (+10)")

            # 4. Age / Unresolved Duration Signal
            age_days = (datetime.utcnow() - c.created_at).days
            if age_days >= 2:
                score += 8
                factors.append(f"Pending {age_days} days (+8)")

            dept = ai.department if (ai and ai.department) else "CSE"
            title = ai.issue_summary if (ai and ai.issue_summary) else (c.title or c.description[:50])

            ranked_items.append(
                AIPriorityItem(
                    case_id=c.case_id,
                    title=title,
                    category=c.category or (ai.category if ai else "General"),
                    location=c.location or (ai.location if ai else "Campus"),
                    department=dept,
                    ai_suggested_priority=ai.suggested_priority if (ai and ai.suggested_priority) else c.priority,
                    current_status=c.status,
                    calculated_score=score,
                    score_factors=factors,
                    created_at=c.created_at,
                )
            )

        ranked_items.sort(key=lambda x: x.calculated_score, reverse=True)
        return ranked_items[:limit]

    def get_domain_health(self, db: Session) -> list[DomainHealthItem]:
        """Compute operational health across standard campus functional domains."""
        complaints = db.query(Complaint).all()
        patterns = db.query(EmergingPattern).filter(EmergingPattern.status == "ACTIVE").all()

        domain_mapping = {
            "Academics": ["academic", "laboratory", "examinations", "cse", "ece", "eee", "mech", "civil", "it"],
            "Infrastructure": ["infrastructure", "classroom", "maintenance", "electrical", "cleanliness", "projector", "ac"],
            "Transport": ["transport", "bus", "shuttle", "parking", "transit", "gate"],
            "Hostel": ["hostel", "dorm", "mess", "canteen"],
            "Security": ["security", "guard", "gate", "safety", "conduct"],
            "Student Experience": ["wi-fi", "wifi", "network", "student affairs", "canteen", "library", "sports"],
            "Faculty Experience": ["faculty", "staff", "cabin", "workstation", "conduct", "grievance", "attendance"],
        }

        domain_results: list[DomainHealthItem] = []

        for domain, keywords in domain_mapping.items():
            domain_cases = []
            for c in complaints:
                cat = (c.category or "").lower()
                desc = c.description.lower()
                dept = (c.ai_analysis.department if c.ai_analysis and c.ai_analysis.department else "").lower()

                if any(kw in cat or kw in desc or kw in dept for kw in keywords):
                    domain_cases.append(c)

            open_cases = [c for c in domain_cases if c.status.upper() not in ["RESOLVED", "CLOSED"]]
            critical_count = sum(1 for c in open_cases if c.priority.upper() in ["CRITICAL", "HIGH"])

            # Find matching patterns for this domain
            matched_patterns = [
                p for p in patterns
                if any(kw in (p.primary_department or "").lower() or kw in p.title.lower() for kw in keywords)
            ]

            # Health classification
            if critical_count >= 2 or any(p.severity == "CRITICAL" for p in matched_patterns):
                health = "High Risk"
            elif critical_count >= 1 or len(open_cases) >= 3 or len(matched_patterns) >= 1:
                health = "Elevated"
            elif len(open_cases) >= 1:
                health = "Watch"
            else:
                health = "Healthy"

            # Primary issue summary
            if open_cases:
                primary_summary = open_cases[0].title or open_cases[0].description[:60]
            elif matched_patterns:
                primary_summary = matched_patterns[0].title
            else:
                primary_summary = "All systems functioning normally with zero open incidents."

            case_ids = [c.case_id for c in open_cases[:5]]

            domain_results.append(
                DomainHealthItem(
                    domain=domain,
                    health_status=health,
                    active_cases=len(open_cases),
                    critical_cases=critical_count,
                    patterns_count=len(matched_patterns),
                    trend="RISING" if critical_count > 0 else "STABLE",
                    primary_issue_summary=primary_summary,
                    supporting_case_ids=case_ids,
                )
            )

        return domain_results

    def get_trend_analytics(self, db: Session, time_range: str = "30d") -> CampusTrendAnalytics:
        """Aggregate statistical breakdowns by category, department, status, and volume over time."""
        complaints = db.query(Complaint).order_by(Complaint.created_at.asc()).all()

        total = len(complaints)
        resolved_count = sum(1 for c in complaints if c.status.upper() in ["RESOLVED", "CLOSED"])
        resolution_rate = round((resolved_count / total * 100), 1) if total > 0 else 0.0

        # Category Breakdown
        cat_counts = defaultdict(int)
        for c in complaints:
            cat = c.category or (c.ai_analysis.category if c.ai_analysis else "General")
            cat_counts[cat] += 1
        category_distribution = [{"category": k, "count": v} for k, v in cat_counts.items()]

        # Department Breakdown
        dept_counts = defaultdict(int)
        for c in complaints:
            dept = (c.ai_analysis.department if c.ai_analysis and c.ai_analysis.department else None) or "CSE"
            dept_counts[dept] += 1
        department_distribution = [{"department": k, "count": v} for k, v in dept_counts.items()]

        # Status Breakdown
        status_counts = defaultdict(int)
        for c in complaints:
            status_counts[c.status.upper()] += 1
        status_distribution = [{"status": k, "count": v} for k, v in status_counts.items()]

        # Priority Breakdown
        priority_counts = defaultdict(int)
        for c in complaints:
            priority_counts[c.priority.upper()] += 1
        priority_distribution = [{"priority": k, "count": v} for k, v in priority_counts.items()]

        # Volume Timeline (Grouped by date)
        timeline_counts = defaultdict(int)
        for c in complaints:
            date_str = c.created_at.strftime("%b %d")
            timeline_counts[date_str] += 1
        volume_timeline = [{"date": k, "volume": v} for k, v in timeline_counts.items()]

        return CampusTrendAnalytics(
            volume_timeline=volume_timeline,
            category_distribution=category_distribution,
            department_distribution=department_distribution,
            status_distribution=status_distribution,
            priority_distribution=priority_distribution,
            resolution_rate=resolution_rate,
            time_range=time_range,
        )

    def get_activity_stream(self, db: Session, limit: int = 12) -> list[AIActivityEvent]:
        """Aggregate chronological processing, routing, and pattern discovery events."""
        events: list[AIActivityEvent] = []

        # 1. AI Analysis events
        analyses = db.query(ComplaintAIAnalysis).order_by(ComplaintAIAnalysis.created_at.desc()).limit(limit).all()
        for a in analyses:
            events.append(
                AIActivityEvent(
                    id=f"act-ai-{a.id}",
                    event_type="ANALYSIS",
                    case_id=a.complaint.case_id if a.complaint else None,
                    title="Complaint Structured Intelligence Extracted",
                    description=f"AI extracted category '{a.category}', suggested priority '{a.suggested_priority}', and detected location '{a.location}'.",
                    timestamp=a.created_at,
                    tag="AI-assisted",
                )
            )

        # 2. Routing Audit events
        audits = db.query(RoutingAudit).order_by(RoutingAudit.created_at.desc()).limit(limit).all()
        for aud in audits:
            events.append(
                AIActivityEvent(
                    id=f"act-rt-{aud.id}",
                    event_type="ROUTING",
                    case_id=aud.complaint.case_id if aud.complaint else None,
                    title="Deterministic Routing Policy Evaluated",
                    description=f"Policy Result: {aud.policy_validation_result} → Authorized Route: {aud.final_route}.",
                    timestamp=aud.created_at,
                    tag="Policy Validated",
                )
            )

        # 3. Emerging Pattern discovery events
        patterns = db.query(EmergingPattern).order_by(EmergingPattern.created_at.desc()).limit(5).all()
        for p in patterns:
            events.append(
                AIActivityEvent(
                    id=f"act-pat-{p.id}",
                    event_type="PATTERN_DISCOVERY",
                    case_id=None,
                    title=f"Pattern Discovered: {p.title}",
                    description=f"Detected {p.pattern_type} involving {p.case_count} cases in {p.primary_location}.",
                    timestamp=p.created_at,
                    tag="Pattern Engine",
                )
            )

        # Sort all events chronologically
        events.sort(key=lambda x: x.timestamp, reverse=True)
        return events[:limit]


analytics_engine = AnalyticsEngine()
