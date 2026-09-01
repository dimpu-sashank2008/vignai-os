"""
Automated Test Suite for Ask VIGNAI Conversational Intent & Clean User-Facing Response Contract.
Verifies:
1. "hi", "hello", "hey", "good morning" -> CONVERSATIONAL_GREETING (No raw educational template).
2. "thanks", "thank you", "who are you", "what can you do" -> CONVERSATIONAL_GREETING.
3. Compound greeting + question:
   - "hi, what is my attendance?" -> ACADEMIC / STUDENT_ATTENDANCE
   - "hello, are there any internships?" -> CAREER / CAREER_MATCHED_OPPORTUNITIES
   - "hey, what are the biggest campus problems?" -> CAMPUS_INTELLIGENCE / CAMPUS_OVERVIEW
4. Clean General Knowledge:
   - "What is recursion in C?" -> GENERAL_KNOWLEDGE (Clean explanation, no raw headers).
5. Clean Career:
   - "Are there any new jobs?" -> CAREER
6. Clean Campus:
   - "What are the biggest problems on campus?" -> CAMPUS_INTELLIGENCE
7. Clean Simulation:
   - "What if we add one bus?" -> SIMULATION_WHAT_IF
8. Zero diagnostic / internal template leak in user-facing answer text across all domains.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.main import app
from app.database import SessionLocal
from app.models.user import User
from app.services.ask_vignex.query_router import query_router
from app.services.ask_vignex.answer_service import ask_vignex_answer_service
from app.services.ask_vignex.schemas import AskVignexQueryPayload

@pytest.fixture(scope="module")
def client():
    return TestClient(app)

@pytest.fixture(scope="module")
def db():
    session = SessionLocal()
    yield session
    session.close()

@pytest.fixture(scope="module")
def student_user(db: Session):
    return db.query(User).filter_by(role="student").first()

@pytest.fixture(scope="module")
def management_user(db: Session):
    return db.query(User).filter_by(role="management").first()

# TEST 1: Pure Greetings route to CONVERSATIONAL_GREETING
@pytest.mark.parametrize("query_text", [
    "hi",
    "hello",
    "hey",
    "good morning",
    "good evening",
    "hi vignai",
    "hello vignai",
])
def test_pure_greetings_classified_as_conversational(query_text):
    res = query_router.route_query(query_text)
    assert res.intent == "CONVERSATIONAL_GREETING", f"Failed for '{query_text}': got {res.intent}"
    assert res.domain == "CONVERSATIONAL"

# TEST 2: Courtesies and Identity Inquiries route to CONVERSATIONAL_GREETING
@pytest.mark.parametrize("query_text", [
    "thanks",
    "thank you",
    "who are you",
    "what can you do",
    "ok",
    "cool",
])
def test_courtesies_and_capabilities_classified_as_conversational(query_text):
    res = query_router.route_query(query_text)
    assert res.intent == "CONVERSATIONAL_GREETING"
    assert res.domain == "CONVERSATIONAL"

# TEST 3: Greeting response text is natural and free of educational / template noise
def test_greeting_response_cleanliness(db, student_user):
    payload = AskVignexQueryPayload(query="hi")
    res = ask_vignex_answer_service.process_query(payload=payload, db=db, user=student_user)
    
    assert res.intent == "CONVERSATIONAL_GREETING"
    assert res.domain == "CONVERSATIONAL"
    assert "Hi!" in res.answer or "VIGNAI" in res.answer
    assert "### 📖" not in res.answer
    assert "foundational topic in educational" not in res.answer
    assert "KEY COMPUTED FINDINGS" not in res.answer
    assert len(res.key_findings) == 0

# TEST 4: Identity response text is helpful and clean
def test_who_are_you_response_cleanliness(db, student_user):
    payload = AskVignexQueryPayload(query="who are you")
    res = ask_vignex_answer_service.process_query(payload=payload, db=db, user=student_user)
    
    assert res.intent == "CONVERSATIONAL_GREETING"
    assert "VIGNAI" in res.answer
    assert "Academics" in res.answer
    assert "Career" in res.answer
    assert "### 📖" not in res.answer

# TEST 5: Compound greeting + question routes to the actual question domain
def test_compound_greeting_and_question_routing():
    # Academic
    r_acad = query_router.route_query("hi, what is my attendance?")
    assert r_acad.intent == "STUDENT_ATTENDANCE"
    assert r_acad.domain == "ACADEMIC"

    # Career
    r_car = query_router.route_query("hello, are there any internships?")
    assert r_car.intent in ["CAREER_MATCHED_OPPORTUNITIES", "CAREER_SKILL_GAPS"]
    assert r_car.domain == "CAREER"

    # Campus Issues
    r_camp = query_router.route_query("hey, what are the biggest campus problems?")
    assert r_camp.intent in ["CAMPUS_OVERVIEW", "EMERGING_ISSUES"]
    assert r_camp.domain == "CAMPUS_INTELLIGENCE"

# TEST 6: Clean General Knowledge Response for technical inquiries
def test_general_knowledge_technical_cleanliness(db, student_user):
    payload = AskVignexQueryPayload(query="What is recursion in C?")
    res = ask_vignex_answer_service.process_query(payload=payload, db=db, user=student_user)
    
    assert res.intent == "GENERAL_KNOWLEDGE"
    assert "Recursion" in res.answer
    assert "Base Case" in res.answer
    assert "### 📖" not in res.answer
    assert "educational and conceptual topic evaluated under" not in res.answer

# TEST 7: Clean Career Opportunities Response
def test_career_opportunities_cleanliness(db, student_user):
    payload = AskVignexQueryPayload(query="Are there any new jobs?")
    res = ask_vignex_answer_service.process_query(payload=payload, db=db, user=student_user)
    
    assert res.intent == "CAREER_MATCHED_OPPORTUNITIES"
    assert res.domain == "CAREER"
    assert "General Knowledge Overview" not in res.answer
    assert "### 📖" not in res.answer
    assert "KEY COMPUTED FINDINGS" not in res.answer

# TEST 8: Clean Campus Overview Response
def test_campus_overview_cleanliness(db, student_user):
    payload = AskVignexQueryPayload(query="What are the biggest problems on campus?")
    res = ask_vignex_answer_service.process_query(payload=payload, db=db, user=student_user)
    
    assert res.domain == "CAMPUS_INTELLIGENCE"
    assert "VIGNAI Top Emerging Issues" not in res.answer
    assert "active operational patterns" in res.answer or "complaints" in res.answer

# TEST 9: Clean Simulation Response
def test_simulation_cleanliness(db, management_user):
    payload = AskVignexQueryPayload(query="What if we add one bus?")
    res = ask_vignex_answer_service.process_query(payload=payload, db=db, user=management_user)
    
    assert res.intent == "SIMULATION_WHAT_IF"
    assert res.domain == "SIMULATIONS"
    assert "General Knowledge Overview" not in res.answer
    assert "KEY COMPUTED FINDINGS" not in res.answer

# TEST 10: Zero Diagnostic Heading Leakage across multiple standard queries
@pytest.mark.parametrize("query_text", [
    "hi",
    "hello",
    "What is photosynthesis?",
    "What is my attendance?",
    "Are there any new jobs?",
    "What are the biggest problems on campus?",
])
def test_no_forbidden_diagnostic_text_in_answer(db, student_user, query_text):
    payload = AskVignexQueryPayload(query=query_text)
    res = ask_vignex_answer_service.process_query(payload=payload, db=db, user=student_user)
    
    # Assert answer text does not contain raw debug/internal labels
    forbidden_tokens = [
        "### 📖 General Knowledge Overview",
        "KEY COMPUTED FINDINGS",
        "Data Limitations",
        "AI Interpretation",
        "educational and conceptual topic evaluated under",
        "independent of campus operational databases",
    ]
    for token in forbidden_tokens:
        assert token not in res.answer, f"Forbidden token '{token}' found in answer for query '{query_text}'"
