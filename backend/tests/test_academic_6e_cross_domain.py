"""
Tests for Phase 6E: Ask VIGNEX Academic + Cross-Domain Integration.
Verifies:
1. Domain routing architecture (GENERAL_KNOWLEDGE, ACADEMIC, COMPLAINTS, CAMPUS_INTELLIGENCE, SIMULATIONS, HYBRID)
2. Strict retrieval boundaries (zero cross-domain leakage)
3. Student, Faculty, and Management role authorizations
4. Privacy refusals and allegation neutrality
5. Dynamic domain switching across multi-turn conversation
6. Context badges mapping accurately to response domain
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app


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
# 1. GENERAL KNOWLEDGE DOMAIN ISOLATION
# ─────────────────────────────────────────────────────────────

def test_ask_vignex_photosynthesis_general_knowledge_isolation(client, student_token):
    headers = {"Authorization": f"Bearer {student_token}"}
    res = client.post(
        "/api/intelligence/ask-vignex",
        json={"query": "What is photosynthesis?"},
        headers=headers,
    )
    assert res.status_code == 200
    data = res.json()
    assert data["domain"] == "GENERAL_KNOWLEDGE"
    assert data["query_mode"] == "GENERAL_KNOWLEDGE"
    assert "📖 GENERAL KNOWLEDGE" in data["context_badge"]
    assert len(data["supporting_case_ids"]) == 0
    assert len(data["supporting_cases"]) == 0
    assert "chloroplast" in data["answer"].lower() or "glucose" in data["answer"].lower()


def test_ask_vignex_recursion_in_c_general_knowledge(client, faculty_token):
    headers = {"Authorization": f"Bearer {faculty_token}"}
    res = client.post(
        "/api/intelligence/ask-vignex",
        json={"query": "Explain recursion in C."},
        headers=headers,
    )
    assert res.status_code == 200
    data = res.json()
    assert data["domain"] == "GENERAL_KNOWLEDGE"
    assert data["query_mode"] == "GENERAL_KNOWLEDGE"
    assert "Base Case" in data["answer"]


# ─────────────────────────────────────────────────────────────
# 2. ACADEMIC DOMAIN RETRIEVAL & ROLE ISOLATION
# ─────────────────────────────────────────────────────────────

def test_ask_vignex_student_next_exam_academic_domain(client, student_token):
    headers = {"Authorization": f"Bearer {student_token}"}
    res = client.post(
        "/api/intelligence/ask-vignex",
        json={"query": "When is my next exam?"},
        headers=headers,
    )
    assert res.status_code == 200
    data = res.json()
    assert data["domain"] == "ACADEMIC"
    assert "📚 ACADEMIC" in data["context_badge"]
    assert "Assessment" in data["answer"] or "Exam" in data["answer"] or "Quiz" in data["answer"] or "recorded" in data["answer"]


def test_ask_vignex_student_attendance_academic_domain(client, student_token):
    headers = {"Authorization": f"Bearer {student_token}"}
    res = client.post(
        "/api/intelligence/ask-vignex",
        json={"query": "How is my attendance?"},
        headers=headers,
    )
    assert res.status_code == 200
    data = res.json()
    assert data["domain"] == "ACADEMIC"
    assert "📚 ACADEMIC" in data["context_badge"]
    assert "Attendance" in data["answer"]


def test_ask_vignex_student_assignments_due_academic_domain(client, student_token):
    headers = {"Authorization": f"Bearer {student_token}"}
    res = client.post(
        "/api/intelligence/ask-vignex",
        json={"query": "What's due this week?"},
        headers=headers,
    )
    assert res.status_code == 200
    data = res.json()
    assert data["domain"] == "ACADEMIC"
    assert "📚 ACADEMIC" in data["context_badge"]
    assert "Assignment" in data["answer"] or "due" in data["answer"].lower()


# ─────────────────────────────────────────────────────────────
# 3. COMPLAINTS DOMAIN ISOLATION
# ─────────────────────────────────────────────────────────────

def test_ask_vignex_student_own_complaints(client, student_token):
    headers = {"Authorization": f"Bearer {student_token}"}
    res = client.post(
        "/api/intelligence/ask-vignex",
        json={"query": "What are my complaints?"},
        headers=headers,
    )
    assert res.status_code == 200
    data = res.json()
    assert data["domain"] == "COMPLAINTS"
    assert "🏛️ VIGNAN CAMPUS DATA" in data["context_badge"] or "🏛️ VIGNEX CAMPUS DATA" in data["context_badge"]
    assert "Submitted" in data["answer"] or "complaint" in data["answer"].lower() or "report" in data["answer"].lower()


def test_ask_vignex_unresolved_department_complaints(client, management_token):
    headers = {"Authorization": f"Bearer {management_token}"}
    res = client.post(
        "/api/intelligence/ask-vignex",
        json={"query": "Which department has the most unresolved complaints?"},
        headers=headers,
    )
    assert res.status_code == 200
    data = res.json()
    assert data["domain"] == "COMPLAINTS"
    assert "🏛️ VIGNAN CAMPUS DATA" in data["context_badge"] or "🏛️ VIGNEX CAMPUS DATA" in data["context_badge"]
    assert "unresolved" in data["answer"].lower()


# ─────────────────────────────────────────────────────────────
# 4. CAMPUS INTELLIGENCE DOMAIN
# ─────────────────────────────────────────────────────────────

def test_ask_vignex_block_a_risk_campus_intelligence(client, management_token):
    headers = {"Authorization": f"Bearer {management_token}"}
    res = client.post(
        "/api/intelligence/ask-vignex",
        json={"query": "Why is Block A becoming a risk?"},
        headers=headers,
    )
    assert res.status_code == 200
    data = res.json()
    assert data["domain"] == "CAMPUS_INTELLIGENCE"
    assert "🏛️ VIGNAN CAMPUS DATA" in data["context_badge"] or "🏛️ VIGNEX CAMPUS DATA" in data["context_badge"]
    assert "Block A" in data["answer"]


def test_ask_vignex_biggest_campus_problems_intelligence(client, management_token):
    headers = {"Authorization": f"Bearer {management_token}"}
    res = client.post(
        "/api/intelligence/ask-vignex",
        json={"query": "What are the biggest campus problems?"},
        headers=headers,
    )
    assert res.status_code == 200
    data = res.json()
    assert data["domain"] == "CAMPUS_INTELLIGENCE"
    assert "🏛️ VIGNAN CAMPUS DATA" in data["context_badge"] or "🏛️ VIGNEX CAMPUS DATA" in data["context_badge"]


# ─────────────────────────────────────────────────────────────
# 5. SIMULATION WHAT-IF DOMAIN & ROLE AUTHORIZATION
# ─────────────────────────────────────────────────────────────

def test_ask_vignex_management_simulation_what_if(client, management_token):
    headers = {"Authorization": f"Bearer {management_token}"}
    res = client.post(
        "/api/intelligence/ask-vignex",
        json={"query": "What happens if we add one bus?"},
        headers=headers,
    )
    assert res.status_code == 200
    data = res.json()
    assert data["domain"] == "SIMULATIONS"
    assert "🛠️ SIMULATION" in data["context_badge"]
    assert "Simulation" in data["answer"]
    assert "Capacity" in data["answer"] or "Wait Time" in data["answer"]


def test_ask_vignex_student_academic_scenario_workload(client, student_token):
    headers = {"Authorization": f"Bearer {student_token}"}
    res = client.post(
        "/api/intelligence/ask-vignex",
        json={"query": "What if I have 3 assignments due tomorrow?"},
        headers=headers,
    )
    assert res.status_code == 200
    data = res.json()
    assert data["domain"] == "SIMULATIONS"
    assert "Academic Workload Concentration" in data["answer"] or "Workload" in data["answer"]
    assert len(data["action_links"]) > 0


def test_ask_vignex_faculty_academic_scenario_deadline(client, faculty_token):
    headers = {"Authorization": f"Bearer {faculty_token}"}
    res = client.post(
        "/api/intelligence/ask-vignex",
        json={"query": "What if assignment deadlines are moved?"},
        headers=headers,
    )
    assert res.status_code == 200
    data = res.json()
    assert data["domain"] == "SIMULATIONS"
    assert "Academic Deadline Adjustment" in data["answer"] or "Deadline" in data["answer"]
    assert len(data["action_links"]) > 0


def test_ask_vignex_management_wifi_simulation(client, management_token):
    headers = {"Authorization": f"Bearer {management_token}"}
    res = client.post(
        "/api/intelligence/ask-vignex",
        json={"query": "What if Block A Wi-Fi bandwidth increases?"},
        headers=headers,
    )
    assert res.status_code == 200
    data = res.json()
    assert data["domain"] == "SIMULATIONS"
    assert "Wi-Fi Infrastructure Upgrade" in data["answer"] or "Wi-Fi" in data["answer"]
    assert any("/management/simulations" in link["url"] for link in data["action_links"])


def test_ask_vignex_management_maintenance_simulation(client, management_token):
    headers = {"Authorization": f"Bearer {management_token}"}
    res = client.post(
        "/api/intelligence/ask-vignex",
        json={"query": "What if maintenance staffing increases?"},
        headers=headers,
    )
    assert res.status_code == 200
    data = res.json()
    assert data["domain"] == "SIMULATIONS"
    assert "Maintenance Staffing Expansion" in data["answer"] or "Maintenance" in data["answer"]
    assert any("/management/simulations" in link["url"] for link in data["action_links"])


def test_ask_vignex_unsupported_disaster_scenario(client, management_token):
    headers = {"Authorization": f"Bearer {management_token}"}
    res = client.post(
        "/api/intelligence/ask-vignex",
        json={"query": "What if an earthquake happens?"},
        headers=headers,
    )
    assert res.status_code == 200
    data = res.json()
    assert data["domain"] == "SIMULATIONS"
    assert "does not currently have a validated simulation model" in data["answer"]


# ─────────────────────────────────────────────────────────────
# 6. HYBRID CROSS-DOMAIN SYNTHESIS
# ─────────────────────────────────────────────────────────────

def test_ask_vignex_hybrid_academic_and_complaint_correlation(client, management_token):
    headers = {"Authorization": f"Bearer {management_token}"}
    res = client.post(
        "/api/intelligence/ask-vignex",
        json={"query": "Are academic complaints increasing while attendance is decreasing?"},
        headers=headers,
    )
    assert res.status_code == 200
    data = res.json()
    assert data["domain"] == "HYBRID"
    assert data["query_mode"] == "HYBRID"
    assert "⚡ HYBRID" in data["context_badge"]
    assert "Attendance" in data["answer"]
    # Check non-causal Responsible-AI language
    assert "because" not in data["interpretation"].lower() or "direct causation" in data["limitations"][0].lower()


# ─────────────────────────────────────────────────────────────
# 7. PRIVACY & ALLEGATION REFUSALS
# ─────────────────────────────────────────────────────────────

def test_ask_vignex_protected_identity_refusal(client, management_token):
    headers = {"Authorization": f"Bearer {management_token}"}
    res = client.post(
        "/api/intelligence/ask-vignex",
        json={"query": "Who submitted the protected complaint?"},
        headers=headers,
    )
    assert res.status_code == 200
    data = res.json()
    assert data["intent"] == "PRIVACY_REFUSAL"
    assert "can't provide protected reporter identity" in data["answer"]


def test_ask_vignex_allegation_neutrality(client, management_token):
    headers = {"Authorization": f"Bearer {management_token}"}
    res = client.post(
        "/api/intelligence/ask-vignex",
        json={"query": "Is the faculty member guilty?"},
        headers=headers,
    )
    assert res.status_code == 200
    data = res.json()
    assert data["intent"] == "ALLEGATION_NEUTRALITY"
    assert "cannot determine whether an allegation is true" in data["answer"]


# ─────────────────────────────────────────────────────────────
# 8. DYNAMIC DOMAIN SWITCHING IN MULTI-TURN CONVERSATION
# ─────────────────────────────────────────────────────────────

def test_ask_vignex_dynamic_domain_switching(client, student_token):
    headers = {"Authorization": f"Bearer {student_token}"}

    # Turn 1: Academic
    res1 = client.post(
        "/api/intelligence/ask-vignex",
        json={"query": "How is my attendance?"},
        headers=headers,
    )
    assert res1.status_code == 200
    assert res1.json()["domain"] == "ACADEMIC"

    # Turn 2: Campus Intelligence
    res2 = client.post(
        "/api/intelligence/ask-vignex",
        json={
            "query": "What are the biggest campus issues?",
            "conversation_context": [{"query": "How is my attendance?", "intent": "STUDENT_ATTENDANCE"}],
        },
        headers=headers,
    )
    assert res2.status_code == 200
    assert res2.json()["domain"] == "CAMPUS_INTELLIGENCE"

    # Turn 3: General Knowledge
    res3 = client.post(
        "/api/intelligence/ask-vignex",
        json={
            "query": "What is recursion in C?",
            "conversation_context": [{"query": "What are the biggest campus issues?", "intent": "CAMPUS_OVERVIEW"}],
        },
        headers=headers,
    )
    assert res3.status_code == 200
    assert res3.json()["domain"] == "GENERAL_KNOWLEDGE"


# ─────────────────────────────────────────────────────────────
# 9. UNIVERSAL AVAILABILITY & ROLE-AWARE ACCESS VERIFICATION
# ─────────────────────────────────────────────────────────────

def test_universal_ask_vignex_student_queries(client, student_token):
    headers = {"Authorization": f"Bearer {student_token}"}

    # 1. Student General Knowledge: What is photosynthesis?
    r1 = client.post("/api/intelligence/ask-vignex", json={"query": "What is photosynthesis?"}, headers=headers)
    assert r1.status_code == 200
    d1 = r1.json()
    assert d1["domain"] == "GENERAL_KNOWLEDGE"
    assert "📖 GENERAL KNOWLEDGE" in d1["context_badge"]
    assert len(d1["supporting_cases"]) == 0

    # 2. Student Own Attendance: What is my attendance?
    r2 = client.post("/api/intelligence/ask-vignex", json={"query": "What is my attendance?"}, headers=headers)
    assert r2.status_code == 200
    d2 = r2.json()
    assert d2["domain"] == "ACADEMIC"
    assert "🎓 ACADEMIC" in d2["context_badge"] or "📚 ACADEMIC" in d2["context_badge"]
    assert "Attendance" in d2["answer"]

    # 3. Student Own Complaints: What are my complaints?
    r3 = client.post("/api/intelligence/ask-vignex", json={"query": "What are my complaints?"}, headers=headers)
    assert r3.status_code == 200
    d3 = r3.json()
    assert d3["domain"] == "COMPLAINTS"
    assert "🏛️ VIGNAN CAMPUS DATA" in d3["context_badge"] or "🏛️ VIGNEX CAMPUS DATA" in d3["context_badge"] or "🏛️ VIGNAN CAMPUS DATA" in d3["context_badge"]

    # 4. Student Campus Overview: What are the biggest problems on campus?
    r4 = client.post("/api/intelligence/ask-vignex", json={"query": "What are the biggest problems on campus?"}, headers=headers)
    assert r4.status_code == 200
    d4 = r4.json()
    assert d4["domain"] == "CAMPUS_INTELLIGENCE"
    assert "🏛️ VIGNAN CAMPUS DATA" in d4["context_badge"] or "🏛️ VIGNEX CAMPUS DATA" in d4["context_badge"] or "🏛️ VIGNAN CAMPUS DATA" in d4["context_badge"]


def test_universal_ask_vignex_faculty_queries(client, faculty_token):
    headers = {"Authorization": f"Bearer {faculty_token}"}

    # 1. Faculty General Knowledge: What is recursion?
    r1 = client.post("/api/intelligence/ask-vignex", json={"query": "What is recursion?"}, headers=headers)
    assert r1.status_code == 200
    d1 = r1.json()
    assert d1["domain"] == "GENERAL_KNOWLEDGE"
    assert "📖 GENERAL KNOWLEDGE" in d1["context_badge"]
    assert len(d1["supporting_cases"]) == 0

    # 2. Faculty Class Attendance: What is the attendance trend in my class?
    r2 = client.post("/api/intelligence/ask-vignex", json={"query": "What is the attendance trend in my class?"}, headers=headers)
    assert r2.status_code == 200
    d2 = r2.json()
    assert d2["domain"] == "ACADEMIC"
    assert "🎓 ACADEMIC" in d2["context_badge"] or "📚 ACADEMIC" in d2["context_badge"]

    # 3. Faculty Department Issues: What are the department issues?
    r3 = client.post("/api/intelligence/ask-vignex", json={"query": "What are the department issues?"}, headers=headers)
    assert r3.status_code == 200
    d3 = r3.json()
    assert d3["domain"] == "COMPLAINTS"
    assert "🏛️ VIGNAN CAMPUS DATA" in d3["context_badge"] or "🏛️ VIGNEX CAMPUS DATA" in d3["context_badge"] or "🏛️ VIGNAN CAMPUS DATA" in d3["context_badge"]


def test_universal_ask_vignex_management_queries(client, management_token):
    headers = {"Authorization": f"Bearer {management_token}"}

    # 1. Management Campus Problems: What are the biggest campus problems?
    r1 = client.post("/api/intelligence/ask-vignex", json={"query": "What are the biggest campus problems?"}, headers=headers)
    assert r1.status_code == 200
    d1 = r1.json()
    assert d1["domain"] == "CAMPUS_INTELLIGENCE"
    assert "🏛️ VIGNAN CAMPUS DATA" in d1["context_badge"] or "🏛️ VIGNEX CAMPUS DATA" in d1["context_badge"] or "🏛️ VIGNAN CAMPUS DATA" in d1["context_badge"]

    # 2. Management Department Attendance: What is the attendance trend across departments?
    r2 = client.post("/api/intelligence/ask-vignex", json={"query": "What is the attendance trend across departments?"}, headers=headers)
    assert r2.status_code == 200
    d2 = r2.json()
    assert d2["domain"] == "ACADEMIC"
    assert "🎓 ACADEMIC" in d2["context_badge"] or "📚 ACADEMIC" in d2["context_badge"]
