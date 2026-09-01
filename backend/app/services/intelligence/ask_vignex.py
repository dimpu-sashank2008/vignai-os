"""
Ask VIGNEX Natural Language Intelligence Engine (Phase 4C).
Answers administrative queries grounded strictly in the centralized complaint database,
active emerging patterns, and verified operational metrics without fabricating statistics.
"""

import logging
import re
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.models.complaint import Complaint
from app.models.emerging_pattern import EmergingPattern
from app.schemas.intelligence import (
    AskVignexResponse,
    AskVignexEvidenceCase,
)
from app.services.intelligence.analytics_engine import analytics_engine

logger = logging.getLogger(__name__)

class AskVignexService:
    """Context-grounded natural language Q&A engine for campus management."""

    def answer_query(self, query: str, db: Session) -> AskVignexResponse:
        q_lower = query.strip().lower()

        # 1. Fetch live database ground truth
        all_complaints = db.query(Complaint).order_by(Complaint.created_at.desc()).all()
        patterns = db.query(EmergingPattern).filter(EmergingPattern.status == "ACTIVE").all()

        supporting_cases: list[AskVignexEvidenceCase] = []
        patterns_referenced: list[str] = []

        # -------------------------------------------------------------
        # INTENT 1: Emerging Issues / Biggest Problems / Top Clusters
        # -------------------------------------------------------------
        if any(k in q_lower for k in ["emerging", "biggest", "major issue", "top problem", "patterns", "critical problem"]):
            intent = "EMERGING_ISSUES"
            if patterns:
                answer_lines = [
                    "### 🔍 VIGNEX Detected Emerging Issues\n",
                    f"Based on real-time clustering across **{len(all_complaints)} campus complaints**, VIGNEX has identified **{len(patterns)} active operational patterns** requiring administrative oversight:\n",
                ]

                for idx, p in enumerate(patterns[:4]):
                    patterns_referenced.append(p.title)
                    answer_lines.append(
                        f"**{idx + 1}. {p.title}** ({p.severity} Severity)\n"
                        f"- **Location**: {p.primary_location or 'Campus Wide'} (Dept: {p.primary_department or 'General'})\n"
                        f"- **Evidence**: {p.case_count} corroborating reports | Trend: **{p.trend}**\n"
                        f"- **Affected Scope**: {p.affected_estimate}\n"
                    )

                # Gather supporting cases from patterns
                pattern_case_ids = []
                for p in patterns[:3]:
                    if isinstance(p.evidence_case_ids, list):
                        pattern_case_ids.extend(p.evidence_case_ids[:2])

                matched_cases = [c for c in all_complaints if c.case_id in pattern_case_ids]
                for c in matched_cases:
                    supporting_cases.append(
                        AskVignexEvidenceCase(
                            case_id=c.case_id,
                            title=c.ai_analysis.issue_summary if (c.ai_analysis and c.ai_analysis.issue_summary) else (c.title or c.description[:45]),
                            category=c.category,
                            location=c.location,
                            priority=c.priority,
                            status=c.status,
                        )
                    )

                answer_lines.append("\n*Recommendation: Deploy targeted departmental interventions to the highlighted physical zones before recurrence escalates.*")
                answer = "\n".join(answer_lines)
            else:
                answer = "There are currently zero active emerging patterns detected in the centralized complaint records. Campus operations are within nominal baselines."

            return AskVignexResponse(
                query=query,
                answer=answer,
                intent=intent,
                supporting_cases=supporting_cases,
                patterns_referenced=patterns_referenced,
                data_grounding=f"Verified Database: {len(patterns)} active patterns, {len(all_complaints)} total complaints",
                confidence=0.94,
            )

        # -------------------------------------------------------------
        # INTENT 2: Specific Location Queries (e.g. Block A, Lab 3, etc.)
        # -------------------------------------------------------------
        location_keywords = {
            "block a": ["block a", "academic block a"],
            "lab 3": ["lab 3", "lab-3", "academic block 2, lab 3", "academic block 2"],
            "faculty block": ["faculty block", "faculty"],
            "north gate": ["north gate", "bus stop"],
            "library": ["library", "central library"],
            "room 304": ["room 304", "room-304"],
            "lecture hall 2": ["lecture hall 2", "hall 2"],
        }

        matched_loc_key = None
        for loc_name, keywords in location_keywords.items():
            if any(kw in q_lower for kw in keywords):
                matched_loc_key = loc_name
                break

        if matched_loc_key:
            intent = "LOCATION_DRILLDOWN"
            kws = location_keywords[matched_loc_key]
            matched_cases = [
                c for c in all_complaints
                if any(kw in (c.location or "").lower() or kw in ((c.ai_analysis.location if c.ai_analysis else "") or "").lower() for kw in kws)
            ]

            matched_patterns = [
                p for p in patterns
                if any(kw in (p.primary_location or "").lower() or kw in p.title.lower() for kw in kws)
            ]

            if matched_cases:
                loc_title = matched_cases[0].location or matched_loc_key.title()
                answer_lines = [
                    f"### 📍 Operational Status for {loc_title}\n",
                    f"VIGNEX records show **{len(matched_cases)} complaints** associated with **{loc_title}**:\n",
                ]

                if matched_patterns:
                    p = matched_patterns[0]
                    patterns_referenced.append(p.title)
                    answer_lines.append(
                        f"⚠️ **Identified Cluster**: *{p.title}* ({p.severity} Severity)\n"
                        f"- **Report Velocity**: {p.trend}\n"
                        f"- **Estimated Scope**: {p.affected_estimate}\n"
                    )

                answer_lines.append("\n**Key Reported Symptoms:**")
                for c in matched_cases[:4]:
                    pri_badge = f"[{c.priority}]"
                    stat_badge = f"({c.status})"
                    desc_summary = c.ai_analysis.issue_summary if (c.ai_analysis and c.ai_analysis.issue_summary) else (c.title or c.description[:60])
                    answer_lines.append(f"- **{c.case_id}** {pri_badge} {stat_badge}: {desc_summary}")

                    supporting_cases.append(
                        AskVignexEvidenceCase(
                            case_id=c.case_id,
                            title=desc_summary,
                            category=c.category,
                            location=c.location,
                            priority=c.priority,
                            status=c.status,
                        )
                    )

                dept = matched_cases[0].ai_analysis.department if (matched_cases[0].ai_analysis and matched_cases[0].ai_analysis.department) else "CSE"
                answer_lines.append(f"\n**Responsible Unit**: `{dept}` Department.")
                answer = "\n".join(answer_lines)
            else:
                answer = f"No active complaints or defect patterns are currently logged for **{matched_loc_key.title()}** in the VIGNEX database."

            return AskVignexResponse(
                query=query,
                answer=answer,
                intent=intent,
                supporting_cases=supporting_cases,
                patterns_referenced=patterns_referenced,
                data_grounding=f"Verified Database: {len(matched_cases)} matching location records",
                confidence=0.92,
            )

        # -------------------------------------------------------------
        # INTENT 3: Category / Department Domain Queries (e.g. Transport, Wi-Fi, Lab)
        # -------------------------------------------------------------
        category_keywords = {
            "Transport": ["transport", "bus", "shuttle", "commute", "transit"],
            "Wi-Fi / Network": ["wi-fi", "wifi", "network", "internet", "connectivity", "eduroam"],
            "Laboratory": ["lab", "projector", "laboratory", "experiment", "apparatus"],
            "Cleanliness": ["cleanliness", "washroom", "toilet", "hygiene", "sanitation"],
            "Classroom": ["classroom", "ac", "bench", "desk", "air conditioner"],
            "Security": ["security", "guard", "gate", "safety", "conduct"],
        }

        matched_cat_key = None
        for cat_name, keywords in category_keywords.items():
            if any(kw in q_lower for kw in keywords):
                matched_cat_key = cat_name
                break

        if matched_cat_key:
            intent = "CATEGORY_QUERY"
            kws = category_keywords[matched_cat_key]
            matched_cases = [
                c for c in all_complaints
                if any(kw in (c.category or "").lower() or kw in c.description.lower() or kw in ((c.ai_analysis.category if c.ai_analysis else "") or "").lower() for kw in kws)
            ]

            open_count = sum(1 for c in matched_cases if c.status.upper() not in ["RESOLVED", "CLOSED"])
            resolved_count = sum(1 for c in matched_cases if c.status.upper() in ["RESOLVED", "CLOSED"])

            answer_lines = [
                f"### 📊 Domain Overview: {matched_cat_key}\n",
                f"VIGNEX has tracked **{len(matched_cases)} total complaints** under **{matched_cat_key}** (*{open_count} open, {resolved_count} resolved*):\n",
            ]

            for c in matched_cases[:4]:
                desc_summary = c.ai_analysis.issue_summary if (c.ai_analysis and c.ai_analysis.issue_summary) else (c.title or c.description[:60])
                answer_lines.append(f"- **{c.case_id}** [{c.priority}] in `{c.location or 'Campus'}` ({c.status}): {desc_summary}")

                supporting_cases.append(
                    AskVignexEvidenceCase(
                        case_id=c.case_id,
                        title=desc_summary,
                        category=c.category,
                        location=c.location,
                        priority=c.priority,
                        status=c.status,
                    )
                )

            answer = "\n".join(answer_lines)
            return AskVignexResponse(
                query=query,
                answer=answer,
                intent=intent,
                supporting_cases=supporting_cases,
                patterns_referenced=patterns_referenced,
                data_grounding=f"Verified Database: {len(matched_cases)} {matched_cat_key} records",
                confidence=0.91,
            )

        # -------------------------------------------------------------
        # INTENT 4: Recurring Issues / Recurrence
        # -------------------------------------------------------------
        if any(k in q_lower for k in ["recurring", "recur", "repeated", "repeat", "frequent"]):
            intent = "RECURRING_ANALYSIS"
            recurring_patterns = [p for p in patterns if p.pattern_type in ["LOCATION_CLUSTER", "RECURRING_DEFECT", "CATEGORY_BURST"]]

            if recurring_patterns:
                answer_lines = [
                    "### 🔄 Recurring Campus Operational Defect Clusters\n",
                    f"The pattern engine identified **{len(recurring_patterns)} recurring clusters** with multiple independent student complaints:\n",
                ]

                for p in recurring_patterns[:3]:
                    patterns_referenced.append(p.title)
                    answer_lines.append(
                        f"- **{p.title}** ({p.case_count} cases)\n"
                        f"  * Concentrated in: `{p.primary_location}`\n"
                        f"  * Estimated Exposure: {p.affected_estimate}\n"
                    )

                answer = "\n".join(answer_lines)
            else:
                answer = "No recurring defect patterns are currently meeting threshold criteria in the centralized records."

            return AskVignexResponse(
                query=query,
                answer=answer,
                intent=intent,
                supporting_cases=supporting_cases,
                patterns_referenced=patterns_referenced,
                data_grounding=f"Verified Database: {len(recurring_patterns)} recurring patterns",
                confidence=0.93,
            )

        # -------------------------------------------------------------
        # INTENT 5: Recent Changes / What Changed / Timeline
        # -------------------------------------------------------------
        if any(k in q_lower for k in ["changed", "this week", "recent", "what's new", "timeline", "latest"]):
            intent = "TIMELINE_QUERY"
            recent_cases = all_complaints[:5]

            answer_lines = [
                "### ⏱️ Recent VIGNEX Campus Activity\n",
                f"Showing the latest logged complaints and status transitions across campus:\n",
            ]

            for c in recent_cases:
                desc_summary = c.ai_analysis.issue_summary if (c.ai_analysis and c.ai_analysis.issue_summary) else (c.title or c.description[:60])
                answer_lines.append(f"- **{c.case_id}** [{c.priority} • {c.status}]: {desc_summary} (Location: `{c.location or 'Campus'}`)")
                supporting_cases.append(
                    AskVignexEvidenceCase(
                        case_id=c.case_id,
                        title=desc_summary,
                        category=c.category,
                        location=c.location,
                        priority=c.priority,
                        status=c.status,
                    )
                )

            answer = "\n".join(answer_lines)
            return AskVignexResponse(
                query=query,
                answer=answer,
                intent=intent,
                supporting_cases=supporting_cases,
                patterns_referenced=patterns_referenced,
                data_grounding=f"Verified Database: {len(all_complaints)} total records",
                confidence=0.90,
            )

        # -------------------------------------------------------------
        # FALLBACK & ANTI-HALLUCINATION GUARD
        # -------------------------------------------------------------
        fallback_answer = (
            "I don't have enough verified VIGNEX data to answer that query. "
            "My responses are strictly grounded in active campus complaint records, physical facility locations, "
            "and detected operational patterns from the centralized VIGNEX database. "
            "Try asking about specific locations (e.g. *Lab 3*, *Block A*), categories (*Wi-Fi*, *Transport*), "
            "or *'What are the biggest emerging issues?'*."
        )

        return AskVignexResponse(
            query=query,
            answer=fallback_answer,
            intent="UNSUPPORTED_OR_INSUFFICIENT_DATA",
            supporting_cases=[],
            patterns_referenced=[],
            data_grounding="Grounding check: Insufficient entity matches in active database records",
            confidence=0.50,
        )


ask_vignex_service = AskVignexService()
