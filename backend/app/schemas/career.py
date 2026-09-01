from datetime import datetime
from typing import Optional, List, Any, Dict
from pydantic import BaseModel, ConfigDict, Field


class CareerSkillSchema(BaseModel):
    id: Optional[int] = None
    name: str
    category: str = "TECHNICAL"
    source: str = "VERIFIED_FROM_RESUME" # VERIFIED_FROM_RESUME, STUDENT_PROVIDED, AI_ASSISTED_EXTRACTION
    proficiency_level: str = "INTERMEDIATE"

    model_config = ConfigDict(from_attributes=True)


class CareerProjectSchema(BaseModel):
    id: Optional[int] = None
    title: str
    description: Optional[str] = None
    technologies: List[str] = Field(default_factory=list)
    source: str = "VERIFIED_FROM_RESUME"

    model_config = ConfigDict(from_attributes=True)


class CareerCertificationSchema(BaseModel):
    id: Optional[int] = None
    title: str
    issuer: Optional[str] = None
    issue_date: Optional[str] = None
    source: str = "VERIFIED_FROM_RESUME"

    model_config = ConfigDict(from_attributes=True)


class CareerExperienceSchema(BaseModel):
    id: Optional[int] = None
    title: str
    organization: Optional[str] = None
    duration: Optional[str] = None
    description: Optional[str] = None
    source: str = "VERIFIED_FROM_RESUME"

    model_config = ConfigDict(from_attributes=True)


class CareerProfileResponse(BaseModel):
    id: int
    student_id: int
    headline: Optional[str] = None
    summary: Optional[str] = None
    education: Optional[str] = None
    interests: List[str] = Field(default_factory=list)
    resume_file_name: Optional[str] = None
    resume_file_size: Optional[int] = None
    resume_uploaded_at: Optional[datetime] = None
    extraction_status: str = "NOT_UPLOADED"
    data_source: str = "STUDENT_PROVIDED"
    skills: List[CareerSkillSchema] = Field(default_factory=list)
    projects: List[CareerProjectSchema] = Field(default_factory=list)
    certifications: List[CareerCertificationSchema] = Field(default_factory=list)
    experiences: List[CareerExperienceSchema] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class OpportunitySkillSchema(BaseModel):
    id: Optional[int] = None
    skill_name: str
    is_required: bool = True

    model_config = ConfigDict(from_attributes=True)


class OpportunityResponse(BaseModel):
    id: int
    opportunity_id: str
    title: str
    organization: str
    opportunity_type: str # INTERNSHIP, JOB, RESEARCH, HACKATHON, COURSE, CERTIFICATION
    description: str
    location: str
    work_mode: str # REMOTE, HYBRID, ON_SITE
    deadline: Optional[datetime] = None
    eligibility: str
    source_name: str = "VIGNAI Development Partner"
    source_type: str = "SYNTHETIC_DEVELOPMENT"
    verification_status: str = "VERIFIED" # DRAFT, VERIFIED, REJECTED, EXPIRED
    lifecycle_status: str = "ACTIVE" # NEW, VERIFIED, ACTIVE, EXPIRING, EXPIRED
    submitted_at: Optional[datetime] = None
    verified_at: Optional[datetime] = None
    data_source: str = "SYNTHETIC DEVELOPMENT DATA"
    is_active: bool = True
    skills: List[OpportunitySkillSchema] = Field(default_factory=list)
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class OpportunityMatchResponse(BaseModel):
    id: int
    opportunity: OpportunityResponse
    match_score: float # 0.0 to 100.0
    matched_skills: List[str]
    missing_skills: List[str]
    location_fit: bool
    work_mode_fit: bool
    eligibility_fit: bool
    match_reasons: Dict[str, Any]
    is_closing_soon: bool = False
    days_remaining: Optional[int] = None
    recommendation_text: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class SkillGapResponse(BaseModel):
    skill_name: str
    occurrence_count: int
    target_opportunities: List[str]
    recommendation: str
    category: str = "TECHNICAL"
    priority: str = "HIGH" # HIGH, MEDIUM, LOW


class DailyCareerBriefResponse(BaseModel):
    student_name: str
    total_matched_opportunities: int
    top_match_title: Optional[str] = None
    top_match_score: Optional[float] = None
    top_match_org: Optional[str] = None
    closing_soon_count: int
    skill_gaps_count: int
    skill_gaps: List[SkillGapResponse] = Field(default_factory=list)
    brief_message: str
    top_career_direction: Optional[str] = None
    high_fit_count: int = 0
    data_source: str = "SYNTHETIC DEVELOPMENT DATA"


class ResumeUploadResponse(BaseModel):
    message: str
    file_name: str
    file_size: int
    extracted_skills_count: int
    extracted_projects_count: int
    profile: CareerProfileResponse


class CareerSubjectPerformance(BaseModel):
    code: str
    name: str
    score: float
    credits: int = 3


class CareerDomainStrength(BaseModel):
    domain_id: str
    domain_name: str
    category: str
    alignment_score: float
    alignment_level: str # STRONG_ALIGNMENT, GOOD_ALIGNMENT, MODERATE_ALIGNMENT, DEVELOPING_FIT
    relevant_subjects: List[CareerSubjectPerformance] = Field(default_factory=list)
    matched_skills: List[str] = Field(default_factory=list)
    matching_projects_count: int = 0
    matching_certs_count: int = 0
    interest_matched: bool = False
    summary_phrase: str


class CareerStrengthsResponse(BaseModel):
    student_name: str
    top_career_direction: str
    top_alignment_score: float
    domain_strengths: List[CareerDomainStrength]
    data_source: str = "SYNTHETIC DEVELOPMENT DATA"


class WhyRecommendedEvidence(BaseModel):
    primary_domain: str
    domain_alignment_score: float
    academic_highlights: List[str]
    skill_highlights: List[str]
    project_highlights: str
    eligibility_statement: str
    strengths: List[str]
    skill_gaps: List[str]
    learning_recommendation: Optional[str] = None
    responsible_disclaimer: str


class EligibilityEvaluation(BaseModel):
    status: str # ELIGIBLE, INELIGIBLE, UNKNOWN
    is_eligible: bool
    reasons: List[str]
    warnings: List[str]
    criteria_summary: str


class PersonalizedRecommendationResponse(BaseModel):
    id: int
    opportunity: OpportunityResponse
    match_score: float
    personalized_profile_fit: float
    eligibility: EligibilityEvaluation
    matched_skills: List[str]
    missing_skills: List[str]
    primary_domain: str
    why_recommended: WhyRecommendedEvidence
    is_closing_soon: bool = False
    days_remaining: Optional[int] = None
