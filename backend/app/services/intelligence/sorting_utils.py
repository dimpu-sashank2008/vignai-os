"""
Deterministic Priority Sorting and Tie-Breaking Utilities for VIGNEX.
Enforces the mandatory hierarchy:
CRITICAL > HIGH > MEDIUM > LOW
Tie-breakers:
1. Impact / case count (higher first)
2. Recurrence / active status (unresolved first)
3. Unresolved duration (older unresolved issues first)
4. Recent trend (Increasing > Stable > Resolving)
"""

from typing import Any
from datetime import datetime

PRIORITY_RANKS = {
    "CRITICAL": 4,
    "HIGH": 3,
    "MEDIUM": 2,
    "LOW": 1,
}

TREND_RANKS = {
    "INCREASING": 3,
    "RISING": 3,
    "STABLE": 2,
    "RESOLVING": 1,
}

STATUS_ACTIVE_WEIGHT = {
    "SUBMITTED": 4,
    "UNDER_REVIEW": 3,
    "IN_PROGRESS": 2,
    "RESOLVED": 1,
    "CLOSED": 0,
}

def get_priority_rank(priority: str | None) -> int:
    if not priority:
        return 2  # Default to MEDIUM
    return PRIORITY_RANKS.get(priority.strip().upper(), 2)

def get_trend_rank(trend: str | None) -> int:
    if not trend:
        return 2  # Default to STABLE
    return TREND_RANKS.get(trend.strip().upper(), 2)

def sort_complaints_by_priority(complaints: list[Any]) -> list[Any]:
    """Sort individual complaint records by priority (CRITICAL > HIGH > MEDIUM > LOW)
    with deterministic tie-breakers (active status weight, unresolved duration, recency).
    """
    def complaint_sort_key(c: Any):
        pri_rank = get_priority_rank(getattr(c, "priority", "MEDIUM"))
        status = getattr(c, "status", "SUBMITTED")
        stat_weight = STATUS_ACTIVE_WEIGHT.get(status.upper(), 1)
        created_at = getattr(c, "created_at", None)
        timestamp = created_at.timestamp() if isinstance(created_at, datetime) else 0.0
        
        # If unresolved, older complaints (smaller timestamp) have higher urgency
        # We invert timestamp for unresolved so older unresolved comes first
        if status.upper() not in ["RESOLVED", "CLOSED"]:
            unresolved_urgency = -timestamp
        else:
            unresolved_urgency = timestamp

        return (
            pri_rank,             # 1. Primary priority rank (descending)
            stat_weight,          # 2. Active status priority (descending)
            unresolved_urgency,   # 3. Unresolved duration (older unresolved first)
        )

    return sorted(complaints, key=complaint_sort_key, reverse=True)


def sort_groups_by_priority(groups: list[Any]) -> list[Any]:
    """Sort related case groups by group priority (CRITICAL > HIGH > MEDIUM > LOW)
    with tie-breakers: impact/case_count, active status, and trend.
    """
    def group_sort_key(g: Any):
        if isinstance(g, dict):
            pri = g.get("priority", "MEDIUM")
            count = g.get("case_count", 1)
            trend = g.get("trend", "STABLE")
            status = g.get("status", "SUBMITTED")
            created_at = g.get("created_at")
        else:
            pri = getattr(g, "priority", "MEDIUM")
            count = getattr(g, "case_count", 1)
            trend = getattr(g, "trend", "STABLE")
            status = getattr(g, "status", "SUBMITTED")
            created_at = getattr(g, "created_at", None)

        pri_rank = get_priority_rank(pri)
        trend_rank = get_trend_rank(trend)
        stat_weight = STATUS_ACTIVE_WEIGHT.get(status.upper(), 1)
        timestamp = created_at.timestamp() if isinstance(created_at, datetime) else 0.0

        return (
            pri_rank,      # 1. Group priority (CRITICAL > HIGH > MEDIUM > LOW)
            count,         # 2. Impact / case count (higher first)
            stat_weight,   # 3. Active queue status (unresolved first)
            trend_rank,    # 4. Trend (Increasing > Stable > Resolving)
            timestamp,     # 5. Recency
        )

    return sorted(groups, key=group_sort_key, reverse=True)
