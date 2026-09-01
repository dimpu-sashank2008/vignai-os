"""
AI Provider abstraction layer for VIGNEX Complaint Intelligence (Phase 3).
Provides unified interface across Google Gemini and Local Heuristic analyzers.
"""

import json
import logging
import re
from abc import ABC, abstractmethod
from typing import Any

from app.config import settings
from app.config.categories import CATEGORY_TAXONOMY, normalize_category_name
from app.schemas.ai_analysis import ComplaintAIAnalysisSchema
from app.services.ai.policy.rules import (
    CONFIGURED_DEPARTMENTS,
    ROUTE_TYPES,
    SENSITIVITY_LEVELS,
)
from app.services.ai.prompts.complaint_analysis import (
    COMPLAINT_ANALYSIS_SYSTEM_PROMPT,
    build_complaint_analysis_prompt,
)

logger = logging.getLogger(__name__)

# Official top-level categories from centralized taxonomy config
VALID_CATEGORIES = list(CATEGORY_TAXONOMY.keys())


class AIProvider(ABC):
    """Abstract interface for AI complaint understanding providers."""

    @abstractmethod
    async def analyze_complaint(
        self,
        description: str,
        location: str | None = None,
        category: str | None = None,
    ) -> ComplaintAIAnalysisSchema:
        """Analyze natural language complaint and return structured intelligence."""
        ...

    @abstractmethod
    def get_provider_name(self) -> str:
        """Return provider identifier."""
        ...

    @abstractmethod
    def get_model_name(self) -> str:
        """Return model identifier."""
        ...


class LocalHeuristicProvider(AIProvider):
    """Deterministic, resilient local rule-based classifier and extractor.
    Serves as safe offline fallback and benchmark engine adhering strictly to VIGNEX AI Policy.
    """

    def get_provider_name(self) -> str:
        return "local-heuristic"

    def get_model_name(self) -> str:
        return "vignex-nlp-rules-v2"

    async def analyze_complaint(
        self,
        description: str,
        location: str | None = None,
        category: str | None = None,
    ) -> ComplaintAIAnalysisSchema:
        desc_lower = description.lower()

        # Check for High-Sensitivity Conduct / Grievance First
        is_conduct_allegation = any(
            k in desc_lower
            for k in [
                "conduct",
                "inappropriate",
                "harass",
                "misconduct",
                "assault",
                "bribe",
                "abuse",
                "faculty conduct",
            ]
        )

        # 1. Categorization — output official top-level taxonomy keys
        detected_category = normalize_category_name(category) if category else None
        if is_conduct_allegation:
            detected_category = "SENSITIVE_GRIEVANCE"
        elif not detected_category or detected_category not in VALID_CATEGORIES:
            if any(k in desc_lower for k in ["lab", "projector", "microscope", "experiment", "apparatus", "chemicals"]):
                detected_category = "INFRASTRUCTURE"
            elif any(k in desc_lower for k in ["wi-fi", "wifi", "eduroam", "internet", "disconnect", "network", "signal", "dns"]):
                detected_category = "TECHNOLOGY"
            elif any(k in desc_lower for k in ["washroom", "toilet", "clean", "smell", "odor", "dirty", "trash", "garbage", "hygiene"]):
                detected_category = "CAMPUS_OPERATIONS"
            elif any(k in desc_lower for k in ["fan", "light", "power", "socket", "switchboard", "wiring", "electricity", "blackout"]):
                detected_category = "INFRASTRUCTURE"
            elif any(k in desc_lower for k in ["bench", "whiteboard", "blackboard", "podium", "desk", "chair", "ac", "air condition"]):
                detected_category = "INFRASTRUCTURE"
            elif any(k in desc_lower for k in ["bus", "shuttle", "parking", "transit"]):
                detected_category = "CAMPUS_OPERATIONS"
            elif any(k in desc_lower for k in ["hostel", "dorm", "mess", "warden", "hot water"]):
                detected_category = "CAMPUS_OPERATIONS"
            elif any(k in desc_lower for k in ["pipe", "water", "plumbing", "road", "wall", "ceiling", "lift", "elevator"]):
                detected_category = "INFRASTRUCTURE"
            elif any(k in desc_lower for k in ["exam", "marks", "grade", "professor", "course", "schedule", "syllabus", "timetable"]):
                detected_category = "ACADEMIC"
            elif any(k in desc_lower for k in ["guard", "gate", "theft", "lost", "security", "id card"]):
                detected_category = "CAMPUS_OPERATIONS"
            elif any(k in desc_lower for k in ["scholarship", "certificate", "admission", "fee", "student affair"]):
                detected_category = "STUDENT_SERVICES"
            else:
                detected_category = "OTHER"

        # 2. Subcategory & Issue Summary — use official taxonomy subcategories
        subcategory = "General"
        issue_summary = description[:50].strip()

        if is_conduct_allegation:
            subcategory = "Faculty Conduct"
            issue_summary = "Faculty conduct report"
        elif detected_category == "INFRASTRUCTURE":
            if any(k in desc_lower for k in ["projector"]):
                subcategory = "Projector"
                issue_summary = "Projector malfunction"
            elif any(k in desc_lower for k in ["lab", "microscope", "experiment", "apparatus", "chemicals"]):
                subcategory = "Laboratory"
                issue_summary = "Laboratory equipment defect"
            elif any(k in desc_lower for k in ["bench", "whiteboard", "blackboard", "podium", "desk", "chair"]):
                subcategory = "Furniture"
                issue_summary = "Classroom furniture issue"
            elif any(k in desc_lower for k in ["ac", "air condition"]):
                subcategory = "Air Conditioning"
                issue_summary = "Air conditioning malfunction"
            elif any(k in desc_lower for k in ["fan", "light", "power", "socket", "switchboard", "wiring", "electricity", "blackout"]):
                subcategory = "Electrical"
                issue_summary = "Electrical fixture failure"
            elif any(k in desc_lower for k in ["pipe", "water", "plumbing", "road", "wall", "ceiling", "lift", "elevator"]):
                subcategory = "Maintenance"
                issue_summary = "Infrastructure maintenance required"
            else:
                subcategory = "Classroom"
                issue_summary = "Classroom amenity maintenance"
        elif detected_category == "TECHNOLOGY":
            if any(k in desc_lower for k in ["erp", "portal"]):
                subcategory = "ERP / Portal"
                issue_summary = "ERP/Portal access issue"
            elif any(k in desc_lower for k in ["computer", "pc", "system"]):
                subcategory = "Computer System"
                issue_summary = "Computer system issue"
            elif any(k in desc_lower for k in ["software", "access", "license"]):
                subcategory = "Software / Access"
                issue_summary = "Software access issue"
            else:
                subcategory = "Wi-Fi / Network"
                issue_summary = "Intermittent Wi-Fi disconnection" if "disconnect" in desc_lower else "Network connectivity degradation"
        elif detected_category == "CAMPUS_OPERATIONS":
            if any(k in desc_lower for k in ["bus", "shuttle", "parking", "transit", "transport"]):
                subcategory = "Transport"
                issue_summary = "Campus bus schedule delay"
            elif any(k in desc_lower for k in ["hostel", "dorm", "mess", "warden", "hot water"]):
                subcategory = "Hostel"
                issue_summary = "Hostel utility maintenance"
            elif any(k in desc_lower for k in ["washroom", "toilet", "clean", "smell", "odor", "dirty", "trash", "garbage", "hygiene"]):
                subcategory = "Cleanliness"
                issue_summary = "Washroom hygiene & odor concern" if "washroom" in desc_lower or "toilet" in desc_lower else "Sanitation & cleaning required"
            elif any(k in desc_lower for k in ["guard", "gate", "theft", "lost", "security", "id card"]):
                subcategory = "Security"
                issue_summary = "Campus security concern"
            else:
                subcategory = "Campus Maintenance"
                issue_summary = "Campus operations issue"
        elif detected_category == "ACADEMIC":
            if "timetable" in desc_lower or "schedule" in desc_lower:
                subcategory = "Timetable"
                issue_summary = "Timetable scheduling conflict"
            elif "exam" in desc_lower:
                subcategory = "Examination"
                issue_summary = "Examination schedule conflict"
            elif "attendance" in desc_lower:
                subcategory = "Attendance"
                issue_summary = "Attendance dispute"
            elif "assignment" in desc_lower:
                subcategory = "Assignment"
                issue_summary = "Assignment concern"
            elif any(k in desc_lower for k in ["teaching", "lecture", "class quality"]):
                subcategory = "Teaching Quality"
                issue_summary = "Teaching quality concern"
            else:
                subcategory = "Academic Administration"
                issue_summary = "Academic consultation request"
        elif detected_category == "STUDENT_SERVICES":
            if "scholarship" in desc_lower:
                subcategory = "Scholarships"
                issue_summary = "Scholarship inquiry"
            elif "certificate" in desc_lower:
                subcategory = "Certificates"
                issue_summary = "Certificate request"
            else:
                subcategory = "Administration"
                issue_summary = "Student services request"

        # 3. Location Extraction
        extracted_location = location
        if not extracted_location:
            loc_match = re.search(r'\b(lab\s*\d+|block\s*[a-z0-9]+|room\s*\d+|library|cafeteria|auditorium|hostel\s*[a-z0-9]*|bus\s*stop|faculty\s*block)\b', desc_lower, re.IGNORECASE)
            if loc_match:
                extracted_location = loc_match.group(0).title()

        # 4. Duration Extraction
        duration = None
        dur_match = re.search(r'\b(since\s+[a-z]+|for\s+\d+\s+(?:days?|hours?|weeks?)|past\s+\d+\s+(?:days?|hours?)|yesterday|today|recurring)\b', desc_lower, re.IGNORECASE)
        if dur_match:
            duration = dur_match.group(0).capitalize()

        # 5. Impact & Priority
        impact = None
        suggested_priority = "MEDIUM"
        priority_reason = "Standard campus operational issue requiring routine resolution."

        if is_conduct_allegation or any(k in desc_lower for k in ["danger", "hazard", "fire", "injury", "emergency", "shock", "flood", "harass"]):
            suggested_priority = "HIGH" if is_conduct_allegation else "CRITICAL"
            impact = "Institutional conduct standard or student safety concern"
            priority_reason = "Confidential report involving sensitive institutional conduct standards requiring authorized review."
        elif any(k in desc_lower for k in ["missed", "canceled", "cancelled", "exam", "classes", "urgent", "dead", "blocked", "conflict", "burst"]):
            suggested_priority = "HIGH"
            impact = "Academic sessions or core practical classes affected"
            priority_reason = "Interruption to scheduled academic activities or critical infrastructure."
        elif any(k in desc_lower for k in ["minor", "cosmetic", "suggestion", "slight"]):
            suggested_priority = "LOW"
            impact = "Low operational impact"
            priority_reason = "Non-urgent convenience or aesthetic maintenance item."

        # 6. Phase 3: Department, Sensitivity & Suggested Route Type Extraction
        department = None
        sensitivity = "NORMAL"
        suggested_route_type = "DEPARTMENT_AND_MANAGEMENT"
        routing_reason = "Standard departmental issue routed for localized handling and central oversight."

        # Sensitivity rules
        if is_conduct_allegation:
            sensitivity = "HIGH_SENSITIVITY"
            suggested_route_type = "AUTHORIZED_GRIEVANCE"
            department = "Student Affairs"
            routing_reason = "Confidential personnel conduct allegation requiring authorized grievance investigation and management oversight."
        elif any(k in desc_lower for k in ["exam", "timetable", "schedule clash", "conflict", "dark pathway", "flood", "rupture"]):
            sensitivity = "SENSITIVE"

        # Department identification
        if not department:
            if any(k in desc_lower for k in ["cse", "computer science", "cs lab", "lab 3"]):
                department = "CSE"
                suggested_route_type = "DEPARTMENT_AND_MANAGEMENT"
                routing_reason = "Department-specific laboratory and computing facility issue."
            elif any(k in desc_lower for k in ["ece", "electronics"]):
                department = "ECE"
                suggested_route_type = "DEPARTMENT_AND_MANAGEMENT"
                routing_reason = "Electronics department specialized equipment issue."
            elif any(k in desc_lower for k in ["eee", "electrical"]):
                department = "EEE" if "department" in desc_lower else "Maintenance"
            elif any(k in desc_lower for k in ["mech", "mechanical"]):
                department = "Mechanical"
            elif any(k in desc_lower for k in ["civil"]):
                department = "Civil"
            elif any(k in desc_lower for k in ["exam", "timetable", "hall"]):
                department = "Examinations"
                suggested_route_type = "DEPARTMENT_AND_MANAGEMENT"
                routing_reason = "Examination cell scheduling and logistics."
            elif any(k in desc_lower for k in ["bus", "shuttle", "transport"]):
                department = "Transport"
                suggested_route_type = "DEPARTMENT_AND_MANAGEMENT"
                routing_reason = "Campus transit authority operational routing."
            elif any(k in desc_lower for k in ["hostel", "dorm", "mess", "warden"]):
                department = "Hostel"
                suggested_route_type = "DEPARTMENT_AND_MANAGEMENT"
                routing_reason = "Hostel administration residential facility routing."
            elif any(k in desc_lower for k in ["security", "guard", "gate", "theft", "dark"]):
                department = "Security"
                suggested_route_type = "CAMPUS_OPERATIONS"
                routing_reason = "Campus security and safety authority."
            elif any(k in desc_lower for k in ["wi-fi", "wifi", "network", "eduroam"]):
                department = "IT"
                suggested_route_type = "CAMPUS_OPERATIONS"
                routing_reason = "Campus-wide IT network infrastructure operations."
            elif any(k in desc_lower for k in ["pipe", "water", "plumbing", "clean", "washroom", "trash", "power", "fan", "light"]):
                department = "Maintenance"
                suggested_route_type = "CAMPUS_OPERATIONS"
                routing_reason = "Campus physical facilities & maintenance operations."
            else:
                department = "Administration"
                suggested_route_type = "MANAGEMENT_ONLY"
                routing_reason = "General administrative review by central management."

        confidence = 0.90 if detected_category != "OTHER" else 0.75

        return ComplaintAIAnalysisSchema(
            category=detected_category,
            subcategory=subcategory,
            issue_summary=issue_summary,
            location=extracted_location,
            duration=duration,
            impact=impact,
            suggested_priority=suggested_priority,
            priority_reason=priority_reason,
            confidence=confidence,
            department=department,
            suggested_route_type=suggested_route_type,
            sensitivity=sensitivity,
            routing_reason=routing_reason,
        )


class GeminiProvider(AIProvider):
    """Google Gemini AI Provider utilizing the official google-genai SDK with structured output."""

    def __init__(self, api_key: str, model_name: str = "gemini-3.6-flash"):
        self.api_key = api_key
        self.model_name = model_name
        self.fallback = LocalHeuristicProvider()

    def get_provider_name(self) -> str:
        return "gemini"

    def get_model_name(self) -> str:
        return self.model_name

    async def analyze_complaint(
        self,
        description: str,
        location: str | None = None,
        category: str | None = None,
    ) -> ComplaintAIAnalysisSchema:
        if not self.api_key or not self.api_key.strip():
            logger.info("No GEMINI_API_KEY configured. Falling back to local heuristic analyzer.")
            return await self.fallback.analyze_complaint(description, location, category)

        try:
            from google import genai
            from google.genai import types

            client = genai.Client(api_key=self.api_key)
            prompt = build_complaint_analysis_prompt(description, location, category)

            # Request structured JSON output with strict Pydantic validation
            response = client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    system_instruction=COMPLAINT_ANALYSIS_SYSTEM_PROMPT,
                    response_mime_type="application/json",
                    response_schema=ComplaintAIAnalysisSchema,
                    temperature=0.1,
                ),
            )

            if not response.text:
                raise ValueError("Empty response from Gemini API")

            parsed = json.loads(response.text)

            # Validate department against configured whitelist
            dept = parsed.get("department")
            if dept and dept not in CONFIGURED_DEPARTMENTS:
                parsed["department"] = "Administration"

            return ComplaintAIAnalysisSchema(**parsed)

        except Exception as exc:
            logger.warning(
                f"Gemini API analysis failed: {exc}. Gracefully falling back to heuristic engine.",
                exc_info=True,
            )
            return await self.fallback.analyze_complaint(description, location, category)


def get_ai_provider() -> AIProvider:
    """Factory function returning the configured AI provider."""
    api_key = settings.GEMINI_API_KEY
    if api_key and settings.AI_PROVIDER == "gemini":
        return GeminiProvider(api_key=api_key, model_name=settings.GEMINI_MODEL)
    return LocalHeuristicProvider()
