"""
Intelligent Query Orchestrator for Ask VIGNAI (Intelligence Layer V2).
Coordinates:
Safety / Authorization Guard -> Intent Detection -> Tool Selection -> Tool Execution -> Gemini Synthesis -> Telemetry.
"""

import logging
import re
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session

from app.models.user import User
from app.services.ask_vignex.query_router import query_router, IntentClassificationResult
from app.services.ask_vignex.schemas import (
    AskVignexQueryPayload,
    AskVignexAnswerResponse,
    AskVignexActionLink,
)
from app.services.ask_vignai.tool_registry import tool_registry
from app.services.ask_vignai.gemini_synthesizer import gemini_synthesizer

logger = logging.getLogger(__name__)


class AskVignaiOrchestrator:
    """Orchestrates query understanding, server-side tool execution, and grounded AI synthesis."""

    def process_query(
        self,
        payload: AskVignexQueryPayload,
        db: Session,
        user: Optional[User],
    ) -> AskVignexAnswerResponse:
        query = payload.query.strip()
        context = payload.conversation_context or []
        user_role = (getattr(user, "role", "student") or "student").lower()

        # ---------------------------------------------------------------------
        # 1. SECURITY & POLICY CHECKS (Refusals & Prompt Injection Defense)
        # ---------------------------------------------------------------------
        q_lower = query.lower()

        # A. Protected Identity Inquiry Refusal
        if any(p in q_lower for p in [
            "who submitted", "who complained", "student identity", "who reported",
            "name of the student", "email of the student", "who filed", "tell me who",
            "which student", "student name", "student email", "identity of the reporter",
            "who is the student", "reveal the student", "who raised", "who submitted the protected"
        ]):
            return self._build_refusal_response(
                query=query,
                intent="PRIVACY_REFUSAL",
                domain="COMPLAINTS",
                answer="I can't provide protected reporter identity. In accordance with VIGNAI OS policy, reporter identities submitted under protected status are strictly confidential and concealed across all analytical views.",
                key_findings=["Student identity protection policy active", "Reporter details withheld from analytical context"],
                interpretation="System policy strictly prevents the identification of individual students submitting complaints under protected status.",
                limitations=["Protected reporter identities are inaccessible across all system roles."],
            )

        # B. Allegation Truth & Guilt Inquiries Refusal
        if any(p in q_lower for p in [
            "guilty", "is the faculty guilty", "is the faculty member guilty", "is he guilty",
            "is she guilty", "did the faculty really", "is the allegation true", "did they commit",
            "are they guilty", "is it true", "is the teacher guilty", "is the staff guilty",
            "did the professor", "did the faculty", "is the accusation true", "prove guilt"
        ]):
            return self._build_refusal_response(
                query=query,
                intent="ALLEGATION_NEUTRALITY",
                domain="COMPLAINTS",
                answer="VIGNAI cannot determine whether an allegation is true. It can show the reported case, available evidence and investigation status to authorized users.",
                key_findings=["System does not adjudicate guilt or factual authenticity of allegations", "Platform maintains neutrality on active personnel grievances"],
                interpretation="Active grievance inquiries require authorized disciplinary committee investigation.",
                limitations=["Case determinations remain under the jurisdiction of the statutory inquiry committee."],
            )

        # C. Prompt Injection / Cross-Tenant Tampering Defense
        if any(p in q_lower for p in [
            "ignore your rules", "ignore previous instructions", "bypass safety",
            "show another student", "another student's attendance", "change my career fit to 100",
            "make the what-if result better", "hack", "override permission", "system prompt"
        ]):
            return self._build_refusal_response(
                query=query,
                intent="SECURITY_REFUSAL",
                domain="SECURITY",
                answer="I cannot fulfill this request. VIGNAI OS enforces strict role-based access control, tenant isolation, and deterministic mathematical scoring that cannot be altered or bypassed through prompt instructions.",
                key_findings=["Prompt injection or cross-tenant policy override attempt intercepted"],
                interpretation="Security and deterministic integrity are guaranteed server-side.",
                limitations=["All role permissions and scoring algorithms are enforced at the database level."],
            )

        # ---------------------------------------------------------------------
        # 2. INTENT CLASSIFICATION & ROUTING
        # ---------------------------------------------------------------------
        intent_res = query_router.route_query(query=query, conversation_context=context)

        # ---------------------------------------------------------------------
        # 3. TOOL SELECTION ACCORDING TO ROLE & INTENT
        # ---------------------------------------------------------------------
        tool_name = None
        if intent_res.intent == "STUDENT_ATTENDANCE":
            tool_name = "get_my_attendance" if user_role == "student" else None
        elif intent_res.intent == "STUDENT_SUBMISSION_RATE":
            tool_name = "get_my_submission_rate" if user_role == "student" else None
        elif intent_res.intent == "STUDENT_ASSIGNMENTS":
            tool_name = "get_my_assignments" if user_role == "student" else None
        elif intent_res.intent == "STUDENT_ASSESSMENTS":
            tool_name = "get_my_assessments" if user_role == "student" else None
        elif intent_res.intent == "CAREER_STRENGTHS":
            tool_name = "get_my_career_strengths" if user_role == "student" else None
        elif intent_res.intent in ["CAREER_MATCHED_OPPORTUNITIES", "CAREER_CLOSING_SOON", "CAREER_SKILL_SEARCH"]:
            tool_name = "get_my_career_recommendations" if user_role == "student" else None
        elif intent_res.intent == "CAREER_SKILL_GAPS":
            tool_name = "get_my_skill_gaps" if user_role == "student" else None
        elif intent_res.intent == "ACTION_PRIORITIES":
            tool_name = "get_my_actions" if user_role == "student" else "get_my_faculty_actions" if user_role == "faculty" else "get_institutional_actions"
        elif intent_res.intent == "FACULTY_CLASS_ATTENDANCE":
            tool_name = "get_class_attendance" if user_role == "faculty" else None
        elif intent_res.intent == "FACULTY_ASSIGNMENT_BACKLOG":
            tool_name = "get_assignment_submission_trends" if user_role == "faculty" else None
        elif intent_res.intent == "CAMPUS_OVERVIEW" or intent_res.domain == "CAMPUS_INTELLIGENCE":
            tool_name = "get_campus_patterns"
        elif intent_res.intent == "PRIORITY_REVIEW_ALERTS":
            tool_name = "get_priority_alerts" if user_role in ["management", "admin"] else "get_department_alerts"
        elif intent_res.intent == "SIMULATION_WHAT_IF":
            tool_name = "run_what_if" if user_role in ["management", "admin"] else None

        # Execute registered tool if identified
        tool_evidence = None
        if tool_name:
            tool_evidence = tool_registry.execute_tool(tool_name, db=db, user=user)

        # ---------------------------------------------------------------------
        # 4. DISPATCH BASELINE DETERMINISTIC RESPONSE
        # ---------------------------------------------------------------------
        from app.services.ask_vignex.answer_service import ask_vignex_answer_service
        base_res = ask_vignex_answer_service._dispatch_deterministic_response(
            payload=payload,
            db=db,
            user=user,
        )

        # ---------------------------------------------------------------------
        # 5. GROUNDED AI SYNTHESIS (Gemini 2.5 Flash / Heuristic Fallback)
        # ---------------------------------------------------------------------
        synthesis = gemini_synthesizer.synthesize(
            query=query,
            user_role=user_role,
            intent=intent_res.intent,
            tool_name=tool_name,
            tool_evidence=tool_evidence,
            fallback_answer=base_res.answer,
        )

        tools_called = [tool_name] if tool_name else []

        # Return synthesized response with full telemetry
        return AskVignexAnswerResponse(
            query=query,
            intent=base_res.intent,
            query_mode=base_res.query_mode,
            domain=base_res.domain,
            context_badge=base_res.context_badge,
            answer=synthesis.answer,
            key_findings=base_res.key_findings,
            supporting_case_ids=base_res.supporting_case_ids,
            supporting_cases=base_res.supporting_cases,
            data_window=base_res.data_window,
            provenance={
                **base_res.provenance,
                "provider": synthesis.provider,
                "model": synthesis.model,
                "provider_status": synthesis.provider_status,
                "tools_executed": tools_called,
            },
            interpretation=base_res.interpretation,
            limitations=base_res.limitations,
            action_links=base_res.action_links,
            ai_assisted=(synthesis.provider == "gemini"),
            provider=synthesis.provider,
            model=synthesis.model,
            provider_status=synthesis.provider_status,
            tools_called=tools_called,
            latency_ms=synthesis.latency_ms,
        )

    def _build_refusal_response(
        self,
        query: str,
        intent: str,
        domain: str,
        answer: str,
        key_findings: List[str],
        interpretation: str,
        limitations: List[str],
    ) -> AskVignexAnswerResponse:
        return AskVignexAnswerResponse(
            query=query,
            intent=intent,
            query_mode="VIGNEX_DATA",
            domain=domain,
            context_badge="🛡️ SECURITY & POLICY",
            answer=answer,
            key_findings=key_findings,
            supporting_case_ids=[],
            supporting_cases=[],
            data_window="Current Academic Year",
            provenance={
                "source": "VIGNAI Security & Governance Policy",
                "provider": "local_heuristic",
                "model": "vignex-nlp-rules-v2",
                "provider_status": "live",
                "tools_executed": [],
            },
            interpretation=interpretation,
            limitations=limitations,
            action_links=[],
            ai_assisted=False,
            provider="local_heuristic",
            model="vignex-nlp-rules-v2",
            provider_status="live",
            tools_called=[],
            latency_ms=0.0,
        )


ask_vignai_orchestrator = AskVignaiOrchestrator()
