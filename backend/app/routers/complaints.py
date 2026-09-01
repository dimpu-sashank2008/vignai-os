import os
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, BackgroundTasks, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from app.database import get_db
from app.dependencies import get_current_user, require_role
from app.models.user import User
from app.models.evidence import Evidence
from app.models.complaint import Complaint
from app.models.ai_analysis import ComplaintAIAnalysis
from app.schemas.complaint import ComplaintCreateRequest, ComplaintResponse, ComplaintSummaryResponse, TaxonomyResponse, TaxonomyCategoryItem
from app.schemas.evidence import EvidenceResponse
from app.schemas.ai_analysis import ComplaintAIAnalysisResponse, RelatedCaseSchema
from app.services import complaint_service
from app.services.ai.complaint_ai import complaint_ai_service
from app.services.ai.duplicate_detection import find_related_complaints
from app.config.categories import CATEGORY_TAXONOMY, CATEGORY_DISPLAY_LABELS

router = APIRouter(prefix="/complaints", tags=["complaints"])

@router.get("/taxonomy", response_model=TaxonomyResponse)
async def get_category_taxonomy():
    """Retrieve the central configurable category and subcategory taxonomy."""
    categories_list = [
        TaxonomyCategoryItem(
            key=key,
            label=CATEGORY_DISPLAY_LABELS.get(key, key.replace("_", " ").title()),
            subcategories=subcats,
        )
        for key, subcats in CATEGORY_TAXONOMY.items()
    ]
    return TaxonomyResponse(
        categories=categories_list,
        taxonomy_map=CATEGORY_TAXONOMY,
    )


@router.post("", response_model=ComplaintResponse, status_code=status.HTTP_201_CREATED)
async def submit_complaint(
    request: ComplaintCreateRequest,
    current_user: User = Depends(require_role("student")),
    db: Session = Depends(get_db),
):
    """Create a new campus complaint and immediately trigger AI structured analysis."""
    complaint = complaint_service.create_complaint(
        db=db,
        student_id=current_user.id,
        request=request,
    )

    # Execute AI Analysis (resilient, non-blocking to complaint persistence)
    try:
        await complaint_ai_service.analyze_and_save(db=db, complaint_id=complaint.id)
        db.refresh(complaint)
    except Exception as exc:
        # Guarantee complaint submission never crashes if AI encounters an unexpected issue
        pass

    return complaint

@router.get("/my", response_model=list[ComplaintResponse])
async def list_my_complaints(
    current_user: User = Depends(require_role("student")),
    db: Session = Depends(get_db),
):
    """Retrieve all complaints submitted by the authenticated student."""
    return complaint_service.get_student_complaints(db=db, student_id=current_user.id)

@router.get("/summary", response_model=ComplaintSummaryResponse)
async def get_complaint_summary(
    current_user: User = Depends(require_role("student")),
    db: Session = Depends(get_db),
):
    """Retrieve count summary for dashboard metrics."""
    complaints = complaint_service.get_student_complaints(db=db, student_id=current_user.id)
    total = len(complaints)
    open_count = sum(1 for c in complaints if c.status.upper() == "SUBMITTED")
    under_review = sum(1 for c in complaints if c.status.upper() == "UNDER_REVIEW")
    in_progress = sum(1 for c in complaints if c.status.upper() == "IN_PROGRESS")
    resolved = sum(1 for c in complaints if c.status.upper() == "RESOLVED")
    closed = sum(1 for c in complaints if c.status.upper() == "CLOSED")

    return ComplaintSummaryResponse(
        total=total,
        open=open_count,
        under_review=under_review,
        in_progress=in_progress,
        resolved=resolved,
        closed=closed,
    )

@router.get("/{case_id}", response_model=ComplaintResponse)
async def get_complaint_detail(
    case_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Retrieve detailed case information with role-based ownership validation."""
    return complaint_service.get_complaint_by_case_id(
        db=db,
        case_id=case_id,
        current_user_id=current_user.id,
        user_role=current_user.role,
    )

@router.get("/{case_id}/ai-analysis", response_model=ComplaintAIAnalysisResponse)
async def get_complaint_ai_analysis(
    case_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Retrieve AI-assisted intelligence for an authorized complaint."""
    complaint = complaint_service.get_complaint_by_case_id(
        db=db,
        case_id=case_id,
        current_user_id=current_user.id,
        user_role=current_user.role,
    )

    analysis = db.query(ComplaintAIAnalysis).filter(
        ComplaintAIAnalysis.complaint_id == complaint.id
    ).first()

    if not analysis:
        # If not analyzed yet, run it on-demand
        analysis = await complaint_ai_service.analyze_and_save(db=db, complaint_id=complaint.id)

    if not analysis:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="AI analysis not found.")

    return analysis

@router.post("/{case_id}/ai-analysis/retry", response_model=ComplaintAIAnalysisResponse)
async def retry_complaint_ai_analysis(
    case_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Re-run AI analysis on an existing complaint."""
    complaint = complaint_service.get_complaint_by_case_id(
        db=db,
        case_id=case_id,
        current_user_id=current_user.id,
        user_role=current_user.role,
    )

    analysis = await complaint_ai_service.analyze_and_save(db=db, complaint_id=complaint.id)
    if not analysis:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to run AI analysis.")

    return analysis

@router.get("/{case_id}/related", response_model=list[RelatedCaseSchema])
async def get_related_complaints(
    case_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Discover potentially related campus complaints using semantic similarity."""
    target_complaint = complaint_service.get_complaint_by_case_id(
        db=db,
        case_id=case_id,
        current_user_id=current_user.id,
        user_role=current_user.role,
    )

    # For students, only compare against all cases to show relationship signals (or student's cases)
    # The comparison finds similarity without exposing private student records
    all_complaints = db.query(Complaint).all()
    related = find_related_complaints(target=target_complaint, all_complaints=all_complaints)
    return related

@router.post("/{case_id}/evidence", response_model=list[EvidenceResponse])
async def upload_case_evidence(
    case_id: str,
    files: list[UploadFile] = File(...),
    current_user: User = Depends(require_role("student")),
    db: Session = Depends(get_db),
):
    """Upload one or more evidence files attached to a case."""
    complaint = complaint_service.get_complaint_by_case_id(
        db=db,
        case_id=case_id,
        current_user_id=current_user.id,
        user_role=current_user.role,
    )

    uploaded_evidence = []
    for file in files:
        evidence = await complaint_service.save_evidence_file(db=db, complaint=complaint, file=file)
        uploaded_evidence.append(evidence)

    return uploaded_evidence

@router.get("/{case_id}/evidence/{evidence_id}/download")
async def download_evidence(
    case_id: str,
    evidence_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Download/view an evidence file with permission check."""
    complaint = complaint_service.get_complaint_by_case_id(
        db=db,
        case_id=case_id,
        current_user_id=current_user.id,
        user_role=current_user.role,
    )

    evidence = db.query(Evidence).filter(
        Evidence.id == evidence_id,
        Evidence.complaint_id == complaint.id,
    ).first()

    if not evidence or not os.path.exists(evidence.storage_path):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Evidence file not found.")

    return FileResponse(
        path=evidence.storage_path,
        media_type=evidence.file_type,
        filename=evidence.file_name,
    )
