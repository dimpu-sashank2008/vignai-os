"""
Career Intelligence REST API Router for Students.
Provides endpoints for career profile, secure resume upload, deterministic matching, skill gaps, and daily briefs.
"""

import os
import uuid
from datetime import datetime, date
from pathlib import Path
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user, require_role
from app.models.user import User
from app.models.career import (
    CareerProfile,
    CareerSkill,
    CareerProject,
    CareerCertification,
    CareerExperience,
    Opportunity,
    OpportunitySkill,
    OpportunityMatch,
)
from app.schemas.career import (
    CareerProfileResponse,
    OpportunityResponse,
    OpportunityMatchResponse,
    SkillGapResponse,
    DailyCareerBriefResponse,
    ResumeUploadResponse,
    CareerStrengthsResponse,
    PersonalizedRecommendationResponse,
    CareerDomainStrength,
    WhyRecommendedEvidence,
    EligibilityEvaluation,
)
from app.services.career.matching_engine import matching_engine
from app.services.career.resume_parser import resume_parser
from app.services.career.career_fit_service import career_strength_analyzer, personalized_ranking_engine
from app.services.complaint_service import sanitize_filename

router = APIRouter(prefix="/api/student/career", tags=["Career Intelligence"])

UPLOAD_DIR = Path(__file__).resolve().parent.parent.parent / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

ALLOWED_RESUME_TYPES = {
    "application/pdf": ".pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": ".docx",
    "application/msword": ".doc",
    "text/plain": ".txt",
}
MAX_RESUME_SIZE = 25 * 1024 * 1024  # 25 MB


def _get_or_create_career_profile(db: Session, student_user: User) -> CareerProfile:
    """Helper to retrieve or initialize a student's CareerProfile."""
    profile = db.query(CareerProfile).filter(CareerProfile.student_id == student_user.id).first()
    if not profile:
        profile = CareerProfile(
            student_id=student_user.id,
            headline="B.Tech Student | Software Engineering & AI",
            summary="Aspiring developer exploring opportunities in full-stack engineering, AI, and distributed systems.",
            education="B.Tech in Computer Science & Engineering, Vignan's Institute of Information Technology (VIIT)",
            interests=["Artificial Intelligence", "Full-Stack Development", "Cloud Computing"],
            extraction_status="NOT_UPLOADED",
            data_source="STUDENT_PROVIDED",
        )
        db.add(profile)
        db.commit()
        db.refresh(profile)

        # Seed starter skills
        init_skills = [
            ("Python", "TECHNICAL", "STUDENT_PROVIDED", "INTERMEDIATE"),
            ("React", "FRAMEWORK", "STUDENT_PROVIDED", "INTERMEDIATE"),
            ("SQL", "DATABASE", "STUDENT_PROVIDED", "INTERMEDIATE"),
            ("FastAPI", "FRAMEWORK", "STUDENT_PROVIDED", "INTERMEDIATE"),
            ("Git", "TOOL", "STUDENT_PROVIDED", "INTERMEDIATE"),
            ("Data Structures", "TECHNICAL", "STUDENT_PROVIDED", "INTERMEDIATE"),
        ]
        for s_name, cat, src, prof in init_skills:
            db.add(CareerSkill(
                career_profile_id=profile.id,
                name=s_name,
                category=cat,
                source=src,
                proficiency_level=prof,
            ))
        db.commit()
        db.refresh(profile)

        # Sync matches against active opportunities
        matching_engine.sync_student_matches(db, profile.id)

    return profile


@router.get("/profile", response_model=CareerProfileResponse)
def get_career_profile(
    current_user: User = Depends(require_role("student")),
    db: Session = Depends(get_db),
):
    """Retrieve the authenticated student's career profile."""
    profile = _get_or_create_career_profile(db, current_user)
    return profile


@router.post("/resume", response_model=ResumeUploadResponse)
async def upload_resume(
    file: UploadFile = File(...),
    current_user: User = Depends(require_role("student")),
    db: Session = Depends(get_db),
):
    """Upload resume (PDF/DOCX), extract structured skills and projects, and compute opportunity matches."""
    content_type = file.content_type or "application/octet-stream"
    original_name = sanitize_filename(file.filename or "resume.pdf")
    ext = Path(original_name).suffix.lower()

    if content_type not in ALLOWED_RESUME_TYPES and ext not in [".pdf", ".docx", ".doc", ".txt"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unsupported file format. Please upload a PDF or DOCX resume document.",
        )

    content = await file.read()
    file_size = len(content)

    if file_size > MAX_RESUME_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File size exceeds maximum limit of 25MB.",
        )
    if file_size == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded resume file is empty.",
        )

    # Secure storage
    unique_name = f"resume_{current_user.id}_{uuid.uuid4().hex[:8]}{ext}"
    target_path = UPLOAD_DIR / unique_name
    with open(target_path, "wb") as f:
        f.write(content)

    # Extract structured text
    extracted_text = resume_parser.extract_text_from_file(str(target_path))
    parsed_data = resume_parser.parse_resume_text(extracted_text)

    profile = _get_or_create_career_profile(db, current_user)
    profile.resume_file_name = original_name
    profile.resume_file_path = str(target_path)
    profile.resume_file_size = file_size
    profile.resume_uploaded_at = datetime.utcnow()
    profile.extraction_status = "COMPLETED"
    profile.data_source = "VERIFIED_FROM_RESUME"
    if parsed_data.get("headline"):
        profile.headline = parsed_data["headline"]
    if parsed_data.get("summary"):
        profile.summary = parsed_data["summary"]
    if parsed_data.get("education"):
        profile.education = parsed_data["education"]
    if parsed_data.get("interests"):
        profile.interests = parsed_data["interests"]

    # Replace extracted skills
    db.query(CareerSkill).filter(CareerSkill.career_profile_id == profile.id).delete()
    for s in parsed_data.get("skills", []):
        db.add(CareerSkill(
            career_profile_id=profile.id,
            name=s["name"],
            category=s.get("category", "TECHNICAL"),
            source=s.get("source", "VERIFIED_FROM_RESUME"),
            proficiency_level=s.get("proficiency_level", "INTERMEDIATE"),
        ))

    # Replace extracted projects
    db.query(CareerProject).filter(CareerProject.career_profile_id == profile.id).delete()
    for p in parsed_data.get("projects", []):
        db.add(CareerProject(
            career_profile_id=profile.id,
            title=p["title"],
            description=p.get("description"),
            technologies=p.get("technologies", []),
            source=p.get("source", "VERIFIED_FROM_RESUME"),
        ))

    # Replace certifications
    db.query(CareerCertification).filter(CareerCertification.career_profile_id == profile.id).delete()
    for c in parsed_data.get("certifications", []):
        db.add(CareerCertification(
            career_profile_id=profile.id,
            title=c["title"],
            issuer=c.get("issuer"),
            issue_date=c.get("issue_date"),
            source=c.get("source", "VERIFIED_FROM_RESUME"),
        ))

    # Replace experiences
    db.query(CareerExperience).filter(CareerExperience.career_profile_id == profile.id).delete()
    for exp in parsed_data.get("experiences", []):
        db.add(CareerExperience(
            career_profile_id=profile.id,
            title=exp["title"],
            organization=exp.get("organization"),
            duration=exp.get("duration"),
            description=exp.get("description"),
            source=exp.get("source", "VERIFIED_FROM_RESUME"),
        ))

    db.commit()
    db.refresh(profile)

    # Re-calculate matches
    matching_engine.sync_student_matches(db, profile.id)

    return ResumeUploadResponse(
        message="Resume uploaded and processed successfully. Career profile updated.",
        file_name=original_name,
        file_size=file_size,
        extracted_skills_count=len(parsed_data.get("skills", [])),
        extracted_projects_count=len(parsed_data.get("projects", [])),
        profile=profile,
    )


@router.get("/resume/download")
def download_resume(
    current_user: User = Depends(require_role("student")),
    db: Session = Depends(get_db),
):
    """Securely download the authenticated student's uploaded resume."""
    profile = db.query(CareerProfile).filter(CareerProfile.student_id == current_user.id).first()
    if not profile or not profile.resume_file_path or not os.path.exists(profile.resume_file_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No resume on file for this student account.",
        )

    ext = Path(profile.resume_file_path).suffix.lower()
    media_type = "application/pdf" if ext == ".pdf" else "application/octet-stream"

    return FileResponse(
        path=profile.resume_file_path,
        media_type=media_type,
        filename=profile.resume_file_name or f"resume{ext}",
    )


@router.get("/opportunities", response_model=List[OpportunityResponse])
def list_opportunities(
    opportunity_type: Optional[str] = Query(None, alias="type"),
    work_mode: Optional[str] = Query(None, alias="work_mode"),
    trust: Optional[str] = Query("verified", alias="trust"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List active career opportunities with optional filtering and verification trust filter."""
    query = db.query(Opportunity).filter(
        Opportunity.is_active == True,
        Opportunity.lifecycle_status != "EXPIRED",
    )
    if trust != "all":
        query = query.filter(Opportunity.verification_status == "VERIFIED")

    if opportunity_type:
        query = query.filter(Opportunity.opportunity_type == opportunity_type.upper())
    if work_mode:
        query = query.filter(Opportunity.work_mode == work_mode.upper())

    return query.order_by(Opportunity.created_at.desc()).all()


@router.get("/matches", response_model=List[OpportunityMatchResponse])
def get_opportunity_matches(
    sort_by: str = Query("best_match", pattern="^(best_match|closing_soon|newest|type)$"),
    opportunity_type: Optional[str] = Query(None, alias="type"),
    work_mode: Optional[str] = Query(None, alias="work_mode"),
    current_user: User = Depends(require_role("student")),
    db: Session = Depends(get_db),
):
    """Retrieve opportunity matches for the authenticated student with deterministic scores and explainability."""
    profile = _get_or_create_career_profile(db, current_user)
    matches = matching_engine.sync_student_matches(db, profile.id)

    now = datetime.utcnow()
    results = []

    for m in matches:
        opp = m.opportunity
        if not opp or not opp.is_active or opp.verification_status != "VERIFIED" or opp.lifecycle_status == "EXPIRED":
            continue

        # Filter by type
        if opportunity_type and opp.opportunity_type != opportunity_type.upper():
            continue
        # Filter by work mode
        if work_mode and opp.work_mode != work_mode.upper():
            continue

        days_remaining = None
        is_closing_soon = False
        if opp.deadline:
            days = (opp.deadline - now).days
            days_remaining = max(0, days)
            if 0 <= days <= 14:
                is_closing_soon = True

        rec_text = "Strong profile alignment based on matching technical requirements."
        if m.match_score >= 85:
            rec_text = "High alignment across core required skills. Highly recommended to review."
        elif m.match_score >= 70:
            rec_text = "Solid foundational match. Developing 1 optional skill will strengthen alignment."
        else:
            rec_text = "Foundational prerequisites present. Review missing skills to evaluate readiness."

        results.append(OpportunityMatchResponse(
            id=m.id,
            opportunity=OpportunityResponse.model_validate(opp),
            match_score=m.match_score,
            matched_skills=m.matched_skills or [],
            missing_skills=m.missing_skills or [],
            location_fit=m.location_fit,
            work_mode_fit=m.work_mode_fit,
            eligibility_fit=m.eligibility_fit,
            match_reasons=m.match_reasons or {},
            is_closing_soon=is_closing_soon,
            days_remaining=days_remaining,
            recommendation_text=rec_text,
        ))

    # Sort
    if sort_by == "best_match":
        results.sort(key=lambda x: x.match_score, reverse=True)
    elif sort_by == "closing_soon":
        results.sort(key=lambda x: (x.days_remaining if x.days_remaining is not None else 9999))
    elif sort_by == "newest":
        results.sort(key=lambda x: x.opportunity.created_at, reverse=True)
    elif sort_by == "type":
        results.sort(key=lambda x: x.opportunity.opportunity_type)

    return results


@router.get("/skill-gaps", response_model=List[SkillGapResponse])
def get_skill_gaps(
    current_user: User = Depends(require_role("student")),
    db: Session = Depends(get_db),
):
    """Retrieve aggregated skill gaps and responsible learning recommendations."""
    profile = _get_or_create_career_profile(db, current_user)
    gaps = matching_engine.get_skill_gaps(db, profile.id)
    return gaps


@router.get("/brief", response_model=DailyCareerBriefResponse)
def get_daily_career_brief(
    current_user: User = Depends(require_role("student")),
    db: Session = Depends(get_db),
):
    """Retrieve daily career brief, top career direction, and closing deadlines summary."""
    brief = matching_engine.get_daily_career_brief(db, current_user)
    strengths = career_strength_analyzer.analyze_strengths(db, current_user)
    if strengths:
        brief["top_career_direction"] = strengths[0]["domain_name"]
    recs = personalized_ranking_engine.get_recommendations(db, current_user)
    brief["high_fit_count"] = sum(1 for r in recs if r["personalized_profile_fit"] >= 80.0)
    return brief


@router.get("/strengths", response_model=CareerStrengthsResponse)
def get_career_strengths(
    current_user: User = Depends(require_role("student")),
    db: Session = Depends(get_db),
):
    """Retrieve deterministic career-domain strengths and transparent supporting evidence."""
    strengths = career_strength_analyzer.analyze_strengths(db, current_user)
    top_direction = strengths[0]["domain_name"] if strengths else "General Engineering"
    top_score = strengths[0]["alignment_score"] if strengths else 75.0
    return CareerStrengthsResponse(
        student_name=current_user.email.split("@")[0],
        top_career_direction=top_direction,
        top_alignment_score=top_score,
        domain_strengths=strengths,
    )


@router.get("/recommendations", response_model=List[PersonalizedRecommendationResponse])
def get_personalized_recommendations(
    current_user: User = Depends(require_role("student")),
    db: Session = Depends(get_db),
):
    """Retrieve personalized recommendations ranked by ProfileFit with [Why VIGNAI Recommends This] evidence."""
    recs = personalized_ranking_engine.get_recommendations(db, current_user)
    return recs
