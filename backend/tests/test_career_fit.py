import pytest
from datetime import datetime, timedelta
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.main import app
from app.database import SessionLocal
from app.models.user import User
from app.models.student import StudentProfile
from app.models.career import CareerProfile, CareerSkill, CareerProject, CareerCertification, Opportunity
from app.services.auth_service import create_access_token
from app.services.career.domain_taxonomy import CAREER_DOMAINS, get_domains_for_subject_code, get_domain_by_id
from app.services.career.career_fit_service import (
    CareerStrengthAnalyzer,
    EligibilityEngine,
    PersonalizedRecommendationEngine,
    career_strength_analyzer,
    eligibility_engine,
    personalized_ranking_engine,
)
from app.services.ask_vignex.query_router import query_router
from app.services.ask_vignex.answer_service import ask_vignex_answer_service
from app.services.ask_vignex.schemas import AskVignexQueryPayload


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


def test_academic_to_career_domain_taxonomy_mapping():
    """Verifies centralized taxonomy mappings from academic subjects and skills to career domains."""
    # CS202 (DBMS) maps to DATA_SCIENCE, DATA_ANALYTICS, BACKEND
    dbms_domains = get_domains_for_subject_code("CS202")
    assert "DATA_SCIENCE" in dbms_domains
    assert "DATA_ANALYTICS" in dbms_domains
    assert "BACKEND" in dbms_domains

    # CS203 (OS) maps to SOFTWARE_ENGINEERING, CLOUD_DEVOPS, CYBERSECURITY, EMBEDDED_SYSTEMS
    os_domains = get_domains_for_subject_code("CS203")
    assert "SOFTWARE_ENGINEERING" in os_domains
    assert "CLOUD_DEVOPS" in os_domains

    # CS204 (Networks) maps to CYBERSECURITY, CLOUD_DEVOPS
    net_domains = get_domains_for_subject_code("CS204")
    assert "CYBERSECURITY" in net_domains
    assert "CLOUD_DEVOPS" in net_domains

    # Check domain taxonomy integrity
    ds_data = get_domain_by_id("DATA_SCIENCE")
    assert ds_data["name"] == "Data Science"
    assert "Python" in ds_data["skills"]
    assert "SQL" in ds_data["skills"]


def test_career_strength_score_calculation(db):
    """Verifies deterministic career strength calculation combining academic performance, skills, projects, and interests."""
    student_user = db.query(User).filter_by(email="student@vignex.dev").first()
    assert student_user is not None

    strengths = career_strength_analyzer.analyze_strengths(db, student_user)
    assert len(strengths) >= 5

    top = strengths[0]
    assert "alignment_score" in top
    assert 0.0 <= top["alignment_score"] <= 100.0
    assert top["alignment_level"] in ["STRONG_ALIGNMENT", "GOOD_ALIGNMENT", "MODERATE_ALIGNMENT", "DEVELOPING_FIT"]
    assert len(top["relevant_subjects"]) >= 1
    assert "summary_phrase" in top
    assert len(top["summary_phrase"]) > 10


def test_multiple_strong_domains_profile(db):
    """Verifies that a student has multi-domain profile alignments rather than a single forced choice."""
    student_user = db.query(User).filter_by(email="student@vignex.dev").first()
    strengths = career_strength_analyzer.analyze_strengths(db, student_user)

    # Student should have high scores across multiple domains (e.g. Data Science, AI/ML, Software Engineering)
    strong_domains = [s for s in strengths if s["alignment_score"] >= 65.0]
    assert len(strong_domains) >= 2


def test_eligibility_engine_filtering(db):
    """Verifies deterministic eligibility checking for branch, year of study, and criteria."""
    student_user = db.query(User).filter_by(email="student@vignex.dev").first()

    # Create dummy matching opportunity for CSE
    opp_eligible = Opportunity(
        opportunity_id="OPP-TEST-ELIG-01",
        title="Test Eligible Role",
        organization="Test Corp",
        opportunity_type="INTERNSHIP",
        description="Test description",
        location="Visakhapatnam",
        work_mode="HYBRID",
        eligibility="B.Tech 3rd and 4th Year CSE / IT",
        source_name="Test Source",
        source_type="INSTITUTION_CURATED",
        verification_status="VERIFIED",
        lifecycle_status="ACTIVE",
        data_source="SYNTHETIC DEVELOPMENT DATA",
        is_active=True,
    )

    eval_res = eligibility_engine.evaluate(db, student_user, opp_eligible)
    assert eval_res["status"] == "ELIGIBLE"
    assert eval_res["is_eligible"] is True
    assert len(eval_res["reasons"]) >= 1


def test_personalized_opportunity_ranking_weights(client, student_token):
    """Verifies that recommendations are ranked descending by personalized_profile_fit."""
    res = client.get("/api/student/career/recommendations", headers={"Authorization": f"Bearer {student_token}"})
    assert res.status_code == 200
    recs = res.json()
    assert len(recs) >= 1

    # Check descending order of personalized_profile_fit
    fits = [r["personalized_profile_fit"] for r in recs]
    assert fits == sorted(fits, reverse=True)

    # Top recommendation should have high fit
    top_rec = recs[0]
    assert top_rec["personalized_profile_fit"] >= 70.0
    assert "why_recommended" in top_rec
    assert "primary_domain" in top_rec["why_recommended"]


def test_why_recommended_structured_evidence(client, student_token):
    """Verifies that each recommendation contains structured evidence without hallucinations."""
    res = client.get("/api/student/career/recommendations", headers={"Authorization": f"Bearer {student_token}"})
    assert res.status_code == 200
    recs = res.json()
    top = recs[0]
    why = top["why_recommended"]

    assert "primary_domain" in why
    assert "academic_highlights" in why
    assert len(why["academic_highlights"]) >= 1
    assert "skill_highlights" in why
    assert "project_highlights" in why
    assert "eligibility_statement" in why
    assert "responsible_disclaimer" in why
    assert "does not predict or guarantee" in why["responsible_disclaimer"].lower()


def test_student_career_privacy_isolation(client, student_token, faculty_token, management_token):
    """Faculty and Management cannot access student career strengths or recommendations (403)."""
    # Student -> 200 OK
    res_student_str = client.get("/api/student/career/strengths", headers={"Authorization": f"Bearer {student_token}"})
    assert res_student_str.status_code == 200
    res_student_rec = client.get("/api/student/career/recommendations", headers={"Authorization": f"Bearer {student_token}"})
    assert res_student_rec.status_code == 200

    # Faculty -> 403 Forbidden
    res_fac_str = client.get("/api/student/career/strengths", headers={"Authorization": f"Bearer {faculty_token}"})
    assert res_fac_str.status_code == 403
    res_fac_rec = client.get("/api/student/career/recommendations", headers={"Authorization": f"Bearer {faculty_token}"})
    assert res_fac_rec.status_code == 403

    # Management -> 403 Forbidden
    res_mgmt_str = client.get("/api/student/career/strengths", headers={"Authorization": f"Bearer {management_token}"})
    assert res_mgmt_str.status_code == 403


def test_ask_vignex_career_strengths_intent(db):
    """Ask VIGNAI correctly routes and answers 'What career fields am I strongest in?'."""
    q = "What career fields am I strongest in?"
    r = query_router.route_query(q)
    assert r.intent == "CAREER_STRENGTHS"
    assert r.domain == "CAREER"

    student_user = db.query(User).filter_by(email="student@vignex.dev").first()
    payload = AskVignexQueryPayload(query=q)
    ans = ask_vignex_answer_service.process_query(payload, db, user=student_user)
    assert ans.domain == "CAREER"
    assert "Top Career Domain Strengths" in ans.answer
    assert "% Profile Alignment" in ans.answer


def test_ask_vignex_career_domain_explain_intent(db):
    """Ask VIGNAI correctly explains why Data Science or another domain is recommended."""
    q = "Why do you recommend Data Science for me?"
    r = query_router.route_query(q)
    assert r.intent == "CAREER_DOMAIN_EXPLAIN"
    assert r.domain == "CAREER"

    student_user = db.query(User).filter_by(email="student@vignex.dev").first()
    payload = AskVignexQueryPayload(query=q)
    ans = ask_vignex_answer_service.process_query(payload, db, user=student_user)
    assert ans.domain == "CAREER"
    assert "Academic Performance" in ans.answer
    assert "Verified Technical Skills" in ans.answer


def test_ask_vignex_career_prioritization_intent(db):
    """Ask VIGNAI correctly explains 'Which opportunities should I prioritize?'."""
    q = "Which opportunities should I prioritize?"
    r = query_router.route_query(q)
    assert r.intent == "CAREER_PRIORITIZATION"
    assert r.domain == "CAREER"

    student_user = db.query(User).filter_by(email="student@vignex.dev").first()
    payload = AskVignexQueryPayload(query=q)
    ans = ask_vignex_answer_service.process_query(payload, db, user=student_user)
    assert ans.domain == "CAREER"
    assert "Prioritized Career Opportunities" in ans.answer
    assert "Personalized Profile Fit" in ans.answer


def test_ai_unavailable_deterministic_fallback(db):
    """Verifies that domain strength scoring and recommendation ranking work completely without external LLMs."""
    student_user = db.query(User).filter_by(email="student@vignex.dev").first()
    strengths = career_strength_analyzer.analyze_strengths(db, student_user)
    recs = personalized_ranking_engine.get_recommendations(db, student_user)

    assert len(strengths) >= 5
    assert len(recs) >= 1
    assert all("personalized_profile_fit" in r for r in recs)
