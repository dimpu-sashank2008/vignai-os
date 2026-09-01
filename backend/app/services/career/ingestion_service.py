import hashlib
import uuid
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.models.career import Opportunity, OpportunitySkill, OpportunitySource, CareerProfile
from app.models.notification import Notification
from app.models.user import User
from app.services.career.connectors import (
    OpportunityConnector,
    MockVIITPlacementConnector,
    LiveVIITPlacementConnector,
    ApprovedPublicFeedConnector,
)
from app.services.career.matching_engine import matching_engine

class OpportunityIngestionService:
    """
    Ingests and synchronizes opportunities from registered connectors,
    applies deterministic deduplication, tracks source health, updates lifecycles,
    and refreshes student matches without duplicate notifications.
    """

    @classmethod
    def get_registered_connectors(cls) -> List[OpportunityConnector]:
        return [
            MockVIITPlacementConnector(),
            ApprovedPublicFeedConnector(),
            LiveVIITPlacementConnector(),
        ]

    @classmethod
    def sync_all_sources(cls, db: Session) -> Dict[str, Any]:
        connectors = cls.get_registered_connectors()
        total_sources = len(connectors)
        new_count = 0
        dup_count = 0
        expired_count = 0

        for connector in connectors:
            source_rec = db.query(OpportunitySource).filter(
                OpportunitySource.source_name == connector.source_name
            ).first()

            if not source_rec:
                source_rec = OpportunitySource(
                    source_name=connector.source_name,
                    source_type=connector.source_type,
                    status="HEALTHY",
                    items_found=0,
                )
                db.add(source_rec)
                db.flush()

            source_rec.last_checked = datetime.utcnow()

            try:
                import asyncio
                try:
                    raw_items = asyncio.run(connector.fetch())
                except RuntimeError:
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    raw_items = loop.run_until_complete(connector.fetch())

                source_rec.status = "HEALTHY"
                source_rec.last_success = datetime.utcnow()
                source_rec.error_message = None
                source_rec.items_found = len(raw_items)

                for raw in raw_items:
                    norm = connector.normalize(raw)
                    
                    # Deterministic deduplication fingerprint
                    deadline_str = norm["deadline"].strftime("%Y-%m-%d") if norm.get("deadline") else ""
                    fp_str = f"{norm['title'].lower()}|{norm['organization'].lower()}|{norm['opportunity_type'].lower()}|{deadline_str}"
                    fingerprint = hashlib.sha256(fp_str.encode()).hexdigest()

                    existing = db.query(Opportunity).filter(Opportunity.fingerprint == fingerprint).first()
                    if existing:
                        dup_count += 1
                        # Update description / deadline if needed
                        existing.is_active = True
                        if existing.verification_status != "REJECTED":
                            existing.verification_status = "VERIFIED"
                        continue

                    # Insert new opportunity
                    opp_id = f"OPP-{datetime.utcnow().year}-{uuid.uuid4().hex[:6].upper()}"
                    opp = Opportunity(
                        opportunity_id=opp_id,
                        title=norm["title"],
                        organization=norm["organization"],
                        opportunity_type=norm["opportunity_type"],
                        description=norm["description"],
                        location=norm["location"],
                        work_mode=norm["work_mode"],
                        deadline=norm["deadline"],
                        eligibility=norm["eligibility"],
                        source_name=norm["source_name"],
                        source_type=norm["source_type"],
                        verification_status="VERIFIED",
                        lifecycle_status="ACTIVE",
                        fingerprint=fingerprint,
                        data_source=norm["data_source"],
                        is_active=True,
                    )
                    db.add(opp)
                    db.flush()

                    for sk in norm.get("skills_required", []):
                        db.add(OpportunitySkill(opportunity_id=opp.id, skill_name=sk, is_required=True))
                    for sk in norm.get("skills_preferred", []):
                        db.add(OpportunitySkill(opportunity_id=opp.id, skill_name=sk, is_required=False))

                    new_count += 1

            except Exception as e:
                # Source failure -> mark degraded/offline, but DO NOT delete existing records
                source_rec.status = "DEGRADED" if "not configured" in str(e).lower() else "OFFLINE"
                source_rec.error_message = str(e)

        # Update lifecycle statuses across all opportunities
        now = datetime.utcnow()
        all_opps = db.query(Opportunity).all()
        for opp in all_opps:
            if opp.deadline:
                if opp.deadline < now:
                    opp.lifecycle_status = "EXPIRED"
                    opp.is_active = False
                    expired_count += 1
                elif opp.deadline <= now + timedelta(days=3):
                    opp.lifecycle_status = "EXPIRING"
                else:
                    opp.lifecycle_status = "ACTIVE"

        db.commit()

        # Recalculate matches for all existing student profiles
        profiles = db.query(CareerProfile).all()
        for profile in profiles:
            matching_engine.sync_student_matches(db, profile.id)
            
            # Send duplicate-safe notifications for top matches closing soon (<= 3 days)
            closing_matches = [
                m for m in profile.matches
                if m.opportunity.is_active
                and m.opportunity.deadline
                and m.opportunity.deadline <= now + timedelta(days=3)
                and m.match_score >= 70.0
            ]
            for m in closing_matches:
                existing_notif = db.query(Notification).filter(
                    Notification.user_id == profile.student_id,
                    Notification.title.like(f"%{m.opportunity.title[:30]}%"),
                ).first()
                if not existing_notif:
                    db.add(Notification(
                        user_id=profile.student_id,
                        title=f"Closing Soon: {m.opportunity.title}",
                        message=f"{m.opportunity.title} at {m.opportunity.organization} closes soon ({m.match_score}% alignment).",
                        notification_type="CAREER",
                        target_route="/student/career",
                        target_entity_type="CAREER",
                        target_entity_id=str(m.opportunity.id),
                        target_anchor=f"opportunity-{m.opportunity.id}",
                    ))

        db.commit()

        sources_health = db.query(OpportunitySource).all()
        return {
            "message": f"Sync complete. Ingested {new_count} new opportunities, skipped {dup_count} duplicates, updated {expired_count} expired.",
            "total_sources_polled": total_sources,
            "new_opportunities_ingested": new_count,
            "duplicates_skipped": dup_count,
            "expired_count": expired_count,
            "sources_health": sources_health,
        }
