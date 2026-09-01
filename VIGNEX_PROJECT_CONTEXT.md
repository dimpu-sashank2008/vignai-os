# VIGNEX PROJECT CONTEXT

## Product

VIGNEX is an AI-Native Campus Operating System.

**Tagline:**
*Understand. Connect. Predict. Act.*

VIGNEX is being developed as a standalone software product first.
Future goal: potentially replace/integrate existing Vignan campus systems.

---

# USER ROLES & DEVELOPMENT CREDENTIALS

VIGNEX has three core authenticated roles with isolated permissions and dedicated workspaces:

1. **Student**
   - Email: `student@vignex.dev`
   - Password: `password123`
   - Role: `student`
   - Workspace: Issue reporting, multi-evidence uploads, protected identity toggling, personal complaint timeline, notifications, and profile.

2. **Faculty**
   - Email: `faculty@vignex.dev`
   - Password: `password123`
   - Role: `faculty` (Department: CSE)
   - Workspace: Department queue, assigned cases, clustered issue groups, investigation notes, escalation, status synchronization.

3. **Management**
   - Email: `management@vignex.dev`
   - Password: `password123`
   - Role: `management`
   - Workspace: Campus Issues console, clustered case groups, AI Intelligence Center (KPIs, active patterns, AI priorities, domain health, trend analytics, activity stream), Intelligence Knowledge Graph, Explainability ("Why this insight?"), Ask VIGNEX natural language console, What-If Simulation Lab.

---

# CORE ARCHITECTURE & TECH STACK

- **Frontend:** React 18, Vite, TypeScript, Tailwind CSS, React Router v6, Lucide Icons, Axios.
- **Backend:** Python 3.11, FastAPI, SQLAlchemy ORM, Pydantic v2, PyJWT, Passlib (bcrypt).
- **Database:** SQLite development database (`backend/vignex.db`) with deterministic backend path resolution (`get_database_url()`).
- **AI Abstraction Layer:** Unified `AIProvider` interface supporting Google Gemini (`gemini-3.6-flash` with structured outputs) and `LocalHeuristicProvider` (resilient offline rule-based fallback).
- **Security:** Backend-only AI API keys, JWT Bearer authentication, role-based authorization dependencies (`require_role`), deterministic routing policy governance.

---

# SINGLE SOURCE OF TRUTH (SSOT)

There is **ONE canonical Complaint/Case record** in the database:
- Example: `VX-839336`.
- Student sees `VX-839336`.
- Faculty sees `VX-839336` (if authorized by department routing policy).
- Management sees `VX-839336` with full administrative oversight.
- Status changes (`SUBMITTED` → `UNDER_REVIEW` → `IN_PROGRESS` → `RESOLVED` → `CLOSED`), investigation notes, and timeline events update the single centralized record and propagate immediately across all role views.
- **No duplicate complaint records are ever created.**

---

# PRIVACY & IDENTITY PROTECTION MODEL

Students are fully authenticated; the platform knows their verified identity.

**Protected Identity Workflow:**
- When `identity_protected=True` is selected by the student:
  - Faculty and Management detail and list views redact student personal identifiers (`reporter_visibility="IDENTITY_PROTECTED"`).
  - Student name, email, and enrollment ID are withheld from case handlers by default.
  - Internal database relationships maintain student linkage for status updates and notifications without leaking data to handlers.
- **Subject Restriction:** A faculty member or staff member who is the subject of a complaint is strictly restricted from viewing the case.
- **Ask VIGNEX Privacy Refusal:** Queries inquiring about student identity (e.g., *"Who submitted case VX-123456?"*) trigger an immediate `PRIVACY_REFUSAL` short-circuit without querying or exposing database identity fields.

---

# EVIDENCE HANDLING

- Students can attach photos (`.jpg`, `.png`, `.webp`, `.gif`), videos (`.mp4`, `.webm`, `.mov`), and documents (`.pdf`, `.doc`, `.docx`, `.txt`) up to 25MB per file.
- Evidence files are securely stored on the backend filesystem with randomized UUID filenames, path traversal sanitization, and database metadata linking.
- Case handlers and students can download evidence via authenticated `/api/complaints/{case_id}/evidence/{evidence_id}/download` endpoints.
- AI analyzes natural language complaint descriptions but **never determines whether evidence proves an allegation**. Evidence is preserved for authorized human review.

---

# OFFICIAL CATEGORY TAXONOMY

Centralized in `backend/app/config/categories.py`, the official 7 top-level categories and their subcategories are:

1. **ACADEMIC**
   - Faculty Conduct
   - Teaching Quality
   - Attendance
   - Assignment
   - Examination
   - Timetable
   - Academic Administration

2. **INFRASTRUCTURE**
   - Classroom
   - Laboratory
   - Projector
   - Furniture
   - Electrical
   - Air Conditioning
   - Maintenance

3. **TECHNOLOGY**
   - Wi-Fi / Network
   - ERP / Portal
   - Computer System
   - Software / Access

4. **CAMPUS_OPERATIONS**
   - Transport
   - Hostel
   - Cleanliness
   - Security
   - Campus Maintenance

5. **STUDENT_SERVICES**
   - Scholarships
   - Certificates
   - Administration
   - Student Affairs

6. **SENSITIVE_GRIEVANCE**
   - Faculty Conduct
   - Serious Conduct Concern
   - Retaliation Concern
   - Other Sensitive Matter

7. **OTHER**
   - General

**Taxonomy Rules:**
- All AI providers (Gemini and Heuristic) strictly output official top-level category keys.
- `normalize_category_name()` maps subcategories, colloquial aliases, and abbreviations (e.g., `wifi` → `TECHNOLOGY`, `bus` → `CAMPUS_OPERATIONS`, `lab` → `INFRASTRUCTURE`) to the canonical top-level keys.
- **Critical Policy:** Faculty conduct complaints must NEVER default to `OTHER` or `ACADEMIC`; they must classify as `SENSITIVE_GRIEVANCE` with `HIGH_SENSITIVITY`.

---

# DETERMINISTIC ROUTING POLICY ENGINE

The LLM is **never** the authorization system. Routing recommendations generated by AI are validated and enforced by `backend/app/services/routing/routing_policy.py`:

1. **Rule 1 (Sensitive Grievance & Conduct Allegation):**
   - Category: `SENSITIVE_GRIEVANCE` or `sensitivity="HIGH_SENSITIVITY"` or `suggested_route_type="AUTHORIZED_GRIEVANCE"`.
   - Routing: `Authorized Grievance Authority (Student Affairs)` + `Management Oversight (Administration)`.
   - Policy Result: `RESTRICTED_OVERRIDE`.
   - Restricted: `["SUBJECT_FACULTY", "DEPARTMENT_FACULTY"]`. Department faculty are strictly denied access.

2. **Rule 2 (Transport Authority):**
   - Subcategory: `Transport` or keywords (`bus`, `shuttle`, `transit`).
   - Routing: `Campus Transport Authority` + `Management Oversight`.

3. **Rule 3 (Hostel Administration):**
   - Subcategory: `Hostel` or keywords (`hostel`, `dorm`, `warden`, `mess`).
   - Routing: `Hostel Administration (Hostel Warden)` + `Management Oversight`.

4. **Rule 4 (Examinations Authority):**
   - Subcategory: `Examination` / `Timetable` or keywords (`exam`, `timetable`).
   - Routing: `Examinations Authority (Examination Cell)` + `Management Oversight`.

5. **Rule 5 (Technology / Network Operations):**
   - Category: `TECHNOLOGY` or subcategory `Wi-Fi / Network` / `ERP / Portal`.
   - Routing: `Campus Operations (IT)` + `Management Oversight`.

6. **Rule 6 (Campus Operations & Facilities):**
   - Category: `CAMPUS_OPERATIONS` or subcategory `Cleanliness`, `Security`, `Campus Maintenance`.
   - Routing: `Campus Operations (Maintenance / Security)` + `Management Oversight`.
   - **Critical Rule:** `CAMPUS_OPERATIONS` cases will never fall through to default CSE academic routing.

7. **Rule 7 (Student Services):**
   - Category: `STUDENT_SERVICES` (scholarships, certificates, student affairs).
   - Routing: `Student Services & Affairs` + `Management Oversight`.

8. **Rule 8 (Department-Specific Academic / Lab Infrastructure):**
   - Category: `INFRASTRUCTURE` / `ACADEMIC` with department context.
   - Routing: `{Matched Dept} Department Faculty` + `Management Oversight`.

---

# RELATED COMPLAINT GROUPING LAYER

Implemented in `backend/app/services/intelligence/grouping_service.py`:
- Clusters related complaints into cohesive `RelatedCaseGroup` structures (e.g. 5 individual Wi-Fi reports in Block A cluster into 1 group).
- **Non-Destructive:** Underlying complaint records (`Complaint`) remain individual, untouched, and fully tracked.
- **Explainability Signals:** Each group provides explicit signals explaining *"Why Grouped?"* (e.g., shared location, matching category, common keywords, time window).
- Group metrics calculate aggregate impact, affected location, time span, and highest priority.
- Supported in both Management (`/api/management/case-groups`) and Faculty (`/api/faculty/department-groups`) consoles with toggleable view modes (`Grouped Clusters` vs `Individual Cases`).

---

# DETERMINISTIC PRIORITY SORTING

Implemented in `backend/app/services/intelligence/sorting_utils.py`:
- Deterministic priority ranking: `CRITICAL` (rank 4) > `HIGH` (rank 3) > `MEDIUM` (rank 2) > `LOW` (rank 1).
- Multi-factor deterministic tie-breaking:
  1. Priority level (highest first)
  2. Active status priority (`SUBMITTED` / `UNDER_REVIEW` / `IN_PROGRESS` prioritized over `RESOLVED` / `CLOSED`)
  3. Evidence presence (cases with uploaded photos/docs rank higher)
  4. Recency (newest `created_at` timestamp first)
- Both individual complaint lists and clustered case groups are deterministically sorted by priority-first order by default.

---

# ASK VIGNEX INTELLIGENCE CONSOLE

Implemented in `backend/app/services/ask_vignex/`:
- **Dual Query Mode Architecture:**
  1. `GENERAL_KNOWLEDGE`: Handles open-ended concepts, definitions, STEM explanations (e.g., *"What is photosynthesis?"*, *"Explain recursion in C"*, *"How does TCP work?"*). Returns synthesized knowledge without querying or exposing campus complaint data.
  2. `VIGNEX_DATA`: Handles campus operational queries (e.g., *"What are the biggest problems on campus?"*, *"Why is Block A becoming a risk?"*, *"How many transport cases are unresolved?"*). Deterministically retrieves verified SQLite records and grounds responses strictly in campus data.
- **Intent Safety & Neutrality Guards:**
  - `PRIVACY_REFUSAL`: Rejects inquiries attempting to identify student reporters.
  - `ALLEGATION_NEUTRALITY`: Rejects requests to adjudicate guilt or confirm allegation truth (e.g., *"Is the professor guilty?"*).
  - Contextual follow-up memory tracks referenced items across conversational turns.
- **UI Mode Badges:** Visual indicators (`VIGNEX Campus Intelligence` vs `General Knowledge Q&A`) inform the user of the active mode.

---

# MANAGEMENT INTELLIGENCE CENTER, GRAPH & WHAT-IF LAB

1. **AI Intelligence Center (Phase 4A):**
   - Top-level KPI summary cards (Resolved Rate, Active Clusters, Risk Index, Score Breakdown).
   - Emerging pattern cards with supporting case counts and trend direction.
   - AI priority ranking table with transparent score calculation.
   - Campus Domain Health Matrix (Academics, Infrastructure, Tech, Operations).
   - Trend analytics timeline with 7d / 30d / 90d / all-time filters.
   - Real-time AI processing and routing activity stream.
   - Structured *"Why this insight?"* modal with supporting signals, data provenance, and limitations.

2. **Intelligence Knowledge Graph (Phase 4B):**
   - Graph visualization connecting actual database entities: `Case`, `Category`, `Location`, `Department`, and `Pattern`.
   - Strictly forbids fabricating non-existent relationships or leaking protected identity.

3. **What-If Simulation Lab (Phase 4D):**
   - Deterministic mathematical models for campus scenario simulations:
     - Transport route adjustments & bus additions
     - Infrastructure & Wi-Fi capacity enhancements
     - Preventive maintenance scheduling
     - Resource reallocation
   - AI generates trade-off explanations and recommendations grounded strictly in deterministic simulation formulas.
   - Outputs clearly labeled as *Estimated / Modeled Simulation*.

---

# THEME SYSTEM

- Supports `LIGHT`, `DARK`, and `SYSTEM` modes.
- Theme preference persists in `localStorage` (`vignex_theme`).
- Applied universally across Student, Faculty, and Management workspaces, modals, charts, graph canvases, and consoles.

---

# COMPLETED PHASES SUMMARY

- **Phase 0 — Foundation:** React, Vite, TypeScript, Tailwind, FastAPI, SQLite, JWT Auth, role routing.
- **Phase 1 — Student Experience:** Dashboard, Report Issue, My Complaints, Case Detail, Evidence Uploads, Protected Identity, Timeline.
- **Phase 2 — AI Complaint Engine:** AI classification, structured extraction, priority suggestion, graceful heuristic fallback.
- **Phase 3 — Routing & Faculty Workflow:** Deterministic policy engine, faculty workspace, case actions, investigation notes, escalation, grievance isolation.
- **Phase 4A — AI Intelligence Center:** Executive dashboard, patterns, priority ranking, domain health matrix, trend analytics.
- **Phase 4B — Intelligence Graph:** Relationship graph linking verified cases, locations, categories, departments.
- **Phase 4C — Ask VIGNEX:** Intent routing, verified context retrieval, grounded Q&A, safety short-circuits.
- **Phase 4D — What-If Lab:** Deterministic scenario simulations with multi-scenario comparison and AI trade-off analysis.
- **Phase 4E / Polish — Intelligence Correction:** Dual query modes (`GENERAL_KNOWLEDGE` vs `VIGNEX_DATA`), `RelatedCaseGroup` non-destructive clustering, deterministic priority sorting, UI mode badges.
- **Architecture Hardening:** Centralized taxonomy normalization, routing policy rule ordering, heuristic conduct classification hardening, duplicate router cleanup, database path resolution hardening.
- **Phase 5 — Faculty Feedback & Concern Intelligence + Category Taxonomy + Light/Dark/System Theme:**
  - Backend: Central 7-category taxonomy in `backend/app/config/categories.py`; `GET /api/complaints/taxonomy` endpoint.
  - Backend: `faculty_intelligence.py` service — thematic grouping, concern overview, privacy-enforced concern list, formal faculty response (`FACULTY_RESPONSE` note type).
  - Backend: `GET /api/faculty/feedback/overview`, `GET /api/faculty/feedback/concerns`, `POST /api/faculty/cases/{id}/response`, `GET /api/management/faculty-insights` endpoints.
  - Frontend: `ThemeContext.tsx` with localStorage persistence (`vignex_theme`), `light`/`dark`/`system` modes, OS-level media query listening.
  - Frontend: `AppearanceSettings.tsx` — compact (icon cycle) and full (three-button panel) variants.
  - Frontend: Dark mode applied across `DashboardLayout`, `Sidebar`, `TopNav`, `ReportIssuePage` (with `dark:` Tailwind classes).
  - Frontend: `FacultyFeedbackPage.tsx` at `/faculty/feedback` — KPIs, concern themes, case list with status/search filters, Provide Response flow.
  - Frontend: `ReportIssuePage.tsx` now fetches live taxonomy (`GET /api/complaints/taxonomy`) and renders two-tier Category + Subcategory optional dropdowns.
  - Frontend: Faculty sidebar updated — "Insights" replaced with "Feedback & Concerns" → `/faculty/feedback`.
  - All Phase 5 backend tests: 6/6 PASSED. Frontend build: 0 TypeScript errors.
- **Phase 6A — Academic Database & APIs:**
  - Backend Models: `AcademicSubject`, `StudentSubjectEnrollment`, `AttendanceRecord`, `Assessment`, `AssessmentResult`, `Assignment`, `TimetableEntry` in `backend/app/models/`.
  - Synthetic Data: Full 30-day realistic attendance logs, scored assessments, assignments (submitted/pending/overdue), and weekly timetable in `backend/app/seed.py`.
  - Academic Services: Deterministic metrics calculation in `academic_service.py` and structured, explainable AI insights in `academic_insight_service.py`.
  - API Router: `backend/app/routers/academics.py` mounted at `/api`.
- **Phase 6B — Student Academic Intelligence:**
  - Frontend: `StudentAcademicsPage.tsx` at `/student/academics` with top KPIs, subject cards, attendance logs & trends, assessments, assignment tracker, academic calendar, workload concentration detection, timetable schedule overlap detection, and explainable AI insights with "Why this insight?" modal.
  - Sidebar & Navigation: Added "Academics" to student sidebar in `Sidebar.tsx` and route in `App.tsx`.
  - Ask VIGNEX Integration: Added student academic intents (`STUDENT_ATTENDANCE`, `STUDENT_ASSESSMENTS`, `STUDENT_ASSIGNMENTS`, `STUDENT_WORKLOAD`, `STUDENT_SCHEDULE`) with user-isolated data retrieval and strict domain separation from complaints and general knowledge.
- **Phase 6C — Faculty Academic Intelligence:**
  - Backend: Class-level endpoints at `/api/faculty/academic-intelligence/subjects/{subject_id}/*` with strict 403 authorization checking `subject.faculty_user_id == current_user.id`.
  - Backend: Deterministic class analytics (`academic_service.py`) for attendance trends, submission velocity vs baseline, assessment averages, timetable timeline, and corroboration with authorized department complaints (`Complaint.category.in_(["ACADEMIC", "INFRASTRUCTURE", "TECHNOLOGY"])`).
  - Backend: Explainable AI insights (`academic_insight_service.py`) with non-punitive tone, data basis, and limitations.
  - Backend: Faculty Ask VIGNEX intents (`FACULTY_CLASS_ATTENDANCE`, `FACULTY_ASSIGNMENT_BACKLOG`, `FACULTY_UPCOMING_ASSESSMENTS`, `FACULTY_HYBRID_COMPLAINTS`) in `query_router.py` & `answer_service.py`.
  - Frontend: `FacultyAcademicPage.tsx` at `/faculty/academic-intelligence` with top summary KPIs, Class/Subject selector dropdown, alerts, AI insight cards with "[ Why this insight? ]" modal, 6 detail tabs, quick actions, and full light/dark theme support.
  - Sidebar & Navigation: Added "Academic Intelligence" to faculty sidebar in `Sidebar.tsx` and route in `App.tsx`.
- **Phase 6D — Management Academic Intelligence:**
  - Backend: Institutional endpoints (`/api/management/academic-intelligence/overview`, `/departments`, `/trends`, `/patterns`, `/insights`, `/ask`) with time window filtering (`7d`, `30d`, `90d`, `all`).
  - Backend: Deterministic Academic Health calculation (`HEALTHY`, `WATCH`, `ELEVATED`, `HIGH RISK`), department-level comparative aggregation (attendance, submission rates, assessments), and institutional pattern detection.
- **Phase 6E — Ask VIGNEX Academic + Cross-Domain Integration:**
  - Intent & Domain Architecture: 6 explicit data domains (`GENERAL_KNOWLEDGE`, `ACADEMIC`, `COMPLAINTS`, `CAMPUS_INTELLIGENCE`, `SIMULATIONS`, `HYBRID`) with deterministic query router boundaries.
  - Safe Retrieval Boundaries: Zero cross-domain leakage; general STEM queries (e.g. Photosynthesis, Recursion) bypass database entirely.
  - Strict Role Authorization:
    - Student: Only own academic records, only own complaints (`STUDENT_OWN_COMPLAINTS`), simulations restricted.
    - Faculty: Only authorized classes, only authorized cases, protected reporter identities concealed.
    - Management: Institutional aggregates, campus patterns, deterministic What-If transit simulations (`SIMULATION_WHAT_IF`).
  - Cross-Domain Hybrid Intelligence: Non-causal observational correlation between infrastructure complaints and academic velocity.
  - Privacy & Neutrality Safeguards: `PRIVACY_REFUSAL` and `ALLEGATION_NEUTRALITY` enforced across all analytical endpoints.
  - Context Badges: Distinct badges (`📖 GENERAL KNOWLEDGE`, `📚 ACADEMIC`, `🏛️ VIGNEX CAMPUS DATA`, `🛠️ SIMULATION`, `⚡ HYBRID`) rendered dynamically in Ask VIGNEX UI.
  - Multi-turn Conversational Memory: Follow-up intent resolution with dynamic domain switching.

---

# EXPO DEMO FLOW POLICY

- **There is NO separate "Expo Demo Mode".**
- `ExpoDemoPage.tsx` has been permanently removed.
- Demonstrations are conducted manually through standard role accounts:
  1. Student logs in (`student@vignex.dev`), submits an issue with evidence and identity protection.
  2. Faculty logs in (`faculty@vignex.dev`), inspects department cluster, investigates, adds note, updates status.
  3. Management logs in (`management@vignex.dev`), inspects Intelligence Center, runs What-If simulation, explores Graph, queries Ask VIGNEX.
  4. Student receives real-time notification and sees propagated status update on the single canonical case record.

---

# TESTING & VERIFICATION STATUS

- **Backend Test Suite:** 90/90 automated tests passing (100%):
  - `tests/test_architecture_hardening.py` (13 tests): Taxonomy consistency, heuristic classification, routing policy non-fallthrough, sensitive grievance isolation.
  - `tests/test_auth_endpoints.py` (5 tests): User existence, development logins, `/api/auth/me`, invalid password rejection.
  - `tests/test_intelligence_correction.py` (8 tests): Ask VIGNEX query modes, Block A grouping, priority sorting, tie-breaking hierarchy.
  - `tests/test_academic_6a.py` (19 tests): Student overview, subjects, attendance calculation, assessments, assignments, timetable conflict detection, workload window, AI insight schema, faculty overview, management aggregates, cross-role security.
  - `tests/test_academic_6b_student.py` (9 tests): Student Ask VIGNEX intents, domain isolation, deterministic workload window calculations, Responsible-AI neutrality.
  - `tests/test_academic_6c_faculty.py` (11 tests): Class-level overview authorization, 403 rejection on unauthorized classes, student access denial, deterministic attendance/assignment/assessment math, AI schema and non-punitive language, and faculty Ask VIGNEX & hybrid intents.
  - `tests/test_academic_6d_management.py` (10 tests): Management aggregate access, role rejection for student/faculty (403), deterministic health status, department breakdown metrics, AI schema and non-punitive checks, and management Ask VIGNEX intents.
  - `tests/test_academic_6e_cross_domain.py` (15 tests): Domain classification across all 6 domains, general knowledge isolation, student own complaints, campus risk, management simulation math and student restriction, hybrid cross-domain correlation, privacy refusal, allegation neutrality, and dynamic domain switching.
- **Frontend Production Build:** `npm run build` succeeds with zero TypeScript errors (1665 modules transformed).

---

# KNOWN LIMITATIONS & FUTURE ROADMAP (PHASE 6)

1. **General Knowledge Synthesis:** Offline GK mode currently uses structured pedagogical templates for core STEM/network topics; future phases can optionally pipe open general knowledge questions through Gemini while maintaining zero campus data exposure.
2. **Semantic Duplicate Scanning:** Currently executes in-memory Jaccard/keyword scanning across active complaints; indexed vector pre-filtering planned for enterprise scale.
3. **Phase 6 Roadmap:**
   - Academic & Faculty Feedback Intelligence (summarized student concern themes without simplistic or punitive scoring).
   - Advanced trend forecasting and proactive campus maintenance triggers.
   - PostgreSQL production migration configuration.

---

# IMPORTANT RESPONSIBLE-AI PRINCIPLES

1. **AI is NOT the final authority.** AI assists with understanding, grouping, explaining, and modeling; human authorized personnel make operational decisions.
2. **AI never determines truth or guilt.** AI must not adjudicate allegations or claim evidence is conclusive proof.
3. **Deterministic backend rules remain authoritative** for privacy, routing, authorization, and simulation mathematics.
4. **Never expose student identity** through AI outputs, graph nodes, or unauthorized responses.
5. **Never invent statistics, case numbers, or evidence.** If data is missing or insufficient, state it clearly.
6. **AI API keys remain backend-only.** Never expose keys or model credentials to the frontend.