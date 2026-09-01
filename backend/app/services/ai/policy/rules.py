"""
VIGNEX AI Policy & Behavioral Governance System (Version 1.0)

Defines explicit behavioral constraints, sensitivity classifications,
configured campus departments, and routing policy constants.

CRITICAL PRINCIPLE:
The LLM is NOT the authorization system.
AI suggestions must always be validated by a deterministic backend Policy Engine.
"""

VIGNEX_AI_POLICY_VERSION = "1.0"

# Explicit Behavioral Guidelines
AI_BEHAVIORAL_RULES = [
    "1. Never determine whether an allegation is true or false.",
    "2. Never claim submitted evidence proves an allegation as absolute fact.",
    "3. Never invent missing information (use null/None when details are omitted).",
    "4. Clearly distinguish reported observations from analytical interpretations.",
    "5. Protect student identity according to complaint privacy settings.",
    "6. Never automatically route a complaint to its subject individual.",
    "7. Suggest routing recommendations, never authorize routing or access rights.",
    "8. Suggest priority recommendations, never make the final operational decision.",
    "9. Use null/unknown when information is unavailable.",
    "10. Never send passwords, auth tokens, or unnecessary personal student data to external models.",
    "11. Return strictly structured, schema-validated JSON only.",
    "12. All AI outputs remain reviewable and auditable by authorized human personnel.",
]

# Configured Standard Campus Departments
CONFIGURED_DEPARTMENTS = [
    "CSE",
    "ECE",
    "EEE",
    "Mechanical",
    "Civil",
    "IT",
    "Administration",
    "Student Affairs",
    "Hostel",
    "Transport",
    "Maintenance",
    "Security",
    "Academic Office",
    "Examinations",
]

# Standard Route Types
ROUTE_TYPES = [
    "DEPARTMENT_AND_MANAGEMENT",
    "MANAGEMENT_ONLY",
    "AUTHORIZED_GRIEVANCE",
    "CAMPUS_OPERATIONS",
    "OTHER",
]

# Sensitivity Classifications
SENSITIVITY_LEVELS = [
    "NORMAL",
    "SENSITIVE",
    "HIGH_SENSITIVITY",
]
