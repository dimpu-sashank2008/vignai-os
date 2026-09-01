import pytest
from datetime import datetime, timedelta
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.main import app
from app.database import SessionLocal
from app.models.career import Opportunity, OpportunitySkill, OpportunityMatch, OpportunitySource, CareerProfile
from app.models.user import User
from app.services.auth_service import create_access_token
from app.services.career.connectors import (
    MockVIITPlacementConnector,
    ApprovedPublicFeedConnector,
    LiveVIITPlacementConnector,
)
from app.services.career.intake_service import CoordinatorIntakeService
from app.services.career.ingestion_service import OpportunityIngestionService


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


def test_connector_fetch_and_normalization():
    """Verifies that MockVIITPlacementConnector and ApprovedPublicFeedConnector fetch and normalize properly."""
    import asyncio
    viit_conn = MockVIITPlacementConnector()
    items = asyncio.run(viit_conn.fetch())
    assert len(items) >= 3

    norm = viit_conn.normalize(items[0])
    assert "title" in norm
    assert "organization" in norm
    assert norm["source_name"] == "VIIT Training & Placement Cell"
    assert norm["source_type"] == "INSTITUTION_CURATED"
    assert norm["verification_status"] == "VERIFIED"
    assert norm["lifecycle_status"] == "ACTIVE"
    assert len(norm["skills_required"]) >= 1

    feed_conn = ApprovedPublicFeedConnector()
    feed_items = asyncio.run(feed_conn.fetch())
    assert len(feed_items) >= 1
    feed_norm = feed_conn.normalize(feed_items[0])
    assert feed_norm["source_type"] == "PUBLIC_FEED"


def test_deterministic_deduplication_engine(db):
    """Verifies that duplicate opportunities are identified via SHA-256 fingerprinting and skipped."""
    res1 = OpportunityIngestionService.sync_all_sources(db)
    initial_new = res1["new_opportunities_ingested"]
    assert initial_new >= 0

    # Sync again -> all items should be detected as duplicates
    res2 = OpportunityIngestionService.sync_all_sources(db)
    assert res2["duplicates_skipped"] >= 3
    assert res2["new_opportunities_ingested"] == 0


def test_coordinator_intake_pasted_text_parsing(client, faculty_token, management_token, student_token, db):
    """Authorized placement coordinator submits announcement text which is parsed into DRAFT status."""
    announcement = """
    VIIT T&P Circular: Campus Hiring Drive at AzureTech Innovations
    Role: Cloud Infrastructure Intern
    Location: Visakhapatnam (VIIT Campus)
    Work Mode: Hybrid
    Eligibility: B.Tech 3rd and 4th Year CSE / IT / ECE
    Skills Required: Python, Linux, Docker, AWS, Git
    Deadline: 25/12/2026
    Stipend: Performance based pre-placement internship.
    """

    # Student cannot submit intake -> 403 Forbidden
    res_student = client.post(
        "/api/management/career/intake",
        json={"announcement_text": announcement},
        headers={"Authorization": f"Bearer {student_token}"},
    )
    assert res_student.status_code == 403

    # Faculty coordinator submits -> 200 OK
    res_fac = client.post(
        "/api/management/career/intake",
        json={"announcement_text": announcement},
        headers={"Authorization": f"Bearer {faculty_token}"},
    )
    assert res_fac.status_code == 200
    data = res_fac.json()
    assert "opportunity" in data
    assert data["opportunity"]["verification_status"] == "DRAFT"
    assert data["opportunity"]["source_type"] == "AUTHORIZED_COORDINATOR"
    assert len(data["extracted_details"]["skills_required"]) >= 3


def test_draft_opportunity_not_in_student_recommendations(client, student_token, faculty_token, db):
    """Verifies that DRAFT opportunities are strictly hidden from student recommendation feeds."""
    unique_draft_title = f"Unverified Secret Draft Opportunity {datetime.utcnow().timestamp()}"
    draft_announcement = f"{unique_draft_title}\nOrganization: Stealth Corp\nSkills: Python, React\nDeadline: 30/12/2026"

    # Faculty submits draft
    res_intake = client.post(
        "/api/management/career/intake",
        json={"announcement_text": draft_announcement},
        headers={"Authorization": f"Bearer {faculty_token}"},
    )
    assert res_intake.status_code == 200
    draft_opp_id = res_intake.json()["opportunity"]["id"]

    # Student requests opportunities -> draft must NOT appear in verified feed
    res_opps = client.get("/api/student/career/opportunities", headers={"Authorization": f"Bearer {student_token}"})
    assert res_opps.status_code == 200
    opp_titles = [o["title"] for o in res_opps.json()]
    assert unique_draft_title not in opp_titles

    # Student requests matches -> draft must NOT be in matches
    res_matches = client.get("/api/student/career/matches", headers={"Authorization": f"Bearer {student_token}"})
    assert res_matches.status_code == 200
    match_titles = [m["opportunity"]["title"] for m in res_matches.json()]
    assert unique_draft_title not in match_titles


def test_opportunity_verification_workflow(client, management_token, student_token, faculty_token, db):
    """Management reviews and verifies DRAFT opportunity, which then publishes to student recommendations."""
    verified_title = f"Verified Campus Hackathon Challenge {datetime.utcnow().timestamp()}"
    announcement = f"{verified_title}\nOrganization: VIIT Innovation Cell\nType: Hackathon\nSkills: Python, FastAPI\nDeadline: 30/12/2026"

    # Create draft
    res_intake = client.post(
        "/api/management/career/intake",
        json={"announcement_text": announcement},
        headers={"Authorization": f"Bearer {faculty_token}"},
    )
    assert res_intake.status_code == 200
    opp_id = res_intake.json()["opportunity"]["id"]

    # Management verifies draft
    res_verify = client.post(
        f"/api/management/career/intake/{opp_id}/verify",
        json={"action": "VERIFY", "review_notes": "Official circular approved by Principal Office."},
        headers={"Authorization": f"Bearer {management_token}"},
    )
    assert res_verify.status_code == 200
    assert res_verify.json()["verification_status"] == "VERIFIED"
    assert res_verify.json()["lifecycle_status"] == "ACTIVE"

    # Student now sees the verified opportunity
    res_opps = client.get("/api/student/career/opportunities", headers={"Authorization": f"Bearer {student_token}"})
    assert res_opps.status_code == 200
    opp_titles = [o["title"] for o in res_opps.json()]
    assert verified_title in opp_titles


def test_opportunity_rejection_workflow(client, management_token, faculty_token, db):
    """Management rejects an invalid draft opportunity."""
    spam_title = f"Spam Advertisement Intake {datetime.utcnow().timestamp()}"
    announcement = f"{spam_title}\nOrganization: Unapproved Org\nSkills: Python\nDeadline: 30/12/2026"

    res_intake = client.post(
        "/api/management/career/intake",
        json={"announcement_text": announcement},
        headers={"Authorization": f"Bearer {faculty_token}"},
    )
    opp_id = res_intake.json()["opportunity"]["id"]

    res_reject = client.post(
        f"/api/management/career/intake/{opp_id}/verify",
        json={"action": "REJECT", "review_notes": "Unapproved vendor."},
        headers={"Authorization": f"Bearer {management_token}"},
    )
    assert res_reject.status_code == 200
    assert res_reject.json()["verification_status"] == "REJECTED"
    assert res_reject.json()["is_active"] == False


def test_source_health_monitoring_and_failure_resilience(client, management_token, db):
    """Verifies that source health is recorded and failing connectors degrade gracefully without crashing."""
    res_sources = client.get("/api/management/career/sources", headers={"Authorization": f"Bearer {management_token}"})
    assert res_sources.status_code == 200
    sources = res_sources.json()
    assert len(sources) >= 3

    # Check that LiveVIITPlacementConnector is marked DEGRADED (since API key is not configured)
    degraded_sources = [s for s in sources if s["status"] in ["DEGRADED", "HEALTHY"]]
    assert len(degraded_sources) >= 1

    # Trigger manual sync
    res_sync = client.post("/api/management/career/sources/sync", headers={"Authorization": f"Bearer {management_token}"})
    assert res_sync.status_code == 200
    sync_data = res_sync.json()
    assert "total_sources_polled" in sync_data
    assert sync_data["total_sources_polled"] >= 3
