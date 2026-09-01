import pytest
from app.database import SessionLocal
from app.services.ask_vignex.query_router import query_router
from app.services.ask_vignex.answer_service import ask_vignex_answer_service
from app.models.user import User
from app.models.career import CareerProfile, Opportunity, OpportunitySkill
from app.models.student import StudentProfile
from datetime import datetime, timedelta

@pytest.fixture(scope="module")
def db():
    session = SessionLocal()
    yield session
    session.close()


def test_career_intent_classification_new_jobs():
    queries = [
        "are they any new jobs",
        "are there any new jobs",
        "any new internships",
        "show me new opportunities",
        "what jobs match my skills",
        "what jobs are available",
        "show me new jobs",
        "any new career opportunities",
        "what opportunities are available",
        "are there new internships for me",
        "find me jobs",
        "show me jobs",
        "any openings for me",
        "what new opportunities can I apply for",
        "are there any new jobs I can apply for",
        "any new job",
        "new jobs?",
        "jobs available?",
        "any jobs for me",
        "got any jobs?",
        "anything new for me?",
        "any openings?",
        "what's new in careers?",
        "anything I can apply for?",
    ]
    for q in queries:
        res = query_router.route_query(q)
        assert res.domain == "CAREER", f"Query '{q}' expected CAREER domain, got {res.domain}"
        assert res.intent == "CAREER_MATCHED_OPPORTUNITIES", f"Query '{q}' expected CAREER_MATCHED_OPPORTUNITIES, got {res.intent}"

def test_conceptual_definition_queries_stay_general_knowledge():
    conceptual_queries = [
        "what is a job",
        "what is an internship",
        "explain internships",
        "define internship",
        "what does a software engineer do",
        "what is machine learning",
        "explain recursion in C",
    ]
    for q in conceptual_queries:
        res = query_router.route_query(q)
        assert res.domain == "GENERAL_KNOWLEDGE", f"Query '{q}' expected GENERAL_KNOWLEDGE, got {res.domain}"
        assert res.intent == "GENERAL_KNOWLEDGE", f"Query '{q}' expected GENERAL_KNOWLEDGE, got {res.intent}"

def test_career_matched_response_contains_actual_data(db):
    from app.services.ask_vignex.schemas import AskVignexQueryPayload
    # Ensure student user exists
    user = db.query(User).filter_by(email="student@vignex.dev").first()
    assert user is not None, "Student user not found"

    payload = AskVignexQueryPayload(query="are they any new jobs")
    resp = ask_vignex_answer_service.process_query(
        payload=payload,
        db=db,
        user=user
    )

    assert resp.domain == "CAREER"
    assert resp.intent == "CAREER_MATCHED_OPPORTUNITIES"
    assert "opportunities" in resp.answer.lower() or "yes — i found" in resp.answer.lower()
    assert len(resp.action_links) > 0
    assert resp.action_links[0].url.startswith("/student/career")

    # Verify no developer diagnostic jargon is exposed
    raw_text = resp.answer.lower()
    forbidden_terms = [
        "evaluated under vignai general knowledge mode",
        "independent of campus operational databases",
        "general knowledge overview",
        "synthetic development records",
    ]
    for term in forbidden_terms:
        assert term not in raw_text, f"Forbidden developer diagnostic term '{term}' leaked in response"

def test_general_knowledge_response_cleanliness(db):
    from app.services.ask_vignex.schemas import AskVignexQueryPayload
    user = db.query(User).filter_by(email="student@vignex.dev").first()
    payload = AskVignexQueryPayload(query="what is an internship")
    resp = ask_vignex_answer_service.process_query(
        payload=payload,
        db=db,
        user=user
    )

    assert resp.domain == "GENERAL_KNOWLEDGE"
    assert "internship" in resp.answer.lower()
    assert "evaluated under vignai general knowledge mode" not in resp.answer.lower()
    assert len(resp.limitations) == 0


