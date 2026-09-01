from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from app.database import get_db
from app.dependencies import require_role
from app.models.user import User
from app.models.faculty import FacultyProfile
from app.models.complaint import Complaint
from app.models.routing import ComplaintRouting
from app.models.routing_audit import RoutingAudit
from app.models.investigation_note import InvestigationNote
from app.models.notification import Notification
from app.schemas.management import (
    ManagementComplaintListResponse,
    ManagementComplaintDetailResponse,
    ReporterInfo,
    StatusUpdatePayload,
)
from app.schemas.routing import (
    InvestigationNoteCreatePayload,
    InvestigationNoteResponse,
    RoutingAuditResponse,
    FacultyCaseActionPayload,
)

router = APIRouter(prefix="/faculty", tags=["faculty"])

def check_faculty_case_access(db: Session, complaint: Complaint, faculty_user: User) -> bool:
    """Determine if a faculty user has legitimate authorized access to view a case.
    Enforces Critical Privacy Rule: High-sensitivity grievance allegations are strictly isolated.
    """
    # Check if case has restricted policy override (e.g. conduct/grievance)
    latest_audit = db.query(RoutingAudit).filter(
        RoutingAudit.complaint_id == complaint.id
    ).order_by(RoutingAudit.created_at.desc()).first()

    if latest_audit and latest_audit.policy_validation_result == "RESTRICTED_OVERRIDE":
        # Sensitive grievance allegations are strictly isolated from department faculty
        return False

    faculty_profile = faculty_user.faculty_profile
    dept_id = faculty_profile.department_id if faculty_profile else None
    dept_code = faculty_profile.department.code if (faculty_profile and faculty_profile.department) else None

    # Check routing records
    routing = db.query(ComplaintRouting).filter(
        ComplaintRouting.complaint_id == complaint.id,
        (
            (ComplaintRouting.recipient_user_id == faculty_user.id) |
            (ComplaintRouting.department_id == dept_id if dept_id else False) |
            (ComplaintRouting.department_code == dept_code if dept_code else False) |
            (ComplaintRouting.department_code == "CSE" if dept_code == "CS" else False)
        )
    ).first()

    return routing is not None

from app.schemas.grouping import RelatedCaseGroupDetailResponse
from app.services.intelligence.grouping_service import grouping_service
from app.services.intelligence.sorting_utils import sort_complaints_by_priority

@router.get("/department-groups", response_model=list[RelatedCaseGroupDetailResponse])
async def list_faculty_department_groups(
    status_filter: str | None = Query(None, alias="status"),
    priority_filter: str | None = Query(None, alias="priority"),
    search: str | None = Query(None),
    current_user: User = Depends(require_role("faculty")),
    db: Session = Depends(get_db),
):
    """List department-level campus issues clustered into RelatedCaseGroups, sorted deterministically by priority."""
    return grouping_service.get_faculty_department_groups(
        db=db,
        faculty_user=current_user,
        status_filter=status_filter,
        priority_filter=priority_filter,
        search=search,
    )

@router.get("/cases", response_model=list[ManagementComplaintListResponse])
async def list_faculty_cases(
    scope: str | None = Query("all", description="all, my_cases, unassigned"),
    status_filter: str | None = Query(None, alias="status"),
    priority_filter: str | None = Query(None, alias="priority"),
    search: str | None = Query(None),
    current_user: User = Depends(require_role("faculty")),
    db: Session = Depends(get_db),
):
    """List complaints in the faculty member's actionable queue, sorted by priority."""
    all_complaints = db.query(Complaint).order_by(Complaint.created_at.desc()).all()
    authorized_cases = [c for c in all_complaints if check_faculty_case_access(db, c, current_user)]

    if scope == "my_cases":
        authorized_cases = [
            c for c in authorized_cases
            if any(r.recipient_user_id == current_user.id for r in c.routings)
        ]

    # Filters
    if status_filter and status_filter.upper() != "ALL":
        authorized_cases = [c for c in authorized_cases if c.status.upper() == status_filter.upper()]

    if priority_filter and priority_filter.upper() != "ALL":
        authorized_cases = [c for c in authorized_cases if c.priority.upper() == priority_filter.upper()]

    if search and search.strip():
        term = search.strip().lower()
        authorized_cases = [
            c for c in authorized_cases
            if term in c.case_id.lower() or term in c.description.lower() or (c.location and term in c.location.lower())
        ]

    # Sort deterministically by priority (CRITICAL > HIGH > MEDIUM > LOW)
    authorized_cases = sort_complaints_by_priority(authorized_cases)

    response_items = []
    for c in authorized_cases:
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

@router.get("/department-issues", response_model=list[ManagementComplaintListResponse])
async def list_department_issues(
    category_filter: str | None = Query(None, alias="category"),
    status_filter: str | None = Query(None, alias="status"),
    priority_filter: str | None = Query(None, alias="priority"),
    search: str | None = Query(None),
    current_user: User = Depends(require_role("faculty")),
    db: Session = Depends(get_db),
):
    """List all authorized campus issues relevant to the faculty member's department, sorted by priority."""
    all_complaints = db.query(Complaint).order_by(Complaint.created_at.desc()).all()
    dept_cases = [c for c in all_complaints if check_faculty_case_access(db, c, current_user)]

    if category_filter and category_filter.upper() != "ALL":
        dept_cases = [
            c for c in dept_cases
            if (c.category and c.category.upper() == category_filter.upper()) or
               (c.ai_analysis and c.ai_analysis.category and c.ai_analysis.category.upper() == category_filter.upper())
        ]

    if status_filter and status_filter.upper() != "ALL":
        dept_cases = [c for c in dept_cases if c.status.upper() == status_filter.upper()]

    if priority_filter and priority_filter.upper() != "ALL":
        dept_cases = [c for c in dept_cases if c.priority.upper() == priority_filter.upper()]

    if search and search.strip():
        term = search.strip().lower()
        dept_cases = [
            c for c in dept_cases
            if term in c.case_id.lower() or term in c.description.lower() or (c.location and term in c.location.lower())
        ]

    # Sort deterministically by priority
    dept_cases = sort_complaints_by_priority(dept_cases)

    response_items = []
    for c in dept_cases:
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

@router.get("/department-issues/summary")
async def get_department_issues_summary(
    current_user: User = Depends(require_role("faculty")),
    db: Session = Depends(get_db),
):
    """Retrieve overview metrics for the faculty department issues overview."""
    all_complaints = db.query(Complaint).all()
    dept_cases = [c for c in all_complaints if check_faculty_case_access(db, c, current_user)]

    faculty_profile = current_user.faculty_profile
    dept_name = faculty_profile.department.name if (faculty_profile and faculty_profile.department) else "Computer Science & Engineering"
    dept_code = faculty_profile.department.code if (faculty_profile and faculty_profile.department) else "CSE"

    total = len(dept_cases)
    lab_issues = sum(
        1 for c in dept_cases
        if (c.category and "lab" in c.category.lower()) or (c.ai_analysis and c.ai_analysis.category and "lab" in c.ai_analysis.category.lower())
    )
    classroom_issues = sum(
        1 for c in dept_cases
        if (c.category and "class" in c.category.lower()) or (c.ai_analysis and c.ai_analysis.category and "class" in c.ai_analysis.category.lower())
    )
    pending_review = sum(1 for c in dept_cases if c.status.upper() in ["SUBMITTED", "UNDER_REVIEW"])
    in_progress = sum(1 for c in dept_cases if c.status.upper() == "IN_PROGRESS")
    resolved = sum(1 for c in dept_cases if c.status.upper() == "RESOLVED")

    return {
        "department_name": dept_name,
        "department_code": dept_code,
        "total_department_issues": total,
        "laboratory_issues": lab_issues,
        "classroom_issues": classroom_issues,
        "pending_review": pending_review,
        "in_progress": in_progress,
        "resolved": resolved,
    }

@router.get("/cases/summary")
async def get_faculty_case_summary(
    current_user: User = Depends(require_role("faculty")),
    db: Session = Depends(get_db),
):
    """Retrieve overview metrics for faculty personal investigation dashboard."""
    all_complaints = db.query(Complaint).all()
    my_cases = [c for c in all_complaints if check_faculty_case_access(db, c, current_user)]

    total = len(my_cases)
    pending_review = sum(1 for c in my_cases if c.status.upper() in ["SUBMITTED", "UNDER_REVIEW"])
    in_progress = sum(1 for c in my_cases if c.status.upper() == "IN_PROGRESS")
    resolved = sum(1 for c in my_cases if c.status.upper() == "RESOLVED")
    high_priority = sum(1 for c in my_cases if c.priority.upper() in ["HIGH", "CRITICAL"])

    return {
        "total_assigned": total,
        "pending_review": pending_review,
        "in_progress": in_progress,
        "resolved": resolved,
        "high_priority": high_priority,
    }

@router.get("/cases/{case_id}", response_model=ManagementComplaintDetailResponse)
async def get_faculty_case_detail(
    case_id: str,
    current_user: User = Depends(require_role("faculty")),
    db: Session = Depends(get_db),
):
    """Retrieve full details of an authorized complaint for faculty investigation."""
    complaint = db.query(Complaint).filter(Complaint.case_id == case_id).first()
    if not complaint:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Case {case_id} not found.")

    if not check_faculty_case_access(db, complaint, current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access restricted: This case is not routed to your department or is confidential.",
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
        created_at=complaint.created_at,
        updated_at=complaint.updated_at,
    )

@router.post("/cases/{case_id}/accept", response_model=ManagementComplaintDetailResponse)
async def accept_case(
    case_id: str,
    current_user: User = Depends(require_role("faculty")),
    db: Session = Depends(get_db),
):
    """Accept an assigned case and transition status to Under Review."""
    complaint = db.query(Complaint).filter(Complaint.case_id == case_id).first()
    if not complaint or not check_faculty_case_access(db, complaint, current_user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Unauthorized access.")

    # Update routing entry assignment status
    routing = db.query(ComplaintRouting).filter(
        ComplaintRouting.complaint_id == complaint.id,
        ComplaintRouting.role == "faculty"
    ).first()
    if routing:
        routing.assignment_status = "ACCEPTED"
        routing.recipient_user_id = current_user.id

    if complaint.status == "SUBMITTED":
        complaint.status = "UNDER_REVIEW"

    # Add Action Note
    note = InvestigationNote(
        complaint_id=complaint.id,
        author_user_id=current_user.id,
        author_role="faculty",
        author_email=current_user.email,
        note_type="ACTION",
        content="Case accepted by departmental faculty investigator.",
        is_visible_to_student=False,
    )
    db.add(note)

    # Notify student
    notif = Notification(
        user_id=complaint.student_id,
        title=f"Case Update ({complaint.case_id})",
        message=f"Your case {complaint.case_id} has been accepted by faculty and is now Under Review.",
        notification_type="COMPLAINT",
        target_route="/student/complaints",
        target_entity_type="CASE",
        target_entity_id=complaint.case_id,
        target_anchor=f"case-{complaint.case_id}",
    )
    db.add(notif)
    db.commit()

    return await get_faculty_case_detail(case_id=case_id, current_user=current_user, db=db)

@router.patch("/cases/{case_id}/status", response_model=ManagementComplaintDetailResponse)
async def update_faculty_case_status(
    case_id: str,
    payload: StatusUpdatePayload,
    current_user: User = Depends(require_role("faculty")),
    db: Session = Depends(get_db),
):
    """Update case status on the centralized complaint record and notify student."""
    complaint = db.query(Complaint).filter(Complaint.case_id == case_id).first()
    if not complaint or not check_faculty_case_access(db, complaint, current_user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Unauthorized access.")

    target_status = payload.status.upper()
    complaint.status = target_status

    # Record action note
    note_content = f"Status updated to {target_status} by faculty."
    if payload.notes:
        note_content += f" Note: {payload.notes.strip()}"

    note = InvestigationNote(
        complaint_id=complaint.id,
        author_user_id=current_user.id,
        author_role="faculty",
        author_email=current_user.email,
        note_type="ACTION",
        content=note_content,
        is_visible_to_student=False,
    )
    db.add(note)

    # Notify Student
    status_label = target_status.replace("_", " ").title()
    notif = Notification(
        user_id=complaint.student_id,
        title=f"Case Status Updated ({complaint.case_id})",
        message=f"Your case {complaint.case_id} is now {status_label}.",
        notification_type="COMPLAINT",
        target_route="/student/complaints",
        target_entity_type="CASE",
        target_entity_id=complaint.case_id,
        target_anchor=f"case-{complaint.case_id}",
    )
    db.add(notif)
    db.commit()

    return await get_faculty_case_detail(case_id=case_id, current_user=current_user, db=db)

@router.post("/cases/{case_id}/notes", response_model=InvestigationNoteResponse)
async def add_investigation_note(
    case_id: str,
    payload: InvestigationNoteCreatePayload,
    current_user: User = Depends(require_role("faculty")),
    db: Session = Depends(get_db),
):
    """Add a staff-internal investigation note (strictly concealed from students)."""
    complaint = db.query(Complaint).filter(Complaint.case_id == case_id).first()
    if not complaint or not check_faculty_case_access(db, complaint, current_user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Unauthorized access.")

    note = InvestigationNote(
        complaint_id=complaint.id,
        author_user_id=current_user.id,
        author_role="faculty",
        author_email=current_user.email,
        note_type=payload.note_type.upper(),
        content=payload.content.strip(),
        is_visible_to_student=False,
    )
    db.add(note)
    db.commit()
    db.refresh(note)
    return note

@router.get("/cases/{case_id}/notes", response_model=list[InvestigationNoteResponse])
async def list_investigation_notes(
    case_id: str,
    current_user: User = Depends(require_role("faculty")),
    db: Session = Depends(get_db),
):
    """List investigation notes for an authorized case."""
    complaint = db.query(Complaint).filter(Complaint.case_id == case_id).first()
    if not complaint or not check_faculty_case_access(db, complaint, current_user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Unauthorized access.")

    return db.query(InvestigationNote).filter(
        InvestigationNote.complaint_id == complaint.id
    ).order_by(InvestigationNote.created_at.asc()).all()

@router.post("/cases/{case_id}/escalate")
async def escalate_case(
    case_id: str,
    reason: str = Query(..., min_length=5),
    current_user: User = Depends(require_role("faculty")),
    db: Session = Depends(get_db),
):
    """Escalate a case to campus management oversight."""
    complaint = db.query(Complaint).filter(Complaint.case_id == case_id).first()
    if not complaint or not check_faculty_case_access(db, complaint, current_user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Unauthorized access.")

    note = InvestigationNote(
        complaint_id=complaint.id,
        author_user_id=current_user.id,
        author_role="faculty",
        author_email=current_user.email,
        note_type="ESCALATION",
        content=f"Case escalated to Management. Reason: {reason.strip()}",
        is_visible_to_student=False,
    )
    db.add(note)

    # Notify all management users
    management_users = db.query(User).filter(User.role == "management").all()
    for mgmt in management_users:
        notif = Notification(
            user_id=mgmt.id,
            title=f"Case Escalated ({complaint.case_id})",
            message=f"Faculty {current_user.email} escalated case {complaint.case_id}: {reason.strip()}",
            notification_type="CASE",
            target_route=f"/management/cases/{complaint.case_id}",
            target_entity_type="CASE",
            target_entity_id=complaint.case_id,
            target_anchor=f"case-{complaint.case_id}",
        )
        db.add(notif)

    db.commit()
    return {"status": "ok", "message": "Case escalated to management successfully."}

@router.post("/cases/{case_id}/request-info")
async def request_additional_info(
    case_id: str,
    query_text: str = Query(..., min_length=5),
    current_user: User = Depends(require_role("faculty")),
    db: Session = Depends(get_db),
):
    """Request additional clarifying information from the student reporter."""
    complaint = db.query(Complaint).filter(Complaint.case_id == case_id).first()
    if not complaint or not check_faculty_case_access(db, complaint, current_user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Unauthorized access.")

    # Record public student query note
    note = InvestigationNote(
        complaint_id=complaint.id,
        author_user_id=current_user.id,
        author_role="faculty",
        author_email=current_user.email,
        note_type="STUDENT_QUERY",
        content=f"Information Request: {query_text.strip()}",
        is_visible_to_student=True,
    )
    db.add(note)

    # Notify student
    notif = Notification(
        user_id=complaint.student_id,
        title=f"Additional Information Requested ({complaint.case_id})",
        message=f"Faculty investigator requested details for case {complaint.case_id}: {query_text.strip()}",
        notification_type="COMPLAINT",
        target_route="/student/complaints",
        target_entity_type="CASE",
        target_entity_id=complaint.case_id,
        target_anchor=f"case-{complaint.case_id}",
    )
    db.add(notif)
    db.commit()
    return {"status": "ok", "message": "Information request dispatched to student."}

# -------------------------------------------------------------
# Phase 5: Faculty Feedback & Concern Intelligence Endpoints
# -------------------------------------------------------------
class FacultyResponsePayload(BaseModel):
    response_text: str = Field(..., min_length=5, description="Formal faculty response statement")

@router.get("/feedback/overview")
async def get_faculty_feedback_overview(
    current_user: User = Depends(require_role("faculty")),
    db: Session = Depends(get_db),
):
    """Retrieve authentic concern counts, thematic grouping, and trends for authorized faculty."""
    from app.services.intelligence.faculty_intelligence import faculty_intelligence_service
    return faculty_intelligence_service.get_faculty_feedback_overview(db=db, faculty_user=current_user)

@router.get("/feedback/concerns", response_model=list[ManagementComplaintListResponse])
async def list_faculty_feedback_concerns(
    category_filter: str | None = Query(None, alias="category"),
    status_filter: str | None = Query(None, alias="status"),
    search: str | None = Query(None),
    current_user: User = Depends(require_role("faculty")),
    db: Session = Depends(get_db),
):
    """List accessible feedback and concern cases with strict identity protection."""
    all_complaints = db.query(Complaint).order_by(Complaint.created_at.desc()).all()
    authorized_cases = [c for c in all_complaints if check_faculty_case_access(db, c, current_user)]

    if category_filter and category_filter.upper() != "ALL":
        authorized_cases = [
            c for c in authorized_cases
            if (c.category and c.category.upper() == category_filter.upper()) or
               (c.ai_analysis and c.ai_analysis.category and c.ai_analysis.category.upper() == category_filter.upper())
        ]

    if status_filter and status_filter.upper() != "ALL":
        authorized_cases = [c for c in authorized_cases if c.status.upper() == status_filter.upper()]

    if search and search.strip():
        term = search.strip().lower()
        authorized_cases = [
            c for c in authorized_cases
            if term in c.case_id.lower() or term in c.description.lower() or (c.location and term in c.location.lower())
        ]

    response_items = []
    for c in authorized_cases:
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

@router.post("/cases/{case_id}/response", response_model=InvestigationNoteResponse)
async def submit_faculty_formal_response(
    case_id: str,
    payload: FacultyResponsePayload,
    current_user: User = Depends(require_role("faculty")),
    db: Session = Depends(get_db),
):
    """Submit a formal faculty response to an authorized case.
    Does not allow modifying original complaints, evidence, or reporter identity.
    """
    complaint = db.query(Complaint).filter(Complaint.case_id == case_id).first()
    if not complaint or not check_faculty_case_access(db, complaint, current_user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Unauthorized access.")

    # Record formal faculty response as an immutable InvestigationNote
    note = InvestigationNote(
        complaint_id=complaint.id,
        author_user_id=current_user.id,
        author_role="faculty",
        author_email=current_user.email,
        note_type="FACULTY_RESPONSE",
        content=f"Formal Faculty Response: {payload.response_text.strip()}",
        is_visible_to_student=True,
    )
    db.add(note)

    # If case was under review, advance to IN_PROGRESS
    if complaint.status in ["SUBMITTED", "UNDER_REVIEW"]:
        complaint.status = "IN_PROGRESS"

    # Notify student
    notif = Notification(
        user_id=complaint.student_id,
        title=f"Faculty Response Submitted ({complaint.case_id})",
        message=f"Faculty submitted a formal response for case {complaint.case_id}.",
        notification_type="COMPLAINT",
        target_route="/student/complaints",
        target_entity_type="CASE",
        target_entity_id=complaint.case_id,
        target_anchor=f"case-{complaint.case_id}",
    )
    db.add(notif)
    db.commit()
    db.refresh(note)

    return InvestigationNoteResponse(
        id=note.id,
        complaint_id=note.complaint_id,
        author_user_id=note.author_user_id,
        author_role=note.author_role,
        author_email=note.author_email,
        note_type=note.note_type,
        content=note.content,
        is_visible_to_student=note.is_visible_to_student,
        created_at=note.created_at,
    )

