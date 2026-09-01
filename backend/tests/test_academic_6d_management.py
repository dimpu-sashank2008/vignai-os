"""
Tests for Phase 6D: Management Academic Intelligence & Authorization.
Verifies institutional aggregate analytics, role security (students and faculty rejected with 403),
deterministic health calculation, department comparisons, pattern detection, AI insight schema,
Responsible-AI safeguards, and Management Ask VIGNEX integration (including cross-domain hybrid queries).
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import SessionLocal


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c


def get_auth_token(client: TestClient, email: str) -> str:
    res = client.post("/api/auth/login", json={"email": email, "password": "password123"})
    assert res.status_code == 200, f"Login failed for {email}: {res.text}"
    return res.json()["access_token"]


@pytest.fixture(scope="module")
def management_token(client):
    return get_auth_token(client, "management@vignex.dev")


@pytest.fixture(scope="module")
def faculty_token(client):
    return get_auth_token(client, "faculty@vignex.dev")


@pytest.fixture(scope="module")
def student_token(client):
    return get_auth_token(client, "student@vignex.dev")


# ─────────────────────────────────────────────────────────────
# 1. ACCESS CONTROL & ROLE SECURITY TESTS
# ─────────────────────────────────────────────────────────────

def test_management_can_access_all_academic_intelligence_endpoints(client, management_token):
    headers = {"Authorization": f"Bearer {management_token}"}
    
    # Overview
    ov_res = client.get("/api/management/academic-intelligence/overview", headers=headers)
    assert ov_res.status_code == 200
    ov_data = ov_res.json()
    assert "health_status" in ov_data
    assert ov_data["health_status"] in ["HEALTHY", "WATCH", "ELEVATED", "HIGH RISK"]
    assert ov_data["total_subjects"] > 0
    assert ov_data["total_departments"] > 0
    assert ov_data["overall_attendance_pct"] > 0

    # Departments
    dept_res = client.get("/api/management/academic-intelligence/departments", headers=headers)
    assert dept_res.status_code == 200
    dept_data = dept_res.json()
    assert "departments" in dept_data
    assert len(dept_data["departments"]) > 0

    # Trends
    tr_res = client.get("/api/management/academic-intelligence/trends?window=30d", headers=headers)
    assert tr_res.status_code == 200

    # Patterns
    pat_res = client.get("/api/management/academic-intelligence/patterns", headers=headers)
    assert pat_res.status_code == 200
    pat_data = pat_res.json()
    assert "patterns" in pat_data

    # Insights
    ins_res = client.get("/api/management/academic-intelligence/insights", headers=headers)
    assert ins_res.status_code == 200
    assert isinstance(ins_res.json(), list)


def test_student_cannot_access_management_academic_endpoints(client, student_token):
    headers = {"Authorization": f"Bearer {student_token}"}
    res = client.get("/api/management/academic-intelligence/overview", headers=headers)
    assert res.status_code == 403


def test_faculty_cannot_access_management_academic_endpoints(client, faculty_token):
    headers = {"Authorization": f"Bearer {faculty_token}"}
    res = client.get("/api/management/academic-intelligence/overview", headers=headers)
    assert res.status_code == 403


# ─────────────────────────────────────────────────────────────
# 2. DETERMINISTIC AGGREGATION ACCURACY
# ─────────────────────────────────────────────────────────────

def test_management_attendance_and_assignment_math(client, management_token):
    headers = {"Authorization": f"Bearer {management_token}"}
    res = client.get("/api/management/academic-intelligence/overview", headers=headers)
    assert res.status_code == 200
    data = res.json()

    total_att = data["total_attendance_records"]
    assert total_att == data["attendance_present"] + data["attendance_absent"]
    if total_att > 0:
        expected_pct = round(data["attendance_present"] / total_att * 100, 1)
        assert data["overall_attendance_pct"] == expected_pct

    total_assign = data["total_assignments"]
    assert total_assign == data["submitted_assignments"] + data["pending_assignments"] + data["overdue_assignments"]
    if total_assign > 0:
        expected_comp = round(data["submitted_assignments"] / total_assign * 100, 1)
        assert data["assignment_completion_rate"] == expected_comp


def test_management_department_breakdown_metrics(client, management_token):
    headers = {"Authorization": f"Bearer {management_token}"}
    res = client.get("/api/management/academic-intelligence/departments", headers=headers)
    assert res.status_code == 200
    depts = res.json()["departments"]

    cs = next((d for d in depts if d["department_code"] in ["CS", "CSE"]), None)
    assert cs is not None
    assert cs["subject_count"] >= 1
    assert cs["attendance_pct"] > 0
    assert cs["assignment_completion_rate"] > 0
    assert cs["data_sufficient"] is True


# ─────────────────────────────────────────────────────────────
# 3. AI INSIGHTS & RESPONSIBLE-AI VALIDATION
# ─────────────────────────────────────────────────────────────

def test_management_ai_insights_schema_and_safety(client, management_token):
    headers = {"Authorization": f"Bearer {management_token}"}
    res = client.get("/api/management/academic-intelligence/insights", headers=headers)
    assert res.status_code == 200
    insights = res.json()
    assert len(insights) >= 1

    forbidden = ["bad department", "worst department", "lazy", "failing", "poor faculty", "fail"]
    for ins in insights:
        assert "insight_type" in ins
        assert "title" in ins
        assert "summary" in ins
        assert "supporting_factors" in ins
        assert "limitations" in ins
        assert ins["confidence"] >= 0.5
        all_text = (ins["title"] + " " + ins["summary"]).lower()
        for f in forbidden:
            assert f not in all_text, f"Responsible AI violation: '{f}' in insight: {ins}"


# ─────────────────────────────────────────────────────────────
# 4. MANAGEMENT ASK VIGNEX INTENT TESTS
# ─────────────────────────────────────────────────────────────

def test_ask_vignex_management_department_attendance_intent(client, management_token):
    headers = {"Authorization": f"Bearer {management_token}"}
    res = client.post(
        "/api/management/academic-intelligence/ask",
        json={"query": "What is the attendance trend across departments?"},
        headers=headers,
    )
    assert res.status_code == 200
    data = res.json()
    assert data["intent"] == "MANAGEMENT_DEPARTMENT_ATTENDANCE"
    assert data["query_mode"] == "VIGNEX_DATA"
    assert "Attendance" in data["answer"]


def test_ask_vignex_management_academic_patterns_intent(client, management_token):
    headers = {"Authorization": f"Bearer {management_token}"}
    res = client.post(
        "/api/management/academic-intelligence/ask",
        json={"query": "What academic patterns are emerging?"},
        headers=headers,
    )
    assert res.status_code == 200
    data = res.json()
    assert data["intent"] == "MANAGEMENT_ACADEMIC_PATTERNS"
    assert data["query_mode"] == "VIGNEX_DATA"
    assert "Academic" in data["answer"] or "Pattern" in data["answer"]


def test_ask_vignex_management_assignment_trends_intent(client, management_token):
    headers = {"Authorization": f"Bearer {management_token}"}
    res = client.post(
        "/api/management/academic-intelligence/ask",
        json={"query": "How is assignment completion changing?"},
        headers=headers,
    )
    assert res.status_code == 200
    data = res.json()
    assert data["intent"] == "MANAGEMENT_ASSIGNMENT_TRENDS"
    assert data["query_mode"] == "VIGNEX_DATA"
    assert "Assignment" in data["answer"]


def test_ask_vignex_management_hybrid_complaints_query(client, management_token):
    headers = {"Authorization": f"Bearer {management_token}"}
    res = client.post(
        "/api/management/academic-intelligence/ask",
        json={"query": "Are academic complaint trends changing alongside attendance?"},
        headers=headers,
    )
    assert res.status_code == 200
    data = res.json()
    assert data["intent"] == "MANAGEMENT_HYBRID_COMPLAINTS"
    assert data["query_mode"] == "HYBRID"
    assert "Attendance" in data["answer"]
    assert len(data["supporting_case_ids"]) > 0
