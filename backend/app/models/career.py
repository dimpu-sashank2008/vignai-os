from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, Float, ForeignKey, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base

class CareerProfile(Base):
    __tablename__ = "career_profiles"

    id = Column(Integer, primary_key=True, autoincrement=True)
    student_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True, index=True)
    headline = Column(String(255), nullable=True)
    summary = Column(Text, nullable=True)
    education = Column(Text, nullable=True)
    interests = Column(JSON, nullable=True, default=list)
    resume_file_name = Column(String(255), nullable=True)
    resume_file_path = Column(String(500), nullable=True)
    resume_file_size = Column(Integer, nullable=True)
    resume_uploaded_at = Column(DateTime, nullable=True)
    extraction_status = Column(String(50), default="NOT_UPLOADED", nullable=False) # NOT_UPLOADED, COMPLETED, FAILED
    data_source = Column(String(100), default="STUDENT_PROVIDED", nullable=False)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)

    user = relationship("User")
    skills = relationship("CareerSkill", back_populates="career_profile", cascade="all, delete-orphan")
    projects = relationship("CareerProject", back_populates="career_profile", cascade="all, delete-orphan")
    certifications = relationship("CareerCertification", back_populates="career_profile", cascade="all, delete-orphan")
    experiences = relationship("CareerExperience", back_populates="career_profile", cascade="all, delete-orphan")
    matches = relationship("OpportunityMatch", back_populates="career_profile", cascade="all, delete-orphan")


class CareerSkill(Base):
    __tablename__ = "career_skills"

    id = Column(Integer, primary_key=True, autoincrement=True)
    career_profile_id = Column(Integer, ForeignKey("career_profiles.id"), nullable=False, index=True)
    name = Column(String(100), nullable=False, index=True)
    category = Column(String(50), default="TECHNICAL", nullable=False) # TECHNICAL, FRAMEWORK, DATABASE, TOOL, SOFT_SKILL
    source = Column(String(50), default="VERIFIED_FROM_RESUME", nullable=False) # VERIFIED_FROM_RESUME, STUDENT_PROVIDED, AI_ASSISTED_EXTRACTION
    proficiency_level = Column(String(50), default="INTERMEDIATE", nullable=False) # BEGINNER, INTERMEDIATE, ADVANCED
    created_at = Column(DateTime, default=func.now(), nullable=False)

    career_profile = relationship("CareerProfile", back_populates="skills")


class CareerProject(Base):
    __tablename__ = "career_projects"

    id = Column(Integer, primary_key=True, autoincrement=True)
    career_profile_id = Column(Integer, ForeignKey("career_profiles.id"), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    technologies = Column(JSON, nullable=True, default=list)
    source = Column(String(50), default="VERIFIED_FROM_RESUME", nullable=False)
    created_at = Column(DateTime, default=func.now(), nullable=False)

    career_profile = relationship("CareerProfile", back_populates="projects")


class CareerCertification(Base):
    __tablename__ = "career_certifications"

    id = Column(Integer, primary_key=True, autoincrement=True)
    career_profile_id = Column(Integer, ForeignKey("career_profiles.id"), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    issuer = Column(String(255), nullable=True)
    issue_date = Column(String(50), nullable=True)
    source = Column(String(50), default="VERIFIED_FROM_RESUME", nullable=False)
    created_at = Column(DateTime, default=func.now(), nullable=False)

    career_profile = relationship("CareerProfile", back_populates="certifications")


class CareerExperience(Base):
    __tablename__ = "career_experiences"

    id = Column(Integer, primary_key=True, autoincrement=True)
    career_profile_id = Column(Integer, ForeignKey("career_profiles.id"), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    organization = Column(String(255), nullable=True)
    duration = Column(String(100), nullable=True)
    description = Column(Text, nullable=True)
    source = Column(String(50), default="VERIFIED_FROM_RESUME", nullable=False)
    created_at = Column(DateTime, default=func.now(), nullable=False)

    career_profile = relationship("CareerProfile", back_populates="experiences")


class Opportunity(Base):
    __tablename__ = "opportunities"

    id = Column(Integer, primary_key=True, autoincrement=True)
    opportunity_id = Column(String(50), unique=True, nullable=False, index=True) # e.g. OPP-2026-001
    title = Column(String(255), nullable=False)
    organization = Column(String(255), default="VIGNAI Development Partner", nullable=False)
    opportunity_type = Column(String(50), default="INTERNSHIP", nullable=False) # INTERNSHIP, JOB, RESEARCH, HACKATHON, COURSE, CERTIFICATION
    description = Column(Text, nullable=False)
    location = Column(String(100), default="Remote", nullable=False)
    work_mode = Column(String(50), default="REMOTE", nullable=False) # REMOTE, HYBRID, ON_SITE
    deadline = Column(DateTime, nullable=True)
    eligibility = Column(String(255), default="B.Tech All Years / Branches", nullable=False)
    source_name = Column(String(100), default="VIGNAI Development Partner", nullable=False)
    source_type = Column(String(50), default="SYNTHETIC_DEVELOPMENT", nullable=False) # INSTITUTION_CURATED, AUTHORIZED_COORDINATOR, APPROVED_API, PUBLIC_FEED, SYNTHETIC_DEVELOPMENT
    verification_status = Column(String(50), default="VERIFIED", nullable=False) # DRAFT, VERIFIED, REJECTED, EXPIRED
    lifecycle_status = Column(String(50), default="ACTIVE", nullable=False) # NEW, VERIFIED, ACTIVE, EXPIRING, EXPIRED
    submitted_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    submitted_at = Column(DateTime, nullable=True)
    verified_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    verified_at = Column(DateTime, nullable=True)
    fingerprint = Column(String(64), nullable=True, index=True) # Deterministic SHA-256 for deduplication
    raw_content = Column(Text, nullable=True)
    data_source = Column(String(100), default="SYNTHETIC DEVELOPMENT DATA", nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=func.now(), nullable=False)

    skills = relationship("OpportunitySkill", back_populates="opportunity", cascade="all, delete-orphan")
    matches = relationship("OpportunityMatch", back_populates="opportunity", cascade="all, delete-orphan")
    submitted_by = relationship("User", foreign_keys=[submitted_by_id])
    verified_by = relationship("User", foreign_keys=[verified_by_id])


class OpportunitySkill(Base):
    __tablename__ = "opportunity_skills"

    id = Column(Integer, primary_key=True, autoincrement=True)
    opportunity_id = Column(Integer, ForeignKey("opportunities.id"), nullable=False, index=True)
    skill_name = Column(String(100), nullable=False, index=True)
    is_required = Column(Boolean, default=True, nullable=False)

    opportunity = relationship("Opportunity", back_populates="skills")


class OpportunityMatch(Base):
    __tablename__ = "opportunity_matches"

    id = Column(Integer, primary_key=True, autoincrement=True)
    career_profile_id = Column(Integer, ForeignKey("career_profiles.id"), nullable=False, index=True)
    opportunity_id = Column(Integer, ForeignKey("opportunities.id"), nullable=False, index=True)
    match_score = Column(Float, default=0.0, nullable=False) # 0.0 to 100.0 (deterministic)
    matched_skills = Column(JSON, nullable=False, default=list)
    missing_skills = Column(JSON, nullable=False, default=list)
    location_fit = Column(Boolean, default=True, nullable=False)
    work_mode_fit = Column(Boolean, default=True, nullable=False)
    eligibility_fit = Column(Boolean, default=True, nullable=False)
    match_reasons = Column(JSON, nullable=True, default=dict)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)

    career_profile = relationship("CareerProfile", back_populates="matches")
    opportunity = relationship("Opportunity", back_populates="matches")


class OpportunitySource(Base):
    __tablename__ = "opportunity_sources"

    id = Column(Integer, primary_key=True, autoincrement=True)
    source_name = Column(String(100), unique=True, nullable=False, index=True)
    source_type = Column(String(50), nullable=False) # INSTITUTION_CURATED, AUTHORIZED_COORDINATOR, APPROVED_API, PUBLIC_FEED
    status = Column(String(50), default="HEALTHY", nullable=False) # HEALTHY, DEGRADED, OFFLINE
    last_checked = Column(DateTime, nullable=True)
    last_success = Column(DateTime, nullable=True)
    items_found = Column(Integer, default=0, nullable=False)
    error_message = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=func.now(), nullable=False)
