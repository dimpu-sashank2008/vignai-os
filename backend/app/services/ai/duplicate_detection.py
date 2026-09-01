"""
Semantic similarity and potential duplicate detection service for VIGNEX.
Analyzes complaints to detect related campus incidents without performing automatic merges.
"""

import re
from typing import Any
from app.models.complaint import Complaint

def _tokenize(text: str) -> set[str]:
    """Tokenize text into lowercase alphanumeric words, filtering common stop words."""
    stop_words = {
        "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", "with",
        "of", "is", "was", "are", "been", "has", "have", "our", "my", "we", "it",
        "this", "that", "since", "from", "by", "as", "be", "so", "very", "there"
    }
    words = re.findall(r'\b[a-zA-Z0-9_-]{2,}\b', text.lower())
    return {w for w in words if w not in stop_words}

def compute_complaint_similarity(c1: Complaint, c2: Complaint) -> tuple[float, str]:
    """Compute semantic similarity score between two complaints.
    Returns (score between 0.0 and 1.0, descriptive reason).
    """
    if c1.id == c2.id or c1.case_id == c2.case_id:
        return (1.0, "Identical case record")

    tokens1 = _tokenize(f"{c1.description} {c1.title or ''}")
    tokens2 = _tokenize(f"{c2.description} {c2.title or ''}")

    if not tokens1 or not tokens2:
        return (0.0, "Insufficient text content")

    # Jaccard overlap on keywords
    intersection = tokens1.intersection(tokens2)
    union = tokens1.union(tokens2)
    jaccard = len(intersection) / len(union) if union else 0.0

    # Category and Location Match bonuses
    category_match = (
        bool(c1.category and c2.category and c1.category.lower() == c2.category.lower())
    )
    location_match = False
    if c1.location and c2.location:
        loc1_tokens = _tokenize(c1.location)
        loc2_tokens = _tokenize(c2.location)
        if loc1_tokens and loc2_tokens and loc1_tokens.intersection(loc2_tokens):
            location_match = True

    # Weighted similarity score calculation
    score = jaccard * 0.6
    reasons = []

    if category_match:
        score += 0.2
        reasons.append(f"Matching category '{c1.category}'")
    if location_match:
        score += 0.2
        reasons.append(f"Nearby/same location ('{c1.location}')")
    if intersection:
        common_sample = list(intersection)[:3]
        reasons.append(f"Shared keywords ({', '.join(common_sample)})")

    score = min(1.0, round(score, 2))
    reason_str = "; ".join(reasons) if reasons else "Moderate text similarity"

    return (score, reason_str)


def find_related_complaints(
    target: Complaint,
    all_complaints: list[Complaint],
    threshold: float = 0.35,
    limit: int = 5,
) -> list[dict[str, Any]]:
    """Scan candidate complaints and return list of potentially related cases above threshold."""
    related = []
    for candidate in all_complaints:
        if candidate.id == target.id or candidate.case_id == target.case_id:
            continue

        score, reason = compute_complaint_similarity(target, candidate)
        if score >= threshold:
            related.append({
                "case_id": candidate.case_id,
                "title": candidate.title or candidate.description[:50],
                "category": candidate.category,
                "location": candidate.location,
                "status": candidate.status,
                "similarity_score": score,
                "reason": f"Potentially related: {reason}",
            })

    related.sort(key=lambda x: x["similarity_score"], reverse=True)
    return related[:limit]
