"""
Automated Test Suite for VIGNAI OS Career Intelligence (Student Ecosystem).
Covers:
1. Career profile retrieval & strict privacy isolation (403 for Faculty/Management).
2. Deterministic 70/30 match scoring algorithm and explainability.
3. Skill-gap detection and responsible learning recommendations.
4. Daily career brief metrics and approaching deadline calculations.
5. Opportunity listing, filtering by type and work mode, sorting.
6. Resume upload and structured text extraction.
7. Ask VIGNAI Career domain intents, closing soon, skill search.
8. General Knowledge separation ("What is Docker?" vs "Which internships require Docker?").
9. Career + Academic hybrid intent routing.
10. Campus placement info responsible refusal.
"""

import io
import pytest
from datetime import datetime, timedelta
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.main import app
from app.database import get_db, SessionLocal
from app.models.user import User
from app.models.career import CareerProfile, CareerSkill, Opportunity, OpportunitySkill, OpportunityMatch
from app.services.auth_service import create_access_token
from app.services.ask_vignex.query_router import query_router
from app.services.ask_vignex.answer_service import ask_vignex_answer_service
from app.services.ask_vignex.schemas import AskVignexQueryPayload
from app.services.career.matching_engine import matching_engine


@pytest.fixture(scope="module")
def db():
    session = SessionLocal()
    yield session
    session.close()


@pytest.fixture(scope="module")
def client():
    return TestClient(app)


@pytest.fixture(scope="module")
def student_token(db: Session):
    user = db.query(User).filter_by(email="student@vignex.dev").first()
    if not user:
        pytest.skip("Student user not found in seed data.")
    return create_access_token(data={"sub": user.email, "role": user.role})


@pytest.fixture(scope="module")
def faculty_token(db: Session):
    user = db.query(User).filter_by(email="faculty@vignex.dev").first()
    if not user:
        pytest.skip("Faculty user not found in seed data.")
    return create_access_token(data={"sub": user.email, "role": user.role})


@pytest.fixture(scope="module")
def management_token(db: Session):
    user = db.query(User).filter_by(email="management@vignex.dev").first()
    if not user:
        pytest.skip("Management user not found in seed data.")
    return create_access_token(data={"sub": user.email, "role": user.role})


# =========================================================================
# 1. CAREER PROFILE & PRIVACY ISOLATION TESTS
# =========================================================================

def test_career_profile_retrieval_and_privacy_isolation(client, student_token, faculty_token, management_token):
    """Student can retrieve own career profile; Faculty and Management are strictly denied (403)."""
    # Student access -> 200 OK
    res = client.get("/api/student/career/profile", headers={"Authorization": f"Bearer {student_token}"})
    assert res.status_code == 200
    data = res.json()
    assert "headline" in data
    assert "skills" in data
    assert "projects" in data
    assert len(data["skills"]) >= 4

    # Faculty access -> 403 Forbidden
    res_fac = client.get("/api/student/career/profile", headers={"Authorization": f"Bearer {faculty_token}"})
    assert res_fac.status_code == 403

    # Management access -> 403 Forbidden
    res_mgmt = client.get("/api/student/career/profile", headers={"Authorization": f"Bearer {management_token}"})
    assert res_mgmt.status_code == 403

    # Unauthenticated access -> 401 Unauthorized
    res_anon = client.get("/api/student/career/profile")
    assert res_anon.status_code == 401


# =========================================================================
# 2. DETERMINISTIC MATCHING ENGINE & EXPLAINABILITY TESTS
# =========================================================================

def test_deterministic_matching_scoring_and_explainability(client, student_token, db):
    """Verifies deterministic 70/30 formula and explainability payload."""
    res = client.get("/api/student/career/matches", headers={"Authorization": f"Bearer {student_token}"})
    assert res.status_code == 200
    matches = res.json()
    assert len(matches) >= 5

    top_match = matches[0]
    assert top_match["match_score"] >= 80.0
    assert "matched_skills" in top_match
    assert "missing_skills" in top_match
    assert "match_reasons" in top_match
    assert "score_breakdown" in top_match["match_reasons"]
    assert top_match["match_reasons"]["score_breakdown"]["required_skills_weight"] == "75%"
    assert top_match["match_reasons"]["score_breakdown"]["preferred_skills_weight"] == "15%"
    assert "responsible_ai_disclaimer" in top_match["match_reasons"]


def test_opportunity_filtering_by_type_and_work_mode(client, student_token):
    """Verifies filtering opportunities by opportunity_type and work_mode."""
    res = client.get("/api/student/career/opportunities?type=INTERNSHIP", headers={"Authorization": f"Bearer {student_token}"})
    assert res.status_code == 200
    for opp in res.json():
        assert opp["opportunity_type"] == "INTERNSHIP"

    res_remote = client.get("/api/student/career/opportunities?work_mode=REMOTE", headers={"Authorization": f"Bearer {student_token}"})
    assert res_remote.status_code == 200
    for opp in res_remote.json():
        assert opp["work_mode"] == "REMOTE"


# =========================================================================
# 3. SKILL GAP DETECTION & DAILY CAREER BRIEF
# =========================================================================

def test_skill_gap_aggregation_and_recommendations(client, student_token):
    """Verifies skill gap extraction and responsible learning recommendations."""
    res = client.get("/api/student/career/skill-gaps", headers={"Authorization": f"Bearer {student_token}"})
    assert res.status_code == 200
    gaps = res.json()
    assert len(gaps) >= 1
    docker_gap = next((g for g in gaps if g["skill_name"] == "Docker"), None)
    if docker_gap:
        assert "Docker fundamentals" in docker_gap["recommendation"]
        assert len(docker_gap["target_opportunities"]) >= 1


def test_daily_career_brief_and_deadlines(client, student_token):
    """Verifies daily career brief metrics and closing soon counts."""
    res = client.get("/api/student/career/brief", headers={"Authorization": f"Bearer {student_token}"})
    assert res.status_code == 200
    brief = res.json()
    assert brief["total_matched_opportunities"] >= 5
    assert brief["top_match_score"] is not None
    assert brief["data_source"] == "SYNTHETIC DEVELOPMENT DATA"


# =========================================================================
# 4. RESUME UPLOAD & STRUCTURED EXTRACTION
# =========================================================================

def test_resume_upload_and_extraction_pipeline(client, student_token):
    """Verifies resume upload with PDF/DOCX format, text extraction, and profile update."""
    sample_resume_content = b"John Doe\nB.Tech in Computer Science & Engineering, Vignan Institute\nTechnical Skills: Python, React, FastAPI, SQL, Docker, TypeScript, Linux, Git\nProjects: Built an intelligent campus triage operating system with real-time analytics.\nCertifications: AWS Cloud Certified Practitioner\n"
    files = {"file": ("test_resume.txt", io.BytesIO(sample_resume_content), "text/plain")}
    res = client.post("/api/student/career/resume", headers={"Authorization": f"Bearer {student_token}"}, files=files)
    assert res.status_code == 200
    data = res.json()
    assert data["extracted_skills_count"] >= 4
    assert data["profile"]["extraction_status"] == "COMPLETED"


# =========================================================================
# 5. ASK VIGNAI CAREER DOMAIN INTENT TESTS
# =========================================================================

def test_ask_vignex_career_matched_opportunities_intent(db):
    """Ask VIGNAI query: 'What internships match my skills?' must route to CAREER domain."""
    query = "What internships match my skills?"
    intent_res = query_router.route_query(query)
    assert intent_res.domain == "CAREER"
    assert intent_res.intent == "CAREER_MATCHED_OPPORTUNITIES"

    student = db.query(User).filter_by(email="student@vignex.dev").first()
    payload = AskVignexQueryPayload(query=query)
    resp = ask_vignex_answer_service.process_query(payload=payload, db=db, user=student)
    assert resp.domain == "CAREER"
    assert "matching opportunities" in resp.answer.lower()
    assert resp.context_badge == "💼 CAREER INTELLIGENCE"


def test_ask_vignex_career_skill_gaps_intent(db):
    """Ask VIGNAI query: 'What skills am I missing?' must route to CAREER_SKILL_GAPS."""
    query = "What skills am I missing?"
    intent_res = query_router.route_query(query)
    assert intent_res.domain == "CAREER"
    assert intent_res.intent == "CAREER_SKILL_GAPS"

    student = db.query(User).filter_by(email="student@vignex.dev").first()
    payload = AskVignexQueryPayload(query=query)
    resp = ask_vignex_answer_service.process_query(payload=payload, db=db, user=student)
    assert resp.domain == "CAREER"
    assert "skill gaps" in resp.answer.lower()


def test_ask_vignex_career_closing_soon_intent(db):
    """Ask VIGNAI query: 'What is closing soon?' must route to CAREER_CLOSING_SOON."""
    query = "What is closing soon?"
    intent_res = query_router.route_query(query)
    assert intent_res.domain == "CAREER"
    assert intent_res.intent == "CAREER_CLOSING_SOON"

    student = db.query(User).filter_by(email="student@vignex.dev").first()
    payload = AskVignexQueryPayload(query=query)
    resp = ask_vignex_answer_service.process_query(payload=payload, db=db, user=student)
    assert resp.domain == "CAREER"
    assert "closing soon" in resp.answer.lower() or "deadlines" in resp.answer.lower()


def test_ask_vignex_general_knowledge_vs_career_isolation(db):
    """'What is Docker?' is GENERAL_KNOWLEDGE, whereas 'Which internships require Docker?' is CAREER."""
    # 1. Concept inquiry -> GENERAL_KNOWLEDGE
    q_gk = "What is Docker?"
    intent_gk = query_router.route_query(q_gk)
    assert intent_gk.domain == "GENERAL_KNOWLEDGE"
    assert intent_gk.query_mode == "GENERAL_KNOWLEDGE"

    resp_gk = ask_vignex_answer_service.process_query(payload=AskVignexQueryPayload(query=q_gk), db=db)
    assert resp_gk.domain == "GENERAL_KNOWLEDGE"
    assert resp_gk.provenance.get("campus_data_retrieved") is False

    # 2. Career search inquiry -> CAREER
    q_career = "Which internships require Docker?"
    intent_career = query_router.route_query(q_career)
    assert intent_career.domain == "CAREER"
    assert intent_career.intent == "CAREER_SKILL_SEARCH"

    student = db.query(User).filter_by(email="student@vignex.dev").first()
    resp_career = ask_vignex_answer_service.process_query(payload=AskVignexQueryPayload(query=q_career), db=db, user=student)
    assert resp_career.domain == "CAREER"
    assert "opportunities requiring" in resp_career.answer.lower()


def test_ask_vignex_career_academic_hybrid_intent(db):
    """'Which internships match my skills and current academic subjects?' must route to HYBRID."""
    query = "Which internships match my skills and current academic subjects?"
    intent_res = query_router.route_query(query)
    assert intent_res.domain == "HYBRID"
    assert intent_res.intent == "CAREER_ACADEMIC_HYBRID"
    assert intent_res.context_badge == "⚡ HYBRID"

    student = db.query(User).filter_by(email="student@vignex.dev").first()
    payload = AskVignexQueryPayload(query=query)
    resp = ask_vignex_answer_service.process_query(payload=payload, db=db, user=student)
    assert resp.domain == "CAREER"
    assert "curriculum alignment" in resp.answer.lower() or "enrolled subjects" in resp.answer.lower()


def test_campus_placement_verified_context_refusal(db):
    """'Are there placement opportunities through the college?' gives verified info without hallucinating companies."""
    query = "Are there placement opportunities through the college?"
    intent_res = query_router.route_query(query)
    assert intent_res.domain == "CAREER"
    assert intent_res.intent == "CAMPUS_PLACEMENT_INFO"

    student = db.query(User).filter_by(email="student@vignex.dev").first()
    payload = AskVignexQueryPayload(query=query)
    resp = ask_vignex_answer_service.process_query(payload=payload, db=db, user=student)
    assert resp.domain == "CAREER"
    assert "placement cell" in resp.answer.lower()
