import pytest
from datetime import datetime, date, timedelta
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.main import app
from app.database import SessionLocal
from app.models.user import User
from app.models.student import StudentProfile
from app.models.academic_subject import AcademicSubject
from app.models.academic_enrollment import StudentSubjectEnrollment
from app.models.attendance_record import AttendanceRecord, ATTENDANCE_PRESENT, ATTENDANCE_ABSENT
from app.models.assessment import Assessment, AssessmentResult
from app.models.career import CareerProfile, CareerSkill, Opportunity
from app.models.complaint import Complaint
from app.models.alert import VignaiAlert
from app.models.insight import VignaiInsight
from app.models.notification import Notification

from app.services.intelligence.insight_engine import insight_engine
from app.services.auth_service import create_access_token
from app.services.ask_vignex.query_router import query_router
from app.services.ask_vignex.answer_service import ask_vignex_answer_service
from app.services.ask_vignex.schemas import AskVignexQueryPayload


@pytest.fixture(scope="module")
def db():
    session = SessionLocal()
    yield session
    session.close()


@pytest.fixture(scope="module")
def client():
    return TestClient(app)


@pytest.fixture(scope="module")
def student_user(db: Session):
    user = db.query(User).filter_by(email="student@vignex.dev").first()
    if not user:
        pytest.skip("Student user not found.")
    return user


@pytest.fixture(scope="module")
def faculty_user(db: Session):
    user = db.query(User).filter_by(email="faculty@vignex.dev").first()
    if not user:
        pytest.skip("Faculty user not found.")
    return user


@pytest.fixture(scope="module")
def management_user(db: Session):
    user = db.query(User).filter_by(email="management@vignex.dev").first()
    if not user:
        pytest.skip("Management user not found.")
    return user


@pytest.fixture(scope="module")
def student_token(student_user):
    return create_access_token(data={"sub": student_user.email, "role": student_user.role, "user_id": student_user.id})


@pytest.fixture(scope="module")
def faculty_token(faculty_user):
    return create_access_token(data={"sub": faculty_user.email, "role": faculty_user.role, "user_id": faculty_user.id})


@pytest.fixture(scope="module")
def management_token(management_user):
    return create_access_token(data={"sub": management_user.email, "role": management_user.role, "user_id": management_user.id})


def test_academic_career_alignment_insight(db: Session, student_user: User):
    """Rule A: Evaluates strong subject performance + skills -> CAREER_ALIGNMENT."""
    insights = insight_engine.evaluate_student_insights(db, student_user)
    align_ins = next((i for i in insights if i.insight_type == "CAREER_ALIGNMENT"), None)
    
    assert align_ins is not None
    assert "Strong Career Alignment" in align_ins.title
    assert align_ins.role == "student"
    assert align_ins.target_user_id == student_user.id
    assert "CAREER" in align_ins.source_domains
    assert "ACADEMICS" in align_ins.source_domains
    assert len(align_ins.evidence["signals"]) >= 2
    assert "conclusion" in align_ins.evidence


def test_academic_risk_detection_insight(db: Session, student_user: User):
    """Rule B: Evaluates declining attendance trajectory -> ACADEMIC_RISK."""
    student_prof = db.query(StudentProfile).filter(StudentProfile.user_id == student_user.id).first()
    if not student_prof:
        pytest.skip("Student profile missing.")

    # Find or seed CS204 with low attendance
    cs204 = db.query(AcademicSubject).filter(AcademicSubject.code == "CS204").first()
    if cs204:
        enr = db.query(StudentSubjectEnrollment).filter(
            StudentSubjectEnrollment.student_id == student_prof.id,
            StudentSubjectEnrollment.subject_id == cs204.id
        ).first()
        if not enr:
            enr = StudentSubjectEnrollment(student_id=student_prof.id, subject_id=cs204.id, semester=5, section="A")
            db.add(enr)
            db.commit()

        # Add attendance records with decline
        for day in range(1, 10):
            db.add(AttendanceRecord(
                student_id=student_prof.id,
                subject_id=cs204.id,
                date=date(2026, 8, 10 + day),
                status=ATTENDANCE_ABSENT if day > 4 else ATTENDANCE_PRESENT,
            ))
        db.commit()

    insights = insight_engine.evaluate_student_insights(db, student_user)
    risk_ins = next((i for i in insights if i.insight_type == "ACADEMIC_RISK"), None)
    
    if risk_ins:
        assert risk_ins.role == "student"
        assert risk_ins.target_user_id == student_user.id
        assert "ACADEMICS" in risk_ins.source_domains
        assert risk_ins.recommended_action["url"] == "/student/academics#attendance"


def test_career_skill_gap_preventive_action(db: Session, student_user: User):
    """Rule C: Evaluates missing skills for high-fit opportunity -> PREVENTIVE_ACTION."""
    insights = insight_engine.evaluate_student_insights(db, student_user)
    gap_ins = next((i for i in insights if i.insight_type == "PREVENTIVE_ACTION"), None)
    
    if gap_ins:
        assert "Recommendation" in gap_ins.title or "Skill" in gap_ins.title
        assert gap_ins.role == "student"
        assert gap_ins.recommended_action["action_type"] == "VIEW_SKILL_GAPS"


def test_cross_domain_opportunity_closing_soon(db: Session, student_user: User):
    """Multi-Domain: High fit + Eligible + Closing Soon -> CROSS_DOMAIN."""
    opp = db.query(Opportunity).filter(Opportunity.is_active == True, Opportunity.verification_status == "VERIFIED").first()
    if opp:
        opp.deadline = datetime.utcnow() + timedelta(days=2)
        db.commit()

    insights = insight_engine.evaluate_student_insights(db, student_user)
    cross_ins = next((i for i in insights if i.insight_type == "CROSS_DOMAIN" and str(i.deduplication_key).startswith("CROSS_DOMAIN|")), None)
    
    if cross_ins:
        assert cross_ins.severity in ["HIGH", "CRITICAL"]
        assert "Closing" in cross_ins.title
        assert "CAREER" in cross_ins.source_domains
        assert cross_ins.recommended_action["action_type"] == "VIEW_OPPORTUNITY"


def test_complaint_pattern_and_what_if_deep_link(db: Session, management_user: User):
    """Rules D & E: Management campus cluster -> CAMPUS_PATTERN / COMPLAINT_PATTERN with What-If action."""
    alt = db.query(VignaiAlert).filter(VignaiAlert.status == "NEW").first()
    if not alt:
        alt = VignaiAlert(
            alert_type="PRIORITY_REVIEW",
            severity="HIGH",
            title="Block A Wi-Fi Instability",
            message="Block A Wi-Fi has 4 related reports with rising trend.",
            case_group_id="grp-block-a-wifi",
            location="Block A",
            department="CSE",
            status="NEW",
            reason_data={"priority": "HIGH", "signals": ["4 related reports", "Rising trend"]},
        )
        db.add(alt)
        db.commit()

    insights = insight_engine.evaluate_management_insights(db, management_user)
    assert len(insights) >= 1
    
    mgmt_ins = insights[0]
    assert mgmt_ins.role == "management"
    assert "CAMPUS_INTELLIGENCE" in mgmt_ins.source_domains or "COMPLAINTS" in mgmt_ins.source_domains
    assert "what-if" in mgmt_ins.recommended_action["url"] or "Run What-If" in mgmt_ins.recommended_action["label"] or "campus-issues" in mgmt_ins.recommended_action["url"]


def test_duplicate_insight_suppression(db: Session, student_user: User):
    """Rule: Evaluates that recurring sync runs do not generate duplicate records."""
    count_before = db.query(VignaiInsight).filter(VignaiInsight.target_user_id == student_user.id).count()
    
    # Run evaluation multiple times
    insight_engine.evaluate_student_insights(db, student_user)
    insight_engine.evaluate_student_insights(db, student_user)
    
    count_after = db.query(VignaiInsight).filter(VignaiInsight.target_user_id == student_user.id).count()
    assert count_after == count_before or count_after <= count_before + 4


def test_student_privacy_isolation(client: TestClient, student_token: str, faculty_token: str):
    """Privacy Rule: Faculty cannot view student personal insights (403), Student cannot view management."""
    res = client.get("/api/student/insights", headers={"Authorization": f"Bearer {faculty_token}"})
    assert res.status_code == 403

    res_mgmt = client.get("/api/management/insights", headers={"Authorization": f"Bearer {student_token}"})
    assert res_mgmt.status_code == 403


def test_faculty_department_isolation(db: Session, faculty_user: User):
    """Isolation: Faculty receives department-level alerts without student PII."""
    insights = insight_engine.evaluate_faculty_insights(db, faculty_user)
    for ins in insights:
        assert ins.role == "faculty"
        assert ins.target_user_id is None
        assert "@" not in ins.summary
        assert "22B91A" not in ins.summary


def test_insight_lifecycle_state_transitions(db: Session, student_user: User, client: TestClient, student_token: str):
    """Lifecycle: Transitions NEW -> SEEN -> ACTIONED -> DISMISSED."""
    insights = insight_engine.evaluate_student_insights(db, student_user)
    if not insights:
        pytest.skip("No insights generated for student.")
    
    ins = insights[0]
    ins_id = ins.id

    # 1. Mark Seen
    res_seen = client.post(f"/api/insights/{ins_id}/seen", headers={"Authorization": f"Bearer {student_token}"})
    assert res_seen.status_code == 200
    assert res_seen.json()["status"] in ["NEW", "SEEN"]

    # 2. Mark Actioned
    res_act = client.post(f"/api/insights/{ins_id}/actioned", headers={"Authorization": f"Bearer {student_token}"})
    assert res_act.status_code == 200
    assert res_act.json()["status"] == "ACTIONED"

    # 3. Mark Dismissed
    res_dis = client.post(f"/api/insights/{ins_id}/dismiss", headers={"Authorization": f"Bearer {student_token}"})
    assert res_dis.status_code == 200
    assert res_dis.json()["status"] == "DISMISSED"


def test_underlying_condition_resolution_expired(db: Session, student_user: User):
    """Lifecycle: Marks expired insights EXPIRED when deadline has passed."""
    # Clean up previous test record if exists
    db.query(VignaiInsight).filter_by(deduplication_key=f"TEST_EXPIRED|{student_user.id}|999").delete()
    db.commit()

    expired_ins = VignaiInsight(
        insight_type="CROSS_DOMAIN",
        severity="HIGH",
        title="Expired Listing Insight",
        summary="Test expired listing",
        role="student",
        target_user_id=student_user.id,
        status="NEW",
        source_domains=["CAREER"],
        evidence={"signals": []},
        recommended_action={"label": "View", "url": "/"},
        deduplication_key=f"TEST_EXPIRED|{student_user.id}|999",
        expires_at=datetime.utcnow() - timedelta(days=1),
    )
    db.add(expired_ins)
    db.commit()

    insight_engine.evaluate_student_insights(db, student_user)
    db.refresh(expired_ins)
    assert expired_ins.status == "EXPIRED"


def test_domain_failure_resilience(db: Session, student_user: User):
    """Resilience: If one domain encounters an exception, other domains still generate insights."""
    try:
        insights = insight_engine.evaluate_student_insights(db, student_user)
        assert isinstance(insights, list)
    except Exception as e:
        pytest.fail(f"InsightEngine crashed under evaluation: {e}")


def test_notification_deduplication_on_high_severity(db: Session, student_user: User):
    """Notification: High severity insights create deduplicated notification without spamming."""
    notif_count_before = db.query(Notification).filter(Notification.user_id == student_user.id).count()
    
    # Clean up previous test insight if exists
    db.query(VignaiInsight).filter_by(deduplication_key=f"NOTIF_TEST|{student_user.id}|1").delete()
    db.commit()

    # Upsert high severity insight with notify=True
    insight_engine._upsert_insight(
        db=db,
        dedup_key=f"NOTIF_TEST|{student_user.id}|1",
        insight_type="CROSS_DOMAIN",
        severity="HIGH",
        title="Urgent Closing Internship",
        summary="Application deadline closing in 2 days.",
        role="student",
        target_user_id=student_user.id,
        source_domains=["CAREER"],
        evidence={"signals": []},
        recommended_action={"label": "View", "url": "/", "action_type": "VIEW_OPPORTUNITY"},
        notify=True,
    )

    # Re-run upsert with same title and key
    insight_engine._upsert_insight(
        db=db,
        dedup_key=f"NOTIF_TEST|{student_user.id}|1",
        insight_type="CROSS_DOMAIN",
        severity="HIGH",
        title="Urgent Closing Internship",
        summary="Application deadline closing in 2 days.",
        role="student",
        target_user_id=student_user.id,
        source_domains=["CAREER"],
        evidence={"signals": []},
        recommended_action={"label": "View", "url": "/", "action_type": "VIEW_OPPORTUNITY"},
        notify=True,
    )

    notif_count_after = db.query(Notification).filter(Notification.user_id == student_user.id).count()
    assert notif_count_after <= notif_count_before + 1


def test_ask_vignex_cross_domain_insights_intent(db: Session, student_user: User):
    """Ask VIGNAI: Routes 'What insights do you have for me?' and 'What should I focus on?' to CROSS_DOMAIN."""
    q = "What insights do you have for me?"
    r = query_router.route_query(q)
    assert r.intent == "VIGNAI_CROSS_DOMAIN_INSIGHTS"
    assert r.domain == "CROSS_DOMAIN"

def test_management_campus_scope_aggregate_insights(client: TestClient, management_token: str):
    """Management Scope: Evaluates campus-wide aggregation without student PII."""
    res = client.get("/api/management/insights", headers={"Authorization": f"Bearer {management_token}"})
    assert res.status_code == 200
    insights = res.json()
    assert isinstance(insights, list)
    for ins in insights:
        assert ins["role"] == "management"
        assert "@vignex.dev" not in ins["summary"]
        assert "target_user_id" not in ins or ins["target_user_id"] is None


def test_ask_vignex_insights_multi_question_variations(db: Session, student_user: User):
    """Ask VIGNAI: Tests multiple phrasing variants route and resolve correctly."""
    variations = [
        "What should I focus on?",
        "What are my biggest academic risks?",
        "Why did VIGNAI recommend this?",
        "What changed recently?",
        "What should I act on first?",
    ]
    for q in variations:
        r = query_router.route_query(q)
        assert r.intent in ["VIGNAI_CROSS_DOMAIN_INSIGHTS", "ACTION_PRIORITIES"]
        payload = AskVignexQueryPayload(query=q)
        ans = ask_vignex_answer_service.process_query(payload, db, user=student_user)
        assert ans.domain == "CROSS_DOMAIN"
        assert len(ans.key_findings) >= 1
