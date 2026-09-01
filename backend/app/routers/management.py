from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.dependencies import require_role
from app.models.user import User
from app.models.complaint import Complaint
from app.models.notification import Notification
from app.models.routing_audit import RoutingAudit
from app.models.investigation_note import InvestigationNote
from app.schemas.management import (
    ManagementComplaintListResponse,
    ManagementComplaintDetailResponse,
    ReporterInfo,
    StatusUpdatePayload,
    ManagementSummaryResponse,
)
from app.schemas.routing import InvestigationNoteCreatePayload, InvestigationNoteResponse
from app.services.ask_vignex.schemas import AskVignexQueryPayload, AskVignexAnswerResponse
from app.services.simulation.schemas import (
    SimulationRunRequest,
    SimulationComparisonResponse,
    SavedSimulationPayload,
    SavedSimulationResponse,
)

router = APIRouter(prefix="/management", tags=["management"])

VALID_STATUSES = ["SUBMITTED", "UNDER_REVIEW", "IN_PROGRESS", "RESOLVED", "CLOSED"]

def format_status_label(s: str) -> str:
    mapping = {
        "SUBMITTED": "Submitted",
        "UNDER_REVIEW": "Under Review",
        "IN_PROGRESS": "In Progress",
        "RESOLVED": "Resolved",
        "CLOSED": "Closed",
    }
    return mapping.get(s.upper(), s.title())

from app.schemas.grouping import RelatedCaseGroupDetailResponse, RelatedCaseGroupResponse
from app.services.intelligence.grouping_service import grouping_service
from app.services.intelligence.sorting_utils import sort_complaints_by_priority

@router.get("/case-groups", response_model=list[RelatedCaseGroupDetailResponse])
async def list_management_case_groups(
    status_filter: str | None = Query(None, alias="status"),
    category_filter: str | None = Query(None, alias="category"),
    priority_filter: str | None = Query(None, alias="priority"),
    department_filter: str | None = Query(None, alias="department"),
    search: str | None = Query(None),
    current_user: User = Depends(require_role("management")),
    db: Session = Depends(get_db),
):
    """Retrieve campus issues clustered into RelatedCaseGroups, sorted deterministically by priority."""
    return grouping_service.get_management_case_groups(
        db=db,
        status_filter=status_filter,
        category_filter=category_filter,
        priority_filter=priority_filter,
        department_filter=department_filter,
        search=search,
    )

@router.get("/complaints", response_model=list[ManagementComplaintListResponse])
async def list_management_complaints(
    status_filter: str | None = Query(None, alias="status"),
    category_filter: str | None = Query(None, alias="category"),
    priority_filter: str | None = Query(None, alias="priority"),
    department_filter: str | None = Query(None, alias="department"),
    sensitivity_filter: str | None = Query(None, alias="sensitivity"),
    search: str | None = Query(None),
    sort: str = Query("priority", description="priority, newest, oldest"),
    current_user: User = Depends(require_role("management")),
    db: Session = Depends(get_db),
):
    """Retrieve all campus complaints for Management console with server-side filters and priority sorting."""
    query = db.query(Complaint)

    if status_filter and status_filter.upper() != "ALL":
        query = query.filter(Complaint.status == status_filter.upper())

    if category_filter and category_filter.upper() != "ALL":
        query = query.filter(Complaint.category == category_filter)

    if priority_filter and priority_filter.upper() != "ALL":
        query = query.filter(Complaint.priority == priority_filter.upper())

    if search and search.strip():
        term = f"%{search.strip()}%"
        query = query.filter(
            (Complaint.case_id.ilike(term)) |
            (Complaint.title.ilike(term)) |
            (Complaint.description.ilike(term)) |
            (Complaint.location.ilike(term)) |
            (Complaint.category.ilike(term))
        )

    if sort == "oldest":
        query = query.order_by(Complaint.created_at.asc())
    else:
        query = query.order_by(Complaint.created_at.desc())

    complaints = query.all()

    # In-memory filter for department & sensitivity if specified
    if department_filter and department_filter.upper() != "ALL":
        complaints = [
            c for c in complaints
            if c.ai_analysis and (c.ai_analysis.department or "").upper() == department_filter.upper()
        ]

    if sensitivity_filter and sensitivity_filter.upper() != "ALL":
        complaints = [
            c for c in complaints
            if c.ai_analysis and (c.ai_analysis.sensitivity or "").upper() == sensitivity_filter.upper()
        ]

    # Apply deterministic backend priority sorting if sort == 'priority'
    if sort == "priority":
        complaints = sort_complaints_by_priority(complaints)

    response_items = []
    for c in complaints:
        is_protected = c.identity_protected
        reporter_visibility = "IDENTITY_PROTECTED" if is_protected else "VISIBLE"
        reporter_email = None if is_protected else (c.student.email if c.student else None)

        response_items.append(
            ManagementComplaintListResponse(
                id=c.id,
                case_id=c.case_id,
                title=c.title,
                description=c.description,
                location=c.location,
                category=c.category,
                status=c.status,
                priority=c.priority,
                identity_protected=c.identity_protected,
                reporter_visibility=reporter_visibility,
                reporter_email=reporter_email,
                evidence_count=len(c.evidences) if c.evidences else 0,
                ai_analysis=c.ai_analysis,
                created_at=c.created_at,
                updated_at=c.updated_at,
            )
        )

    return response_items

@router.get("/complaints/summary", response_model=ManagementSummaryResponse)
async def get_management_complaint_summary(
    current_user: User = Depends(require_role("management")),
    db: Session = Depends(get_db),
):
    """Retrieve campus-wide complaint metrics for Management dashboard."""
    complaints = db.query(Complaint).all()
    total = len(complaints)
    open_count = sum(1 for c in complaints if c.status.upper() == "SUBMITTED")
    under_review = sum(1 for c in complaints if c.status.upper() == "UNDER_REVIEW")
    in_progress = sum(1 for c in complaints if c.status.upper() == "IN_PROGRESS")
    resolved = sum(1 for c in complaints if c.status.upper() == "RESOLVED")
    closed = sum(1 for c in complaints if c.status.upper() == "CLOSED")

    return ManagementSummaryResponse(
        total=total,
        open=open_count,
        under_review=under_review,
        in_progress=in_progress,
        resolved=resolved,
        closed=closed,
    )

@router.get("/complaints/{case_id}", response_model=ManagementComplaintDetailResponse)
async def get_management_complaint_detail(
    case_id: str,
    current_user: User = Depends(require_role("management")),
    db: Session = Depends(get_db),
):
    """Retrieve full complaint details for management review with privacy enforcement and routing audit."""
    complaint = db.query(Complaint).filter(Complaint.case_id == case_id).first()
    if not complaint:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Case {case_id} not found."
        )

    if complaint.identity_protected:
        reporter = ReporterInfo(
            is_protected=True,
            visibility="IDENTITY_PROTECTED",
            email=None,
            enrollment_number=None,
            year_of_study=None,
        )
    else:
        student_user = complaint.student
        profile = student_user.student_profile if student_user else None
        reporter = ReporterInfo(
            is_protected=False,
            visibility="VISIBLE",
            email=student_user.email if student_user else None,
            enrollment_number=profile.enrollment_number if profile else None,
            year_of_study=profile.year_of_study if profile else None,
        )

    latest_audit = db.query(RoutingAudit).filter(
        RoutingAudit.complaint_id == complaint.id
    ).order_by(RoutingAudit.created_at.desc()).first()

    notes = db.query(InvestigationNote).filter(
        InvestigationNote.complaint_id == complaint.id
    ).order_by(InvestigationNote.created_at.asc()).all()

    return ManagementComplaintDetailResponse(
        id=complaint.id,
        case_id=complaint.case_id,
        title=complaint.title,
        description=complaint.description,
        location=complaint.location,
        category=complaint.category,
        status=complaint.status,
        priority=complaint.priority,
        identity_protected=complaint.identity_protected,
        reporter=reporter,
        evidence_count=len(complaint.evidences) if complaint.evidences else 0,
        evidences=complaint.evidences or [],
        ai_analysis=complaint.ai_analysis,
        routing_audit=latest_audit,
        investigation_notes=notes,
        created_at=complaint.created_at,
        updated_at=complaint.updated_at,
    )

@router.patch("/complaints/{case_id}/status", response_model=ManagementComplaintDetailResponse)
async def update_complaint_status(
    case_id: str,
    payload: StatusUpdatePayload,
    current_user: User = Depends(require_role("management")),
    db: Session = Depends(get_db),
):
    """Update case status and automatically notify the student on the same centralized record."""
    target_status = payload.status.upper()
    if target_status not in VALID_STATUSES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid status '{payload.status}'. Allowed: {', '.join(VALID_STATUSES)}",
        )

    complaint = db.query(Complaint).filter(Complaint.case_id == case_id).first()
    if not complaint:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Case {case_id} not found."
        )

    # Update status on the exact centralized record
    complaint.status = target_status

    # Record action note
    note_content = f"Status updated to {target_status} by Management."
    if payload.notes:
        note_content += f" Note: {payload.notes.strip()}"

    note = InvestigationNote(
        complaint_id=complaint.id,
        author_user_id=current_user.id,
        author_role="management",
        author_email=current_user.email,
        note_type="ACTION",
        content=note_content,
        is_visible_to_student=False,
    )
    db.add(note)

    # Send Notification to the student reporter
    status_label = format_status_label(target_status)
    notif_msg = f"Your case {complaint.case_id} status has been updated to {status_label}."
    if payload.notes:
        notif_msg += f" Note: {payload.notes.strip()}"

    notification = Notification(
        user_id=complaint.student_id,
        title=f"Case Status Updated ({complaint.case_id})",
        message=notif_msg,
        notification_type="COMPLAINT",
        target_route="/student/complaints",
        target_entity_type="CASE",
        target_entity_id=complaint.case_id,
        target_anchor=f"case-{complaint.case_id}",
    )
    db.add(notification)
    db.commit()

    return await get_management_complaint_detail(
        case_id=case_id,
        current_user=current_user,
        db=db,
    )

@router.post("/complaints/{case_id}/notes", response_model=InvestigationNoteResponse)
async def add_management_investigation_note(
    case_id: str,
    payload: InvestigationNoteCreatePayload,
    current_user: User = Depends(require_role("management")),
    db: Session = Depends(get_db),
):
    """Add a management investigation note."""
    complaint = db.query(Complaint).filter(Complaint.case_id == case_id).first()
    if not complaint:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Case {case_id} not found.")

    note = InvestigationNote(
        complaint_id=complaint.id,
        author_user_id=current_user.id,
        author_role="management",
        author_email=current_user.email,
        note_type=payload.note_type.upper(),
        content=payload.content.strip(),
        is_visible_to_student=False,
    )
    db.add(note)
    db.commit()
    db.refresh(note)
    return note

@router.post("/ask-vignex", response_model=AskVignexAnswerResponse)
async def ask_vignex_direct(
    payload: AskVignexQueryPayload,
    current_user: User = Depends(require_role("management")),
    db: Session = Depends(get_db),
):
    """Answer natural language administrative queries strictly grounded in SQLite database records."""
    from app.services.ask_vignex.answer_service import ask_vignex_answer_service
    return ask_vignex_answer_service.process_query(
        payload=payload,
        db=db,
        user=current_user,
    )

# -------------------------------------------------------------
# Phase 4D: What-If Lab Simulation Endpoints
# -------------------------------------------------------------
@router.post("/simulations/run", response_model=SimulationComparisonResponse)
async def run_management_simulation(
    payload: SimulationRunRequest,
    current_user: User = Depends(require_role("management")),
    db: Session = Depends(get_db),
):
    """Run deterministic what-if scenario simulations with multi-scenario comparison and AI trade-off analysis."""
    from app.services.simulation.engine import simulation_engine
    return simulation_engine.run_simulation(request=payload, db=db)

@router.post("/simulations", response_model=SavedSimulationResponse)
async def save_management_simulation(
    payload: SavedSimulationPayload,
    current_user: User = Depends(require_role("management")),
    db: Session = Depends(get_db),
):
    """Save a what-if scenario result for historical review."""
    from app.models.simulation import SavedSimulation
    sim = SavedSimulation(
        user_id=current_user.id,
        name=payload.name.strip(),
        scenario_type=payload.scenario_type.upper(),
        input_data=payload.input_data,
        result_data=payload.result_data,
    )
    db.add(sim)
    db.commit()
    db.refresh(sim)
    return sim

@router.get("/simulations", response_model=list[SavedSimulationResponse])
async def list_management_simulations(
    current_user: User = Depends(require_role("management")),
    db: Session = Depends(get_db),
):
    """List saved what-if scenario simulations."""
    from app.models.simulation import SavedSimulation
    return db.query(SavedSimulation).order_by(SavedSimulation.created_at.desc()).all()

@router.get("/simulations/{simulation_id}", response_model=SavedSimulationResponse)
async def get_management_simulation(
    simulation_id: int,
    current_user: User = Depends(require_role("management")),
    db: Session = Depends(get_db),
):
    """Get a single saved simulation by ID."""
    from app.models.simulation import SavedSimulation
    sim = db.query(SavedSimulation).filter(SavedSimulation.id == simulation_id).first()
    if not sim:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Simulation {simulation_id} not found.")
    return sim

@router.delete("/simulations/{simulation_id}")
async def delete_management_simulation(
    simulation_id: int,
    current_user: User = Depends(require_role("management")),
    db: Session = Depends(get_db),
):
    """Delete a saved simulation."""
    from app.models.simulation import SavedSimulation
    sim = db.query(SavedSimulation).filter(SavedSimulation.id == simulation_id).first()
    if not sim:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Simulation {simulation_id} not found.")
    db.delete(sim)
    db.commit()
    return {"message": "Simulation deleted successfully"}

# -------------------------------------------------------------
# Phase 5: Management Faculty Insights
# -------------------------------------------------------------
@router.get("/faculty-insights")
async def get_management_faculty_insights(
    current_user: User = Depends(require_role("management")),
    db: Session = Depends(get_db),
):
    """Retrieve aggregated campus-wide faculty concern patterns without student identity exposure."""
    from app.services.intelligence.faculty_intelligence import faculty_intelligence_service
    return faculty_intelligence_service.get_management_faculty_insights(db=db)

