"""
Automated Test Suite for VIGNAI OS Authentication UX Flows.
Verifies all 9 core UX rules:
- TEST A: First login setup for student (must_change_password=True -> changed -> False)
- TEST B: Second login for student goes straight to dashboard (must_change_password=False)
- TEST C: Voluntary profile password change for student
- TEST D: Faculty complete flow (first login -> change -> second login direct)
- TEST E: Management complete flow (first login -> change -> second login direct)
- TEST F: Forgot Password recovery available for all roles (Student, Faculty, Management)
- TEST G: Forgot Password reset leaves must_change_password=False on future logins
- TEST H: Old password rejected after change
- TEST I: New password works reliably across all auth endpoints
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.main import app
from app.database import SessionLocal
from app.models.user import User
from app.services.auth_service import hash_password

@pytest.fixture(scope="module")
def client():
    return TestClient(app)

@pytest.fixture(scope="module")
def db():
    session = SessionLocal()
    yield session
    session.close()

def _create_or_reset_test_user(db: Session, email: str, role: str, roll_number: str = None, faculty_id: str = None, management_id: str = None, must_change: bool = True):
    user = db.query(User).filter_by(email=email).first()
    if not user:
        user = User(
            email=email,
            role=role,
            roll_number=roll_number,
            faculty_id=faculty_id,
            management_id=management_id,
            password_hash=hash_password("tempPass123"),
            must_change_password=must_change,
            is_active=True,
        )
        db.add(user)
    else:
        user.password_hash = hash_password("tempPass123")
        user.must_change_password = must_change
        user.is_active = True
    db.commit()
    db.refresh(user)
    return user

# TEST A: New Student account must_change_password=true -> first login -> password changed -> false
def test_a_student_first_login_password_setup(client, db):
    email = "test_student_a@vignex.dev"
    _create_or_reset_test_user(db, email=email, role="student", roll_number="221FA04991", must_change=True)

    # 1. First login with temporary password
    login_res = client.post("/api/auth/login", json={"identifier": email, "password": "tempPass123"})
    assert login_res.status_code == 200
    data = login_res.json()
    assert data["user"]["must_change_password"] is True, "First login must flag must_change_password=True"
    token = data["access_token"]

    # 2. Mandatory password setup
    change_res = client.post(
        "/api/auth/change-password",
        json={
            "current_password": "tempPass123",
            "new_password": "NewStudentPass456!",
            "confirm_password": "NewStudentPass456!",
        },
        headers={"Authorization": f"Bearer {token}"}
    )
    assert change_res.status_code == 200
    change_data = change_res.json()
    assert change_data["user"]["must_change_password"] is False, "After change, must_change_password must be False"

# TEST B: Same Student logs out -> logs in again -> dashboard directly -> NO change-password
def test_b_student_second_login_goes_directly_to_dashboard(client):
    email = "test_student_a@vignex.dev"
    # Second login with new password
    login_res = client.post("/api/auth/login", json={"identifier": email, "password": "NewStudentPass456!"})
    assert login_res.status_code == 200
    data = login_res.json()
    assert data["user"]["must_change_password"] is False, "Future logins must NOT have must_change_password=True"

# TEST C: Student opens Profile -> voluntary Change Password available
def test_c_student_voluntary_profile_password_change(client):
    email = "test_student_a@vignex.dev"
    login_res = client.post("/api/auth/login", json={"identifier": email, "password": "NewStudentPass456!"})
    token = login_res.json()["access_token"]

    # Voluntary change from Profile -> Security
    change_res = client.post(
        "/api/auth/change-password",
        json={
            "current_password": "NewStudentPass456!",
            "new_password": "VoluntaryStudentPass789!",
            "confirm_password": "VoluntaryStudentPass789!",
        },
        headers={"Authorization": f"Bearer {token}"}
    )
    assert change_res.status_code == 200
    assert change_res.json()["user"]["must_change_password"] is False

# TEST D: Faculty same complete flow (first login setup -> second login direct -> profile change)
def test_d_faculty_complete_auth_flow(client, db):
    email = "test_faculty_d@vignex.dev"
    _create_or_reset_test_user(db, email=email, role="faculty", faculty_id="FAC-TEST-001", must_change=True)

    # 1. First login
    r1 = client.post("/api/auth/login", json={"identifier": "FAC-TEST-001", "password": "tempPass123"})
    assert r1.status_code == 200
    assert r1.json()["user"]["must_change_password"] is True
    token = r1.json()["access_token"]

    # 2. First password setup
    r_ch = client.post(
        "/api/auth/change-password",
        json={"current_password": "tempPass123", "new_password": "FacultySecurePass!", "confirm_password": "FacultySecurePass!"},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert r_ch.status_code == 200
    assert r_ch.json()["user"]["must_change_password"] is False

    # 3. Second login (must go direct)
    r2 = client.post("/api/auth/login", json={"identifier": "FAC-TEST-001", "password": "FacultySecurePass!"})
    assert r2.status_code == 200
    assert r2.json()["user"]["must_change_password"] is False

# TEST E: Management same complete flow (first login setup -> second login direct -> profile change)
def test_e_management_complete_auth_flow(client, db):
    email = "test_mgmt_e@vignex.dev"
    _create_or_reset_test_user(db, email=email, role="management", management_id="MGMT-TEST-001", must_change=True)

    # 1. First login
    r1 = client.post("/api/auth/login", json={"identifier": "MGMT-TEST-001", "password": "tempPass123"})
    assert r1.status_code == 200
    assert r1.json()["user"]["must_change_password"] is True
    token = r1.json()["access_token"]

    # 2. First password setup
    r_ch = client.post(
        "/api/auth/change-password",
        json={"current_password": "tempPass123", "new_password": "MgmtSecurePass!", "confirm_password": "MgmtSecurePass!"},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert r_ch.status_code == 200
    assert r_ch.json()["user"]["must_change_password"] is False

    # 3. Second login (must go direct)
    r2 = client.post("/api/auth/login", json={"identifier": "MGMT-TEST-001", "password": "MgmtSecurePass!"})
    assert r2.status_code == 200
    assert r2.json()["user"]["must_change_password"] is False

# TEST F: Forgot Password available to all roles (Student, Faculty, Management)
def test_f_forgot_password_identity_verification_all_roles(client, db):
    # Student
    res_stu = client.post("/api/auth/forgot-password", json={"identifier": "test_student_a@vignex.dev"})
    assert res_stu.status_code == 200
    assert res_stu.json()["reset_token"].startswith("RESET-")
    assert "t***a@vignex.dev" in res_stu.json()["masked_email"] or "@" in res_stu.json()["masked_email"]

    # Faculty
    res_fac = client.post("/api/auth/forgot-password", json={"identifier": "FAC-TEST-001"})
    assert res_fac.status_code == 200
    assert res_fac.json()["reset_token"].startswith("RESET-")

    # Management
    res_mgmt = client.post("/api/auth/forgot-password", json={"identifier": "MGMT-TEST-001"})
    assert res_mgmt.status_code == 200
    assert res_mgmt.json()["reset_token"].startswith("RESET-")

# TEST G: Forgot password does not force change-password on future logins (sets must_change_password=False)
def test_g_forgot_password_reset_and_future_login(client):
    email = "test_student_a@vignex.dev"
    forgot_res = client.post("/api/auth/forgot-password", json={"identifier": email})
    token = forgot_res.json()["reset_token"]

    reset_res = client.post(
        "/api/auth/reset-password",
        json={
            "identifier": email,
            "reset_token": token,
            "new_password": "ResetPassViaForgot123!",
            "confirm_password": "ResetPassViaForgot123!",
        }
    )
    assert reset_res.status_code == 200
    assert reset_res.json()["success"] is True

    # Normal login with reset password -> goes straight to dashboard with must_change_password=False
    login_res = client.post("/api/auth/login", json={"identifier": email, "password": "ResetPassViaForgot123!"})
    assert login_res.status_code == 200
    assert login_res.json()["user"]["must_change_password"] is False

# TEST H: Old password rejected after change
def test_h_old_password_rejected_after_change(client):
    email = "test_student_a@vignex.dev"
    old_res = client.post("/api/auth/login", json={"identifier": email, "password": "VoluntaryStudentPass789!"})
    assert old_res.status_code == 401

# TEST I: New password works reliably
def test_i_new_password_works_reliably(client):
    email = "test_student_a@vignex.dev"
    res = client.post("/api/auth/login", json={"identifier": email, "password": "ResetPassViaForgot123!"})
    assert res.status_code == 200
    assert res.json()["user"]["email"] == email
