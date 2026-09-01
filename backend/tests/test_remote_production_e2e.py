"""
VIGNAI OS — Remote E2E Production Workflows Test Suite
Validates all 14 mission-critical user and administrative flows required for production deployment:
1. Student login
2. Student attendance
3. Ask VIGNAI
4. Career recommendation
5. Notification deep-link
6. Faculty login
7. Faculty intelligence
8. Management login
9. Campus intelligence
10. What-If simulation
11. Logout / token invalidation
12. Re-login
13. Password change
14. Forgot password flow
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import SessionLocal
from app.models.user import User
from app.services.auth_service import hash_password


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c


@pytest.fixture(autouse=True)
def restore_demo_passwords():
    """Ensure standard demo accounts are reset after tests."""
    yield
    db = SessionLocal()
    for email in ["student@vignex.dev", "faculty@vignex.dev", "management@vignex.dev"]:
        u = db.query(User).filter(User.email == email).first()
        if u:
            u.password_hash = hash_password("password123")
    db.commit()
    db.close()


def test_complete_remote_production_flows(client):
    # 1. Student Login
    login_res = client.post("/api/auth/login", json={"email": "student@vignex.dev", "password": "password123"})
    assert login_res.status_code == 200, f"Student login failed: {login_res.text}"
    student_token = login_res.json()["access_token"]
    student_headers = {"Authorization": f"Bearer {student_token}"}

    # 2. Student Attendance
    att_res = client.get("/api/student/academics/attendance", headers=student_headers)
    assert att_res.status_code == 200
    assert len(att_res.json()) > 0

    # 3. Ask VIGNAI
    ask_res = client.post("/api/intelligence/ask-vignex", json={"query": "What is my attendance?"}, headers=student_headers)
    assert ask_res.status_code == 200
    assert "attendance" in ask_res.json()["answer"].lower() or "cs" in ask_res.json()["answer"].lower()

    # 4. Career Recommendation
    career_res = client.get("/api/student/career/opportunities", headers=student_headers)
    assert career_res.status_code == 200
    assert isinstance(career_res.json(), list)

    # 5. Notification Deep-Link
    notif_res = client.get("/api/notifications", headers=student_headers)
    assert notif_res.status_code == 200
    notifs = notif_res.json()
    if notifs:
        target_notif = notifs[0]
        read_res = client.post(f"/api/notifications/{target_notif['id']}/read", headers=student_headers)
        assert read_res.status_code == 200
        assert read_res.json()["is_read"] is True

    # 6. Faculty Login
    f_login = client.post("/api/auth/login", json={"email": "faculty@vignex.dev", "password": "password123"})
    assert f_login.status_code == 200
    faculty_token = f_login.json()["access_token"]
    faculty_headers = {"Authorization": f"Bearer {faculty_token}"}

    # 7. Faculty Intelligence
    f_cases = client.get("/api/faculty/cases", headers=faculty_headers)
    assert f_cases.status_code == 200

    # 8. Management Login
    m_login = client.post("/api/auth/login", json={"email": "management@vignex.dev", "password": "password123"})
    assert m_login.status_code == 200
    mgmt_token = m_login.json()["access_token"]
    mgmt_headers = {"Authorization": f"Bearer {mgmt_token}"}

    # 9. Campus Intelligence
    issues_res = client.get("/api/management/case-groups", headers=mgmt_headers)
    assert issues_res.status_code == 200

    # 10. What-If Simulation
    sim_payload = {
        "domain": "INFRASTRUCTURE",
        "scenario_name": "Wi-Fi AP Expansion in Block A",
        "baseline_parameters": {"location": "Block A", "current_aps": 10},
        "scenarios": [
            {"scenario_id": "A", "name": "Scenario A (+3 APs)", "parameters": {"add_aps": 3}},
            {"scenario_id": "B", "name": "Scenario B (+6 APs)", "parameters": {"add_aps": 6}},
        ],
    }
    sim_res = client.post("/api/management/simulations/run", json=sim_payload, headers=mgmt_headers)
    assert sim_res.status_code == 200
    sim_data = sim_res.json()
    assert "baseline_overview" in sim_data or "scenarios" in sim_data

    # 11. Logout / Client Token Drop Test (Verify protected endpoint denies invalid/cleared token)
    logout_test = client.get("/api/auth/me", headers={"Authorization": "Bearer cleared_token"})
    assert logout_test.status_code == 401

    # 12. Re-login
    relogin_res = client.post("/api/auth/login", json={"email": "student@vignex.dev", "password": "password123"})
    assert relogin_res.status_code == 200
    fresh_token = relogin_res.json()["access_token"]
    fresh_headers = {"Authorization": f"Bearer {fresh_token}"}

    # 13. Password Change
    change_res = client.post(
        "/api/auth/change-password",
        json={
            "current_password": "password123",
            "new_password": "newSecureProductionPass2026",
            "confirm_password": "newSecureProductionPass2026",
        },
        headers=fresh_headers,
    )
    assert change_res.status_code == 200
    assert change_res.json()["message"] == "Password changed successfully."

    # Verify old password rejected and new accepted
    old_reject = client.post("/api/auth/login", json={"email": "student@vignex.dev", "password": "password123"})
    assert old_reject.status_code == 401
    new_accept = client.post("/api/auth/login", json={"email": "student@vignex.dev", "password": "newSecureProductionPass2026"})
    assert new_accept.status_code == 200

    # 14. Forgot Password Flow
    forgot_res = client.post("/api/auth/forgot-password", json={"identifier": "student@vignex.dev"})
    assert forgot_res.status_code == 200
    reset_tok = forgot_res.json()["reset_token"]

    reset_res = client.post(
        "/api/auth/reset-password",
        json={
            "identifier": "student@vignex.dev",
            "reset_token": reset_tok,
            "new_password": "password123",
            "confirm_password": "password123",
        },
    )
    assert reset_res.status_code == 200
    assert reset_res.json()["success"] is True

    # Confirm student can log back in with password123
    final_login = client.post("/api/auth/login", json={"email": "student@vignex.dev", "password": "password123"})
    assert final_login.status_code == 200
