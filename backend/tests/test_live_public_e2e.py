"""
VIGNAI OS — Live Public Internet End-to-End Test Suite (Step 7)
Strictly performs real HTTP/HTTPS network calls over the internet against
deployed public frontend and backend endpoints.

CRITICAL CONSTRAINTS:
- Does NOT use FastAPI TestClient
- Does NOT use in-memory ASGI transports
- Does NOT use localhost or testserver
- Rejects non-public URLs in remote mode
"""
import os
import sys
import time
import requests
import pytest

PUBLIC_FRONTEND_URL = os.environ.get("PUBLIC_FRONTEND_URL", "").rstrip("/")
PUBLIC_BACKEND_URL = os.environ.get("PUBLIC_BACKEND_URL", "").rstrip("/")

# If URL has /api appended, handle cleanly
if PUBLIC_BACKEND_URL.endswith("/api"):
    API_BASE = PUBLIC_BACKEND_URL
    HOST_BASE = PUBLIC_BACKEND_URL[:-4]
else:
    API_BASE = f"{PUBLIC_BACKEND_URL}/api" if PUBLIC_BACKEND_URL else ""
    HOST_BASE = PUBLIC_BACKEND_URL


def validate_target_urls():
    if not PUBLIC_FRONTEND_URL or not PUBLIC_BACKEND_URL:
        pytest.skip(
            "LIVE CLOUD DEPLOYMENT VERIFICATION REQUIRES ENVIRONMENT VARIABLES:\n"
            "  PUBLIC_FRONTEND_URL=https://<your-frontend>.vercel.app\n"
            "  PUBLIC_BACKEND_URL=https://<your-backend>.onrender.com\n"
            "Set these environment variables to execute real internet E2E testing."
        )

    forbidden = ["localhost", "127.0.0.1", "0.0.0.0", "testserver"]
    for word in forbidden:
        if word in PUBLIC_FRONTEND_URL.lower() or word in PUBLIC_BACKEND_URL.lower():
            pytest.fail(f"Localhost address '{word}' detected in target URL. Real public HTTPS testing required.")


# =====================================================================
# 1. PUBLIC AVAILABILITY & HEALTH TESTS
# =====================================================================

def test_live_public_frontend_availability():
    """Verify that the deployed frontend URL is accessible publicly over HTTPS."""
    validate_target_urls()
    resp = requests.get(PUBLIC_FRONTEND_URL, timeout=15)
    assert resp.status_code == 200, f"Frontend returned status {resp.status_code}"
    text = resp.text.lower()
    assert "vignai" in text or "vignex" in text or "<div id=\"root\">" in text


def test_live_public_backend_health():
    """Verify GET /health returns OK with live database connection."""
    validate_target_urls()
    health_url = f"{HOST_BASE}/health"
    resp = requests.get(health_url, timeout=15)
    assert resp.status_code == 200, f"Backend /health returned {resp.status_code}: {resp.text}"
    data = resp.json()
    assert data.get("status") == "ok"
    assert data.get("database") == "CONNECTED"


def test_live_public_backend_api_health():
    """Verify GET /api/health responds symmetrically."""
    validate_target_urls()
    api_health_url = f"{API_BASE}/health"
    resp = requests.get(api_health_url, timeout=15)
    assert resp.status_code == 200
    data = resp.json()
    assert data.get("status") == "ok"
    assert data.get("database") == "CONNECTED"


# =====================================================================
# 2. COMPLETE MISSION-CRITICAL REMOTE WORKFLOWS
# =====================================================================

def test_live_public_e2e_user_workflows():
    """Execute all authenticated user and administrative flows over public HTTPS."""
    validate_target_urls()
    session = requests.Session()

    # 1. Student Login
    login_res = session.post(
        f"{API_BASE}/auth/login",
        json={"email": "student@vignex.dev", "password": "password123"},
        timeout=15,
    )
    assert login_res.status_code == 200, f"Student login failed: {login_res.text}"
    student_token = login_res.json()["access_token"]
    student_headers = {"Authorization": f"Bearer {student_token}"}

    # 2. Student Attendance
    att_res = session.get(f"{API_BASE}/student/academics/attendance", headers=student_headers, timeout=15)
    assert att_res.status_code == 200
    assert len(att_res.json()) > 0

    # 3. Ask VIGNAI
    ask_res = session.post(
        f"{API_BASE}/intelligence/ask-vignex",
        json={"query": "What is my attendance?"},
        headers=student_headers,
        timeout=30,
    )
    assert ask_res.status_code == 200
    ask_data = ask_res.json()
    assert "answer" in ask_data
    # Log Gemini / Fallback provider
    print(f"\n[LIVE ASK VIGNAI RESULT] Provider: {ask_data.get('provider')} | Status: {ask_data.get('provider_status')} | Model: {ask_data.get('model')}")

    # 4. Career Opportunities
    career_res = session.get(f"{API_BASE}/student/career/opportunities", headers=student_headers, timeout=15)
    assert career_res.status_code == 200
    assert isinstance(career_res.json(), list)

    # 5. Notification Deep-Link
    notifs_res = session.get(f"{API_BASE}/notifications", headers=student_headers, timeout=15)
    assert notifs_res.status_code == 200
    notifs = notifs_res.json()
    if notifs:
        target_id = notifs[0]["id"]
        read_res = session.post(f"{API_BASE}/notifications/{target_id}/read", headers=student_headers, timeout=15)
        assert read_res.status_code == 200
        assert read_res.json()["is_read"] is True

    # 6. Faculty Login
    f_login = session.post(
        f"{API_BASE}/auth/login",
        json={"email": "faculty@vignex.dev", "password": "password123"},
        timeout=15,
    )
    assert f_login.status_code == 200
    faculty_token = f_login.json()["access_token"]
    faculty_headers = {"Authorization": f"Bearer {faculty_token}"}

    # 7. Faculty Intelligence
    f_cases = session.get(f"{API_BASE}/faculty/cases", headers=faculty_headers, timeout=15)
    assert f_cases.status_code == 200

    # 8. Management Login
    m_login = session.post(
        f"{API_BASE}/auth/login",
        json={"email": "management@vignex.dev", "password": "password123"},
        timeout=15,
    )
    assert m_login.status_code == 200
    mgmt_token = m_login.json()["access_token"]
    mgmt_headers = {"Authorization": f"Bearer {mgmt_token}"}

    # 9. Management Intelligence
    mgmt_cases = session.get(f"{API_BASE}/management/case-groups", headers=mgmt_headers, timeout=15)
    assert mgmt_cases.status_code == 200

    # 10. What-If Simulation
    sim_payload = {
        "domain": "INFRASTRUCTURE",
        "scenario_name": "Live Cloud Wi-Fi AP Test",
        "baseline_parameters": {"location": "Block A", "current_aps": 10},
        "scenarios": [
            {"scenario_id": "A", "name": "Scenario A (+3 APs)", "parameters": {"add_aps": 3}},
            {"scenario_id": "B", "name": "Scenario B (+6 APs)", "parameters": {"add_aps": 6}},
        ],
    }
    sim_res = session.post(f"{API_BASE}/management/simulations/run", json=sim_payload, headers=mgmt_headers, timeout=20)
    assert sim_res.status_code == 200

    # 11. RBAC Isolation Enforcement
    # Student cannot access faculty cases
    s_block_f = session.get(f"{API_BASE}/faculty/cases", headers=student_headers, timeout=15)
    assert s_block_f.status_code == 403

    # Student cannot access management case groups
    s_block_m = session.get(f"{API_BASE}/management/case-groups", headers=student_headers, timeout=15)
    assert s_block_m.status_code == 403

    # Faculty cannot access management case groups
    f_block_m = session.get(f"{API_BASE}/management/case-groups", headers=faculty_headers, timeout=15)
    assert f_block_m.status_code == 403

    # 12. Logout / Invalidation
    drop_test = session.get(f"{API_BASE}/auth/me", headers={"Authorization": "Bearer bad_token"}, timeout=15)
    assert drop_test.status_code == 401

    # 13. Re-login
    relogin = session.post(
        f"{API_BASE}/auth/login",
        json={"email": "student@vignex.dev", "password": "password123"},
        timeout=15,
    )
    assert relogin.status_code == 200


if __name__ == "__main__":
    print("Executing live public E2E suite via standalone runner...")
    test_live_public_frontend_availability()
    test_live_public_backend_health()
    test_live_public_backend_api_health()
    test_live_public_e2e_user_workflows()
    print("All live public tests completed successfully!")
