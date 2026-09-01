"""
Academic Intelligence Router — Phase 6A
Provides role-secured endpoints for:
- Students: own academic performance, attendance, assessments, assignments, timetable, insights.
- Faculty: class aggregates, attendance trends, assessment analytics for authorized subjects only.
- Management: institutional campus-wide aggregates and department trends (no student PII exposed).
"""
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import require_role
from app.models.user import User
from app.models.student import StudentProfile
from app.services.intelligence.academic_service import academic_service
from app.services.intelligence.academic_insight_service import academic_insight_service

router = APIRouter(tags=["Academic Intelligence"])


# ─────────────────────────────────────────────────────────────
# STUDENT ACADEMIC ENDPOINTS
# ─────────────────────────────────────────────────────────────

def _get_student_profile_or_404(db: Session, user: User) -> StudentProfile:
    student_profile = db.query(StudentProfile).filter_by(user_id=user.id).first()
    if not student_profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student academic profile not found",
        )
    return student_profile


@router.get("/student/academics/overview")
def get_student_academic_overview(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("student")),
):
    """Calculated student academic overview (attendance, assessment avg, pending workload)."""
    student_profile = _get_student_profile_or_404(db, current_user)
    return academic_service.get_student_overview(db, student_profile)


@router.get("/student/academics/subjects")
def get_student_academic_subjects(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("student")),
):
    """Enrolled subjects with per-subject attendance, last score, next assessment."""
    student_profile = _get_student_profile_or_404(db, current_user)
    return academic_service.get_student_subjects(db, student_profile)


@router.get("/student/academics/attendance")
def get_student_academic_attendance(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("student")),
):
    """Detailed attendance analytics by subject with trend detection."""
    student_profile = _get_student_profile_or_404(db, current_user)
    return academic_service.get_student_attendance(db, student_profile)


@router.get("/student/academics/assessments")
def get_student_academic_assessments(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("student")),
):
    """Completed results and scheduled upcoming assessments."""
    student_profile = _get_student_profile_or_404(db, current_user)
    return academic_service.get_student_assessments(db, student_profile)


@router.get("/student/academics/assignments")
def get_student_academic_assignments(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("student")),
):
    """Pending, overdue, submitted, and completed assignments."""
    student_profile = _get_student_profile_or_404(db, current_user)
    return academic_service.get_student_assignments(db, student_profile)


@router.get("/student/academics/timetable")
def get_student_academic_timetable(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("student")),
):
    """Weekly timetable entries with deterministic schedule overlap detection."""
    student_profile = _get_student_profile_or_404(db, current_user)
    return academic_service.get_student_timetable(db, student_profile)


@router.get("/student/academics/workload")
def get_student_academic_workload(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("student")),
):
    """Workload concentration metrics for next 3 and 7 days."""
    student_profile = _get_student_profile_or_404(db, current_user)
    return academic_service.get_student_workload(db, student_profile)


@router.get("/student/academics/insights")
def get_student_academic_insights(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("student")),
):
    """Structured, explainable AI-assisted insights for student."""
    student_profile = _get_student_profile_or_404(db, current_user)
    return academic_insight_service.get_student_insights(db, student_profile)


@router.post("/student/academics/ask")
def ask_student_academic_vignex(
    payload: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("student")),
):
    """Natural language Ask VIGNEX queries grounded strictly in authenticated student's academic records."""
    from app.services.ask_vignex.answer_service import ask_vignex_answer_service
    from app.services.ask_vignex.schemas import AskVignexQueryPayload
    query_payload = AskVignexQueryPayload(**payload)
    return ask_vignex_answer_service.process_query(
        payload=query_payload,
        db=db,
        user=current_user,
    )


# ─────────────────────────────────────────────────────────────
# FACULTY ACADEMIC ENDPOINTS
# ─────────────────────────────────────────────────────────────

@router.get("/faculty/academic-intelligence/overview")
def get_faculty_academic_overview(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("faculty")),
):
    """Aggregate metrics for subjects the authenticated faculty member teaches."""
    return academic_service.get_faculty_overview(db, current_user.id)


@router.get("/faculty/academic-intelligence/attendance")
def get_faculty_academic_attendance(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("faculty")),
):
    """Subject-wise attendance distribution and observed trends for faculty's classes."""
    return academic_service.get_faculty_attendance(db, current_user.id)


@router.get("/faculty/academic-intelligence/assessments")
def get_faculty_academic_assessments(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("faculty")),
):
    """Assessment activity and class averages for authorized subjects."""
    return academic_service.get_faculty_assessments(db, current_user.id)


@router.get("/faculty/academic-intelligence/insights")
def get_faculty_academic_insights(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("faculty")),
):
    """Structured AI interpretations for faculty's assigned courses."""
    return academic_insight_service.get_faculty_insights(db, current_user.id)


@router.get("/faculty/academic-intelligence/subjects/{subject_id}/overview")
def get_faculty_class_overview(
    subject_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("faculty")),
):
    """Detailed analytics for one authorized class. Returns 403 if unauthorized."""
    res = academic_service.get_faculty_class_overview(db, current_user.id, subject_id)
    if res is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to view academic data for this subject/class.",
        )
    return res


@router.get("/faculty/academic-intelligence/subjects/{subject_id}/timeline")
def get_faculty_class_timeline(
    subject_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("faculty")),
):
    """Activity timeline for an authorized class."""
    res = academic_service.get_faculty_class_timeline(db, current_user.id, subject_id)
    if res is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to view timeline data for this subject/class.",
        )
    return res


@router.get("/faculty/academic-intelligence/subjects/{subject_id}/insights")
def get_faculty_class_insights(
    subject_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("faculty")),
):
    """Structured explainable AI insights for one authorized class."""
    # Verify authorization
    subj = academic_service.check_faculty_subject_access(db, current_user.id, subject_id)
    if not subj:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to view insights for this subject/class.",
        )
    return academic_insight_service.get_faculty_class_insights(db, current_user.id, subject_id)


@router.get("/faculty/academic-intelligence/subjects/{subject_id}/related-cases")
def get_faculty_class_related_cases(
    subject_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("faculty")),
):
    """Corroborated department complaint cases related to the subject's department."""
    res = academic_service.get_faculty_class_related_cases(db, current_user.id, subject_id)
    if res is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to view related cases for this subject/class.",
        )
    return res


@router.post("/faculty/academic-intelligence/ask")
def ask_faculty_academic_vignex(
    payload: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("faculty")),
):
    """Natural language Ask VIGNEX queries grounded strictly in authorized faculty courses."""
    from app.services.ask_vignex.answer_service import ask_vignex_answer_service
    from app.services.ask_vignex.schemas import AskVignexQueryPayload
    query_payload = AskVignexQueryPayload(**payload)
    return ask_vignex_answer_service.process_query(
        payload=query_payload,
        db=db,
        user=current_user,
    )


# ─────────────────────────────────────────────────────────────
# MANAGEMENT ACADEMIC ENDPOINTS
# ─────────────────────────────────────────────────────────────

@router.get("/management/academic-intelligence/overview")
def get_management_academic_overview(
    window: str = Query("30d", pattern="^(7d|30d|90d|all)$"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("management")),
):
    """Campus-wide institutional academic summary (aggregated, no student PII)."""
    return academic_service.get_management_overview(db, window=window)


@router.get("/management/academic-intelligence/departments")
def get_management_academic_departments(
    window: str = Query("30d", pattern="^(7d|30d|90d|all)$"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("management")),
):
    """Department-level metrics and comparative breakdown."""
    return academic_service.get_management_departments_breakdown(db, window=window)


@router.get("/management/academic-intelligence/trends")
def get_management_academic_trends(
    window: str = Query("30d", pattern="^(7d|30d|90d|all)$"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("management")),
):
    """Department-level comparison trends (attendance, assignment completion)."""
    return academic_service.get_management_trends(db, window=window)


@router.get("/management/academic-intelligence/patterns")
def get_management_academic_patterns(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("management")),
):
    """Institutional emerging academic patterns and signals."""
    return academic_service.get_management_patterns(db)


@router.get("/management/academic-intelligence/insights")
def get_management_academic_insights(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("management")),
):
    """Institutional-level AI insights and cross-department patterns."""
    return academic_insight_service.get_management_insights(db)


@router.post("/management/academic-intelligence/ask")
def ask_management_academic_vignex(
    payload: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("management")),
):
    """Management Ask VIGNEX academic queries grounded in verified institutional records."""
    from app.services.ask_vignex.answer_service import ask_vignex_answer_service
    from app.services.ask_vignex.schemas import AskVignexQueryPayload
    query_payload = AskVignexQueryPayload(**payload)
    return ask_vignex_answer_service.process_query(
        payload=query_payload,
        db=db,
        user=current_user,
    )
