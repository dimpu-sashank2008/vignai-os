"""
Complaint AI Analysis Orchestration Service for VIGNEX (Phase 3).
Handles background/async execution, validation, persistence, and deterministic policy routing.
"""

import logging
from sqlalchemy.orm import Session
from app.models.complaint import Complaint
from app.models.ai_analysis import ComplaintAIAnalysis
from app.services.ai.provider import get_ai_provider
from app.services.routing.routing_service import routing_service

logger = logging.getLogger(__name__)

class ComplaintAIService:
    """Orchestrates AI analysis lifecycle and routing policy enforcement for complaints."""

    async def analyze_and_save(self, db: Session, complaint_id: int) -> ComplaintAIAnalysis | None:
        """Run AI analysis on a complaint, store structured intelligence, and apply routing policy."""
        complaint = db.query(Complaint).filter(Complaint.id == complaint_id).first()
        if not complaint:
            logger.error(f"Cannot run AI analysis: Complaint ID {complaint_id} not found.")
            return None

        # Fetch or initialize AI analysis record
        analysis = db.query(ComplaintAIAnalysis).filter(
            ComplaintAIAnalysis.complaint_id == complaint.id
        ).first()

        provider = get_ai_provider()

        if not analysis:
            analysis = ComplaintAIAnalysis(
                complaint_id=complaint.id,
                processing_status="PROCESSING",
                provider=provider.get_provider_name(),
                model=provider.get_model_name(),
            )
            db.add(analysis)
            db.commit()
            db.refresh(analysis)
        else:
            analysis.processing_status = "PROCESSING"
            analysis.provider = provider.get_provider_name()
            analysis.model = provider.get_model_name()
            analysis.error_message = None
            db.commit()

        try:
            # Execute provider analysis
            result = await provider.analyze_complaint(
                description=complaint.description,
                location=complaint.location,
                category=complaint.category,
            )

            # Persist validated structured output
            analysis.category = result.category
            analysis.subcategory = result.subcategory
            analysis.issue_summary = result.issue_summary
            analysis.location = result.location or complaint.location
            analysis.duration = result.duration
            analysis.impact = result.impact
            analysis.suggested_priority = result.suggested_priority
            analysis.priority_reason = result.priority_reason
            analysis.confidence = result.confidence
            analysis.processing_status = "COMPLETED"
            analysis.error_message = None

            # Phase 3 Routing recommendation fields
            analysis.department = result.department
            analysis.suggested_route_type = result.suggested_route_type
            analysis.sensitivity = result.sensitivity or "NORMAL"
            analysis.routing_reason = result.routing_reason

            # If complaint title was generic or empty, update with concise issue summary
            if not complaint.title or len(complaint.title) > 60:
                if result.issue_summary:
                    complaint.title = result.issue_summary

            db.commit()
            db.refresh(analysis)
            logger.info(f"AI analysis successfully completed for case {complaint.case_id}")

            # Apply Deterministic Routing Policy
            routing_service.apply_routing(db=db, complaint=complaint, ai_analysis=analysis)

            return analysis

        except Exception as exc:
            logger.error(f"AI analysis failed for complaint {complaint.id}: {exc}", exc_info=True)
            analysis.processing_status = "FAILED"
            analysis.error_message = str(exc)[:500]
            db.commit()
            db.refresh(analysis)

            # Apply default fallback routing policy even if AI fails
            routing_service.apply_routing(db=db, complaint=complaint, ai_analysis=None)
            return analysis


complaint_ai_service = ComplaintAIService()
