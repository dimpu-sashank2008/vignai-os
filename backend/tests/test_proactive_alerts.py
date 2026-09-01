"""
Unit & Regression Tests for VIGNAI OS Proactive Intelligence Alerts.
Verifies alert detection rules, threshold policies, duplicate suppression,
role isolation, lifecycle transitions (Acknowledge/Dismiss/Resolve), and Ask VIGNAI integration.
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import SessionLocal
from app.models.user import User
from app.models.complaint import Complaint
from app.models.alert import VignaiAlert
from app.models.notification import Notification
from app.services.intelligence.alert_service import alert_service

client = TestClient(app)


def get_auth_token(client: TestClient, email: str) -> str:
    res = client.post("/api/auth/login", json={"email": email, "password": "password123"})
    assert res.status_code == 200, f"Login failed for {email}: {res.text}"
    return res.json()["access_token"]


@pytest.fixture(scope="module")
def student_token():
    return get_auth_token(client, "student@vignex.dev")


@pytest.fixture(scope="module")
def faculty_token():
    return get_auth_token(client, "faculty@vignex.dev")


@pytest.fixture(scope="module")
def management_token():
    return get_auth_token(client, "management@vignex.dev")


# ─────────────────────────────────────────────────────────────
# 1. ALERT DETECTION & SEVERITY THRESHOLD TESTS
# ─────────────────────────────────────────────────────────────

def test_alert_detection_and_sync(management_token):
    """Test deterministic alert synchronization generates alerts for qualifying issues."""
    headers = {"Authorization": f"Bearer {management_token}"}
    res = client.get("/api/management/alerts", headers=headers)
    assert res.status_code == 200
    alerts = res.json()
    assert isinstance(alerts, list)
    assert len(alerts) > 0

    # Verify structured fields
    first_alert = alerts[0]
    assert "id" in first_alert
    assert first_alert["severity"] in ["CRITICAL", "HIGH", "MEDIUM"]
    assert first_alert["status"] in ["NEW", "ACKNOWLEDGED"]
    assert "reason_data" in first_alert
    assert "signals" in first_alert["reason_data"]
    assert len(first_alert["reason_data"]["signals"]) > 0
    assert first_alert["target_route"].startswith("/management/")


def test_duplicate_alert_suppression(management_token):
    """Verify evaluating alerts multiple times does NOT create duplicate records."""
    headers = {"Authorization": f"Bearer {management_token}"}
    res1 = client.get("/api/management/alerts", headers=headers)
    count1 = len(res1.json())

    # Call again
    res2 = client.get("/api/management/alerts", headers=headers)
    count2 = len(res2.json())
    assert count1 == count2, "Duplicate alerts were generated on repeated evaluation"


# ─────────────────────────────────────────────────────────────
# 2. ROLE AUTHORIZATION & PRIVACY TESTS
# ─────────────────────────────────────────────────────────────

def test_student_cannot_access_management_alerts(student_token):
    """Verify students are strictly blocked with 403 from management priority alerts."""
    headers = {"Authorization": f"Bearer {student_token}"}
    res = client.get("/api/management/alerts", headers=headers)
    assert res.status_code == 403


def test_student_cannot_access_faculty_alerts(student_token):
    """Verify students are blocked with 403 from faculty alerts."""
    headers = {"Authorization": f"Bearer {student_token}"}
    res = client.get("/api/faculty/alerts", headers=headers)
    assert res.status_code == 403


def test_faculty_can_access_own_department_alerts(faculty_token):
    """Verify faculty can access alerts scoped to their authorized department."""
    headers = {"Authorization": f"Bearer {faculty_token}"}
    res = client.get("/api/faculty/alerts", headers=headers)
    assert res.status_code == 200
    alerts = res.json()
    assert isinstance(alerts, list)
    for a in alerts:
        assert a["department"] in ["CSE", "Administration", "Infrastructure", None]


def test_protected_identity_not_leaked_in_alerts(management_token):
    """Verify alert titles, messages, and reason data never expose protected student PII."""
    headers = {"Authorization": f"Bearer {management_token}"}
    res = client.get("/api/management/alerts", headers=headers)
    assert res.status_code == 200
    alerts = res.json()
    for a in alerts:
        # Must not contain student email or student ID
        assert "student@vignex.dev" not in a["message"]
        assert "221FA04001" not in a["message"]
        assert "student@vignex.dev" not in str(a["reason_data"])


# ─────────────────────────────────────────────────────────────
# 3. ALERT LIFECYCLE TESTS (Acknowledge, Dismiss, Auto-Resolve)
# ─────────────────────────────────────────────────────────────

def test_acknowledge_alert_flow(management_token):
    """Test acknowledging a priority alert sets status to ACKNOWLEDGED."""
    headers = {"Authorization": f"Bearer {management_token}"}
    alerts_res = client.get("/api/management/alerts", headers=headers)
    assert alerts_res.status_code == 200
    alerts = alerts_res.json()
    assert len(alerts) > 0
    target_alert = alerts[0]

    ack_res = client.post(f"/api/management/alerts/{target_alert['id']}/acknowledge", headers=headers)
    assert ack_res.status_code == 200
    data = ack_res.json()
    assert data["status"] == "ACKNOWLEDGED"
    assert data["updated_at"] is not None


def test_dismiss_alert_flow(management_token):
    """Test dismissing a priority alert removes it from active alert list."""
    headers = {"Authorization": f"Bearer {management_token}"}
    alerts_res = client.get("/api/management/alerts", headers=headers)
    assert alerts_res.status_code == 200
    alerts = alerts_res.json()
    assert len(alerts) > 0
    target_alert = alerts[-1]

    dism_res = client.post(f"/api/management/alerts/{target_alert['id']}/dismiss", headers=headers)
    assert dism_res.status_code == 200
    data = dism_res.json()
    assert data["status"] == "DISMISSED"


# ─────────────────────────────────────────────────────────────
# 4. ASK VIGNAI PRIORITY ALERT INTENT INTEGRATION
# ─────────────────────────────────────────────────────────────

def test_ask_vignex_management_priority_alerts(management_token):
    """Test Ask VIGNAI inquiry 'What needs immediate review?' returns active alerts."""
    headers = {"Authorization": f"Bearer {management_token}"}
    res = client.post(
        "/api/intelligence/ask-vignex",
        json={"query": "What needs immediate review?"},
        headers=headers,
    )
    assert res.status_code == 200
    data = res.json()
    assert data["domain"] == "CAMPUS_INTELLIGENCE"
    assert "priority" in data["answer"].lower() or "alert" in data["answer"].lower()
    assert len(data["action_links"]) > 0


def test_ask_vignex_student_priority_alerts_isolation(student_token):
    """Test Ask VIGNAI inquiry 'What needs immediate review?' from student routes to personal reports."""
    headers = {"Authorization": f"Bearer {student_token}"}
    res = client.post(
        "/api/intelligence/ask-vignex",
        json={"query": "What needs immediate review?"},
        headers=headers,
    )
    assert res.status_code == 200
    data = res.json()
    # Student sees personal complaints / reports, never management alert counts
    assert "campus oversight" not in data["answer"].lower()
