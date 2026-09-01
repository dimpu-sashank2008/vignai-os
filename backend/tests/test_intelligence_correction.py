"""
Comprehensive automated tests for VIGNEX Intelligence Correction:
1. Ask VIGNEX Intent Safety & Query Mode Separation (General Knowledge vs Campus Data)
2. Related Complaint Grouping Layer (5 Block A complaints cluster into 1 group, originals preserved)
3. Deterministic Priority Sorting (Critical > High > Medium > Low + tiebreaker hierarchy)
4. Explainability Signals and Student Privacy Protection
"""

import os
import sys
import pytest
from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add backend directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.database import Base
from app.models import Complaint, ComplaintAIAnalysis, ComplaintRouting, User
from app.services.ask_vignex.query_router import query_router
from app.services.ask_vignex.answer_service import ask_vignex_answer_service
from app.services.ask_vignex.schemas import AskVignexQueryPayload
from app.services.intelligence.grouping_service import grouping_service
from app.services.intelligence.sorting_utils import sort_complaints_by_priority, sort_groups_by_priority

# Setup in-memory SQLite DB for testing
TEST_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="module")
def db_session():
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    
    # Create test users
    student1 = User(id=1, email="student1@university.edu", password_hash="mock_hash", role="student", is_active=True)
    student2 = User(id=2, email="student2@university.edu", password_hash="mock_hash", role="student", is_active=True)
    mgmt = User(id=3, email="mgmt@university.edu", password_hash="mock_hash", role="management", is_active=True)
    faculty = User(id=4, email="faculty@university.edu", password_hash="mock_hash", role="faculty", is_active=True)
    session.add_all([student1, student2, mgmt, faculty])
    session.commit()

    yield session
    session.close()
    Base.metadata.drop_all(bind=engine)


# =========================================================================
# TEST SUITE 1: ASK VIGNEX INTENT SAFETY & QUERY MODES
# =========================================================================

def test_ask_vignex_general_knowledge_photosynthesis(db_session):
    """General knowledge query: 'What is photosynthesis?' must NOT query database or return cases."""
    query = "What is photosynthesis?"
    payload = AskVignexQueryPayload(query=query)
    
    # Verify Router Classification
    intent_res = query_router.route_query(query)
    assert intent_res.query_mode == "GENERAL_KNOWLEDGE"
    assert intent_res.intent == "GENERAL_KNOWLEDGE"

    # Verify Answer Generation
    resp = ask_vignex_answer_service.process_query(payload=payload, db=db_session)
    assert resp.query_mode == "GENERAL_KNOWLEDGE"
    assert "photosynthesis" in resp.answer.lower()
    assert len(resp.supporting_case_ids) == 0
    assert len(resp.supporting_cases) == 0
    assert resp.provenance.get("campus_data_retrieved") is False


def test_ask_vignex_general_knowledge_recursion(db_session):
    """General knowledge query: 'Explain recursion in C.' must be GENERAL_KNOWLEDGE."""
    query = "Explain recursion in C."
    payload = AskVignexQueryPayload(query=query)
    
    intent_res = query_router.route_query(query)
    assert intent_res.query_mode == "GENERAL_KNOWLEDGE"

    resp = ask_vignex_answer_service.process_query(payload=payload, db=db_session)
    assert resp.query_mode == "GENERAL_KNOWLEDGE"
    assert "recursion" in resp.answer.lower()
    assert len(resp.supporting_case_ids) == 0


def test_ask_vignex_general_knowledge_wifi(db_session):
    """General knowledge query: 'Explain Wi-Fi.' must be GENERAL_KNOWLEDGE, not campus complaints."""
    query = "Explain Wi-Fi."
    payload = AskVignexQueryPayload(query=query)
    
    intent_res = query_router.route_query(query)
    assert intent_res.query_mode == "GENERAL_KNOWLEDGE"

    resp = ask_vignex_answer_service.process_query(payload=payload, db=db_session)
    assert resp.query_mode == "GENERAL_KNOWLEDGE"
    assert "802.11" in resp.answer or "wireless" in resp.answer.lower()
    assert len(resp.supporting_case_ids) == 0


def test_ask_vignex_general_knowledge_maintenance_costs(db_session):
    """General inquiry: 'How can colleges reduce maintenance costs?' must be GENERAL_KNOWLEDGE."""
    query = "How can colleges reduce maintenance costs?"
    payload = AskVignexQueryPayload(query=query)
    
    intent_res = query_router.route_query(query)
    assert intent_res.query_mode == "GENERAL_KNOWLEDGE"

    resp = ask_vignex_answer_service.process_query(payload=payload, db=db_session)
    assert resp.query_mode == "GENERAL_KNOWLEDGE"
    assert len(resp.supporting_case_ids) == 0


def test_ask_vignex_campus_data_mode(db_session):
    """Campus specific queries must route to VIGNEX_DATA mode."""
    campus_queries = [
        "What are the biggest problems on campus?",
        "Why is Block A becoming a risk?",
        "How many transport cases are unresolved?",
        "Which department has the most unresolved cases?",
        "Is there a recurring Wi-Fi issue in Block A?",
    ]
    for q in campus_queries:
        intent_res = query_router.route_query(q)
        assert intent_res.query_mode == "VIGNEX_DATA", f"Query failed VIGNEX_DATA classification: {q}"


# =========================================================================
# TEST SUITE 2: RELATED COMPLAINT GROUPING & SINGLE SOURCE OF TRUTH
# =========================================================================

def test_five_block_a_complaints_grouping(db_session):
    """5 Block A Wi-Fi complaints must cluster into 1 POTENTIALLY RELATED group,
    with all 5 original complaints kept intact and distinct.
    """
    now = datetime.utcnow()
    test_complaints = [
        Complaint(
            id=101,
            case_id="VX-839331",
            student_id=1,
            title="Wi-Fi connection drops in Block A",
            description="The campus Wi-Fi keeps disconnecting repeatedly during morning lectures in Block A.",
            location="Block A",
            category="Wi-Fi / Network",
            priority="MEDIUM",
            status="SUBMITTED",
            identity_protected=True,
            created_at=now - timedelta(hours=5),
            updated_at=now - timedelta(hours=5),
        ),
        Complaint(
            id=102,
            case_id="VX-839332",
            student_id=2,
            title="Block A 2nd floor network failure",
            description="Wi-Fi signal is extremely weak and drops constantly in Block A 2nd floor classrooms.",
            location="Block A",
            category="Wi-Fi / Network",
            priority="HIGH",
            status="UNDER_REVIEW",
            identity_protected=False,
            created_at=now - timedelta(hours=4),
            updated_at=now - timedelta(hours=4),
        ),
        Complaint(
            id=103,
            case_id="VX-839333",
            student_id=1,
            title="No internet access in Block A Room 204",
            description="Wi-Fi router in Block A Room 204 does not assign IP addresses and drops connection.",
            location="Block A",
            category="Wi-Fi / Network",
            priority="MEDIUM",
            status="SUBMITTED",
            identity_protected=True,
            created_at=now - timedelta(hours=3),
            updated_at=now - timedelta(hours=3),
        ),
        Complaint(
            id=104,
            case_id="VX-839334",
            student_id=2,
            title="Block A Wi-Fi down",
            description="Cannot connect to Wi-Fi network in Block A wing. Entire class is affected.",
            location="Block A",
            category="Wi-Fi / Network",
            priority="MEDIUM",
            status="SUBMITTED",
            identity_protected=False,
            created_at=now - timedelta(hours=2),
            updated_at=now - timedelta(hours=2),
        ),
        Complaint(
            id=105,
            case_id="VX-839335",
            student_id=1,
            title="Intermittent Wi-Fi in Block A hallway",
            description="Wi-Fi connection keeps dropping when moving through Block A corridors.",
            location="Block A",
            category="Wi-Fi / Network",
            priority="LOW",
            status="SUBMITTED",
            identity_protected=True,
            created_at=now - timedelta(hours=1),
            updated_at=now - timedelta(hours=1),
        ),
    ]

    # Cluster into RelatedCaseGroups
    groups = grouping_service.build_case_groups(complaints=test_complaints, threshold=0.30)
    
    # Assertions
    assert len(groups) == 1, f"Expected 1 grouped cluster for 5 Block A complaints, got {len(groups)}"
    grp = groups[0]
    
    assert grp.grouping_label == "POTENTIALLY RELATED"
    assert grp.case_count == 5
    assert grp.location == "Block A"
    assert "Wi-Fi" in grp.category or "Network" in grp.category
    
    # Priority check: Max individual is HIGH, volume is 5 -> Group priority is HIGH
    assert grp.priority == "HIGH"

    # Explainability Signals Check
    signal_names = [s.name for s in grp.explainability_signals]
    assert "Shared Location" in signal_names
    assert "Category Match" in signal_names

    # Underlying cases integrity check: All 5 cases present with their exact case IDs
    case_ids = [c.case_id for c in grp.cases]
    assert set(case_ids) == {"VX-839331", "VX-839332", "VX-839333", "VX-839334", "VX-839335"}

    # Privacy verification: Protected cases have reporter_visibility = "IDENTITY_PROTECTED"
    protected_cases = [c for c in grp.cases if c.identity_protected]
    assert len(protected_cases) == 3
    for pc in protected_cases:
        assert pc.reporter_visibility == "IDENTITY_PROTECTED"
        assert pc.reporter_email is None


# =========================================================================
# TEST SUITE 3: DETERMINISTIC PRIORITY SORTING
# =========================================================================

def test_deterministic_priority_sorting():
    """Complaints must sort strictly CRITICAL > HIGH > MEDIUM > LOW."""
    now = datetime.utcnow()
    c_low = Complaint(id=1, case_id="C-LOW", priority="LOW", status="SUBMITTED", created_at=now - timedelta(days=1))
    c_med = Complaint(id=2, case_id="C-MED", priority="MEDIUM", status="SUBMITTED", created_at=now - timedelta(days=2))
    c_high = Complaint(id=3, case_id="C-HIGH", priority="HIGH", status="SUBMITTED", created_at=now - timedelta(days=3))
    c_crit = Complaint(id=4, case_id="C-CRIT", priority="CRITICAL", status="SUBMITTED", created_at=now - timedelta(days=4))

    raw_list = [c_low, c_med, c_crit, c_high]
    sorted_list = sort_complaints_by_priority(raw_list)

    assert [c.case_id for c in sorted_list] == ["C-CRIT", "C-HIGH", "C-MED", "C-LOW"]


def test_priority_tie_breaking_order():
    """Within same priority, unresolved older cases or higher impact should rank first."""
    now = datetime.utcnow()
    c_high_resolved = Complaint(id=1, case_id="HIGH-RES", priority="HIGH", status="RESOLVED", created_at=now - timedelta(days=1))
    c_high_unresolved_recent = Complaint(id=2, case_id="HIGH-UNRES-REC", priority="HIGH", status="SUBMITTED", created_at=now - timedelta(hours=2))
    c_high_unresolved_older = Complaint(id=3, case_id="HIGH-UNRES-OLD", priority="HIGH", status="SUBMITTED", created_at=now - timedelta(days=5))

    sorted_list = sort_complaints_by_priority([c_high_resolved, c_high_unresolved_recent, c_high_unresolved_older])

    # Older unresolved should precede recent unresolved, which precedes resolved
    assert sorted_list[0].case_id == "HIGH-UNRES-OLD"
    assert sorted_list[1].case_id == "HIGH-UNRES-REC"
    assert sorted_list[2].case_id == "HIGH-RES"


if __name__ == "__main__":
    pytest.main(["-v", __file__])
