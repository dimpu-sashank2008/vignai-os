import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.main import app
from app.database import SessionLocal
from app.models.user import User
from app.services.auth_service import create_access_token
from app.services.viit.context import (
    VIIT_METADATA,
    VIIT_DEPARTMENTS,
    VIIT_EXAM_TERMINOLOGY,
    VIIT_REGULATIONS,
    VIIT_ATTENDANCE_POLICY,
    VIIT_CAMPUS_BUILDINGS,
    VIIT_STATUTORY_CELLS,
    VIIT_TRANSPORT_ROUTES,
    VIIT_PLACEMENT_CONTEXT,
    normalize_department_code,
    normalize_exam_term,
    get_location_canonical_name,
    get_attendance_status_context,
    get_student_regulation_display,
)
from app.services.viit.connectors import mock_viit_connector
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
def student_user(db: Session):
    user = db.query(User).filter_by(email="student@vignex.dev").first()
    if not user:
        pytest.skip("Student user not found in seed data.")
    return user


def test_department_normalization_aliases():
    """Verifies VIIT academic department aliases normalize reliably."""
    # AI & DS aliases
    assert normalize_department_code("AI & DS") == "AI&DS"
    assert normalize_department_code("AI&DS") == "AI&DS"
    assert normalize_department_code("Artificial Intelligence and Data Science") == "AI&DS"
    assert normalize_department_code("aids") == "AI&DS"

    # CSM aliases (CSE AI/ML)
    assert normalize_department_code("CSE AI/ML") == "CSM"
    assert normalize_department_code("CSM") == "CSM"
    assert normalize_department_code("CSE-AI&ML") == "CSM"
    assert normalize_department_code("CSE AIML") == "CSM"

    # CSD aliases (CSE Data Science)
    assert normalize_department_code("CSE Data Science") == "CSD"
    assert normalize_department_code("CSD") == "CSD"
    assert normalize_department_code("cse-ds") == "CSD"

    # CSC aliases (CSE Cyber Security)
    assert normalize_department_code("CSE Cyber Security") == "CSC"
    assert normalize_department_code("CSC") == "CSC"

    # Classical & Postgrad departments
    assert normalize_department_code("Information Technology") == "IT"
    assert normalize_department_code("Electronics & Communication Engineering") == "ECE"
    assert normalize_department_code("Mechanical") == "MECH"
    assert normalize_department_code("Civil") == "CIVIL"
    assert normalize_department_code("Basic Sciences") == "BS&H"
    assert normalize_department_code("MCA") == "MCA"
    assert normalize_department_code("MBA") == "MBA"


def test_exam_terminology_mappings():
    """Verifies VIIT autonomous examination terminology mappings."""
    assert normalize_exam_term("CIE") == "CIE"
    assert normalize_exam_term("midterm") == "CIE"
    assert normalize_exam_term("internal exam") == "CIE"
    assert normalize_exam_term("first mid") == "Mid-1"
    assert normalize_exam_term("second mid") == "Mid-2"
    assert normalize_exam_term("semester final") == "SEE"
    assert normalize_exam_term("final exam") == "SEE"
    assert normalize_exam_term("lab internal") == "Lab Internal"
    assert normalize_exam_term("lab external") == "Lab External"


def test_regulation_context_vr22_and_unknown():
    """Verifies VR22 regulation context and strict UNKNOWN fallback."""
    assert get_student_regulation_display("VR22") == "Regulation: VR22"
    assert get_student_regulation_display("VR20") == "Regulation: VR20"
    assert get_student_regulation_display("VR23") == "Regulation: VR23"
    assert get_student_regulation_display(None) == "Regulation: UNKNOWN"
    assert get_student_regulation_display("") == "Regulation: UNKNOWN"
    assert get_student_regulation_display("INVALID_REG") == "Regulation: UNKNOWN"


def test_attendance_policy_ranges_and_disclaimer():
    """Verifies VIIT attendance tiers (>=75% NORMAL, 65-74.9% CONDONATION, <65% DETENTION) and disclaimer."""
    # 1. Normal Tier
    res_norm = get_attendance_status_context(85.0)
    assert res_norm["status_code"] == "NORMAL"
    assert res_norm["status_label"] == "NORMAL ATTENDANCE"
    assert "policy_disclaimer" in res_norm

    # 2. Condonation Range
    res_cond = get_attendance_status_context(71.5)
    assert res_cond["status_code"] == "CONDONATION_RANGE"
    assert res_cond["status_label"] == "CONDONATION RANGE"
    assert "condonation approval" in res_cond["description"].lower()

    # 3. Detention Warning
    res_det = get_attendance_status_context(58.0)
    assert res_det["status_code"] == "DETENTION_WARNING"
    assert res_det["status_label"] == "DETENTION WARNING"
    assert "detention" in res_det["description"].lower()

    # Verify standard disclaimer
    assert "Based on the configured VIIT attendance policy context" in res_norm["policy_disclaimer"]


def test_campus_locations_and_alias_matching():
    """Verifies canonical VIIT building names and alias resolution."""
    assert get_location_canonical_name("kalam block") == "APJ Abdul Kalam Block"
    assert get_location_canonical_name("apj block") == "APJ Abdul Kalam Block"
    assert get_location_canonical_name("library") == "Vignan Dhara Central Library"
    assert get_location_canonical_name("vignan dhara") == "Vignan Dhara Central Library"
    assert get_location_canonical_name("dharitri") == "Dharitri Central Seminar Hall"
    assert get_location_canonical_name("mv block") == "Sir MV Block"
    assert get_location_canonical_name("ramanujan") == "Ramanujan Block"
    assert get_location_canonical_name("girls hostel") == "Priyadarshini Girls Hostel"


def test_statutory_grievance_cells_definitions():
    """Verifies statutory and grievance body definitions without privacy leakage."""
    cells = VIIT_STATUTORY_CELLS
    assert "Anti-Ragging Committee" in cells
    assert "Internal Complaints Committee" in cells
    assert "Women Protection Cell" in cells
    assert "Central Grievance Redressal Committee" in cells
    assert "Dean Student Affairs" in cells


def test_transport_and_placement_context():
    """Verifies transport hubs and T&P / CRT context."""
    routes = VIIT_TRANSPORT_ROUTES
    assert "Maddilapalem" in routes["key_commute_areas"]
    assert "Gajuwaka" in routes["key_commute_areas"]
    assert "Anakapalle" in routes["key_commute_areas"]
    assert "Kurmannapalem" in routes["key_commute_areas"]
    assert "Static route context only" in routes["disclaimer"]

    placement = VIIT_PLACEMENT_CONTEXT
    assert "CRT" in placement["programmes"]
    assert "Campus Recruitment Training" in placement["programmes"]["CRT"]["name"]


def test_ask_vignex_viit_cie_intent(db, student_user):
    """Ask VIGNAI correctly answers 'What is CIE?' and 'Difference between Mid-1 and SEE'."""
    q = "What is the difference between Mid-1 and SEE?"
    r = query_router.route_query(q)
    assert r.intent == "VIIT_EXAM_TERMINOLOGY"
    assert r.domain == "ACADEMIC"

    payload = AskVignexQueryPayload(query=q)
    ans = ask_vignex_answer_service.process_query(payload, db, user=student_user)
    assert ans.domain == "ACADEMIC"
    assert "Continuous Internal Evaluation" in ans.answer
    assert "Semester End Examination" in ans.answer


def test_ask_vignex_viit_locations_intent(db, student_user):
    """Ask VIGNAI correctly answers 'What buildings are on the campus?' and 'Where is Vignan Dhara?'."""
    q = "What buildings are on the campus?"
    r = query_router.route_query(q)
    assert r.intent == "VIIT_CAMPUS_LOCATIONS"
    assert r.domain == "CAMPUS_INTELLIGENCE"

    payload = AskVignexQueryPayload(query=q)
    ans = ask_vignex_answer_service.process_query(payload, db, user=student_user)
    assert ans.domain == "CAMPUS_INTELLIGENCE"
    assert "APJ Abdul Kalam Block" in ans.answer
    assert "Vignan Dhara Central Library" in ans.answer


def test_ask_vignex_viit_departments_intent(db, student_user):
    """Ask VIGNAI correctly answers 'What does CSM mean?'."""
    q = "What does CSM mean?"
    r = query_router.route_query(q)
    assert r.intent == "VIIT_DEPARTMENT_INFO"
    assert r.domain == "ACADEMIC"

    payload = AskVignexQueryPayload(query=q)
    ans = ask_vignex_answer_service.process_query(payload, db, user=student_user)
    assert ans.domain == "ACADEMIC"
    assert "CSE (Artificial Intelligence & Machine Learning)" in ans.answer or "CSM" in ans.answer


def test_ask_vignex_unconnected_live_data_refusal(db, student_user):
    """Ask VIGNAI truthfully refuses live library availability or live bus GPS queries."""
    q = "Is the library open right now and how many books are available?"
    r = query_router.route_query(q)
    assert r.intent == "VIIT_LIVE_REFUSAL"

    payload = AskVignexQueryPayload(query=q)
    ans = ask_vignex_answer_service.process_query(payload, db, user=student_user)
    assert "I don't have verified live information" in ans.answer
    assert "NOT CONFIGURED" in ans.answer


def test_viit_api_endpoints_and_connector_statuses(client):
    """Verifies VIIT router endpoints and connector health statuses."""
    res_ctx = client.get("/api/viit/context")
    assert res_ctx.status_code == 200
    data = res_ctx.json()
    assert data["metadata"]["institution_code"] == "VIIT"
    assert data["departments_count"] >= 12
    assert "connector_statuses" in data
    assert data["connector_statuses"]["ECAP_ERP"] == "NOT CONFIGURED"

    res_loc = client.get("/api/viit/locations")
    assert res_loc.status_code == 200
    locs = res_loc.json()
    assert len(locs) >= 8
    assert any(l["name"] == "APJ Abdul Kalam Block" for l in locs)

    res_depts = client.get("/api/viit/departments")
    assert res_depts.status_code == 200
    depts = res_depts.json()
    assert any(d["code"] == "CSM" for d in depts)
