"""
Comprehensive Regression Test Suite for VIGNEX Architecture Hardening:
1. Category Taxonomy Consistency (Official 7 top-level categories)
2. Heuristic Provider Classification (Faculty Conduct -> SENSITIVE_GRIEVANCE, Wi-Fi -> TECHNOLOGY, etc.)
3. Deterministic Routing Policy Engine (CAMPUS_OPERATIONS non-fallthrough, Transport, IT, Security, Hostel)
4. Sensitive Grievance Isolation & Access Control (Restricted overrides, Subject faculty denied access)
"""

import os
import sys
import pytest
import asyncio
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add backend directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.database import Base
from app.models import Complaint, ComplaintAIAnalysis, ComplaintRouting, RoutingAudit, User, FacultyProfile, Department
from app.config.categories import CATEGORY_TAXONOMY, normalize_category_name
from app.services.ai.provider import LocalHeuristicProvider, VALID_CATEGORIES
from app.services.routing.routing_policy import evaluate_routing_policy
from app.routers.faculty import check_faculty_case_access

# Setup in-memory SQLite DB for testing
TEST_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="module")
def db_session():
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()

    # Create CSE department
    cse_dept = Department(id=1, name="Computer Science & Engineering", code="CSE")
    session.add(cse_dept)
    session.commit()

    # Create test users
    student = User(id=1, email="student@vignex.dev", password_hash="mock_hash", role="student", is_active=True)
    faculty_user = User(id=2, email="faculty@vignex.dev", password_hash="mock_hash", role="faculty", is_active=True)
    mgmt_user = User(id=3, email="mgmt@vignex.dev", password_hash="mock_hash", role="management", is_active=True)
    
    faculty_profile = FacultyProfile(id=1, user_id=2, department_id=1, employee_id="FAC001", designation="Assistant Professor")
    faculty_user.faculty_profile = faculty_profile

    session.add_all([student, faculty_user, mgmt_user, faculty_profile])
    session.commit()

    yield session
    session.close()
    Base.metadata.drop_all(bind=engine)


# =========================================================================
# TEST SUITE 1: CATEGORY TAXONOMY CONSISTENCY
# =========================================================================

def test_category_taxonomy_official_keys():
    """Verify that the official 7 top-level category keys exist in the central config."""
    expected_categories = {
        "ACADEMIC",
        "INFRASTRUCTURE",
        "TECHNOLOGY",
        "CAMPUS_OPERATIONS",
        "STUDENT_SERVICES",
        "SENSITIVE_GRIEVANCE",
        "OTHER",
    }
    assert set(CATEGORY_TAXONOMY.keys()) == expected_categories
    assert set(VALID_CATEGORIES) == expected_categories


def test_category_normalization_mappings():
    """Verify normalize_category_name correctly maps subcategories and variations to official top-level keys."""
    assert normalize_category_name("Wi-Fi / Network") == "TECHNOLOGY"
    assert normalize_category_name("wifi") == "TECHNOLOGY"
    assert normalize_category_name("Transport") == "CAMPUS_OPERATIONS"
    assert normalize_category_name("Hostel") == "CAMPUS_OPERATIONS"
    assert normalize_category_name("Cleanliness") == "CAMPUS_OPERATIONS"
    assert normalize_category_name("Security") == "CAMPUS_OPERATIONS"
    assert normalize_category_name("Laboratory") == "INFRASTRUCTURE"
    assert normalize_category_name("Classroom") == "INFRASTRUCTURE"
    assert normalize_category_name("Projector") == "INFRASTRUCTURE"
    assert normalize_category_name("Electrical") == "INFRASTRUCTURE"
    assert normalize_category_name("Faculty Conduct") in ["ACADEMIC", "SENSITIVE_GRIEVANCE"]
    assert normalize_category_name("Scholarships") == "STUDENT_SERVICES"
    assert normalize_category_name("Unknown Strange Category") == "OTHER"


# =========================================================================
# TEST SUITE 2: HEURISTIC PROVIDER CLASSIFICATION
# =========================================================================

@pytest.mark.asyncio
async def test_heuristic_faculty_conduct_classification():
    """Heuristic provider must classify conduct allegations as SENSITIVE_GRIEVANCE, NEVER Academic."""
    provider = LocalHeuristicProvider()

    # Example 1: Explicit inappropriate conduct report
    res1 = await provider.analyze_complaint(
        description="I want to report inappropriate conduct by a faculty member.",
        location="Faculty Block",
    )
    assert res1.category == "SENSITIVE_GRIEVANCE"
    assert res1.category != "ACADEMIC"
    assert res1.category != "OTHER"
    assert res1.subcategory == "Faculty Conduct"
    assert res1.sensitivity == "HIGH_SENSITIVITY"
    assert res1.suggested_route_type == "AUTHORIZED_GRIEVANCE"
    assert res1.department == "Student Affairs"

    # Example 2: Inappropriate language in class
    res2 = await provider.analyze_complaint(
        description="The professor repeatedly uses inappropriate language in class.",
        location="Room 304",
    )
    assert res2.category == "SENSITIVE_GRIEVANCE"
    assert res2.category != "ACADEMIC"
    assert res2.subcategory == "Faculty Conduct"
    assert res2.sensitivity == "HIGH_SENSITIVITY"
    assert res2.suggested_route_type == "AUTHORIZED_GRIEVANCE"


@pytest.mark.asyncio
async def test_heuristic_academic_instruction_classification():
    """Heuristic provider must classify academic scheduling / cancellations as ACADEMIC, NOT sensitive grievance."""
    provider = LocalHeuristicProvider()

    res = await provider.analyze_complaint(
        description="The lecturer keeps cancelling our scheduled class.",
        location="Block A, Room 201",
    )
    assert res.category == "ACADEMIC"
    assert res.category != "SENSITIVE_GRIEVANCE"
    assert res.sensitivity in ["NORMAL", "SENSITIVE"]


@pytest.mark.asyncio
async def test_heuristic_technology_classification():
    """Heuristic provider must classify network/wifi issues as TECHNOLOGY."""
    provider = LocalHeuristicProvider()

    res = await provider.analyze_complaint(
        description="Wi-Fi is disconnecting frequently across Block A 3rd floor.",
        location="Block A",
    )
    assert res.category == "TECHNOLOGY"
    assert res.subcategory == "Wi-Fi / Network"
    assert res.department == "IT"
    assert res.suggested_route_type == "CAMPUS_OPERATIONS"


@pytest.mark.asyncio
async def test_heuristic_infrastructure_classification():
    """Heuristic provider must classify lab projector defects as INFRASTRUCTURE."""
    provider = LocalHeuristicProvider()

    res = await provider.analyze_complaint(
        description="Lab 3 projector lamp is broken and flashing red.",
        location="Lab 3",
    )
    assert res.category == "INFRASTRUCTURE"
    assert res.subcategory == "Projector"
    assert res.department == "CSE"


@pytest.mark.asyncio
async def test_heuristic_campus_operations_classification():
    """Heuristic provider must classify transit, sanitation, security as CAMPUS_OPERATIONS."""
    provider = LocalHeuristicProvider()

    res_bus = await provider.analyze_complaint(
        description="Route 4 campus bus is arriving 45 minutes late every morning.",
        location="North Gate Bus Stop",
    )
    assert res_bus.category == "CAMPUS_OPERATIONS"
    assert res_bus.subcategory == "Transport"
    assert res_bus.department == "Transport"

    res_clean = await provider.analyze_complaint(
        description="2nd floor washroom is uncleaned and has a strong foul odor.",
        location="Block A",
    )
    assert res_clean.category == "CAMPUS_OPERATIONS"
    assert res_clean.subcategory == "Cleanliness"
    assert res_clean.department == "Maintenance"


# =========================================================================
# TEST SUITE 3: DETERMINISTIC ROUTING POLICY ENGINE
# =========================================================================

def test_routing_sensitive_conduct_allegation():
    """Faculty conduct report must route to Authorized Grievance + Management and RESTRICT subject/dept faculty."""
    complaint = Complaint(
        case_id="VX-TEST-01",
        description="Student reporting serious inappropriate conduct by a professor.",
        category="SENSITIVE_GRIEVANCE",
    )
    ai_analysis = ComplaintAIAnalysis(
        category="SENSITIVE_GRIEVANCE",
        subcategory="Faculty Conduct",
        sensitivity="HIGH_SENSITIVITY",
        suggested_route_type="AUTHORIZED_GRIEVANCE",
        department="Student Affairs",
    )

    decision = evaluate_routing_policy(complaint=complaint, ai_analysis=ai_analysis)
    assert decision.policy_validation_result == "RESTRICTED_OVERRIDE"
    assert "Authorized Grievance" in decision.final_route
    assert "Management Oversight" in decision.final_route
    assert "SUBJECT_FACULTY" in decision.restricted_recipients
    assert "DEPARTMENT_FACULTY" in decision.restricted_recipients
    assert any(r["recipient_type"] == "GRIEVANCE_AUTHORITY" for r in decision.primary_recipients)
    assert any(r["recipient_type"] == "MANAGEMENT" for r in decision.secondary_oversight)


def test_routing_transport_campus_operations():
    """Transport complaints must route to Transport Authority, NOT fallback to CSE."""
    complaint = Complaint(
        case_id="VX-TEST-02",
        description="Route 7 bus delay affecting morning commute.",
        category="CAMPUS_OPERATIONS",
    )
    ai_analysis = ComplaintAIAnalysis(
        category="CAMPUS_OPERATIONS",
        subcategory="Transport",
        suggested_route_type="DEPARTMENT_AND_MANAGEMENT",
        department="Transport",
    )

    decision = evaluate_routing_policy(complaint=complaint, ai_analysis=ai_analysis)
    assert decision.policy_validation_result == "VALIDATED"
    assert "Transport Authority" in decision.final_route
    assert decision.primary_recipients[0]["department_code"] == "Transport"
    assert decision.primary_recipients[0]["department_code"] != "CSE"


def test_routing_hostel_campus_operations():
    """Hostel complaints must route to Hostel Administration, NOT fallback to CSE."""
    complaint = Complaint(
        case_id="VX-TEST-03",
        description="Hot water geyser not working in Block B Hostel.",
        category="CAMPUS_OPERATIONS",
    )
    ai_analysis = ComplaintAIAnalysis(
        category="CAMPUS_OPERATIONS",
        subcategory="Hostel",
        suggested_route_type="DEPARTMENT_AND_MANAGEMENT",
        department="Hostel",
    )

    decision = evaluate_routing_policy(complaint=complaint, ai_analysis=ai_analysis)
    assert decision.policy_validation_result == "VALIDATED"
    assert "Hostel Administration" in decision.final_route
    assert decision.primary_recipients[0]["department_code"] == "Hostel"
    assert decision.primary_recipients[0]["department_code"] != "CSE"


def test_routing_technology_wifi():
    """Technology/Wi-Fi complaints must route to IT Operations, NOT academic faculty."""
    complaint = Complaint(
        case_id="VX-TEST-04",
        description="Campus-wide Wi-Fi latency spike.",
        category="TECHNOLOGY",
    )
    ai_analysis = ComplaintAIAnalysis(
        category="TECHNOLOGY",
        subcategory="Wi-Fi / Network",
        suggested_route_type="CAMPUS_OPERATIONS",
        department="IT",
    )

    decision = evaluate_routing_policy(complaint=complaint, ai_analysis=ai_analysis)
    assert decision.policy_validation_result == "VALIDATED"
    assert "Campus Operations (IT)" in decision.final_route
    assert decision.primary_recipients[0]["recipient_type"] == "OPERATIONS"
    assert decision.primary_recipients[0]["department_code"] == "IT"


def test_routing_department_lab_infrastructure():
    """Department-specific lab issues must route to Department Faculty (e.g. CSE) + Management."""
    complaint = Complaint(
        case_id="VX-TEST-05",
        description="CSE Lab 3 projector is not displaying HDMI input.",
        category="INFRASTRUCTURE",
    )
    ai_analysis = ComplaintAIAnalysis(
        category="INFRASTRUCTURE",
        subcategory="Laboratory",
        suggested_route_type="DEPARTMENT_AND_MANAGEMENT",
        department="CSE",
    )

    decision = evaluate_routing_policy(complaint=complaint, ai_analysis=ai_analysis)
    assert decision.policy_validation_result == "VALIDATED"
    assert "CSE Department" in decision.final_route
    assert decision.primary_recipients[0]["department_code"] == "CSE"
    assert decision.primary_recipients[0]["role"] == "faculty"


# =========================================================================
# TEST SUITE 4: PRIVACY & FACULTY ACCESS CONTROL
# =========================================================================

def test_faculty_case_access_isolation(db_session):
    """Faculty member must NOT be granted access to sensitive grievance cases."""
    faculty_user = db_session.query(User).filter(User.role == "faculty").first()

    # Create sensitive grievance complaint
    complaint = Complaint(
        case_id="VX-SENSITIVE-99",
        student_id=1,
        description="Confidential conduct inquiry regarding faculty member.",
        category="SENSITIVE_GRIEVANCE",
    )
    db_session.add(complaint)
    db_session.commit()
    db_session.refresh(complaint)

    # Attach RESTRICTED_OVERRIDE routing audit
    audit = RoutingAudit(
        complaint_id=complaint.id,
        ai_suggested_route="Student Affairs",
        policy_validation_result="RESTRICTED_OVERRIDE",
        final_route="Authorized Grievance Authority + Management Oversight",
        decision_reason="Isolated confidential inquiry",
    )
    db_session.add(audit)
    db_session.commit()

    # Verify check_faculty_case_access denies access
    has_access = check_faculty_case_access(db=db_session, complaint=complaint, faculty_user=faculty_user)
    assert has_access is False
