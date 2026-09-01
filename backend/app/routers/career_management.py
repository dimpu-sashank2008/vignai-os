from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user, require_role
from app.models.user import User
from app.models.career import Opportunity, OpportunitySource
from app.schemas.career import OpportunityResponse
from app.schemas.career_management import (
    CoordinatorIntakeRequest,
    CoordinatorIntakeResponse,
    CoordinatorIntakeExtraction,
    VerificationActionRequest,
    OpportunitySourceResponse,
    SyncSourcesResponse,
)
from app.services.career.intake_service import CoordinatorIntakeService
from app.services.career.ingestion_service import OpportunityIngestionService

router = APIRouter(prefix="/api/management/career", tags=["Management Career Intelligence & Intake"])


@router.post("/intake", response_model=CoordinatorIntakeResponse)
def submit_opportunity_intake(
    payload: CoordinatorIntakeRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("management", "faculty")),
):
    """
    Authorized placement coordinator submits opportunity circular/announcement.
    VIGNAI parses it into a DRAFT opportunity requiring verification before publishing.
    """
    if not payload.announcement_text or not payload.announcement_text.strip():
        raise HTTPException(status_code=400, detail="Announcement text is required.")

    extracted = CoordinatorIntakeService.extract_from_text(payload.announcement_text)
    opp = CoordinatorIntakeService.create_draft(
        db=db,
        user=current_user,
        announcement_text=payload.announcement_text,
        source_name=payload.source_name,
        source_type=payload.source_type,
    )

    return CoordinatorIntakeResponse(
        message="Opportunity draft created successfully. Review and verify to publish to student feeds.",
        opportunity=OpportunityResponse.model_validate(opp),
        extracted_details=CoordinatorIntakeExtraction(
            title=extracted["title"],
            organization=extracted["organization"],
            opportunity_type=extracted["opportunity_type"],
            description=extracted["description"],
            skills_required=extracted["skills_required"],
            skills_preferred=extracted["skills_preferred"],
            eligibility=extracted["eligibility"],
            location=extracted["location"],
            work_mode=extracted["work_mode"],
            deadline_str=extracted["deadline"].isoformat() if extracted.get("deadline") else None,
        ),
    )


@router.get("/intake/queue", response_model=List[OpportunityResponse])
def get_opportunity_intake_queue(
    status: Optional[str] = Query(None, description="Filter by verification status: DRAFT, VERIFIED, REJECTED, EXPIRED"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("management", "faculty")),
):
    """Retrieves all submitted opportunities in the intake and verification queue."""
    query = db.query(Opportunity)
    if status:
        query = query.filter(Opportunity.verification_status == status.upper())
    
    opps = query.order_by(Opportunity.created_at.desc()).all()
    return [OpportunityResponse.model_validate(opp) for opp in opps]


@router.post("/intake/{opportunity_id}/verify", response_model=OpportunityResponse)
def verify_or_reject_opportunity(
    opportunity_id: int,
    payload: VerificationActionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("management", "faculty")),
):
    """
    Authorized management/faculty coordinator verifies and publishes or rejects an opportunity draft.
    """
    if payload.action.upper() not in ["VERIFY", "REJECT"]:
        raise HTTPException(status_code=400, detail="Action must be 'VERIFY' or 'REJECT'.")

    try:
        opp = CoordinatorIntakeService.verify_opportunity(
            db=db,
            opportunity_id=opportunity_id,
            user=current_user,
            action=payload.action.upper(),
            review_notes=payload.review_notes,
        )
        return OpportunityResponse.model_validate(opp)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/sources", response_model=List[OpportunitySourceResponse])
def get_opportunity_sources(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("management", "faculty")),
):
    """Lists registered opportunity connectors and their real-time synchronization health."""
    sources = db.query(OpportunitySource).order_by(OpportunitySource.id.asc()).all()
    return [OpportunitySourceResponse.model_validate(s) for s in sources]


@router.post("/sources/sync", response_model=SyncSourcesResponse)
def sync_opportunity_sources(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("management", "faculty")),
):
    """
    Triggers an immediate synchronization across all registered opportunity sources,
    deduplicating listings, checking deadlines, and refreshing student matches.
    """
    result = OpportunityIngestionService.sync_all_sources(db)
    return SyncSourcesResponse(
        message=result["message"],
        total_sources_polled=result["total_sources_polled"],
        new_opportunities_ingested=result["new_opportunities_ingested"],
        duplicates_skipped=result["duplicates_skipped"],
        expired_count=result["expired_count"],
        sources_health=[OpportunitySourceResponse.model_validate(s) for s in result["sources_health"]],
    )
