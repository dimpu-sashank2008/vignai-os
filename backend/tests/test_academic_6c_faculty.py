"""
Tests for Phase 6C: Faculty Academic Intelligence & Authorization.
Verifies class-level analytics, strict subject authorization (403), pattern detection,
AI insight schema, Responsible-AI safeguards, and Faculty Ask VIGNEX queries.
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import SessionLocal
from app.models.academic_subject import AcademicSubject


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c


def get_auth_token(client: TestClient, email: str) -> str:
    res = client.post("/api/auth/login", json={"email": email, "password": "password123"})
    assert res.status_code == 200, f"Login failed for {email}: {res.text}"
    return res.json()["access_token"]


@pytest.fixture(scope="module")
def faculty_token(client):
    return get_auth_token(client, "faculty@vignex.dev")


@pytest.fixture(scope="module")
def student_token(client):
    return get_auth_token(client, "student@vignex.dev")


@pytest.fixture(scope="module")
def management_token(client):
    return get_auth_token(client, "management@vignex.dev")


# ─────────────────────────────────────────────────────────────
# 1. AUTHORIZATION & ACCESS CONTROL TESTS
# ─────────────────────────────────────────────────────────────

def test_authorized_faculty_can_access_own_class_overview(client, faculty_token):
    """Faculty teaching CS201 (id=1) can access its detailed overview."""
    headers = {"Authorization": f"Bearer {faculty_token}"}
    res = client.get("/api/faculty/academic-intelligence/subjects/1/overview", headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert data["code"] == "CS201"
    assert "Data Structures" in data["name"]
    assert data["enrolled_count"] > 0
    assert "attendance" in data
    assert "assignments" in data
    assert "assessments" in data


def test_unauthorized_faculty_cannot_access_other_class(client, faculty_token):
    """Faculty NOT assigned to CS204 (id=4) or MA201 (id=5) receives 403 Forbidden."""
    headers = {"Authorization": f"Bearer {faculty_token}"}
    res = client.get("/api/faculty/academic-intelligence/subjects/4/overview", headers=headers)
    assert res.status_code == 403
    assert "not authorized" in res.json()["detail"].lower()

    res2 = client.get("/api/faculty/academic-intelligence/subjects/5/overview", headers=headers)
    assert res2.status_code == 403


def test_student_cannot_access_faculty_class_endpoints(client, student_token):
    """Student receives 403 on faculty class intelligence endpoints."""
    headers = {"Authorization": f"Bearer {student_token}"}
    res = client.get("/api/faculty/academic-intelligence/subjects/1/overview", headers=headers)
    assert res.status_code == 403


def test_faculty_timeline_and_related_cases_authorization(client, faculty_token):
    """Authorized faculty can fetch timeline and related cases for their subject."""
    headers = {"Authorization": f"Bearer {faculty_token}"}
    
    # Timeline
    t_res = client.get("/api/faculty/academic-intelligence/subjects/1/timeline", headers=headers)
    assert t_res.status_code == 200
    t_data = t_res.json()
    assert "weekly_classes" in t_data
    assert "timeline_events" in t_data

    # Related cases
    c_res = client.get("/api/faculty/academic-intelligence/subjects/1/related-cases", headers=headers)
    assert c_res.status_code == 200
    c_data = c_res.json()
    assert isinstance(c_data, list)


# ─────────────────────────────────────────────────────────────
# 2. DETERMINISTIC ANALYTICS ACCURACY
# ─────────────────────────────────────────────────────────────

def test_faculty_class_attendance_and_assignment_math(client, faculty_token):
    headers = {"Authorization": f"Bearer {faculty_token}"}
    res = client.get("/api/faculty/academic-intelligence/subjects/1/overview", headers=headers)
    assert res.status_code == 200
    data = res.json()

    att = data["attendance"]
    assert att["total"] == att["present"] + att["absent"] + att["od"]
    if att["total"] > 0:
        expected_pct = round((att["present"] + att["od"]) / att["total"] * 100, 1)
        assert att["percentage"] == expected_pct

    assign = data["assignments"]
    assert assign["total"] == assign["submitted"] + assign["pending"] + assign["overdue"]
    if assign["total"] > 0:
        expected_comp = round(assign["submitted"] / assign["total"] * 100, 1)
        assert assign["completion_rate"] == expected_comp


def test_faculty_class_assessments_math(client, faculty_token):
    headers = {"Authorization": f"Bearer {faculty_token}"}
    res = client.get("/api/faculty/academic-intelligence/subjects/1/overview", headers=headers)
    assert res.status_code == 200
    assess = res.json()["assessments"]
    assert assess["total_count"] == assess["upcoming_count"] + assess["completed_count"]
    for item in assess["items"]:
        if item["class_average_marks"] is not None:
            expected_pct = round(item["class_average_marks"] / item["max_marks"] * 100, 1)
            assert item["class_average_pct"] == expected_pct


# ─────────────────────────────────────────────────────────────
# 3. AI INSIGHTS & RESPONSIBLE-AI VALIDATION
# ─────────────────────────────────────────────────────────────

def test_faculty_class_ai_insights_schema_and_safety(client, faculty_token):
    headers = {"Authorization": f"Bearer {faculty_token}"}
    res = client.get("/api/faculty/academic-intelligence/subjects/1/insights", headers=headers)
    assert res.status_code == 200
    insights = res.json()
    assert len(insights) >= 1

    forbidden = ["lazy", "bad student", "failing", "poor teacher", "punish", "grade will be"]
    for ins in insights:
        assert "insight_type" in ins
        assert "title" in ins
        assert "summary" in ins
        assert "supporting_factors" in ins
        assert "limitations" in ins
        assert ins["confidence"] >= 0.5
        all_text = (ins["title"] + " " + ins["summary"]).lower()
        for f in forbidden:
            assert f not in all_text, f"Responsible AI violation: '{f}' found in insight: {ins}"


# ─────────────────────────────────────────────────────────────
# 4. FACULTY ASK VIGNEX INTENT TESTS
# ─────────────────────────────────────────────────────────────

def test_ask_vignex_faculty_attendance_trend_intent(client, faculty_token):
    headers = {"Authorization": f"Bearer {faculty_token}"}
    res = client.post(
        "/api/faculty/academic-intelligence/ask",
        json={"query": "What's the attendance trend in my Data Structures class?"},
        headers=headers,
    )
    assert res.status_code == 200
    data = res.json()
    assert data["intent"] == "FACULTY_CLASS_ATTENDANCE"
    assert data["query_mode"] == "VIGNEX_DATA"
    assert "Attendance" in data["answer"]


def test_ask_vignex_faculty_assignment_backlog_intent(client, faculty_token):
    headers = {"Authorization": f"Bearer {faculty_token}"}
    res = client.post(
        "/api/faculty/academic-intelligence/ask",
        json={"query": "Which of my classes has the highest assignment backlog?"},
        headers=headers,
    )
    assert res.status_code == 200
    data = res.json()
    assert data["intent"] == "FACULTY_ASSIGNMENT_BACKLOG"
    assert data["query_mode"] == "VIGNEX_DATA"
    assert "Assignment" in data["answer"]


def test_ask_vignex_faculty_upcoming_assessments_intent(client, faculty_token):
    headers = {"Authorization": f"Bearer {faculty_token}"}
    res = client.post(
        "/api/faculty/academic-intelligence/ask",
        json={"query": "What assessments are upcoming in my classes?"},
        headers=headers,
    )
    assert res.status_code == 200
    data = res.json()
    assert data["intent"] == "FACULTY_UPCOMING_ASSESSMENTS"
    assert data["query_mode"] == "VIGNEX_DATA"
    assert "Assessment" in data["answer"]


def test_ask_vignex_faculty_hybrid_complaints_query(client, faculty_token):
    headers = {"Authorization": f"Bearer {faculty_token}"}
    res = client.post(
        "/api/faculty/academic-intelligence/ask",
        json={"query": "Are assignment completion issues related to recent academic complaints?"},
        headers=headers,
    )
    assert res.status_code == 200
    data = res.json()
    assert data["intent"] == "FACULTY_HYBRID_COMPLAINTS"
    assert data["query_mode"] == "HYBRID"
    assert "Case" in data["answer"] or "complaint" in data["answer"].lower()
