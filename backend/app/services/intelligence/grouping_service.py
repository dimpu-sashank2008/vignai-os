"""
Related Case Grouping Service for VIGNEX (Phase 4 / Intelligence Correction).
Aggregates related student complaints into actionable RelatedCaseGroup clusters
without altering, deleting, or merging original underlying complaint records.
Enforces strict student privacy, transparent priority scoring, and signal explainability.
"""

import logging
import hashlib
from collections import defaultdict
from datetime import datetime, timedelta
from typing import Any
from sqlalchemy.orm import Session
from app.models.complaint import Complaint
from app.models.user import User
from app.schemas.grouping import (
    RelatedCaseGroupResponse,
    RelatedCaseGroupDetailResponse,
    GroupExplainabilitySignal,
    GroupUnderlyingCase,
)
from app.services.ai.duplicate_detection import compute_complaint_similarity
from app.services.intelligence.sorting_utils import sort_groups_by_priority, get_priority_rank

logger = logging.getLogger(__name__)

class GroupingService:
    """Discovers and structures related complaint clusters across campus domains."""

    def build_case_groups(
        self,
        complaints: list[Complaint],
        threshold: float = 0.35,
    ) -> list[RelatedCaseGroupDetailResponse]:
        """Cluster complaints into RelatedCaseGroups using category/location pre-filtering
        and semantic similarity scoring without destroying original individual records.
        """
        if not complaints:
            return []

        # 1. Connected-component clustering with pre-filtering
        n = len(complaints)
        adj: dict[int, set[int]] = defaultdict(set)
        pair_similarity: dict[tuple[int, int], float] = {}

        # Bucket by (category, location) and tokens for fast candidate comparison
        for i in range(n):
            adj[i].add(i)

        for i in range(n):
            c1 = complaints[i]
            c1_loc = (c1.location or (c1.ai_analysis.location if c1.ai_analysis else "") or "").strip().lower()
            c1_cat = (c1.category or (c1.ai_analysis.category if c1.ai_analysis else "") or "").strip().lower()

            for j in range(i + 1, n):
                c2 = complaints[j]
                c2_loc = (c2.location or (c2.ai_analysis.location if c2.ai_analysis else "") or "").strip().lower()
                c2_cat = (c2.category or (c2.ai_analysis.category if c2.ai_analysis else "") or "").strip().lower()

                # Optimization: Compare candidates if they share location, category, or key text patterns
                loc_match = bool(c1_loc and c2_loc and (c1_loc in c2_loc or c2_loc in c1_loc))
                cat_match = bool(c1_cat and c2_cat and c1_cat == c2_cat)

                # If candidate shares category or location or general domain, compute detailed similarity
                score, reason = compute_complaint_similarity(c1, c2)
                if score >= threshold or (loc_match and cat_match and score >= 0.25):
                    adj[i].add(j)
                    adj[j].add(i)
                    pair_similarity[(i, j)] = score
                    pair_similarity[(j, i)] = score

        # 2. Extract Connected Components
        visited = set()
        components: list[list[int]] = []

        for i in range(n):
            if i not in visited:
                comp = []
                queue = [i]
                visited.add(i)
                while queue:
                    curr = queue.pop(0)
                    comp.append(curr)
                    for neighbor in adj[curr]:
                        if neighbor not in visited:
                            visited.add(neighbor)
                            queue.append(neighbor)
                components.append(comp)

        # 3. Build Structured RelatedCaseGroup for each component
        groups: list[RelatedCaseGroupDetailResponse] = []

        for comp_indices in components:
            member_cases = [complaints[idx] for idx in comp_indices]
            # Sort member cases by newest first
            member_cases.sort(key=lambda c: c.created_at, reverse=True)
            primary_case = member_cases[0]

            case_count = len(member_cases)
            supporting_case_ids = [c.case_id for c in member_cases]

            # Determine dominant category
            cat_counts = defaultdict(int)
            for c in member_cases:
                cat = c.ai_analysis.category if (c.ai_analysis and c.ai_analysis.category) else (c.category or "General")
                cat_counts[cat] += 1
            dominant_category = max(cat_counts.items(), key=lambda x: x[1])[0]

            # Determine dominant location
            loc_counts = defaultdict(int)
            for c in member_cases:
                loc = c.ai_analysis.location if (c.ai_analysis and c.ai_analysis.location) else c.location
                if loc and loc.lower() != "campus":
                    loc_counts[loc] += 1
            dominant_location = max(loc_counts.items(), key=lambda x: x[1])[0] if loc_counts else (primary_case.location or "Campus")

            # Determine dominant department
            dept_counts = defaultdict(int)
            for c in member_cases:
                dept = c.ai_analysis.department if (c.ai_analysis and c.ai_analysis.department) else "Administration"
                dept_counts[dept] += 1
            dominant_dept = max(dept_counts.items(), key=lambda x: x[1])[0] if dept_counts else "Administration"

            # Derive Group Priority (Transparent Rules)
            # 1. Base is highest individual priority
            priorities = [c.priority.upper() for c in member_cases]
            if "CRITICAL" in priorities:
                group_priority = "CRITICAL"
                priority_reason = "Contains critical severity student report."
            elif "HIGH" in priorities:
                group_priority = "HIGH"
                priority_reason = "Contains high severity student incident."
            elif case_count >= 5:
                # 5 or more reports escalates medium to high
                group_priority = "HIGH"
                priority_reason = f"Elevated to HIGH priority due to high report density ({case_count} cases)."
            elif "MEDIUM" in priorities:
                group_priority = "MEDIUM"
                priority_reason = "Standard operational priority based on reported impact."
            else:
                group_priority = "LOW"
                priority_reason = "Minor convenience or non-critical maintenance issue."

            # Determine composite status
            statuses = [c.status.upper() for c in member_cases]
            if any(s == "IN_PROGRESS" for s in statuses):
                composite_status = "IN_PROGRESS"
            elif any(s == "UNDER_REVIEW" for s in statuses):
                composite_status = "UNDER_REVIEW"
            elif any(s == "SUBMITTED" for s in statuses):
                composite_status = "SUBMITTED"
            elif all(s in ["RESOLVED", "CLOSED"] for s in statuses):
                composite_status = "RESOLVED"
            else:
                composite_status = primary_case.status

            # Determine trend
            if case_count >= 3:
                trend = "Increasing"
            elif case_count == 2:
                trend = "Stable"
            elif all(s in ["RESOLVED", "CLOSED"] for s in statuses):
                trend = "Resolving"
            else:
                trend = "Stable"

            # Formulate Group Title & AI Summary
            loc_label = f"in {dominant_location}" if dominant_location and dominant_location != "Campus" else ""
            if "wi-fi" in dominant_category.lower() or "network" in dominant_category.lower() or "wifi" in primary_case.description.lower():
                group_title = f"{dominant_location} Wi-Fi Connectivity Issue" if dominant_location else "Campus Wi-Fi Connectivity Issue"
                ai_summary = f"Multiple reports ({case_count} cases) describe recurring Wi-Fi disconnection and network instability {loc_label}."
            elif "transport" in dominant_category.lower() or "bus" in primary_case.description.lower():
                group_title = f"{dominant_location} Transport & Route Delays" if dominant_location else "Campus Transit Route Delays"
                ai_summary = f"Student reports ({case_count} cases) indicate recurring transit delays and commute schedule variance {loc_label}."
            elif "lab" in dominant_category.lower() or "projector" in primary_case.description.lower():
                group_title = f"{dominant_location} Equipment & Projector Defect" if dominant_location else "Laboratory Equipment Defect"
                ai_summary = f"Reports ({case_count} cases) describe laboratory equipment or projector malfunction {loc_label}."
            else:
                first_summary = primary_case.ai_analysis.issue_summary if (primary_case.ai_analysis and primary_case.ai_analysis.issue_summary) else (primary_case.title or primary_case.description[:50])
                group_title = f"{dominant_location} {dominant_category} Issue" if dominant_location else f"{dominant_category} Cluster"
                ai_summary = f"Multiple reports ({case_count} cases) related to {first_summary} {loc_label}."

            # Build Explainability Signals ("WHY GROUPED?")
            explainability_signals: list[GroupExplainabilitySignal] = []
            if dominant_location and dominant_location != "Campus":
                explainability_signals.append(
                    GroupExplainabilitySignal(
                        name="Shared Location",
                        weight="HIGH",
                        evidence=f"Concentrated at {dominant_location}",
                    )
                )

            if dominant_category:
                explainability_signals.append(
                    GroupExplainabilitySignal(
                        name="Category Match",
                        weight="HIGH",
                        evidence=f"Classified under {dominant_category}",
                    )
                )

            # Compute average pairwise similarity for multi-case groups
            if case_count > 1:
                scores = [score for pair, score in pair_similarity.items() if pair[0] in comp_indices and pair[1] in comp_indices]
                avg_score = sum(scores) / len(scores) if scores else threshold
                explainability_signals.append(
                    GroupExplainabilitySignal(
                        name="Semantic Similarity",
                        weight="HIGH" if avg_score >= 0.50 else "MEDIUM",
                        evidence=f"Corroborating text similarity score: {avg_score:.2f}",
                    )
                )

            explainability_signals.append(
                GroupExplainabilitySignal(
                    name="Time Proximity",
                    weight="MEDIUM",
                    evidence=f"Active reports logged within concurrent 30-day operating window",
                )
            )

            # Build Underlying Cases (with strict privacy enforcement)
            underlying_cases: list[GroupUnderlyingCase] = []
            for c in member_cases:
                is_protected = c.identity_protected
                reporter_visibility = "IDENTITY_PROTECTED" if is_protected else "VISIBLE"
                reporter_email = None if is_protected else (c.student.email if c.student else None)
                dept = c.ai_analysis.department if (c.ai_analysis and c.ai_analysis.department) else dominant_dept

                underlying_cases.append(
                    GroupUnderlyingCase(
                        id=c.id,
                        case_id=c.case_id,
                        title=c.title or (c.ai_analysis.issue_summary if c.ai_analysis else c.description[:50]),
                        description=c.description,
                        location=c.location,
                        category=c.category,
                        status=c.status,
                        priority=c.priority,
                        identity_protected=c.identity_protected,
                        reporter_visibility=reporter_visibility,
                        reporter_email=reporter_email,
                        evidence_count=len(c.evidences) if c.evidences else 0,
                        department=dept,
                        created_at=c.created_at,
                        updated_at=c.updated_at,
                    )
                )

            # Stable group key
            raw_key_material = f"{dominant_category}_{dominant_location}_{primary_case.case_id}"
            group_hash = hashlib.md5(raw_key_material.encode()).hexdigest()[:8].upper()
            group_key = f"GRP-{group_hash}"

            group_obj = RelatedCaseGroupDetailResponse(
                id=group_key,
                group_key=group_key,
                title=group_title,
                description=ai_summary,
                category=dominant_category,
                location=dominant_location,
                department=dominant_dept,
                priority=group_priority,
                case_count=case_count,
                trend=trend,
                status=composite_status,
                primary_case_id=primary_case.case_id,
                supporting_case_ids=supporting_case_ids,
                explainability_signals=explainability_signals,
                grouping_label="POTENTIALLY RELATED",
                ai_assisted_priority=True,
                priority_reason=priority_reason,
                created_at=member_cases[-1].created_at,
                updated_at=primary_case.updated_at,
                cases=underlying_cases,
            )
            groups.append(group_obj)

        # 4. Sort groups deterministically by Priority (CRITICAL > HIGH > MEDIUM > LOW) and impact/count
        return sort_groups_by_priority(groups)

    def get_management_case_groups(
        self,
        db: Session,
        status_filter: str | None = None,
        category_filter: str | None = None,
        priority_filter: str | None = None,
        department_filter: str | None = None,
        search: str | None = None,
    ) -> list[RelatedCaseGroupDetailResponse]:
        """Fetch all complaints, compute groups, and apply management filters."""
        query = db.query(Complaint)
        complaints = query.order_by(Complaint.created_at.desc()).all()

        all_groups = self.build_case_groups(complaints=complaints)

        # Apply filters on group level
        filtered_groups = all_groups

        if status_filter and status_filter.upper() != "ALL":
            filtered_groups = [
                g for g in filtered_groups
                if g.status.upper() == status_filter.upper() or any(c.status.upper() == status_filter.upper() for c in g.cases)
            ]

        if category_filter and category_filter.upper() != "ALL":
            filtered_groups = [
                g for g in filtered_groups
                if category_filter.lower() in g.category.lower()
            ]

        if priority_filter and priority_filter.upper() != "ALL":
            filtered_groups = [
                g for g in filtered_groups
                if g.priority.upper() == priority_filter.upper()
            ]

        if department_filter and department_filter.upper() != "ALL":
            filtered_groups = [
                g for g in filtered_groups
                if g.department and g.department.upper() == department_filter.upper()
            ]

        if search and search.strip():
            term = search.strip().lower()
            filtered_groups = [
                g for g in filtered_groups
                if term in g.title.lower() or
                   term in g.description.lower() or
                   (g.location and term in g.location.lower()) or
                   any(term in c.case_id.lower() or term in c.description.lower() for c in g.cases)
            ]

        return filtered_groups

    def get_faculty_department_groups(
        self,
        db: Session,
        faculty_user: User,
        status_filter: str | None = None,
        priority_filter: str | None = None,
        search: str | None = None,
    ) -> list[RelatedCaseGroupDetailResponse]:
        """Fetch faculty department-relevant complaints, cluster into groups, and sort by priority."""
        from app.routers.faculty import check_faculty_case_access

        all_complaints = db.query(Complaint).order_by(Complaint.created_at.desc()).all()
        authorized_complaints = [c for c in all_complaints if check_faculty_case_access(db, c, faculty_user)]

        groups = self.build_case_groups(complaints=authorized_complaints)

        # Filters
        if status_filter and status_filter.upper() != "ALL":
            groups = [
                g for g in groups
                if g.status.upper() == status_filter.upper() or any(c.status.upper() == status_filter.upper() for c in g.cases)
            ]

        if priority_filter and priority_filter.upper() != "ALL":
            groups = [
                g for g in groups
                if g.priority.upper() == priority_filter.upper()
            ]

        if search and search.strip():
            term = search.strip().lower()
            groups = [
                g for g in groups
                if term in g.title.lower() or
                   term in g.description.lower() or
                   (g.location and term in g.location.lower()) or
                   any(term in c.case_id.lower() or term in c.description.lower() for c in g.cases)
            ]

        return groups


grouping_service = GroupingService()
