"""
Tests for Phase 6B: Student Academic Intelligence & Ask VIGNEX Integration.
Verifies student academic queries, domain isolation, deterministic calculations, and safety rules.
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import SessionLocal
from app.models.user import User


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
def management_token(client):
    return get_auth_token(client, "management@vignex.dev")


# ─────────────────────────────────────────────────────────────
# 1. STUDENT ASK VIGNEX ACADEMIC INTENTS
# ─────────────────────────────────────────────────────────────

def test_ask_vignex_student_attendance_intent(client, student_token):
    headers = {"Authorization": f"Bearer {student_token}"}
    res = client.post(
        "/api/student/academics/ask",
        json={"query": "How is my attendance?"},
        headers=headers,
    )
    assert res.status_code == 200
    data = res.json()
    assert data["intent"] == "STUDENT_ATTENDANCE"
    assert data["query_mode"] == "VIGNEX_DATA"
    assert "Attendance Summary" in data["answer"] or "overall academic attendance" in data["answer"].lower()
    assert len(data["key_findings"]) >= 2
    assert data["provenance"]["data_source"] == "SYNTHETIC DEVELOPMENT DATA"


def test_ask_vignex_student_assessments_intent(client, student_token):
    headers = {"Authorization": f"Bearer {student_token}"}
    res = client.post(
        "/api/student/academics/ask",
        json={"query": "When is my next exam?"},
        headers=headers,
    )
    assert res.status_code == 200
    data = res.json()
    assert data["intent"] == "STUDENT_ASSESSMENTS"
    assert data["query_mode"] == "VIGNEX_DATA"
    assert "Assessment" in data["answer"] or "Upcoming" in data["answer"]


def test_ask_vignex_student_assignments_intent(client, student_token):
    headers = {"Authorization": f"Bearer {student_token}"}
    res = client.post(
        "/api/student/academics/ask",
        json={"query": "What's due this week?"},
        headers=headers,
    )
    assert res.status_code == 200
    data = res.json()
    assert data["intent"] == "STUDENT_ASSIGNMENTS"
    assert data["query_mode"] == "VIGNEX_DATA"
    assert "Assignment" in data["answer"] or "pending" in data["answer"].lower()


def test_ask_vignex_student_workload_intent(client, student_token):
    headers = {"Authorization": f"Bearer {student_token}"}
    res = client.post(
        "/api/student/academics/ask",
        json={"query": "What is my busiest academic day?"},
        headers=headers,
    )
    assert res.status_code == 200
    data = res.json()
    assert data["intent"] == "STUDENT_WORKLOAD"
    assert data["query_mode"] == "VIGNEX_DATA"
    assert "Workload" in data["answer"]


def test_ask_vignex_student_schedule_intent(client, student_token):
    headers = {"Authorization": f"Bearer {student_token}"}
    res = client.post(
        "/api/student/academics/ask",
        json={"query": "What classes do I have today?"},
        headers=headers,
    )
    assert res.status_code == 200
    data = res.json()
    assert data["intent"] == "STUDENT_SCHEDULE"
    assert data["query_mode"] == "VIGNEX_DATA"
    assert "Timetable" in data["answer"] or "Schedule" in data["answer"]


# ─────────────────────────────────────────────────────────────
# 2. DOMAIN ISOLATION TESTS
# ─────────────────────────────────────────────────────────────

def test_ask_vignex_general_knowledge_remains_isolated(client, student_token):
    """General STEM questions like photosynthesis must not query or return student academic data."""
    headers = {"Authorization": f"Bearer {student_token}"}
    res = client.post(
        "/api/student/academics/ask",
        json={"query": "What is photosynthesis?"},
        headers=headers,
    )
    assert res.status_code == 200
    data = res.json()
    assert data["intent"] == "GENERAL_KNOWLEDGE"
    assert data["query_mode"] == "GENERAL_KNOWLEDGE"
    assert "Photosynthesis" in data["answer"]
    # Verify no academic or complaint data is leaked
    assert "attendance" not in data["answer"].lower()
    assert "complaint" not in data["answer"].lower()


def test_ask_vignex_campus_complaint_query_isolation(client, management_token):
    """Campus problem query returns complaint data, not academic scores."""
    headers = {"Authorization": f"Bearer {management_token}"}
    res = client.post(
        "/api/management/ask-vignex",
        json={"query": "What are the biggest problems on campus?"},
        headers=headers,
    )
    assert res.status_code == 200
    data = res.json()
    assert data["query_mode"] == "VIGNEX_DATA"
    assert data["intent"] == "CAMPUS_OVERVIEW"


# ─────────────────────────────────────────────────────────────
# 3. DETERMINISTIC WORKLOAD & RESPONSIBLE AI
# ─────────────────────────────────────────────────────────────

def test_student_workload_window_calculation(client, student_token):
    headers = {"Authorization": f"Bearer {student_token}"}
    res = client.get("/api/student/academics/workload", headers=headers)
    assert res.status_code == 200
    data = res.json()
    w3 = data["next_3_days"]
    w7 = data["next_7_days"]
    assert w3["total_events"] == len(w3["events"])
    assert w7["total_events"] == len(w7["events"])
    assert w7["total_events"] >= w3["total_events"]


def test_student_academic_responsible_ai_no_punitive_labels(client, student_token):
    headers = {"Authorization": f"Bearer {student_token}"}
    res = client.get("/api/student/academics/insights", headers=headers)
    assert res.status_code == 200
    insights = res.json()
    forbidden = ["fail", "failing", "lazy", "poor student", "grade will be", "expelled"]
    for ins in insights:
        all_text = (ins["title"] + " " + ins["summary"] + " " + " ".join(ins.get("limitations", []))).lower()
        for f in forbidden:
            assert f not in all_text, f"Responsible AI violation: '{f}' in insight: {ins}"
