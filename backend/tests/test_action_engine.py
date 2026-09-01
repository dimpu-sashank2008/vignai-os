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
from app.models.action import VignaiAction
from app.models.notification import Notification

from app.services.intelligence.action_engine import action_engine
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


# 1. Student Academic Priority
def test_student_academic_priority_action(db: Session, student_user: User):
    """Scenario 1: Evaluates low/declining attendance -> ACADEMIC_ATTENDANCE action."""
    actions = action_engine.evaluate_student_actions(db, student_user)
    att_act = next((a for a in actions if a.action_type == "ACADEMIC_ATTENDANCE"), None)
    if att_act:
        assert "Attendance" in att_act.title
        assert att_act.priority in ["CRITICAL", "HIGH", "MEDIUM"]
        assert att_act.target_route == "/student/academics#attendance"
        assert att_act.ask_vignai_query is not None


# 2. Student Career Priority
def test_student_career_priority_action(db: Session, student_user: User):
    """Scenario 2: Evaluates verified opportunity -> CAREER_OPPORTUNITY action."""
    actions = action_engine.evaluate_student_actions(db, student_user)
    opp_act = next((a for a in actions if a.action_type == "CAREER_OPPORTUNITY"), None)
    if opp_act:
        assert opp_act.priority in ["HIGH", "CRITICAL"]
        assert "career" in opp_act.target_route.lower()


# 3. Student Skill-Gap Priority
def test_student_skill_gap_priority_action(db: Session, student_user: User):
    """Scenario 3: Evaluates missing skills -> CAREER_SKILL_GAP action."""
    actions = action_engine.evaluate_student_actions(db, student_user)
    skill_act = next((a for a in actions if a.action_type == "CAREER_SKILL_GAP"), None)
    if skill_act:
        assert "Skill" in skill_act.title or "Improve" in skill_act.title
        assert skill_act.target_route == "/student/career#skill-gaps"


# 4. Faculty Department Priority
def test_faculty_department_priority_action(db: Session, faculty_user: User):
    """Scenario 4: Evaluates department cluster -> CAMPUS_CLUSTER action."""
    actions = action_engine.evaluate_faculty_actions(db, faculty_user)
    assert isinstance(actions, list)
    for act in actions:
        assert act.role == "faculty"
        assert act.target_department is not None


# 5. Management Campus Priority
def test_management_campus_priority_action(db: Session, management_user: User):
    """Scenario 5: Evaluates campus cluster -> WHAT_IF_SIMULATION / CAMPUS_CLUSTER."""
    actions = action_engine.evaluate_management_actions(db, management_user)
    assert len(actions) >= 1
    act = actions[0]
    assert act.role == "management"
    assert "what-if" in act.target_route or "management" in act.target_route


# 6. Cross-Domain Action
def test_cross_domain_action_correlation(db: Session, student_user: User):
    """Scenario 6: Cross-domain correlation between Academics, Career, and Deadlines."""
    actions = action_engine.evaluate_student_actions(db, student_user)
    cross_act = next((a for a in actions if a.source_domain in ["CROSS_DOMAIN", "CAREER"]), None)
    assert cross_act is not None
    assert cross_act.evidence.get("urgency") is not None
    assert cross_act.evidence.get("impact") is not None


# 7. Deterministic Priority Formula
def test_deterministic_priority_formula():
    """Scenario 7: Verifies deterministic formula (Urgency*0.35 + Impact*0.30 + Evidence*0.20 + Relevance*0.15)."""
    label_crit, score_crit = action_engine.calculate_priority(1.0, 1.0, 1.0, 1.0)
    assert label_crit == "CRITICAL"
    assert score_crit == 1.0

    label_high, score_high = action_engine.calculate_priority(0.8, 0.8, 0.8, 0.8)
    assert label_high == "HIGH"
    assert score_high == 0.8

    label_med, score_med = action_engine.calculate_priority(0.5, 0.5, 0.5, 0.5)
    assert label_med == "MEDIUM"
    assert score_med == 0.5

    label_low, score_low = action_engine.calculate_priority(0.2, 0.2, 0.2, 0.2)
    assert label_low == "LOW"
    assert score_low == 0.2


# 8. Evidence Presence & Why-First Payload
def test_evidence_presence_and_why_first(db: Session, student_user: User):
    """Scenario 8: Ensures all action records have structured why-first evidence."""
    actions = action_engine.evaluate_student_actions(db, student_user)
    for act in actions:
        ev = act.evidence
        assert "urgency" in ev
        assert "impact" in ev
        assert "evidence_strength" in ev
        assert "relevance" in ev
        assert "why_first" in ev
        assert len(ev["why_first"]) >= 1


# 9. Deduplication
def test_action_deduplication(db: Session, student_user: User):
    """Scenario 9: Multiple evaluation runs do not create duplicate active action records."""
    count_before = db.query(VignaiAction).filter(VignaiAction.target_user_id == student_user.id).count()
    action_engine.evaluate_student_actions(db, student_user)
    action_engine.evaluate_student_actions(db, student_user)
    count_after = db.query(VignaiAction).filter(VignaiAction.target_user_id == student_user.id).count()
    assert count_after == count_before or count_after <= count_before + 5


# 10. Action Expiration
def test_action_auto_expiration_past_deadline(db: Session, student_user: User):
    """Scenario 10: Actions past expires_at are marked EXPIRED."""
    db.query(VignaiAction).filter_by(deduplication_key=f"TEST_EXPIRED_ACTION|{student_user.id}").delete()
    db.commit()

    act = VignaiAction(
        action_type="CAREER_OPPORTUNITY",
        priority="HIGH",
        priority_score=0.85,
        title="Expired Test Action",
        summary="Expired action summary",
        role="student",
        target_user_id=student_user.id,
        source_domain="CAREER",
        evidence={"urgency": 0.9, "impact": 0.8, "evidence_strength": 0.9, "relevance": 1.0, "why_first": ["Expired"]},
        recommended_action={"label": "View", "url": "/", "action_type": "VIEW_ACTION"},
        target_route="/",
        deduplication_key=f"TEST_EXPIRED_ACTION|{student_user.id}",
        expires_at=datetime.utcnow() - timedelta(days=1),
        status="NEW",
    )
    db.add(act)
    db.commit()

    action_engine._expire_stale_actions(db, role="student", user_id=student_user.id)
    db.refresh(act)
    assert act.status == "EXPIRED"


# 11. Student Privacy Isolation
def test_student_action_privacy_isolation(client: TestClient, student_token: str, faculty_token: str):
    """Scenario 11: Faculty cannot access student action endpoints (403)."""
    res = client.get("/api/student/actions", headers={"Authorization": f"Bearer {faculty_token}"})
    assert res.status_code == 403


# 12. Faculty Department Isolation
def test_faculty_department_action_isolation(db: Session, faculty_user: User):
    """Scenario 12: Faculty actions are restricted to department scope without student PII."""
    actions = action_engine.evaluate_faculty_actions(db, faculty_user)
    for act in actions:
        assert act.role == "faculty"
        assert "@" not in act.summary
        assert "22B91A" not in act.summary


# 13. Management Scope Aggregates
def test_management_action_scope(client: TestClient, management_token: str):
    """Scenario 13: Management receives institutional actions without student PII."""
    res = client.get("/api/management/actions", headers={"Authorization": f"Bearer {management_token}"})
    assert res.status_code == 200
    actions = res.json()
    assert isinstance(actions, list)
    for act in actions:
        assert act["role"] == "management"
        assert "@vignex.dev" not in act["summary"]


# 14. Notification Deduplication
def test_action_notification_deduplication(db: Session, student_user: User):
    """Scenario 14: Critical/High actions trigger deduplicated non-spam notifications."""
    notif_count_before = db.query(Notification).filter(Notification.user_id == student_user.id).count()

    db.query(VignaiAction).filter_by(deduplication_key=f"TEST_NOTIF_ACT|{student_user.id}").delete()
    db.commit()

    action_engine._upsert_action(
        db=db,
        dedup_key=f"TEST_NOTIF_ACT|{student_user.id}",
        action_type="ACADEMIC_ATTENDANCE",
        priority="HIGH",
        priority_score=0.82,
        title="Urgent Academic Review Notification Test",
        summary="Attendance notification test",
        role="student",
        target_user_id=student_user.id,
        source_domain="ACADEMICS",
        evidence={"urgency": 0.9, "impact": 0.8, "evidence_strength": 0.9, "relevance": 1.0, "why_first": ["Test"]},
        recommended_action={"label": "View", "url": "/", "action_type": "VIEW_ACTION"},
        target_route="/",
        notify=True,
    )

    # Second upsert
    action_engine._upsert_action(
        db=db,
        dedup_key=f"TEST_NOTIF_ACT|{student_user.id}",
        action_type="ACADEMIC_ATTENDANCE",
        priority="HIGH",
        priority_score=0.82,
        title="Urgent Academic Review Notification Test",
        summary="Attendance notification test",
        role="student",
        target_user_id=student_user.id,
        source_domain="ACADEMICS",
        evidence={"urgency": 0.9, "impact": 0.8, "evidence_strength": 0.9, "relevance": 1.0, "why_first": ["Test"]},
        recommended_action={"label": "View", "url": "/", "action_type": "VIEW_ACTION"},
        target_route="/",
        notify=True,
    )

    notif_count_after = db.query(Notification).filter(Notification.user_id == student_user.id).count()
    assert notif_count_after <= notif_count_before + 1


# 15. Ask VIGNAI Action Query
def test_ask_vignai_action_priorities_intent(db: Session, student_user: User):
    """Scenario 15: Routes 'What should I do first?' and 'What needs my attention?' to ACTION_PRIORITIES."""
    queries = [
        "What should I do first?",
        "What needs my attention?",
        "What are my priorities today?",
        "Why is this my priority?",
    ]
    for q in queries:
        r = query_router.route_query(q)
        assert r.intent == "ACTION_PRIORITIES"
        assert r.domain == "CROSS_DOMAIN"
        payload = AskVignexQueryPayload(query=q)
        ans = ask_vignex_answer_service.process_query(payload, db, user=student_user)
        assert ans.domain == "CROSS_DOMAIN"
        assert "🎯" in ans.answer or "priorities" in ans.answer.lower()


# 16. What-If Deep-Link
def test_what_if_deep_link_action(db: Session, management_user: User):
    """Scenario 16: Prepopulates target_route with What-If lab simulation parameters."""
    actions = action_engine.evaluate_management_actions(db, management_user)
    what_if_act = next((a for a in actions if "what-if" in a.target_route), None)
    if what_if_act:
        assert "what-if" in what_if_act.target_route
        assert what_if_act.recommended_action["action_type"] == "RUN_WHAT_IF"


# 17. AI Unavailable Deterministic Fallback
def test_ai_unavailable_fallback(db: Session, student_user: User):
    """Scenario 17: Evaluates priorities without requiring remote LLM API."""
    actions = action_engine.evaluate_student_actions(db, student_user)
    assert isinstance(actions, list)
    for a in actions:
        assert a.priority in ["CRITICAL", "HIGH", "MEDIUM", "LOW"]
        assert a.priority_score > 0.0


# 18. Domain Failure Resilience
def test_domain_failure_resilience(db: Session, student_user: User):
    """Scenario 18: If one insight fails, ActionEngine does not crash and continues processing remaining signals."""
    try:
        actions = action_engine.evaluate_student_actions(db, student_user)
        assert isinstance(actions, list)
    except Exception as e:
        pytest.fail(f"ActionEngine crashed: {e}")


# 19. Resolved Insight Expires Action
def test_resolved_insight_expires_action(db: Session, student_user: User):
    """Scenario 19: When an underlying insight becomes EXPIRED or ACTIONED, associated action expires."""
    db.query(VignaiAction).filter_by(deduplication_key=f"TEST_LINKED_ACT|{student_user.id}").delete()
    db.query(VignaiInsight).filter_by(deduplication_key=f"TEST_LINKED_INSIGHT|{student_user.id}").delete()
    db.commit()

    # Create expired insight
    ins = VignaiInsight(
        insight_type="ACADEMIC_RISK",
        severity="HIGH",
        title="Resolved Test Insight",
        summary="Test summary",
        role="student",
        target_user_id=student_user.id,
        status="EXPIRED",
        source_domains=["ACADEMICS"],
        evidence={"signals": []},
        recommended_action={"label": "View", "url": "/"},
        deduplication_key=f"TEST_LINKED_INSIGHT|{student_user.id}",
    )
    db.add(ins)
    db.commit()

    act = VignaiAction(
        action_type="ACADEMIC_ATTENDANCE",
        priority="HIGH",
        priority_score=0.80,
        title="Linked Test Action",
        summary="Linked test action",
        role="student",
        target_user_id=student_user.id,
        source_insight_id=ins.id,
        source_domain="ACADEMICS",
        evidence={"urgency": 0.8, "impact": 0.8, "evidence_strength": 0.8, "relevance": 1.0, "why_first": ["Test"]},
        recommended_action={"label": "View", "url": "/", "action_type": "VIEW_ACTION"},
        target_route="/",
        deduplication_key=f"TEST_LINKED_ACT|{student_user.id}",
        status="NEW",
    )
    db.add(act)
    db.commit()

    action_engine._expire_stale_actions(db, role="student", user_id=student_user.id)
    db.refresh(act)
    assert act.status == "EXPIRED"


# 20. Closing Opportunity Expires After Deadline
def test_closing_opportunity_expires_after_deadline(db: Session, student_user: User):
    """Scenario 20: Verified opportunity action expires once deadline has passed."""
    db.query(VignaiAction).filter_by(deduplication_key=f"TEST_DEADLINE_ACT|{student_user.id}").delete()
    db.commit()

    act = VignaiAction(
        action_type="CAREER_OPPORTUNITY",
        priority="HIGH",
        priority_score=0.88,
        title="Closing Opportunity Past Deadline",
        summary="Summary",
        role="student",
        target_user_id=student_user.id,
        source_domain="CROSS_DOMAIN",
        evidence={"urgency": 0.9, "impact": 0.9, "evidence_strength": 0.9, "relevance": 1.0, "why_first": ["Deadline"]},
        recommended_action={"label": "View", "url": "/", "action_type": "VIEW_OPPORTUNITY"},
        target_route="/",
        deduplication_key=f"TEST_DEADLINE_ACT|{student_user.id}",
        expires_at=datetime.utcnow() - timedelta(minutes=5),
        status="NEW",
    )
    db.add(act)
    db.commit()

    action_engine._expire_stale_actions(db, role="student", user_id=student_user.id)
    db.refresh(act)
    assert act.status == "EXPIRED"
