"""
VIGNAI OS — Notification Deep-Link & Target Navigation Test Suite
Validates structured notification destination metadata, role authorization,
source linkage (actions, insights, alerts), and API lifecycle.
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import SessionLocal
from app.models.notification import Notification
from app.models.user import User
from app.models.complaint import Complaint
from app.models.action import VignaiAction
from app.models.insight import VignaiInsight
from app.models.alert import VignaiAlert
from app.services.intelligence.alert_service import alert_service
from app.services.intelligence.action_engine import action_engine
from app.services.intelligence.insight_engine import insight_engine


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c


def get_auth_token(client: TestClient, email: str) -> str:
    res = client.post("/api/auth/login", json={"email": email, "password": "password123"})
    assert res.status_code == 200, f"Login failed for {email}: {res.text}"
    return res.json()["access_token"]


@pytest.fixture(scope="module")
def student_token(client):
    return get_auth_token(client, "student@vignex.dev")


@pytest.fixture(scope="module")
def faculty_token(client):
    return get_auth_token(client, "faculty@vignex.dev")


@pytest.fixture(scope="module")
def management_token(client):
    return get_auth_token(client, "management@vignex.dev")


# =====================================================================
# 1. DATA MODEL & SCHEMA TESTS
# =====================================================================

def test_notification_model_has_structured_target_fields():
    """Verify Notification model exposes all structured target destination fields."""
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.role == "student").first()
        notif = Notification(
            user_id=user.id,
            title="Test Structured Notification",
            message="Testing structured metadata schema.",
            notification_type="ACADEMIC",
            target_route="/student/academics",
            target_entity_type="ACADEMIC",
            target_entity_id="CS204",
            target_anchor="attendance-cs204",
            target_query=None,
            source_action_id=1,
            source_insight_id=2,
            source_alert_id=3,
        )
        db.add(notif)
        db.commit()
        db.refresh(notif)

        assert notif.id is not None
        assert notif.notification_type == "ACADEMIC"
        assert notif.target_route == "/student/academics"
        assert notif.target_entity_type == "ACADEMIC"
        assert notif.target_entity_id == "CS204"
        assert notif.target_anchor == "attendance-cs204"
        assert notif.source_action_id == 1
        assert notif.source_insight_id == 2
        assert notif.source_alert_id == 3

        # Cleanup
        db.delete(notif)
        db.commit()
    finally:
        db.close()


def test_api_notifications_returns_structured_target_fields(client, student_token):
    """Verify GET /api/notifications returns structured destination fields in response."""
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == "student@vignex.dev").first()
        notif = Notification(
            user_id=user.id,
            title="CS204 Attendance Advisory",
            message="Your attendance in CS204 is at 70%.",
            notification_type="ACADEMIC",
            target_route="/student/academics",
            target_entity_type="ACADEMIC",
            target_entity_id="CS204",
            target_anchor="attendance-cs204",
            is_read=False,
        )
        db.add(notif)
        db.commit()
        db.refresh(notif)
        notif_id = notif.id

        res = client.get("/api/notifications", headers={"Authorization": f"Bearer {student_token}"})
        assert res.status_code == 200
        items = res.json()
        target_item = next((item for item in items if item["id"] == notif_id), None)
        assert target_item is not None
        assert target_item["target_route"] == "/student/academics"
        assert target_item["target_entity_type"] == "ACADEMIC"
        assert target_item["target_entity_id"] == "CS204"
        assert target_item["target_anchor"] == "attendance-cs204"
        assert target_item["notification_type"] == "ACADEMIC"

        # Cleanup
        db.delete(notif)
        db.commit()
    finally:
        db.close()


# =====================================================================
# 2. ROLE-SPECIFIC NOTIFICATION TARGET TESTS
# =====================================================================

def test_student_complaint_submission_notification_target(client, student_token):
    """When a student files a complaint, notification must link to /student/complaints#case-{id}."""
    res = client.post(
        "/api/complaints",
        json={
            "description": "Wi-Fi in library 2nd floor is intermittently dropping connection during afternoon study hours.",
            "category": "INFRASTRUCTURE",
            "location": "Library 2nd Floor",
            "identity_protected": True,
        },
        headers={"Authorization": f"Bearer {student_token}"},
    )
    assert res.status_code == 201
    case_data = res.json()
    case_id = case_data["case_id"]

    # Check notification in database
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == "student@vignex.dev").first()
        notif = db.query(Notification).filter(
            Notification.user_id == user.id,
            Notification.title.contains(case_id),
        ).first()
        assert notif is not None
        assert notif.target_route == "/student/complaints"
        assert notif.target_entity_type == "CASE"
        assert notif.target_entity_id == case_id
        assert notif.target_anchor == f"case-{case_id}"
        assert notif.notification_type == "COMPLAINT"
    finally:
        db.close()


def test_career_closing_notification_target():
    """Verify career notification sets route /student/career and opportunity anchor."""
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.role == "student").first()
        notif = Notification(
            user_id=user.id,
            title="Closing Soon: AI Research Intern",
            message="AI Research Intern at TechCorp closes in 2 days (85% match).",
            notification_type="CAREER",
            target_route="/student/career",
            target_entity_type="CAREER",
            target_entity_id="101",
            target_anchor="opportunity-101",
        )
        db.add(notif)
        db.commit()
        db.refresh(notif)

        assert notif.target_route == "/student/career"
        assert notif.target_anchor == "opportunity-101"
        assert notif.target_entity_type == "CAREER"
        assert notif.target_entity_id == "101"

        db.delete(notif)
        db.commit()
    finally:
        db.close()


def test_faculty_case_notification_target():
    """Verify faculty case routing notification has route /faculty/cases/{case_id}."""
    db = SessionLocal()
    try:
        faculty = db.query(User).filter(User.role == "faculty").first()
        notif = Notification(
            user_id=faculty.id,
            title="New Case Assigned (CAS-2026-0099)",
            message="Case CAS-2026-0099 has been routed to your department.",
            notification_type="CASE",
            target_route="/faculty/cases/CAS-2026-0099",
            target_entity_type="CASE",
            target_entity_id="CAS-2026-0099",
            target_anchor="case-CAS-2026-0099",
        )
        db.add(notif)
        db.commit()
        db.refresh(notif)

        assert notif.target_route == "/faculty/cases/CAS-2026-0099"
        assert notif.target_entity_type == "CASE"
        assert notif.target_entity_id == "CAS-2026-0099"
        assert notif.target_anchor == "case-CAS-2026-0099"

        db.delete(notif)
        db.commit()
    finally:
        db.close()


def test_management_alert_notification_target():
    """Verify management alert notification targets /management/issues#group-{id}."""
    db = SessionLocal()
    try:
        mgmt = db.query(User).filter(User.role == "management").first()
        notif = Notification(
            user_id=mgmt.id,
            title="🔴 VIGNAI Priority Alert: Block A Wi-Fi",
            message="Block A Wi-Fi now has 5 related reports and an increasing trend.",
            notification_type="ALERT",
            target_route="/management/issues",
            target_entity_type="CASE_GROUP",
            target_entity_id="grp_wifi_block_a",
            target_anchor="group-grp_wifi_block_a",
            source_alert_id=55,
        )
        db.add(notif)
        db.commit()
        db.refresh(notif)

        assert notif.target_route == "/management/issues"
        assert notif.target_entity_type == "CASE_GROUP"
        assert notif.target_entity_id == "grp_wifi_block_a"
        assert notif.target_anchor == "group-grp_wifi_block_a"
        assert notif.source_alert_id == 55

        db.delete(notif)
        db.commit()
    finally:
        db.close()


def test_what_if_notification_target():
    """Verify What-If notification targets /management/what-if with location query parameter."""
    db = SessionLocal()
    try:
        mgmt = db.query(User).filter(User.role == "management").first()
        notif = Notification(
            user_id=mgmt.id,
            title="Simulation Opportunity: Block A Wi-Fi",
            message="VIGNAI recommends running a What-If analysis for Block A.",
            notification_type="WHAT_IF",
            target_route="/management/what-if",
            target_entity_type="WHAT_IF",
            target_entity_id="Block A",
            target_anchor="what-if-lab",
            target_query="location=Block%20A",
        )
        db.add(notif)
        db.commit()
        db.refresh(notif)

        assert notif.target_route == "/management/what-if"
        assert notif.target_entity_type == "WHAT_IF"
        assert notif.target_anchor == "what-if-lab"
        assert notif.target_query == "location=Block%20A"

        db.delete(notif)
        db.commit()
    finally:
        db.close()


def test_informational_notification_has_no_fake_destination():
    """Verify purely informational notifications (e.g. password changed) have no target route."""
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.role == "student").first()
        notif = Notification(
            user_id=user.id,
            title="Your password was changed successfully",
            message="If you did not perform this change, contact security immediately.",
            notification_type="INFORMATIONAL",
            target_route=None,
            target_entity_type=None,
            target_entity_id=None,
            target_anchor=None,
            target_query=None,
        )
        db.add(notif)
        db.commit()
        db.refresh(notif)

        assert notif.notification_type == "INFORMATIONAL"
        assert notif.target_route is None
        assert notif.target_anchor is None
        assert notif.target_entity_type is None

        db.delete(notif)
        db.commit()
    finally:
        db.close()


# =====================================================================
# 3. SOURCE LINKAGE INTEGRITY TESTS
# =====================================================================

def test_action_engine_notification_dispatch_linkage():
    """Verify action_engine populates source_action_id and structured targets."""
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.role == "student").first()
        test_act = VignaiAction(
            action_type="ACADEMIC_ATTENDANCE",
            priority="HIGH",
            priority_score=0.88,
            title="Review CS204 Attendance",
            summary="Attendance in CS204 is at 70%. Immediate review recommended.",
            role="student",
            target_user_id=user.id,
            source_domain="ACADEMICS",
            evidence={"signals": ["Attendance 70%"]},
            recommended_action={"label": "Review", "url": "/student/academics#attendance-cs204"},
            target_route="/student/academics#attendance-cs204",
            status="NEW",
            deduplication_key="TEST|ACTION|STUDENT|CS204|LINKAGE",
        )
        db.add(test_act)
        db.commit()
        db.refresh(test_act)

        # Dispatch notification using action_engine helper
        action_engine._dispatch_action_notification(db, test_act)

        notif = db.query(Notification).filter(
            Notification.user_id == user.id,
            Notification.source_action_id == test_act.id,
        ).first()

        assert notif is not None
        assert notif.notification_type == "ACTION"
        assert notif.source_action_id == test_act.id
        assert notif.target_route == "/student/academics"
        assert notif.target_anchor == "attendance-cs204"
        assert notif.target_entity_type == "ACTION"
        assert notif.target_entity_id == str(test_act.id)

        # Cleanup
        db.delete(notif)
        db.delete(test_act)
        db.commit()
    finally:
        db.close()


def test_insight_engine_notification_dispatch_linkage():
    """Verify insight_engine populates source_insight_id and structured targets."""
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.role == "student").first()
        test_ins = VignaiInsight(
            insight_type="ACADEMIC_RISK",
            severity="HIGH",
            title="Attendance Below Target in CS204",
            summary="Attendance is below 75% threshold in CS204.",
            role="student",
            target_user_id=user.id,
            status="NEW",
            source_domains=["ACADEMICS"],
            evidence={"signals": []},
            recommended_action={"label": "View Attendance", "url": "/student/academics#attendance"},
            deduplication_key="TEST|INSIGHT|STUDENT|CS204|LINKAGE",
        )
        db.add(test_ins)
        db.commit()
        db.refresh(test_ins)

        # Dispatch notification using insight_engine helper
        insight_engine._dispatch_insight_notification(db, test_ins)

        notif = db.query(Notification).filter(
            Notification.user_id == user.id,
            Notification.source_insight_id == test_ins.id,
        ).first()

        assert notif is not None
        assert notif.notification_type == "INSIGHT"
        assert notif.source_insight_id == test_ins.id
        assert notif.target_route == "/student/academics"
        assert notif.target_anchor == "attendance"
        assert notif.target_entity_type == "INSIGHT"
        assert notif.target_entity_id == str(test_ins.id)

        # Cleanup
        db.delete(notif)
        db.delete(test_ins)
        db.commit()
    finally:
        db.close()


# =====================================================================
# 4. MARK-READ API LIFECYCLE & RESILIENCE
# =====================================================================

def test_mark_single_notification_read_api(client, student_token):
    """Verify marking a notification as read preserves structured target destination."""
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == "student@vignex.dev").first()
        notif = Notification(
            user_id=user.id,
            title="Career Milestone Unlocked",
            message="Docker skill verified.",
            notification_type="CAREER",
            target_route="/student/career",
            target_anchor="skill-gaps",
            target_entity_type="CAREER",
            is_read=False,
        )
        db.add(notif)
        db.commit()
        db.refresh(notif)
        notif_id = notif.id

        # Mark as read
        res = client.post(f"/api/notifications/{notif_id}/read", headers={"Authorization": f"Bearer {student_token}"})
        assert res.status_code == 200
        data = res.json()
        assert data["is_read"] is True
        assert data["target_route"] == "/student/career"
        assert data["target_anchor"] == "skill-gaps"

        # Re-query db
        db.refresh(notif)
        assert notif.is_read is True
        assert notif.target_route == "/student/career"

        db.delete(notif)
        db.commit()
    finally:
        db.close()


def test_mark_non_existent_notification_read_returns_404(client, student_token):
    """Verify non-existent notification ID returns 404 without server errors."""
    res = client.post("/api/notifications/99999999/read", headers={"Authorization": f"Bearer {student_token}"})
    assert res.status_code == 404


def test_mark_all_read_preserves_targets(client, student_token):
    """Verify mark-all-as-read marks user notifications as read while preserving target metadata."""
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == "student@vignex.dev").first()
        notif = Notification(
            user_id=user.id,
            title="All Read Test Notification",
            message="Testing read all.",
            notification_type="ACADEMIC",
            target_route="/student/academics",
            target_anchor="overview",
            is_read=False,
        )
        db.add(notif)
        db.commit()
        db.refresh(notif)

        res = client.post("/api/notifications/read-all", headers={"Authorization": f"Bearer {student_token}"})
        assert res.status_code == 200

        db.refresh(notif)
        assert notif.is_read is True
        assert notif.target_route == "/student/academics"

        db.delete(notif)
        db.commit()
    finally:
        db.close()
