"""
Centralized Category Taxonomy Configuration for VIGNEX (Phase 5).

Provides deterministic category and subcategory definitions, normalization helpers,
and validation logic across student reporting, AI classification, routing, and filtering.
"""

from typing import Dict, List

# Official 7 Top-Level Categories and their Subcategories
CATEGORY_TAXONOMY: Dict[str, List[str]] = {
    "ACADEMIC": [
        "Faculty Conduct",
        "Teaching Quality",
        "Attendance",
        "Assignment",
        "Examination",
        "Timetable",
        "Academic Administration",
    ],
    "INFRASTRUCTURE": [
        "Classroom",
        "Laboratory",
        "Projector",
        "Furniture",
        "Electrical",
        "Air Conditioning",
        "Maintenance",
    ],
    "TECHNOLOGY": [
        "Wi-Fi / Network",
        "ERP / Portal",
        "Computer System",
        "Software / Access",
    ],
    "CAMPUS_OPERATIONS": [
        "Transport",
        "Hostel",
        "Cleanliness",
        "Security",
        "Campus Maintenance",
    ],
    "STUDENT_SERVICES": [
        "Scholarships",
        "Certificates",
        "Administration",
        "Student Affairs",
    ],
    "SENSITIVE_GRIEVANCE": [
        "Faculty Conduct",
        "Serious Conduct Concern",
        "Retaliation Concern",
        "Other Sensitive Matter",
    ],
    "OTHER": [
        "General",
    ],
}

CATEGORY_DISPLAY_LABELS: Dict[str, str] = {
    "ACADEMIC": "Academic",
    "INFRASTRUCTURE": "Infrastructure",
    "TECHNOLOGY": "Technology",
    "CAMPUS_OPERATIONS": "Campus Operations",
    "STUDENT_SERVICES": "Student Services",
    "SENSITIVE_GRIEVANCE": "Sensitive Grievance",
    "OTHER": "Other",
}

SUBCATEGORY_TO_TOP_LEVEL: Dict[str, str] = {
    # Common abbreviations & colloquial aliases
    "wifi": "TECHNOLOGY",
    "wi-fi": "TECHNOLOGY",
    "network": "TECHNOLOGY",
    "internet": "TECHNOLOGY",
    "bus": "CAMPUS_OPERATIONS",
    "transit": "CAMPUS_OPERATIONS",
    "shuttle": "CAMPUS_OPERATIONS",
    "lab": "INFRASTRUCTURE",
    "ac": "INFRASTRUCTURE",
    "conduct": "SENSITIVE_GRIEVANCE",
    "harassment": "SENSITIVE_GRIEVANCE",
}

for top_cat, subcats in CATEGORY_TAXONOMY.items():
    for sub in subcats:
        SUBCATEGORY_TO_TOP_LEVEL[sub.lower()] = top_cat

def normalize_category_name(category_str: str | None) -> str:
    """Normalize input category string to official top-level category key."""
    if not category_str:
        return "OTHER"
    cat_upper = category_str.strip().upper().replace(" ", "_").replace("-", "_").replace("/", "_")
    if cat_upper in CATEGORY_TAXONOMY:
        return cat_upper
    
    cat_lower = category_str.strip().lower()
    for official_cat in CATEGORY_TAXONOMY.keys():
        if official_cat.lower() == cat_lower or official_cat.lower().replace("_", " ") == cat_lower:
            return official_cat
            
    if cat_lower in SUBCATEGORY_TO_TOP_LEVEL:
        return SUBCATEGORY_TO_TOP_LEVEL[cat_lower]
        
    return "OTHER"

def get_subcategories_for_category(category_key: str) -> List[str]:
    """Retrieve allowed subcategories for a given top-level category."""
    norm_key = normalize_category_name(category_key)
    return CATEGORY_TAXONOMY.get(norm_key, ["General"])

def is_valid_category(category_key: str) -> bool:
    """Check if category string is a valid official top-level category."""
    return normalize_category_name(category_key) in CATEGORY_TAXONOMY
