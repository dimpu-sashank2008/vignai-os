"""
Career Intelligence Services for VIGNAI OS (Student Ecosystem).
Provides deterministic matching, resume extraction, skill-gap analysis, and daily briefs.
"""
from app.services.career.matching_engine import matching_engine
from app.services.career.resume_parser import resume_parser
from app.services.career.intake_service import CoordinatorIntakeService
from app.services.career.ingestion_service import OpportunityIngestionService
from app.services.career.domain_taxonomy import CAREER_DOMAINS, get_domains_for_subject_code, get_domain_by_id
from app.services.career.career_fit_service import (
    CareerStrengthAnalyzer,
    EligibilityEngine,
    PersonalizedRecommendationEngine,
    career_strength_analyzer,
    eligibility_engine,
    personalized_ranking_engine,
)

__all__ = [
    "matching_engine",
    "resume_parser",
    "CoordinatorIntakeService",
    "OpportunityIngestionService",
    "CAREER_DOMAINS",
    "get_domains_for_subject_code",
    "get_domain_by_id",
    "CareerStrengthAnalyzer",
    "EligibilityEngine",
    "PersonalizedRecommendationEngine",
    "career_strength_analyzer",
    "eligibility_engine",
    "personalized_ranking_engine",
]
