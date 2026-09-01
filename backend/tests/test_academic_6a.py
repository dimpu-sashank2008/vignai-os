"""
Tests for Phase 6A: Academic Data Model, APIs, Deterministic Metrics, and Role Authorization.
Verifies Student, Faculty, and Management academic endpoints and isolation.
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import SessionLocal
from app.models.user import User
from app.models.academic_subject import AcademicSubject
from app.models.attendance_record import AttendanceRecord
from app.models.assessment import Assessment, AssessmentResult
from app.models.assignment import Assignment
from app.models.timetable_entry import TimetableEntry


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c


def get_auth_token(client: TestClient, email: str, role: str) -> str:
    res = client.post("/api/auth/login", json={"email": email, "password": "password123"})
    assert res.status_code == 200, f"Login failed for {email}: {res.text}"
    return res.json()["access_token"]


@pytest.fixture(scope="module")
def student_token(client):
    return get_auth_token(client, "student@vignex.dev", "student")


@pytest.fixture(scope="module")
def faculty_token(client):
    return get_auth_token(client, "faculty@vignex.dev", "faculty")


@pytest.fixture(scope="module")
def management_token(client):
    return get_auth_token(client, "management@vignex.dev", "management")


# ─────────────────────────────────────────────────────────────
# 1. STUDENT ACADEMIC ENDPOINTS & CALCULATIONS
# ─────────────────────────────────────────────────────────────

def test_student_academic_overview(client, student_token):
    headers = {"Authorization": f"Bearer {student_token}"}
    res = client.get("/api/student/academics/overview", headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert data["metric_type"] == "CALCULATED METRIC"
    assert "data_source" in data
    assert data["enrolled_subjects"] >= 5
    assert 0 <= data["overall_attendance_pct"] <= 100
    assert 0 <= data["assessment_average_pct"] <= 100
    assert data["pending_assignments"] >= 0
    assert data["upcoming_assessments_7d"] >= 0


def test_student_academic_subjects(client, student_token):
    headers = {"Authorization": f"Bearer {student_token}"}
    res = client.get("/api/student/academics/subjects", headers=headers)
    assert res.status_code == 200
    subjects = res.json()
    assert len(subjects) >= 5
    codes = [s["code"] for s in subjects]
    assert "CS201" in codes
    assert "CS202" in codes
    for subj in subjects:
        assert "attendance" in subj
        assert "percentage" in subj["attendance"]
        assert subj["data_source"] == "SYNTHETIC DEVELOPMENT DATA"


def test_student_academic_attendance(client, student_token):
    headers = {"Authorization": f"Bearer {student_token}"}
    res = client.get("/api/student/academics/attendance", headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert "overall" in data
    assert "subjects" in data
    assert len(data["subjects"]) >= 5
    for s in data["subjects"]:
        att = s
        assert att["total"] == att["present"] + att["absent"]
        expected_pct = round(att["present"] / att["total"] * 100, 1) if att["total"] > 0 else 0.0
        assert att["percentage"] == expected_pct


def test_student_academic_assessments(client, student_token):
    headers = {"Authorization": f"Bearer {student_token}"}
    res = client.get("/api/student/academics/assessments", headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert "overall_average_pct" in data
    assert "completed" in data
    assert "upcoming" in data
    assert len(data["completed"]) > 0
    for comp in data["completed"]:
        assert comp["percentage"] == round(comp["marks"] / comp["max_marks"] * 100, 1)


def test_student_academic_assignments(client, student_token):
    headers = {"Authorization": f"Bearer {student_token}"}
    res = client.get("/api/student/academics/assignments", headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert "counts" in data
    counts = data["counts"]
    assert counts["total"] == counts["pending"] + counts["overdue"] + counts["submitted"] + counts["completed"]
    assert len(data["pending"]) == counts["pending"]
    assert len(data["overdue"]) == counts["overdue"]


def test_student_academic_timetable_and_conflicts(client, student_token):
    headers = {"Authorization": f"Bearer {student_token}"}
    res = client.get("/api/student/academics/timetable", headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert "by_day" in data
    assert "conflicts_detected" in data
    assert "Monday" in data["by_day"]


def test_student_academic_workload(client, student_token):
    headers = {"Authorization": f"Bearer {student_token}"}
    res = client.get("/api/student/academics/workload", headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert "next_3_days" in data
    assert "next_7_days" in data
    assert "concentration_detected" in data


def test_student_academic_insights_schema_and_safety(client, student_token):
    headers = {"Authorization": f"Bearer {student_token}"}
    res = client.get("/api/student/academics/insights", headers=headers)
    assert res.status_code == 200
    insights = res.json()
    assert isinstance(insights, list)
    assert len(insights) > 0
    forbidden_words = ["fail", "failing", "lazy", "bad student", "poor student", "expelled"]
    for ins in insights:
        assert "insight_type" in ins
        assert "title" in ins
        assert "summary" in ins
        assert "supporting_factors" in ins
        assert "limitations" in ins
        text_lower = (ins["title"] + " " + ins["summary"]).lower()
        for fw in forbidden_words:
            assert fw not in text_lower, f"Forbidden punitive term '{fw}' found in insight: {ins}"


# ─────────────────────────────────────────────────────────────
# 2. FACULTY ACADEMIC ENDPOINTS & AUTHORIZATION
# ─────────────────────────────────────────────────────────────

def test_faculty_academic_overview(client, faculty_token):
    headers = {"Authorization": f"Bearer {faculty_token}"}
    res = client.get("/api/faculty/academic-intelligence/overview", headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert "subjects" in data
    assert data["subjects_count"] >= 1
    # Faculty is CSE, so taught subjects must be CSE
    for subj in data["subjects"]:
        assert subj["code"] in ["CS201", "CS202", "CS203"]
        assert subj["assignment_completion_rate"] >= 0


def test_faculty_academic_attendance(client, faculty_token):
    headers = {"Authorization": f"Bearer {faculty_token}"}
    res = client.get("/api/faculty/academic-intelligence/attendance", headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert "subjects" in data
    assert len(data["subjects"]) >= 1


def test_faculty_academic_assessments(client, faculty_token):
    headers = {"Authorization": f"Bearer {faculty_token}"}
    res = client.get("/api/faculty/academic-intelligence/assessments", headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert "assessments" in data
    for a in data["assessments"]:
        assert "class_average_marks" in a
        assert a["subject_code"] in ["CS201", "CS202", "CS203"]


def test_faculty_academic_insights(client, faculty_token):
    headers = {"Authorization": f"Bearer {faculty_token}"}
    res = client.get("/api/faculty/academic-intelligence/insights", headers=headers)
    assert res.status_code == 200
    insights = res.json()
    assert isinstance(insights, list)


# ─────────────────────────────────────────────────────────────
# 3. MANAGEMENT ACADEMIC ENDPOINTS
# ─────────────────────────────────────────────────────────────

def test_management_academic_overview(client, management_token):
    headers = {"Authorization": f"Bearer {management_token}"}
    res = client.get("/api/management/academic-intelligence/overview", headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert data["total_subjects"] >= 5
    assert data["total_enrollments"] >= 5
    assert data["total_attendance_records"] > 0
    assert 0 <= data["overall_attendance_pct"] <= 100


def test_management_academic_trends(client, management_token):
    headers = {"Authorization": f"Bearer {management_token}"}
    res = client.get("/api/management/academic-intelligence/trends", headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert "department_trends" in data
    assert len(data["department_trends"]) >= 1
    # Verify no student PII is exposed
    data_str = str(data).lower()
    assert "student_id" not in data_str
    assert "student@vignex.dev" not in data_str


def test_management_academic_insights(client, management_token):
    headers = {"Authorization": f"Bearer {management_token}"}
    res = client.get("/api/management/academic-intelligence/insights", headers=headers)
    assert res.status_code == 200
    insights = res.json()
    assert isinstance(insights, list)
    assert len(insights) > 0


# ─────────────────────────────────────────────────────────────
# 4. ROLE ISOLATION & PRIVACY TESTS
# ─────────────────────────────────────────────────────────────

def test_student_cannot_access_faculty_academic_endpoints(client, student_token):
    headers = {"Authorization": f"Bearer {student_token}"}
    res = client.get("/api/faculty/academic-intelligence/overview", headers=headers)
    assert res.status_code == 403


def test_student_cannot_access_management_academic_endpoints(client, student_token):
    headers = {"Authorization": f"Bearer {student_token}"}
    res = client.get("/api/management/academic-intelligence/overview", headers=headers)
    assert res.status_code == 403


def test_faculty_cannot_access_student_academic_endpoints(client, faculty_token):
    headers = {"Authorization": f"Bearer {faculty_token}"}
    res = client.get("/api/student/academics/overview", headers=headers)
    assert res.status_code == 403


def test_management_cannot_access_student_academic_endpoints(client, management_token):
    headers = {"Authorization": f"Bearer {management_token}"}
    res = client.get("/api/student/academics/overview", headers=headers)
    assert res.status_code == 403
