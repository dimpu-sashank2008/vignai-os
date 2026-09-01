"""
Test actual login and /api/auth/me endpoints for all three documented development credentials:
student@vignex.dev / password123
faculty@vignex.dev / password123
management@vignex.dev / password123
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import SessionLocal
from app.models.user import User
from app.services.auth_service import hash_password

client = TestClient(app)

DEV_USERS = [
    ("student@vignex.dev", "password123", "student"),
    ("faculty@vignex.dev", "password123", "faculty"),
    ("management@vignex.dev", "password123", "management"),
]

def test_database_users_exist():
    """Verify that all three dev accounts exist in the database with active status."""
    db = SessionLocal()
    try:
        for email, _, expected_role in DEV_USERS:
            user = db.query(User).filter(User.email == email).first()
            assert user is not None, f"User {email} not found in database"
            assert user.is_active is True, f"User {email} is not active"
            assert user.role == expected_role, f"User {email} role is {user.role}, expected {expected_role}"
    finally:
        db.close()


@pytest.mark.parametrize("email,password,expected_role", DEV_USERS)
def test_login_and_auth_me_success(email, password, expected_role):
    """Test POST /api/auth/login and GET /api/auth/me for development credentials."""
    # 1. Login
    login_resp = client.post("/api/auth/login", json={"email": email, "password": password})
    assert login_resp.status_code == 200, f"Login failed for {email}: {login_resp.text}"
    
    data = login_resp.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["user"]["email"] == email
    assert data["user"]["role"] == expected_role
    
    token = data["access_token"]

    # 2. /api/auth/me
    me_resp = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me_resp.status_code == 200, f"/api/auth/me failed for {email}: {me_resp.text}"
    me_data = me_resp.json()
    assert me_data["email"] == email
    assert me_data["role"] == expected_role


def test_invalid_password_returns_401():
    """Test that wrong password correctly returns 401."""
    resp = client.post("/api/auth/login", json={"email": "student@vignex.dev", "password": "wrongpassword"})
    assert resp.status_code == 401
    assert "Incorrect email or password" in resp.json()["detail"]


def test_login_with_student_roll_number():
    """Test student login using Roll Number."""
    resp = client.post("/api/auth/login", json={"identifier": "221FA04001", "password": "password123"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["user"]["role"] == "student"
    assert data["user"]["roll_number"] == "221FA04001"
    assert "must_change_password" in data["user"]


def test_login_with_faculty_id():
    """Test faculty login using Faculty ID."""
    resp = client.post("/api/auth/login", json={"identifier": "FAC-CSE-001", "password": "password123"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["user"]["role"] == "faculty"
    assert data["user"]["faculty_id"] == "FAC-CSE-001"


def test_login_with_management_id():
    """Test management login using Management ID."""
    resp = client.post("/api/auth/login", json={"identifier": "MGMT-ADMIN-01", "password": "password123"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["user"]["role"] == "management"
    assert data["user"]["management_id"] == "MGMT-ADMIN-01"


def test_case_insensitive_and_whitespace_identifiers():
    """Test normalized case-insensitive identifier resolution."""
    resp = client.post("/api/auth/login", json={"identifier": "  221fa04001  ", "password": "password123"})
    assert resp.status_code == 200
    assert resp.json()["user"]["role"] == "student"


def test_invalid_identifier_returns_401():
    """Test non-existent identifier returns 401."""
    resp = client.post("/api/auth/login", json={"identifier": "INVALID_ID_9999", "password": "password123"})
    assert resp.status_code == 401


def test_change_password_flow_and_relogin():
    """Test change password validation, execution, and subsequent re-login."""
    db = SessionLocal()
    try:
        # 1. Login with dev credentials
        login_resp = client.post("/api/auth/login", json={"identifier": "221FA04001", "password": "password123"})
        assert login_resp.status_code == 200
        token = login_resp.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # 2. Validation failures
        # Wrong current password
        r_bad_curr = client.post("/api/auth/change-password", headers=headers, json={
            "current_password": "wrong_password",
            "new_password": "newSecurePass123",
            "confirm_password": "newSecurePass123"
        })
        assert r_bad_curr.status_code == 400
        assert "Current password is incorrect" in r_bad_curr.json()["detail"]

        # Mismatched confirmation
        r_bad_conf = client.post("/api/auth/change-password", headers=headers, json={
            "current_password": "password123",
            "new_password": "newSecurePass123",
            "confirm_password": "differentPassword"
        })
        assert r_bad_conf.status_code == 400
        assert "do not match" in r_bad_conf.json()["detail"]

        # Too short
        r_short = client.post("/api/auth/change-password", headers=headers, json={
            "current_password": "password123",
            "new_password": "123",
            "confirm_password": "123"
        })
        assert r_short.status_code == 400

        # Same as current
        r_same = client.post("/api/auth/change-password", headers=headers, json={
            "current_password": "password123",
            "new_password": "password123",
            "confirm_password": "password123"
        })
        assert r_same.status_code == 400

        # 3. Successful change
        r_ok = client.post("/api/auth/change-password", headers=headers, json={
            "current_password": "password123",
            "new_password": "newSecurePass123",
            "confirm_password": "newSecurePass123"
        })
        assert r_ok.status_code == 200
        ok_data = r_ok.json()
        assert ok_data["user"]["must_change_password"] is False
        assert "access_token" in ok_data

        # 4. Old password rejected
        r_old = client.post("/api/auth/login", json={"identifier": "221FA04001", "password": "password123"})
        assert r_old.status_code == 401

        # 5. New password accepted
        r_new = client.post("/api/auth/login", json={"identifier": "221FA04001", "password": "newSecurePass123"})
        assert r_new.status_code == 200
        assert r_new.json()["user"]["must_change_password"] is False
    finally:
        # Always restore password back to password123 for all users
        student_u = db.query(User).filter(User.email == "student@vignex.dev").first()
        if student_u:
            student_u.password_hash = hash_password("password123")
        mgmt_u = db.query(User).filter(User.email == "management@vignex.dev").first()
        if mgmt_u:
            mgmt_u.password_hash = hash_password("password123")
        faculty_u = db.query(User).filter(User.email == "faculty@vignex.dev").first()
        if faculty_u:
            faculty_u.password_hash = hash_password("password123")
        db.commit()
        db.close()
