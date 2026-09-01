"""
Intent Classification & Query Routing Layer for Ask VIGNEX (Phase 4C).
Deterministic, lightweight intent parsing without sending massive database dumps to the LLM.
Distinguishes between GENERAL_KNOWLEDGE, VIGNEX_DATA, and HYBRID query modes.
"""

import re
import logging
from typing import Any
from app.services.ask_vignex.schemas import IntentClassificationResult

logger = logging.getLogger(__name__)

# Canonical campus entity keywords
CAMPUS_INDICATOR_KEYWORDS = [
    "campus", "vignai", "vignai os", "vignex", "our college", "university", "complaint", "complaints",
    "case", "cases", "ticket", "tickets", "unresolved", "reported", "reporting",
    "student report", "student reports", "emerging issue", "emerging issues",
    "top problem", "top problems", "biggest problem", "biggest problems",
    "operational", "department", "department queue", "department issues", "department problems",
    "status", "escalated", "assigned",
    "investigation", "incident", "incidents", "cluster", "clusters", "defect",
    "defects", "disruption", "disruptions", "outage", "outages", "breakdown"
]

CAMPUS_LOCATIONS = {
    "Block A": ["block a", "academic block a"],
    "Academic Block 2, Lab 3": ["lab 3", "lab-3", "academic block 2", "block 2"],
    "Faculty Block": ["faculty block", "faculty cabins"],
    "North Gate Bus Stop": ["north gate", "bus stop", "gate stop"],
    "Central Library": ["library", "central library"],
    "Room 304": ["room 304", "room-304"],
    "Lecture Hall 2": ["lecture hall 2", "hall 2"],
}

DEPT_MAP = {
    "CSE": ["cse", "computer science department", "cs dept"],
    "IT": ["it department", "information technology dept"],
    "ECE": ["ece", "electronics department"],
    "Transport": ["transport cell", "transit office", "bus transport"],
    "Student Affairs": ["student affairs", "discipline committee", "grievance cell"],
    "Infrastructure": ["infrastructure maintenance", "facilities department", "civil maintenance"],
}

CATEGORY_MAP = {
    "Transport": ["transport", "bus schedule", "commute bus", "transit route"],
    "Wi-Fi / Network": ["wi-fi", "wifi", "network", "internet access", "eduroam connectivity"],
    "Laboratory": ["lab projector", "lab equipment", "laboratory apparatus"],
    "Cleanliness": ["cleanliness", "washroom", "toilet sanitation", "hygiene"],
    "Classroom": ["classroom bench", "classroom ac", "air conditioner"],
    "Staff Conduct / Grievance": ["faculty conduct", "staff conduct", "grievance", "harassment"],
}


class QueryRouter:
    """Classifies user queries into structured operational intents and extracted entities with query mode isolation."""

    def route_query(
        self,
        query: str,
        conversation_context: list[dict[str, Any]] | None = None,
    ) -> IntentClassificationResult:
        q_raw = query.strip()
        q_lower = q_raw.lower()
        q_clean = re.sub(r'[\.\?!]+$', '', q_lower).strip()

        # -------------------------------------------------------------
        # 1. SPECIAL SAFETY & POLICY GUARDS
        # -------------------------------------------------------------
        # A. Protected Identity Inquiry
        if any(p in q_lower for p in [
            "who submitted", "who complained", "student identity", "who reported",
            "name of the student", "email of the student", "who filed", "tell me who",
            "which student", "student name", "student email", "identity of the reporter",
            "who is the student", "reveal the student", "who raised", "who submitted the protected"
        ]):
            return IntentClassificationResult(
                intent="PRIVACY_REFUSAL",
                domain="COMPLAINTS",
                context_badge="🏛️ VIGNAN CAMPUS DATA",
                query_mode="VIGNEX_DATA",
                confidence=1.0,
            )

        # B. Allegation Truth & Guilt Inquiries
        if any(p in q_lower for p in [
            "guilty", "is the faculty guilty", "is the faculty member guilty", "is he guilty",
            "is she guilty", "did the faculty really", "is the allegation true", "did they commit",
            "are they guilty", "is it true", "is the teacher guilty", "is the staff guilty",
            "did the professor", "did the faculty", "is the accusation true", "prove guilt"
        ]):
            return IntentClassificationResult(
                intent="ALLEGATION_NEUTRALITY",
                domain="COMPLAINTS",
                context_badge="🏛️ VIGNAN CAMPUS DATA",
                query_mode="VIGNEX_DATA",
                confidence=1.0,
            )

        # -------------------------------------------------------------
        # 1.5 CONVERSATIONAL GREETINGS, CAPABILITIES & COURTESIES
        # -------------------------------------------------------------
        pure_greetings = [
            "hi", "hello", "hey", "hiya", "howdy", "good morning", "good afternoon",
            "good evening", "good day", "greetings", "hi vignai", "hello vignai",
            "hey vignai", "hi vignex", "hello vignex", "hey assistant", "yo", "sup"
        ]
        pure_courtesies = [
            "thanks", "thank you", "thx", "thank you so much", "thanks a lot",
            "appreciate it", "thank you vignai", "ok", "okay", "cool", "nice",
            "great", "awesome", "perfect", "got it", "understood", "alright", "sure"
        ]
        pure_identities = [
            "who are you", "what are you", "who created you", "who made you",
            "what can you do", "what can you do?", "what is vignai", "what is vignai os",
            "what is vignex", "how can you help me", "how do you work", "introduce yourself",
            "tell me about yourself", "help", "help me"
        ]

        if q_clean in pure_greetings or q_clean in pure_courtesies or q_clean in pure_identities:
            return IntentClassificationResult(
                intent="CONVERSATIONAL_GREETING",
                domain="CONVERSATIONAL",
                context_badge="👋 VIGNAI ASSISTANT",
                query_mode="GENERAL_KNOWLEDGE",
                confidence=1.0,
            )

        # If query starts with a conversational greeting followed by an actual question:
        # e.g., "hi, what is my attendance?", "hello! are there any internships?"
        # strip the greeting prefix so subsequent domain routing processes the real question.
        q_stripped = re.sub(r'^(hi|hello|hey|good morning|good afternoon|good evening|greetings)[\s,\-\!\:\;]+\s*', '', q_lower).strip()
        if q_stripped and len(q_stripped) >= 3 and q_stripped != q_lower:
            q_lower = q_stripped
            q_clean = re.sub(r'[\.\?!]+$', '', q_lower).strip()

        # -------------------------------------------------------------
        # 2. CONTEXTUAL FOLLOW-UP DETECTION
        # -------------------------------------------------------------
        follow_up_patterns = {
            0: ["first one", "1st one", "the first", "#1", "first issue", "option 1", "item 1", "which one is first", "which is first"],
            1: ["second one", "2nd one", "the second", "#2", "second issue", "option 2", "item 2"],
            2: ["third one", "3rd one", "the third", "#3", "third issue", "option 3", "item 3"],
        }

        matched_follow_up_idx = None
        for idx, patterns in follow_up_patterns.items():
            if any(p in q_lower for p in patterns) or (q_lower.startswith("what about the ") and any(p in q_lower for p in patterns)):
                matched_follow_up_idx = idx
                break

        if matched_follow_up_idx is not None and conversation_context:
            last_msg = conversation_context[-1] if len(conversation_context) > 0 else {}
            last_intent = last_msg.get("intent", "")
            
            # Follow-up in Academic domain
            if last_intent in ["STUDENT_ASSESSMENTS", "STUDENT_ASSIGNMENTS", "STUDENT_SCHEDULE"]:
                return IntentClassificationResult(
                    intent=last_intent,
                    domain="ACADEMIC",
                    context_badge="📚 ACADEMIC",
                    query_mode="VIGNEX_DATA",
                    follow_up_target_index=matched_follow_up_idx,
                    confidence=0.95,
                )

            # Follow-up in Campus/Complaints domain
            if last_intent in ["CAMPUS_OVERVIEW", "EMERGING_ISSUES", "LOCATION_ANALYSIS", "DEPARTMENT_ANALYSIS", "CATEGORY_ANALYSIS"]:
                return IntentClassificationResult(
                    intent="CONTEXTUAL_FOLLOW_UP",
                    domain="CAMPUS_INTELLIGENCE",
                    context_badge="🏛️ VIGNAN CAMPUS DATA",
                    query_mode="VIGNEX_DATA",
                    follow_up_target_index=matched_follow_up_idx,
                    confidence=0.95,
                )

        # -------------------------------------------------------------
        # 2.3 SIMULATION / WHAT-IF SCENARIO ANALYSIS INTENT
        # -------------------------------------------------------------
        if any(p in q_lower for p in [
            "what happens if we add one bus", "what happens if we add a bus", "what happens if we add",
            "simulate adding a bus", "simulate adding", "what if we add one bus", "what if we add a bus",
            "what if we add", "what if one more bus", "what if two buses", "what if 2 buses", "what if 3 buses",
            "run simulation", "simulate scenario", "decision simulation", "what-if simulation",
            "what if block a wi-fi", "what if wifi bandwidth", "what if wi-fi capacity",
            "what if maintenance staffing", "what if a maintenance cycle", "what if maintenance cycle",
            "what if i have 3 assignments", "what if i have three assignments", "what if assignment deadlines",
            "what if assignments are", "what if an earthquake", "what if an asteroid"
        ]) or (
            any(q_lower.startswith(prefix) for prefix in ["what if", "what happens if", "suppose", "what would happen if", "how would", "simulate scenario", "can we simulate"])
            and not any(p in q_lower for p in ["what is my", "what are my", "when is my", "my attendance", "my complaints"])
        ):
            return IntentClassificationResult(
                intent="SIMULATION_WHAT_IF",
                domain="SIMULATIONS",
                context_badge="🛠️ SIMULATION",
                query_mode="VIGNEX_DATA",
                confidence=0.98,
            )

        # -------------------------------------------------------------
        # 2.35 PROACTIVE PRIORITY ALERTS INTENT
        # -------------------------------------------------------------
        if any(p in q_lower for p in [
            "what needs immediate review", "what needs attention", "what issues need review",
            "show priority alerts", "active alerts", "what needs immediate attention",
            "which issues need review", "urgent alerts", "priority alerts", "what needs review"
        ]):
            return IntentClassificationResult(
                intent="PRIORITY_REVIEW_ALERTS",
                domain="CAMPUS_INTELLIGENCE",
                context_badge="🏛️ VIGNAN CAMPUS DATA",
                query_mode="VIGNEX_DATA",
                confidence=0.98,
            )

        # -------------------------------------------------------------
        # 2.4 STUDENT OWN COMPLAINTS INTENT
        # -------------------------------------------------------------
        if any(p in q_lower for p in [
            "what are my complaints", "what are my reported issues", "my complaints",
            "my reported issues", "status of my complaint", "status of my case", "my grievances"
        ]):
            return IntentClassificationResult(
                intent="STUDENT_OWN_COMPLAINTS",
                domain="COMPLAINTS",
                context_badge="🏛️ VIGNAN CAMPUS DATA",
                query_mode="VIGNEX_DATA",
                confidence=0.98,
            )

        # -------------------------------------------------------------
        # 2.5 STUDENT ACADEMIC QUERY ROUTING (Phase 6B)
        # -------------------------------------------------------------
        # -------------------------------------------------------------
        # Hybrid Complaints & Academic Correlation (High Precedence)
        # -------------------------------------------------------------
        if any(p in q_lower for p in [
            "related to recent academic complaints", "related to recent complaints",
            "related to complaints", "complaints affecting my class", "complaints related to my",
            "issues related to recent academic complaints"
        ]):
            return IntentClassificationResult(
                intent="FACULTY_HYBRID_COMPLAINTS",
                domain="HYBRID",
                context_badge="⚡ HYBRID",
                query_mode="HYBRID",
                confidence=0.98,
            )

        if ("complaint" in q_lower or "complaints" in q_lower) and ("attendance" in q_lower or "workload" in q_lower or "academic" in q_lower or "increasing while" in q_lower or "decreasing" in q_lower):
            return IntentClassificationResult(
                intent="MANAGEMENT_HYBRID_COMPLAINTS",
                domain="HYBRID",
                context_badge="⚡ HYBRID",
                query_mode="HYBRID",
                confidence=0.98,
            )

        # Faculty & Management Attendance Inquiries (High Precedence)
        # -------------------------------------------------------------
        if any(p in q_lower for p in [
            "attendance trend in my", "attendance in my data structures", "attendance in my operating systems",
            "attendance in my class", "attendance of my class", "attendance trend in my class",
            "class attendance", "attendance in my classes", "my class attendance"
        ]):
            return IntentClassificationResult(
                intent="FACULTY_CLASS_ATTENDANCE",
                domain="ACADEMIC",
                context_badge="📚 ACADEMIC",
                query_mode="VIGNEX_DATA",
                confidence=0.98,
            )

        if any(p in q_lower for p in [
            "attendance trend across departments", "attendance across departments", "largest attendance change",
            "department has the largest attendance change", "attendance by department", "department attendance trends",
            "which department has the highest attendance", "highest attendance"
        ]):
            return IntentClassificationResult(
                intent="MANAGEMENT_DEPARTMENT_ATTENDANCE",
                domain="ACADEMIC",
                context_badge="📚 ACADEMIC",
                query_mode="VIGNEX_DATA",
                confidence=0.98,
            )

        # A. Student Attendance inquiries
        if any(p in q_lower for p in [
            "how is my attendance", "what is my attendance", "what's my attendance",
            "my attendance", "attendance percentage", "how's my attendance",
            "check my attendance", "how much attendance do i have", "how much attendance",
            "attendance", "my attendance percentage"
        ]):
            return IntentClassificationResult(
                intent="STUDENT_ATTENDANCE",
                domain="ACADEMIC",
                context_badge="📚 ACADEMIC",
                query_mode="VIGNEX_DATA",
                confidence=0.98,
            )

        # A.1 Submission Rate inquiries (Intelligence Layer V2)
        if any(p in q_lower for p in [
            "submission rate", "assignment submission", "how many assignments did i submit",
            "what is my submission percentage", "my submission rate", "what is my submission rate",
            "submission percentage", "assignment completion rate", "my assignment submission rate"
        ]):
            return IntentClassificationResult(
                intent="STUDENT_SUBMISSION_RATE",
                domain="ACADEMIC",
                context_badge="📚 ACADEMIC",
                query_mode="VIGNEX_DATA",
                confidence=0.98,
            )

        # B. Assessment & Exam inquiries
        if any(p in q_lower for p in [
            "when is my next exam", "when is my exam", "next exam", "upcoming exam",
            "next quiz", "next assessment", "which subject has my next assessment",
            "upcoming assessments", "when is my assessment", "my next assessment",
            "exam schedule", "when is the next exam"
        ]):
            return IntentClassificationResult(
                intent="STUDENT_ASSESSMENTS",
                domain="ACADEMIC",
                context_badge="📚 ACADEMIC",
                query_mode="VIGNEX_DATA",
                confidence=0.98,
            )

        # C. Assignment & Deliverable inquiries
        if any(p in q_lower for p in [
            "what's due this week", "what is due this week", "what's due", "what is due",
            "pending assignments", "how many assignments are pending", "assignments due",
            "my assignments", "upcoming assignments", "overdue assignments", "what assignments",
            "what assignments are pending", "pending deliverables"
        ]):
            return IntentClassificationResult(
                intent="STUDENT_ASSIGNMENTS",
                domain="ACADEMIC",
                context_badge="📚 ACADEMIC",
                query_mode="VIGNEX_DATA",
                confidence=0.98,
            )

        # D. Workload inquiries
        if any(p in q_lower for p in [
            "busiest academic day", "what is my busiest academic day", "how is my academic workload",
            "my academic workload", "busiest day", "my workload", "workload this week"
        ]):
            return IntentClassificationResult(
                intent="STUDENT_WORKLOAD",
                domain="ACADEMIC",
                context_badge="📚 ACADEMIC",
                query_mode="VIGNEX_DATA",
                confidence=0.96,
            )

        # E. Schedule & Timetable inquiries
        if any(p in q_lower for p in [
            "classes today", "my schedule today", "what classes do i have", "my timetable",
            "my classes today", "schedule today", "timetable today", "what are my classes",
            "classes do i have", "schedule do i have", "my schedule"
        ]):
            return IntentClassificationResult(
                intent="STUDENT_SCHEDULE",
                domain="ACADEMIC",
                context_badge="📚 ACADEMIC",
                query_mode="VIGNEX_DATA",
                confidence=0.96,
            )

        # -------------------------------------------------------------
        # 2.55 STUDENT CAREER INTELLIGENCE QUERY ROUTING (Career Domain)
        # -------------------------------------------------------------

        # 0. Career Definition Queries (e.g. "what is a job", "what is an internship", "explain internships", "what is a career", "what does a software engineer do")
        # Must be treated as GENERAL_KNOWLEDGE, NOT opportunity retrieval
        if bool(re.search(r'^(what is|what are|define|explain|what does a)\s+(a\s+|an\s+)?(job|jobs|internship|internships|career|careers|software engineer)\b', q_clean)):
            return IntentClassificationResult(
                intent="GENERAL_KNOWLEDGE",
                domain="GENERAL_KNOWLEDGE",
                context_badge="📖 GENERAL KNOWLEDGE",
                query_mode="GENERAL_KNOWLEDGE",
                confidence=0.98,
            )

        # A. Career Strengths & Domain Alignment
        if any(p in q_lower for p in [
            "what career fields am i strongest in", "what fields am i currently strongest in",
            "what fields am i strongest in", "which career fields am i strongest",
            "my career strengths", "career strengths", "strongest career areas", "strongest areas",
            "top career fields", "what career direction", "career direction", "fields am i strongest"
        ]):
            return IntentClassificationResult(
                intent="CAREER_STRENGTHS",
                domain="CAREER",
                context_badge="💼 CAREER INTELLIGENCE",
                query_mode="VIGNEX_DATA",
                confidence=0.98,
            )

        # B. Career Domain Explanation (e.g. "Why do you recommend Data Science for me?")
        if any(p in q_lower for p in [
            "why do you recommend data science", "why recommend data science",
            "why data science", "why ai/ml", "why software engineering",
            "why do you recommend", "why is data science recommended"
        ]):
            return IntentClassificationResult(
                intent="CAREER_DOMAIN_EXPLAIN",
                domain="CAREER",
                context_badge="💼 CAREER INTELLIGENCE",
                query_mode="VIGNEX_DATA",
                confidence=0.97,
            )

        # C. Prioritization & Recommendation Ranking inquiries
        if any(p in q_lower for p in [
            "which opportunities should i prioritize", "which opportunity should i prioritize",
            "which internship should i prioritize", "priority opportunities",
            "top opportunities to apply", "why was this internship ranked first",
            "why is this opportunity recommended to me", "why was this ranked first"
        ]):
            return IntentClassificationResult(
                intent="CAREER_PRIORITIZATION",
                domain="CAREER",
                context_badge="💼 CAREER INTELLIGENCE",
                query_mode="VIGNEX_DATA",
                confidence=0.97,
            )

        # D. Skill Gap inquiries
        if any(p in q_lower for p in [
            "what skills am i missing", "what skills do i need", "what skill gaps",
            "my skill gaps", "skills i am missing", "skills am i missing", "skills to learn",
            "what should i learn", "missing skills", "skill gap", "skill gaps"
        ]):
            return IntentClassificationResult(
                intent="CAREER_SKILL_GAPS",
                domain="CAREER",
                context_badge="💼 CAREER INTELLIGENCE",
                query_mode="VIGNEX_DATA",
                confidence=0.98,
            )

        # E. Closing Soon / Deadline inquiries
        if any(p in q_lower for p in [
            "what's closing soon", "what is closing soon", "which opportunities are closing soon",
            "internships closing soon", "approaching deadlines", "deadlines closing soon",
            "opportunities closing soon", "jobs closing soon", "closing soon"
        ]):
            return IntentClassificationResult(
                intent="CAREER_CLOSING_SOON",
                domain="CAREER",
                context_badge="💼 CAREER INTELLIGENCE",
                query_mode="VIGNEX_DATA",
                confidence=0.96,
            )

        # F. Career + Academic Hybrid
        if (("internship" in q_lower or "opportunities" in q_lower or "jobs" in q_lower or "career" in q_lower) and
            ("academic" in q_lower or "subject" in q_lower or "course" in q_lower or "attendance" in q_lower or "performance" in q_lower)):
            return IntentClassificationResult(
                intent="CAREER_ACADEMIC_HYBRID",
                domain="HYBRID",
                context_badge="⚡ HYBRID",
                query_mode="HYBRID",
                confidence=0.96,
            )

        # G. Placement Cell & College Placement inquiries
        if any(p in q_lower for p in [
            "placement opportunities through the college", "placement opportunities through college",
            "placement opportunities in college", "college placements", "campus placements",
            "training and placement cell", "placement cell opportunities"
        ]):
            return IntentClassificationResult(
                intent="CAMPUS_PLACEMENT_INFO",
                domain="CAREER",
                context_badge="💼 CAREER INTELLIGENCE",
                query_mode="VIGNEX_DATA",
                confidence=0.95,
            )

        # H. Skill-specific Opportunity Search (e.g. "Which internships require Docker?")
        if any(p in q_lower for p in [
            "require docker", "requires docker", "requiring docker",
            "match python", "match react", "requiring python", "require python",
            "opportunities require", "internships require", "opportunities match python",
            "which internships require", "which opportunities require"
        ]) or (("internship" in q_lower or "opportunities" in q_lower) and ("require" in q_lower or "match" in q_lower and not ("skills" in q_lower or "profile" in q_lower))):
            return IntentClassificationResult(
                intent="CAREER_SKILL_SEARCH",
                domain="CAREER",
                context_badge="💼 CAREER INTELLIGENCE",
                query_mode="VIGNEX_DATA",
                confidence=0.95,
            )

        # I. Matched Opportunities / Available Jobs & Internships Inquiries
        # Handles all opportunity retrieval queries and natural typos ("are they any new jobs", "new jobs?", "any openings?", etc.)
        career_opp_terms = ["job", "jobs", "internship", "internships", "opportunity", "opportunities", "opening", "openings", "vacancy", "vacancies", "career", "careers", "role", "roles"]
        career_act_terms = [
            "are there", "are they", "is there", "any", "new", "available", "apply", "match", "matching",
            "fit", "show", "find", "list", "get", "for me", "recommend", "recommended", "latest",
            "closing", "got", "can i apply", "what is available", "what's available", "what are available",
            "anything", "what", "which", "how to apply"
        ]
        
        has_career_opp = any(t in q_lower for t in career_opp_terms)
        has_career_act = any(t in q_lower for t in career_act_terms)

        explicit_career_phrases = [
            "are they any new jobs", "are there any new jobs", "are there any new opportunities",
            "any new internships", "what jobs are available", "show me new jobs", "show me jobs",
            "any new career opportunities", "what opportunities are available", "are there new internships for me",
            "find me jobs", "find jobs", "what jobs match my skills", "any openings for me",
            "what new opportunities can i apply for", "are there any new jobs i can apply for",
            "any new job", "new jobs", "jobs available", "any jobs for me", "got any jobs",
            "anything new for me", "any openings", "what's new in careers", "anything i can apply for",
            "show me internships", "which jobs match my skills", "matched opportunities",
            "matching opportunities", "jobs matching my skills", "internships for me",
            "recommend opportunities", "recommended opportunities", "what jobs match my profile",
            "what internships are available for me", "opportunities match my", "fit my profile",
            "internships match my skills", "opportunities match my profile", "any job", "any internship",
            "job openings", "internship openings", "career opportunities", "available opportunities",
            "opportunities for me", "what opportunities"
        ]

        if any(p in q_lower for p in explicit_career_phrases) or (has_career_opp and has_career_act):
            return IntentClassificationResult(
                intent="CAREER_MATCHED_OPPORTUNITIES",
                domain="CAREER",
                context_badge="💼 CAREER INTELLIGENCE",
                query_mode="VIGNEX_DATA",
                confidence=0.98,
            )

        # -------------------------------------------------------------
        # 2.6 FACULTY ACADEMIC QUERY ROUTING (Phase 6C)
        # -------------------------------------------------------------
        # A. Hybrid queries connecting academic issues to complaints
        if any(p in q_lower for p in [
            "related to recent academic complaints", "related to recent complaints",
            "related to complaints", "complaints affecting my class", "complaints related to my",
            "issues related to recent academic complaints"
        ]):
            return IntentClassificationResult(
                intent="FACULTY_HYBRID_COMPLAINTS",
                domain="HYBRID",
                context_badge="⚡ HYBRID",
                query_mode="HYBRID",
                confidence=0.95,
            )

        # B. Faculty Attendance trend inquiries
        if any(p in q_lower for p in [
            "attendance trend in my", "attendance in my data structures", "attendance in my operating systems",
            "attendance in my class", "attendance trend in", "attendance of my class"
        ]):
            return IntentClassificationResult(
                intent="FACULTY_CLASS_ATTENDANCE",
                domain="ACADEMIC",
                context_badge="📚 ACADEMIC",
                query_mode="VIGNEX_DATA",
                confidence=0.95,
            )

        # C. Faculty Assignment backlog & completion inquiries
        if any(p in q_lower for p in [
            "highest assignment backlog", "assignment backlog in my", "assignment backlog",
            "why did assignment completion change", "assignment completion in my",
            "assignment completion change", "backlog in my classes"
        ]):
            return IntentClassificationResult(
                intent="FACULTY_ASSIGNMENT_BACKLOG",
                domain="ACADEMIC",
                context_badge="📚 ACADEMIC",
                query_mode="VIGNEX_DATA",
                confidence=0.95,
            )

        # D. Faculty Upcoming assessments
        if any(p in q_lower for p in [
            "what assessments are upcoming", "assessments are upcoming", "upcoming assessments in my",
            "assessments in my classes", "upcoming evaluations for my classes"
        ]):
            return IntentClassificationResult(
                intent="FACULTY_UPCOMING_ASSESSMENTS",
                domain="ACADEMIC",
                context_badge="📚 ACADEMIC",
                query_mode="VIGNEX_DATA",
                confidence=0.95,
            )

        # -------------------------------------------------------------
        # 2.7 MANAGEMENT ACADEMIC QUERY ROUTING (Phase 6D)
        # -------------------------------------------------------------
        # A. Hybrid Management queries (complaints + academics)
        if any(p in q_lower for p in [
            "academic complaint trends changing alongside attendance", "complaint trends changing alongside attendance",
            "academic complaints and attendance", "complaints and assignment completion", "complaints affecting attendance",
            "are academic complaints increasing while attendance is decreasing", "academic complaints increasing while attendance is decreasing",
            "transport complaint volume changed during the same period as academic workload"
        ]):
            return IntentClassificationResult(
                intent="MANAGEMENT_HYBRID_COMPLAINTS",
                domain="HYBRID",
                context_badge="⚡ HYBRID",
                query_mode="HYBRID",
                confidence=0.96,
            )

        # B. Department Attendance trends across institution
        if any(p in q_lower for p in [
            "attendance trend across departments", "attendance across departments", "largest attendance change",
            "department has the largest attendance change", "attendance by department", "department attendance trends",
            "which department has the highest attendance", "highest attendance"
        ]):
            return IntentClassificationResult(
                intent="MANAGEMENT_DEPARTMENT_ATTENDANCE",
                domain="ACADEMIC",
                context_badge="📚 ACADEMIC",
                query_mode="VIGNEX_DATA",
                confidence=0.96,
            )

        # C. Institutional Academic Pattern detection
        if any(p in q_lower for p in [
            "what academic patterns are emerging", "academic patterns are emerging", "academic patterns",
            "emerging academic patterns", "institutional academic patterns", "academic patterns detected"
        ]):
            return IntentClassificationResult(
                intent="MANAGEMENT_ACADEMIC_PATTERNS",
                domain="ACADEMIC",
                context_badge="📚 ACADEMIC",
                query_mode="VIGNEX_DATA",
                confidence=0.96,
            )

        # D. Institutional Assignment completion trends
        if any(p in q_lower for p in [
            "how is assignment completion changing", "assignment completion changing",
            "assignment completion across departments", "assignment trends", "institutional assignment completion"
        ]):
            return IntentClassificationResult(
                intent="MANAGEMENT_ASSIGNMENT_TRENDS",
                domain="ACADEMIC",
                context_badge="📚 ACADEMIC",
                query_mode="VIGNEX_DATA",
                confidence=0.95,
            )

        # -------------------------------------------------------------
        # 2.9 VIIT DUVVADA INSTITUTIONAL CONTEXT INTENTS (Phase 8B)
        # -------------------------------------------------------------
        # A. Unconnected Live Data Refusal (Library Live Availability / Bus GPS / Staff Phone Numbers)
        if any(p in q_lower for p in [
            "is the library open right now", "library open right now", "how many books",
            "book availability", "check book in library", "where is bus", "bus gps",
            "live bus position", "live bus location", "live bus tracking", "phone number of hod",
            "professor's phone number", "faculty personal number", "hod contact number",
            "principal phone number", "personal phone number", "bus 14 right now"
        ]):
            return IntentClassificationResult(
                intent="VIIT_LIVE_REFUSAL",
                domain="CAMPUS_INTELLIGENCE",
                context_badge="🏛️ VIIT CONTEXT",
                query_mode="VIGNEX_DATA",
                confidence=0.99,
            )

        # B. VIIT Exam Terminology (CIE, SEE, Mid-1 vs SEE)
        if any(p in q_lower for p in [
            "what is cie", "continuous internal evaluation", "what is see", "semester end exam",
            "difference between mid-1 and see", "difference between mid 1 and see",
            "difference between mid and see", "difference between midterm and final",
            "what is mid-1", "what is mid-2", "what is mid 1", "what is mid 2",
            "lab internal", "lab external"
        ]):
            return IntentClassificationResult(
                intent="VIIT_EXAM_TERMINOLOGY",
                domain="ACADEMIC",
                context_badge="🏛️ VIIT CONTEXT",
                query_mode="VIGNEX_DATA",
                confidence=0.98,
            )

        # C. VIIT Regulation Info (VR20, VR22, VR23)
        if any(p in q_lower for p in [
            "what does vr22 mean", "what is vr22", "what is vr20", "what is vr23",
            "tell me about vr22", "tell me about vr23", "what regulation am i", "viit regulation"
        ]):
            return IntentClassificationResult(
                intent="VIIT_REGULATION_INFO",
                domain="ACADEMIC",
                context_badge="🏛️ VIIT CONTEXT",
                query_mode="VIGNEX_DATA",
                confidence=0.98,
            )

        # D. VIIT Attendance Policy & Condonation Range
        if any(p in q_lower for p in [
            "what is the condonation range", "condonation range", "detention warning",
            "viit attendance policy", "what attendance is required", "attendance condonation"
        ]):
            return IntentClassificationResult(
                intent="VIIT_ATTENDANCE_POLICY",
                domain="ACADEMIC",
                context_badge="🏛️ VIIT CONTEXT",
                query_mode="VIGNEX_DATA",
                confidence=0.98,
            )

        # E. VIIT Campus Locations & Buildings
        if any(p in q_lower for p in [
            "what buildings are on the campus", "what buildings are on campus", "buildings on campus",
            "where is apj abdul kalam", "where is kalam block", "where is sir mv block",
            "where is ramanujan block", "where is aryabhata block", "where is vignan dhara",
            "where is the library", "where is dharitri", "priyadarshini girls hostel", "priyadarshini hostel"
        ]):
            return IntentClassificationResult(
                intent="VIIT_CAMPUS_LOCATIONS",
                domain="CAMPUS_INTELLIGENCE",
                context_badge="🏛️ VIIT CONTEXT",
                query_mode="VIGNEX_DATA",
                confidence=0.98,
            )

        # F. VIIT Department Catalog (CSM, CSD, CSC, AI&DS)
        if any(p in q_lower for p in [
            "what does csm mean", "what is csm", "what is csd", "what is csc",
            "what is ai&ds", "what is aids department", "viit departments", "what engineering branches"
        ]):
            return IntentClassificationResult(
                intent="VIIT_DEPARTMENT_INFO",
                domain="ACADEMIC",
                context_badge="🏛️ VIIT CONTEXT",
                query_mode="VIGNEX_DATA",
                confidence=0.98,
            )

        # G. Statutory & Grievance Bodies (Anti-Ragging, ICC, WPC, CGRC)
        if any(p in q_lower for p in [
            "what is the anti-ragging committee", "anti ragging committee", "internal complaints committee",
            "what is icc", "women protection cell", "where should i report a grievance",
            "where can i report a grievance", "who to report grievance", "central grievance redressal"
        ]):
            return IntentClassificationResult(
                intent="VIIT_STATUTORY_GRIEVANCE",
                domain="COMPLAINTS",
                context_badge="🏛️ VIIT CONTEXT",
                query_mode="VIGNEX_DATA",
                confidence=0.98,
            )

        # H. Transport Routes
        if any(p in q_lower for p in [
            "what bus routes are there", "viit bus routes", "transport routes",
            "what areas does the bus cover", "maddilapalem bus", "gajuwaka bus"
        ]):
            return IntentClassificationResult(
                intent="VIIT_TRANSPORT_ROUTES",
                domain="CAMPUS_INTELLIGENCE",
                context_badge="🏛️ VIIT CONTEXT",
                query_mode="VIGNEX_DATA",
                confidence=0.98,
            )

        # I. Training & Placement / CRT Context
        if any(p in q_lower for p in [
            "what is t&p cell", "what is crt", "campus recruitment training", "placement cell viit", "training and placement cell"
        ]):
            return IntentClassificationResult(
                intent="VIIT_PLACEMENT_CONTEXT",
                domain="CAREER",
                context_badge="🏛️ VIIT CONTEXT",
                query_mode="VIGNEX_DATA",
                confidence=0.98,
            )

        # -------------------------------------------------------------
        # 2.95 ACTION INTELLIGENCE & PRIORITIES INTENTS (Phase 10)
        # -------------------------------------------------------------
        if any(p in q_lower for p in [
            "what should i do first", "what should i do next", "what needs my attention",
            "what are my priorities today", "what are my priorities", "my priorities",
            "why is this my priority", "what should i act on first",
            "what should i focus on first", "what should i focus on",
            "why is this a priority", "why is my priority", "why is this currently a priority"
        ]) or ("priority for me" in q_lower) or ("currently a priority" in q_lower):
            return IntentClassificationResult(
                intent="ACTION_PRIORITIES",
                domain="CROSS_DOMAIN",
                context_badge="🎯 ACTION INTELLIGENCE",
                query_mode="VIGNEX_DATA",
                confidence=0.99,
            )

        # -------------------------------------------------------------
        # 2.96 CROSS-DOMAIN INSIGHTS & PROACTIVE ENGINE INTENTS (Phase 9)
        # -------------------------------------------------------------
        if any(p in q_lower for p in [
            "what insights do you have for me", "what insights do you have", "my insights",
            "why did vignai recommend this", "why was this recommended",
            "what changed recently", "recent insights", "my proactive insights",
            "what are my biggest academic risks", "biggest academic risks",
            "which career opportunity should i prioritize", "career opportunity should i prioritize",
            "why is this campus issue important", "why is this issue important"
        ]):
            return IntentClassificationResult(
                intent="VIGNAI_CROSS_DOMAIN_INSIGHTS",
                domain="CROSS_DOMAIN",
                context_badge="🧠 VIGNAI INSIGHTS",
                query_mode="VIGNEX_DATA",
                confidence=0.98,
            )

        # -------------------------------------------------------------
        # 3. EXPLICIT GENERAL KNOWLEDGE CLASSIFICATION
        # -------------------------------------------------------------
        has_campus_explicit_mention = any(k in q_lower for k in CAMPUS_INDICATOR_KEYWORDS)
        
        matched_loc = None
        for l_name, l_kws in CAMPUS_LOCATIONS.items():
            if any(kw in q_lower for kw in l_kws):
                matched_loc = l_name
                break

        q_clean = re.sub(r'[\.\?!]+$', '', q_lower).strip()

        is_generic_definition = bool(
            re.search(r'^(what is|what are|define|explain|how does|how do|what means|tell me about)\s+([a-zA-Z0-9\s/_-]+)$', q_clean)
        )

        if is_generic_definition and not has_campus_explicit_mention and not (matched_loc and any(w in q_lower for w in ["risk", "issue", "problem", "broken", "complaint", "increasing", "unresolved", "happening"])):
            return IntentClassificationResult(
                intent="GENERAL_KNOWLEDGE",
                domain="GENERAL_KNOWLEDGE",
                context_badge="📖 GENERAL KNOWLEDGE",
                query_mode="GENERAL_KNOWLEDGE",
                confidence=0.98,
            )

        if any(q_lower.startswith(prefix) for prefix in [
            "how can colleges", "how to improve college", "best practices for", "how do universities",
            "general advice on", "how to write", "how to implement", "history of", "tell me about"
        ]) and not has_campus_explicit_mention:
            return IntentClassificationResult(
                intent="GENERAL_KNOWLEDGE",
                domain="GENERAL_KNOWLEDGE",
                context_badge="📖 GENERAL KNOWLEDGE",
                query_mode="GENERAL_KNOWLEDGE",
                confidence=0.95,
            )

        general_stem_terms = [
            "photosynthesis", "recursion", "tcp", "udp", "http", "binary search",
            "quicksort", "machine learning", "neural network", "deep learning",
            "mitochondria", "gravity", "quantum", "calculus", "derivative",
            "c programming", "c++", "python syntax", "data structure", "algorithm",
            "operating system theory", "database normalization", "sql injection"
        ]
        if any(term in q_lower for term in general_stem_terms) and not has_campus_explicit_mention:
            return IntentClassificationResult(
                intent="GENERAL_KNOWLEDGE",
                domain="GENERAL_KNOWLEDGE",
                context_badge="📖 GENERAL KNOWLEDGE",
                query_mode="GENERAL_KNOWLEDGE",
                confidence=0.95,
            )

        # -------------------------------------------------------------
        # 4. TIME WINDOW EXTRACTION
        # -------------------------------------------------------------
        time_window = "30d"
        if any(w in q_lower for w in ["this week", "past 7 days", "last 7 days", "7d", "weekly"]):
            time_window = "7d"
        elif any(w in q_lower for w in ["this month", "past 30 days", "last 30 days", "30d", "recently", "recent"]):
            time_window = "30d"
        elif any(w in q_lower for w in ["90 days", "last 90 days", "quarter", "semester", "3 months"]):
            time_window = "90d"
        elif any(w in q_lower for w in ["all time", "overall", "entire history", "total"]):
            time_window = "all"

        # -------------------------------------------------------------
        # 5. CAMPUS ENTITY MATCHING (Departments, Locations, Categories)
        # -------------------------------------------------------------
        matched_dept = None
        for d_name, d_kws in DEPT_MAP.items():
            if any(kw in q_lower for kw in d_kws):
                matched_dept = d_name
                break

        matched_cat = None
        for c_name, c_kws in CATEGORY_MAP.items():
            if any(kw in q_lower for kw in c_kws):
                matched_cat = c_name
                break

        # -------------------------------------------------------------
        # 6. VIGNEX CAMPUS DATA INTENT CLASSIFICATION
        # -------------------------------------------------------------
        # A. Department Analysis Query (e.g. "Which department has the most unresolved complaints?")
        if any(p in q_lower for p in [
            "most unresolved", "department with the most", "unresolved cases by department",
            "which department has the most unresolved complaints", "which department has the most",
            "department complaints", "dept with highest", "unresolved queue",
            "what are the department issues", "department issues", "department problems", "department concerns"
        ]):
            return IntentClassificationResult(
                intent="DEPARTMENT_ANALYSIS",
                domain="COMPLAINTS",
                context_badge="🏛️ VIGNAN CAMPUS DATA",
                query_mode="VIGNEX_DATA",
                department=matched_dept,
                time_window=time_window,
                confidence=0.95,
            )

        # B. Emerging Issues / Top Problems / Patterns (e.g. "What are the biggest problems on campus?")
        if any(p in q_lower for p in [
            "emerging issues", "biggest emerging", "major problems", "biggest problems",
            "top issues", "campus summary", "overview", "what are the biggest",
            "campus issues", "top complaints", "major concerns on campus", "problems on campus",
            "what are the biggest complaints on campus", "biggest complaints on campus", "biggest campus problems"
        ]):
            return IntentClassificationResult(
                intent="CAMPUS_OVERVIEW",
                domain="CAMPUS_INTELLIGENCE",
                context_badge="🏛️ VIGNAN CAMPUS DATA",
                query_mode="VIGNEX_DATA",
                time_window=time_window,
                confidence=0.95,
            )

        # C. Recurring Defects (e.g. "What issues are recurring?")
        if any(p in q_lower for p in ["recurring", "recur", "repeated", "repeat", "frequent", "recurring issues", "recurring problems"]):
            return IntentClassificationResult(
                intent="RECURRING_ANALYSIS",
                domain="CAMPUS_INTELLIGENCE",
                context_badge="🏛️ VIGNAN CAMPUS DATA",
                query_mode="VIGNEX_DATA",
                location=matched_loc,
                category=matched_cat,
                time_window=time_window,
                confidence=0.92,
            )

        # D. Specific Location Risk Drilldown (e.g. "Why is Block A becoming a risk?")
        if matched_loc:
            return IntentClassificationResult(
                intent="LOCATION_ANALYSIS",
                domain="CAMPUS_INTELLIGENCE",
                context_badge="🏛️ VIGNAN CAMPUS DATA",
                query_mode="VIGNEX_DATA",
                location=matched_loc,
                time_window=time_window,
                confidence=0.94,
            )

        # E. Category Queries (e.g. "Show transport-related cases", "How many transport cases are unresolved?")
        if matched_cat or any(p in q_lower for p in [
            "transport cases", "wifi cases", "wi-fi cases", "network cases", "lab cases",
            "transport complaints", "wifi complaints", "cleanliness cases", "unresolved"
        ]):
            return IntentClassificationResult(
                intent="CATEGORY_ANALYSIS",
                domain="COMPLAINTS",
                context_badge="🏛️ VIGNAN CAMPUS DATA",
                query_mode="VIGNEX_DATA",
                category=matched_cat or ("Transport" if "transport" in q_lower or "bus" in q_lower else "Wi-Fi / Network"),
                time_window=time_window,
                confidence=0.92,
            )

        # F. Trend / Time Comparison (e.g. "What changed this week?")
        if any(p in q_lower for p in ["changed", "this week", "what's new", "timeline", "trend", "latest"]):
            return IntentClassificationResult(
                intent="TIME_COMPARISON",
                domain="CAMPUS_INTELLIGENCE",
                context_badge="🏛️ VIGNAN CAMPUS DATA",
                query_mode="VIGNEX_DATA",
                time_window=time_window,
                confidence=0.90,
            )

        # G. Department Direct Analysis
        if matched_dept:
            return IntentClassificationResult(
                intent="DEPARTMENT_ANALYSIS",
                domain="COMPLAINTS",
                context_badge="🏛️ VIGNAN CAMPUS DATA",
                query_mode="VIGNEX_DATA",
                department=matched_dept,
                time_window=time_window,
                confidence=0.90,
            )

        # H. If the user mentions "vignex", "campus", "complaints", "students", but not specific entities
        if has_campus_explicit_mention:
            return IntentClassificationResult(
                intent="CAMPUS_OVERVIEW",
                domain="CAMPUS_INTELLIGENCE",
                context_badge="🏛️ VIGNAN CAMPUS DATA",
                query_mode="VIGNEX_DATA",
                time_window=time_window,
                confidence=0.85,
            )

        # -------------------------------------------------------------
        # 7. DEFAULT SAFE GENERAL KNOWLEDGE FALLBACK
        # -------------------------------------------------------------
        return IntentClassificationResult(
            intent="GENERAL_KNOWLEDGE",
            domain="GENERAL_KNOWLEDGE",
            context_badge="📖 GENERAL KNOWLEDGE",
            query_mode="GENERAL_KNOWLEDGE",
            time_window=time_window,
            confidence=0.80,
        )


query_router = QueryRouter()

