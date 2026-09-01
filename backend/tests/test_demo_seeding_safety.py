"""
VIGNAI OS — Production Demo Seeding Safety & Idempotency Regression Suite
Verifies that demo seeding is strictly idempotent, non-destructive, does not
overwrite existing accounts, preserves academic data, and enforces RBAC.
"""
import pytest
from app.database import SessionLocal, safe_initialize_database
from app.models.user import User
from app.models.attendance_record import AttendanceRecord
from app.models.assessment import Assessment
from app.models.assignment import Assignment
from app.seed import run_seed
from app.services.auth_service import hash_password, verify_password
from fastapi.testclient import TestClient
from app.main import app


def test_demo_seeding_idempotency():
    """Ensure running seed multiple times produces the exact same counts without duplicating records."""
    db = SessionLocal()
    try:
        # First execution
        run_seed()
        initial_users = db.query(User).count()
        initial_attendance = db.query(AttendanceRecord).count()
        initial_assessments = db.query(Assessment).count()
        initial_assignments = db.query(Assignment).count()

        # Second execution
        run_seed()
        assert db.query(User).count() == initial_users, "User count changed after second seed run"
        assert db.query(AttendanceRecord).count() == initial_attendance, "Attendance count changed after second seed run"
        assert db.query(Assessment).count() == initial_assessments, "Assessment count changed after second seed run"
        assert db.query(Assignment).count() == initial_assignments, "Assignment count changed after second seed run"
    finally:
        db.close()


def test_existing_users_never_overwritten_by_seed():
    """Verify that if a user changes their password, subsequent seed execution does NOT overwrite it."""
    db = SessionLocal()
    try:
        student = db.query(User).filter_by(email="student@vignex.dev").first()
        assert student is not None

        # Simulate user changing password
        new_pwd_hash = hash_password("NewCustomPass2026!")
        student.password_hash = new_pwd_hash
        student.must_change_password = False
        db.commit()

        # Re-run seed
        run_seed()

        db.refresh(student)
        assert student.password_hash == new_pwd_hash, "User password was improperly overwritten by seed"
        assert student.must_change_password is False, "must_change_password was improperly reset by seed"
        assert verify_password("NewCustomPass2026!", student.password_hash) is True

        # Restore demo password for continued test suite compatibility
        student.password_hash = hash_password("password123")
        student.must_change_password = True
        db.commit()
    finally:
        db.close()


def test_user_responses_never_expose_password_hash():
    """Verify that authentication and profile endpoints NEVER expose password hashes in responses."""
    client = TestClient(app)
    res = client.post("/api/auth/login", json={"email": "221FA04001", "password": "password123"})
    assert res.status_code == 200
    data = res.json()
    user_payload = data.get("user", {})

    assert "password" not in user_payload
    assert "password_hash" not in user_payload
    assert "hashed_password" not in user_payload


def test_rbac_security_invariants():
    """Verify that student cannot access management or faculty endpoints."""
    client = TestClient(app)
    # 1. Student login
    s_res = client.post("/api/auth/login", json={"email": "221FA04001", "password": "password123"})
    assert s_res.status_code == 200
    s_token = s_res.json()["access_token"]
    s_headers = {"Authorization": f"Bearer {s_token}"}

    # Student cannot access management
    mgmt_res = client.get("/api/management/academic-intelligence/overview", headers=s_headers)
    assert mgmt_res.status_code == 403

    # Student cannot access faculty
    fac_res = client.get("/api/faculty/academic-intelligence/insights", headers=s_headers)
    assert fac_res.status_code == 403

    # Student CAN access student overview
    own_res = client.get("/api/student/academics/overview", headers=s_headers)
    assert own_res.status_code == 200
