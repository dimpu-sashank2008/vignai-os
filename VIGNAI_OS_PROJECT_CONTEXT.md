# VIGNAI OS — PROJECT CONTEXT & TECHNICAL MASTER SPECIFICATION

> **Current Document Version:** 2.0 (Post-Phase 6 & Brand Migration)  
> **Official Product Name:** **VIGNAI OS**  
> **Subtitle:** *Vignan's AI Campus Operating System*  
> **Tagline:** *Understand • Connect • Predict • Act*  
> **AI Assistant Persona:** **VIGNAI** (*"I am VIGNAI, the AI assistant of VIGNAI OS."*)  
> **Development Status:** Fully Implemented, Verified, and Operational (Phases 0 through 6E Complete)

---

## 1. PRODUCT VISION & OVERVIEW

**VIGNAI OS** is an AI-Native Campus Operating System architected specifically for Vignan University. It serves as a unified digital ecosystem integrating:
1. **Intelligent Campus Grievance & Facility Operations:** Natural language issue submission, multi-evidence uploads, protected student identity, automated triage, deterministic policy routing, and non-destructive issue clustering.
2. **Comprehensive Academic Intelligence (Phases 6A–6E):** Deterministic attendance tracking, assessment scoring, assignment submission velocity, workload concentration detection, timetable conflict analysis, and non-punitive class/institutional diagnostics.
3. **Executive Intelligence Center & What-If Decision Lab:** High-level operational KPIs, cross-domain health matrices, emergent risk pattern detection, knowledge graph entity mapping, and deterministic mathematical scenario simulations.
4. **Universal Ask VIGNAI Natural Language Assistant:** Grounded, role-isolated natural language querying spanning general knowledge, academic metrics, complaint histories, and cross-domain campus insights with anti-hallucination guarantees.

---

## 2. USER ROLES & DEVELOPMENT CREDENTIALS

VIGNAI OS enforces strict role-based access control (RBAC) across three primary authenticated personas, supporting dual **Identifier (Roll Number / Faculty ID / Management ID) + Password** and Email + Password authentication, with an enforced first-login password change policy:

### 1. Student Persona
- **Roll Number:** `221FA04001` (also accepts `STU001` or `student@vignex.dev`)
- **Initial Password:** `password123`
- **Role:** `student`
- **First-Login Policy:** `must_change_password` enforced (`/change-password`)
- **Enrolled Profile:** Year 3, CSE, Student ID `STU-2026-0891`
- **Dedicated Workspace:**
  - **Student Dashboard:** Recent complaints, active status trackers, notifications.
  - **Academic Intelligence (`/student/academics`):** Real-time attendance percentage, attendance trend trajectory, assessment scores, upcoming assignments & deadlines, weekly academic calendar, workload window calculations, timetable conflict alerts, explainable AI guidance cards with *[ Why this insight? ]* modals.
  - **Issue Reporting (`/student/report`):** 2-tier Category/Subcategory taxonomy selector, multi-evidence file uploader, **Protected Identity** toggle with contextual policy tooltips.
  - **My Complaints & Detail (`/student/complaints`):** Live case progress bar (`SUBMITTED` → `CLOSED`), internal timeline events, investigator notes marked visible to student.
  - **Ask VIGNAI (`/student/ask-vignai`):** Inquiries regarding own attendance, upcoming exams, own complaints, or open general knowledge.
  - **Student Profile (`/student/profile`):** Verified enrollment credentials and privacy protection guarantee.

### 2. Faculty Persona
- **Faculty ID:** `FAC-CSE-001` (also accepts `FAC001` or `faculty@vignex.dev`)
- **Initial Password:** `password123`
- **Role:** `faculty`
- **First-Login Policy:** `must_change_password` enforced (`/change-password`)
- **Department:** Computer Science & Engineering (CSE)
- **Dedicated Workspace:**
  - **Faculty Dashboard (`/faculty`):** Department issue overview, active assignments, pending reviews.
  - **Class Academic Intelligence (`/faculty/academic-intelligence`):** Subject/class selector dropdown, attendance trends vs threshold, assignment submission velocity vs class baseline, assessment score distributions, weekly timetable timeline, corroboration with department facility complaints (`ACADEMIC`, `INFRASTRUCTURE`, `TECHNOLOGY`), explainable class diagnostics.
  - **Department Queue & Cases (`/faculty/cases` & `/faculty/department-issues`):** Department complaint queue, investigation notes (`INTERNAL`, `ACTION`, `INVESTIGATION`, `ESCALATION`), status progression, non-destructive grouped cluster views.
  - **Feedback & Concerns (`/faculty/feedback`):** Summarized student academic concern themes, student feedback list, formal faculty response workflow (`FACULTY_RESPONSE` note type).
  - **Ask VIGNAI (`/faculty/ask-vignai`):** Class attendance trends, assignment backlogs, upcoming assessments, department issue summaries.

### 3. Management Persona
- **Management ID:** `MGMT-ADMIN-01` (also accepts `MGMT001` or `management@vignex.dev`)
- **Initial Password:** `password123`
- **Role:** `management`
- **First-Login Policy:** `must_change_password` enforced (`/change-password`)
- **Dedicated Workspace:**
  - **AI Intelligence Center (`/management`):** Top-level KPIs (Resolved Rate, Active Clusters, Risk Index, Resolution Velocity), Emerging Patterns cards, AI Priority Ranking Table, Campus Domain Health Matrix (Academics, Infrastructure, Tech, Operations), 7d/30d/90d Trend Analytics, Live AI Processing Activity Stream.
  - **Institutional Academic Intelligence (`/management/academic-intelligence`):** Campus-wide Academic Health Index (`HEALTHY`, `WATCH`, `ELEVATED`, `HIGH RISK`), department-level comparative matrices (attendance, assignments, assessments), cross-department pattern detection.
  - **Campus Issues Console (`/management/campus-issues`):** Clustered issue groups, full administrative oversight, priority filters, investigation logs.
  - **Intelligence Knowledge Graph (`/management`):** Interactive entity graph linking database `Case`, `Category`, `Location`, `Department`, and `Pattern` nodes.
  - **What-If Decision Lab (`/management/simulations`):** Deterministic scenario simulations (transit fleet expansion, Wi-Fi bandwidth upgrades, preventive maintenance, resource reallocation) with AI trade-off analysis.
  - **Ask VIGNAI (`/management/ask-vignai`):** Campus bottlenecks, risk root causes, cross-department comparisons, What-If simulation modeling.

---

## 3. COMPLETE API ARCHITECTURE

Built on **FastAPI (Python 3.11)** with strict Pydantic v2 schemas and modular routing. All endpoints are mounted under the `/api` prefix:

### 1. Core & Authentication (`/api/auth`, `/api/health`)
- `POST /api/auth/login`: Authenticates credentials, returns JWT bearer token + user role payload.
- `GET /api/auth/me`: Validates JWT token and returns current user profile and role.
- `GET /api/health`: System health check, SQLite database connectivity, AI subsystem status (`ONLINE`, `DEGRADED`, `UNAVAILABLE`), active version (`0.1.0`).

### 2. Grievance & Issue Management (`/api/complaints`)
- `GET /api/complaints`: Returns complaints scoped to authenticated role (Student: own cases; Faculty: department cases; Management: all campus cases).
- `POST /api/complaints`: Creates a new complaint, triggers AI analysis & deterministic routing, persists evidence.
- `GET /api/complaints/{case_id}`: Returns full single-case detail including evidence list, AI routing audit, and visible investigation notes.
- `PATCH /api/complaints/{case_id}/status`: Updates case status (`SUBMITTED`, `UNDER_REVIEW`, `IN_PROGRESS`, `RESOLVED`, `CLOSED`), appends timeline audit log, dispatches student notification.
- `POST /api/complaints/{case_id}/notes`: Adds an investigation note (`INTERNAL`, `ACTION`, `INVESTIGATION`, `ESCALATION`, `STUDENT_QUERY`, `FACULTY_RESPONSE`).
- `POST /api/complaints/{case_id}/evidence`: Uploads evidence attachment files (photos, videos, documents up to 25MB).
- `GET /api/complaints/{case_id}/evidence/{evidence_id}/download`: Authenticated file download endpoint with secure path resolution.
- `GET /api/complaints/taxonomy`: Returns the official 7-category two-tier taxonomy with valid subcategories.

### 3. Faculty Workflows (`/api/faculty`)
- `GET /api/faculty/cases`: Returns department cases assigned to or under the purview of faculty.
- `GET /api/faculty/department-groups`: Returns clustered case groups for the faculty department.
- `GET /api/faculty/feedback/overview`: Summarizes student concern themes and department feedback KPIs.
- `GET /api/faculty/feedback/concerns`: Lists student feedback complaints with privacy safeguards applied.
- `POST /api/faculty/cases/{id}/response`: Submits an official faculty response note (`FACULTY_RESPONSE`) visible to students and management.

### 4. Management Intelligence & Analytics (`/api/management`)
- `GET /api/management/stats`: Executive summary KPIs and campus risk metrics.
- `GET /api/management/patterns`: Active emergent issue clusters and velocity directions.
- `GET /api/management/priority-ranking`: Deterministically sorted complaint priority queue with transparent score breakdowns.
- `GET /api/management/domain-health`: Campus health scores across Academics, Infrastructure, Technology, and Operations.
- `GET /api/management/trends`: Historical trend data over 7d, 30d, 90d, or all-time windows.
- `GET /api/management/activity`: Real-time audit log of AI analyses, routing decisions, and status updates.
- `GET /api/management/case-groups`: Clustered complaint groups with explainability signals and group metrics.
- `GET /api/management/graph`: Verified SQLite database entity graph (cases, locations, categories, departments, patterns).
- `POST /api/management/simulate-scenario`: Deterministic scenario simulation engine with AI trade-off evaluation.
- `GET /api/management/why-modal`: Structured explainability payload detailing data basis, signals, and limitations for any metric.

### 5. Academic Intelligence (`/api/academics`)
- **Student Endpoints:**
  - `GET /api/academics/student/overview`: High-level student academic KPIs (GPA, attendance %, assignment completion rate, active subjects).
  - `GET /api/academics/student/subjects`: List of enrolled subjects with subject codes, credits, and faculty details.
  - `GET /api/academics/student/attendance`: 30-day attendance history logs, present/absent counts, and trajectory trends.
  - `GET /api/academics/student/assessments`: Midterm, lab, and quiz assessment scores, class averages, and weightages.
  - `GET /api/academics/student/assignments`: Assignment tracker with submission statuses (`SUBMITTED`, `PENDING`, `OVERDUE`) and deadlines.
  - `GET /api/academics/student/timetable`: Weekly schedule with room locations and conflict/overlap detection.
  - `GET /api/academics/student/insights`: Explainable AI student diagnostic cards with data provenance and non-punitive guidance.
- **Faculty Endpoints:**
  - `GET /api/academics/faculty/subjects`: List of classes/subjects assigned to the authenticated faculty member.
  - `GET /api/academics/faculty/subjects/{id}/overview`: Class-level KPIs (enrollment, average attendance, submission rate, class GPA).
  - `GET /api/academics/faculty/subjects/{id}/attendance-trends`: Class attendance history and low-attendance alerts (<75%).
  - `GET /api/academics/faculty/subjects/{id}/assignments`: Class assignment submission velocity vs historical baseline.
  - `GET /api/academics/faculty/subjects/{id}/assessments`: Class assessment distribution and score quartiles.
  - `GET /api/academics/faculty/subjects/{id}/timeline`: Weekly teaching timetable and room allocations.
  - `GET /api/academics/faculty/subjects/{id}/corroboration`: Cross-domain correlation with authorized department complaint records.
  - `GET /api/academics/faculty/subjects/{id}/insights`: Non-punitive class diagnostics and pedagogical recommendations.
- **Management Endpoints:**
  - `GET /api/academics/management/overview`: Institutional academic KPIs and aggregate attendance/assignment benchmarks.
  - `GET /api/academics/management/departments`: Comparative department-by-department academic health matrix.
  - `GET /api/academics/management/trends`: Multi-week institutional attendance and submission velocity trends.
  - `GET /api/academics/management/patterns`: Emerging academic signals (e.g. pre-exam stress concentration, lab outage impacts).
  - `GET /api/academics/management/insights`: Strategic institutional academic intelligence and capacity recommendations.

### 6. Ask VIGNAI Universal Assistant (`/api/intelligence/ask-vignai`, `/api/intelligence/ask`)
- `POST /api/intelligence/ask-vignai`: Universal natural language query router and answer synthesis engine supporting all authenticated roles.
- `POST /api/intelligence/ask`: Legacy route alias ensuring 100% backward compatibility with prior console clients.

---

## 4. DATABASE ARCHITECTURE & DATA MODELS

The system utilizes **SQLite** (`backend/vignex.db`) with deterministic path resolution via `get_database_url()`. Database migrations execute automatically during startup via `run_db_migrations()`.

### Core Data Models
1. **User & Identity:**
   - `User`: `id`, `email`, `password_hash`, `role` (`student` | `faculty` | `management`), `is_active`, `created_at`.
   - `StudentProfile`: `id`, `user_id`, `enrollment_number`, `year_of_study`, `department`, `created_at`.
2. **Grievances & Operations:**
   - `Complaint`: `id`, `case_id` (e.g., `VX-839336`), `student_id`, `title`, `description`, `location`, `category`, `subcategory`, `priority` (`LOW` | `MEDIUM` | `HIGH` | `CRITICAL`), `status` (`SUBMITTED` | `UNDER_REVIEW` | `IN_PROGRESS` | `RESOLVED` | `CLOSED`), `identity_protected` (boolean), `assigned_dept`, `assigned_to`, `created_at`, `updated_at`.
   - `Evidence`: `id`, `complaint_id`, `file_name`, `file_path`, `file_type`, `file_size`, `created_at`.
   - `ComplaintAIAnalysis`: `id`, `complaint_id`, `category`, `subcategory`, `issue_summary`, `location`, `suggested_priority`, `priority_reason`, `confidence`, `processing_status`, `provider`, `model`, `department`, `suggested_route_type`, `sensitivity`, `routing_reason`, `created_at`.
   - `ComplaintRouting`: `id`, `complaint_id`, `ai_suggested_route`, `policy_validation_result`, `final_route`, `decision_by`, `decision_reason`, `created_at`.
   - `InvestigationNote`: `id`, `complaint_id`, `author_user_id`, `author_role`, `author_email`, `note_type` (`INTERNAL` | `ACTION` | `INVESTIGATION` | `ESCALATION` | `STUDENT_QUERY` | `FACULTY_RESPONSE`), `content`, `is_visible_to_student`, `created_at`.
   - `Notification`: `id`, `user_id`, `complaint_id`, `title`, `message`, `is_read`, `created_at`.
3. **Academic Database (Phase 6):**
   - `AcademicSubject`: `id`, `code` (e.g. `CS301`), `name`, `department`, `semester`, `credits`, `faculty_user_id`, `created_at`.
   - `StudentSubjectEnrollment`: `id`, `student_id`, `subject_id`, `semester`, `academic_year`, `enrollment_date`.
   - `AttendanceRecord`: `id`, `student_id`, `subject_id`, `date`, `status` (`PRESENT` | `ABSENT` | `LATE` | `EXCUSED`), `session_type`, `remarks`.
   - `Assessment`: `id`, `subject_id`, `title`, `assessment_type` (`MIDTERM` | `QUIZ` | `LAB` | `FINAL` | `ASSIGNMENT`), `max_marks`, `weightage_percent`, `date`.
   - `AssessmentResult`: `id`, `assessment_id`, `student_id`, `marks_obtained`, `grade`, `feedback`, `created_at`.
   - `Assignment`: `id`, `subject_id`, `student_id`, `title`, `description`, `due_date`, `status` (`SUBMITTED` | `PENDING` | `OVERDUE`), `submitted_at`, `max_score`, `score_awarded`.
   - `TimetableEntry`: `id`, `subject_id`, `day_of_week` (`MONDAY`..`SATURDAY`), `start_time`, `end_time`, `room_number`, `building`, `session_type`.

### Single Source of Truth (SSOT) Guarantee
There is **ONE canonical record** for each case (e.g., `VX-839336`). Student submission, faculty notes, management status updates, and timeline events update the same database row. **No duplicate or shadow records are ever created.**

---

## 5. RESPONSIBLE AI & DETERMINISTIC POLICY ENGINE

VIGNAI OS adheres strictly to Responsible-AI engineering principles:

```
                  ┌────────────────────────────────────────┐
                  │    Natural Language Issue Report       │
                  └───────────────────┬────────────────────┘
                                      │
                                      ▼
                  ┌────────────────────────────────────────┐
                  │   AI Abstraction Layer (Provider)      │
                  │  • Primary: Gemini 2.5 Flash           │
                  │  • Fallback: LocalHeuristicProvider    │
                  └───────────────────┬────────────────────┘
                                      │ (Suggestions & Extraction)
                                      ▼
                  ┌────────────────────────────────────────┐
                  │ Deterministic Routing Policy Engine    │
                  │  • 8 Fixed Procedural Rules            │
                  │  • Non-Destructive Fallthrough Checks  │
                  │  • Enforced Authorization Boundaries   │
                  └───────────────────┬────────────────────┘
                                      │
                                      ▼
                  ┌────────────────────────────────────────┐
                  │ Final Enforced Route & Access Control  │
                  └────────────────────────────────────────┘
```

### 1. Dual AI Provider Architecture
- **Primary Provider:** `Google Gemini (gemini-3.6-flash)` with JSON schema structured output. System prompt instructs: *"You are VIGNAI, the AI assistant of VIGNAI OS (Policy Version 1.0)..."*.
- **Fallback Provider:** `LocalHeuristicProvider` providing 100% deterministic, offline keyword/regex extraction matching the official category taxonomy and sensitivity rules when external API keys are unavailable.

### 2. Deterministic Routing Policy Rules (`backend/app/services/routing/routing_policy.py`)
1. **Rule 1 (Sensitive Grievance & Conduct Allegations):** Category `SENSITIVE_GRIEVANCE` or `HIGH_SENSITIVITY` → Routes strictly to `Student Affairs (Authorized Grievance Authority)` + `Management Oversight`. **Department faculty are strictly denied access (`RESTRICTED_OVERRIDE`).**
2. **Rule 2 (Transport Authority):** Subcategory `Transport` → `Campus Transport Authority`.
3. **Rule 3 (Hostel Administration):** Subcategory `Hostel` → `Hostel Administration (Warden)`.
4. **Rule 4 (Examinations Authority):** Subcategory `Examination` / `Timetable` → `Examination Cell`.
5. **Rule 5 (Technology / IT Operations):** Category `TECHNOLOGY` → `Campus Operations (IT)`.
6. **Rule 6 (Campus Operations & Cleanliness):** Category `CAMPUS_OPERATIONS` → `Campus Maintenance / Security` (never falls through to department faculty).
7. **Rule 7 (Student Services):** Category `STUDENT_SERVICES` → `Student Affairs`.
8. **Rule 8 (Department Academic / Lab Infrastructure):** Category `INFRASTRUCTURE` / `ACADEMIC` → `{Matched Dept} Faculty` + `Management`.

### 3. Category Taxonomy & Normalization
Centralized in `backend/app/config/categories.py`:
- 7 Official Categories: `ACADEMIC`, `INFRASTRUCTURE`, `TECHNOLOGY`, `CAMPUS_OPERATIONS`, `STUDENT_SERVICES`, `SENSITIVE_GRIEVANCE`, `OTHER`.
- `normalize_category_name()` normalizes colloquial terms (e.g., `wifi` → `TECHNOLOGY`, `bus` → `CAMPUS_OPERATIONS`, `lab` → `INFRASTRUCTURE`).
- **Critical Policy:** Faculty conduct allegations never default to `OTHER` or `ACADEMIC`; they must classify as `SENSITIVE_GRIEVANCE` with `HIGH_SENSITIVITY`.

### 4. Privacy & Identity Protection Model
- When `identity_protected=True` is enabled, faculty and management views redact student personal identifying information (`reporter_visibility="IDENTITY_PROTECTED"`).
- Subject-of-complaint restriction ensures a faculty or staff member accused in a report is denied case access.
- Inquiries attempting to deanonymize students trigger an immediate `PRIVACY_REFUSAL` short-circuit.

### 5. Non-Destructive Related Complaint Grouping
- Clusters related complaints (e.g. 5 Block A Wi-Fi reports) into unified `RelatedCaseGroup` views with explicit explainability signals (*"Why Grouped?"*).
- Preserves individual underlying `Complaint` records with zero data loss or record merging.

### 6. Deterministic Priority Sorting
- Hierarchy: `CRITICAL` (4) > `HIGH` (3) > `MEDIUM` (2) > `LOW` (1).
- Tie-breaking: Priority level → Active status (`SUBMITTED`/`UNDER_REVIEW`/`IN_PROGRESS` prioritized over `RESOLVED`/`CLOSED`) → Evidence attachment presence → Recency timestamp.

---

## 6. ASK VIGNAI UNIVERSAL ASSISTANT SPECIFICATION

Implemented in `backend/app/services/ask_vignex/`, Ask VIGNAI is universally available to all roles with strict data isolation:

### Dual Query Modes & Intent Routing
1. `GENERAL_KNOWLEDGE`: Educational, STEM, programming, and conceptual inquiries (*"What is photosynthesis?"*, *"Explain recursion in C"*, *"How does TCP work?"*). Synthesizes pedagogical answers with zero database queries or campus data exposure.
2. `VIGNEX_DATA` / `CAMPUS_DATA`: Authorized campus data inquiries. Deterministically queries SQLite records and grounds responses strictly in verified data:
   - **Student:** Own attendance, own assignments, own exams, own complaints (`STUDENT_OWN_COMPLAINTS`).
   - **Faculty:** Class attendance trends, assignment backlogs, upcoming assessments, department issue summaries.
   - **Management:** Campus bottlenecks, risk root causes, cross-department trends, What-If simulation modeling.
   - **Hybrid (`HYBRID`):** Non-causal observational correlation linking infrastructure defects to academic submission patterns.

### Intent Safety Guardrails
- `PRIVACY_REFUSAL`: Rejects inquiries attempting to deanonymize student reporters (*"Who submitted the complaint?"*).
- `ALLEGATION_NEUTRALITY`: Rejects requests to adjudicate guilt or confirm allegation truth (*"Is the faculty member guilty?"*).
- **UI Mode Badges:** Visual indicators (`📖 GENERAL KNOWLEDGE`, `🎓 ACADEMIC`, `🏛️ VIGNAN CAMPUS DATA`, `⚡ HYBRID`, `🛠️ SIMULATION`).

---

## 7. WHAT-IF DECISION SIMULATION LAB

Implemented in `backend/app/services/simulation/` and `/management/simulations`:
- **Deterministic Math Models:**
  - Route additions & bus frequency changes (calculates wait time reduction, overcrowding relief, capital costs).
  - Wi-Fi access point deployment (calculates bandwidth throughput, concurrency capacity, latency improvement).
  - Preventive maintenance cycle optimization.
  - Department resource reallocation.
- **AI Trade-Off Evaluation:** Gemini synthesizes operational trade-offs, fiscal constraints, and implementation feasibility grounded strictly in deterministic formula outputs.
- **Policy Disclosure:** All outputs are clearly labeled as *Estimated / Modeled Simulation*.

---

## 8. FRONTEND DESIGN & THEME SYSTEM

- **Tech Stack:** React 18, Vite, TypeScript, Tailwind CSS, Lucide React.
- **Theme Modes:** `LIGHT`, `DARK`, `SYSTEM`.
- **True OLED Dark Mode:** Pitch-black background (`#000000`), deep dark cards (`#050505`), elevated panels (`#0A0A0A`), subtle high-contrast borders (`#101010` / `border-white/10`).
- **Theme Persistence:** Stored in `localStorage` (`vignex_theme`) with real-time OS system preference synchronization.
- **Global Command Palette (`Ctrl+K`):** Deep-link function finder with automatic section navigation and temporary spotlight highlighting (`triggerSpotlight()`).

---

## 9. EXPO DEMO POLICY & DATA RESET

- **Explicit Architecture Rule:** There is **NO separate "Expo Demo Mode"** and no synthetic bypass page.
- `ExpoDemoPage.tsx` was permanently removed.
- Demonstrations are performed live through authentic role logins:
  1. Student logs in (`student@vignex.dev` / `221FA04001`), submits a complaint with evidence and protected identity.
  2. Faculty logs in (`faculty@vignex.dev` / `FAC-CSE-001`), reviews department queue, inspects class academics, adds an investigation note.
  3. Management logs in (`management@vignex.dev` / `MGMT-ADMIN-01`), reviews AI Intelligence Center, explores Knowledge Graph, runs What-If simulation, queries Ask VIGNAI.
  4. Student receives instant notifications and inspects real-time timeline progress.

### Development Demo Reset Command
To restore predictable, internally consistent demo data between live demo rehearsals:
```bash
cd backend
python scripts/reset_demo_data.py
```
*Note: This command is development-only and guarded against execution in production.*

---

## 10. CAREER INTELLIGENCE (STUDENT ECOSYSTEM)

VIGNAI OS includes a native **Career Intelligence** module for the Student ecosystem:
1. **Resume Diagnostic & Extraction Pipeline:** Upload PDF/DOCX resumes with size validation ($\le 25\text{MB}$) and path traversal protection. Extracts structured technical skills, projects, education, certifications, and experience labeled as `VERIFIED FROM RESUME` and `STUDENT-PROVIDED`.
2. **Deterministic Opportunity Matching:**
   $$\text{Score} = (0.75 \times \text{RequiredMatchPct}) + (0.15 \times \text{PreferredMatchPct}) + (0.10 \times \text{FitPct})$$
   Calculates reproducible profile alignment percentages without LLM score drift.
3. **Personalized Career Fit & Academic-Aware Recommendations (Career Intelligence 2):**
   - **Centralized Career Taxonomy:** 11 standardized career domains (`SOFTWARE_ENGINEERING`, `AI_ML`, `DATA_SCIENCE`, `DATA_ANALYTICS`, `CYBERSECURITY`, `CLOUD_DEVOPS`, `FRONTEND`, `BACKEND`, `EMBEDDED_SYSTEMS`, `ELECTRONICS`, `RESEARCH`) with mapped academic subject codes (e.g. `CS202` DBMS $\rightarrow$ Data Science/Analytics/Backend, `CS204` CN $\rightarrow$ Cybersecurity/DevOps).
   - **Deterministic Career Strength Scoring:** Multi-factor weighting:
     $$\text{DomainStrength} = (0.35 \times \text{AcademicPerformance}) + (0.30 \times \text{VerifiedSkills}) + (0.20 \times \text{ProjectsAndCerts}) + (0.15 \times \text{DeclaredInterests})$$
   - **Deterministic Eligibility Engine:** Validates student branch, year of study, and criteria $\rightarrow$ `ELIGIBLE`, `INELIGIBLE`, or `UNKNOWN`. Ineligible opportunities receive a $0.5\times$ penalty to prevent topping student priority lists.
   - **Personalized Profile Fit Ranking:**
     $$\text{ProfileFit} = (0.45 \times \text{MatchScore}) + (0.25 \times \text{DomainAlignment}) + (0.15 \times \text{AcademicScore}) + (0.15 \times \text{InterestFit})$$
   - **Structured Recommendation Evidence (`[ Why VIGNAI Recommends This ]`):** Discloses primary career domain, academic course highlights, verified skills, project signals, eligibility statement, strengths vs gaps, and constructive learning suggestions.
   - **Responsible AI Disclaimer:** Strictly communicates *"current observed profile alignment"* and expressly disclaims permanent career assignment or guaranteed employment outcomes.
4. **Transparent Explainability (*"Why this match?"*):** Discloses the exact score breakdown, matched required skills, missing preferred competencies, work mode fit, and responsible AI disclaimer.
5. **Skill Gap Diagnostics & Advisory Guidance:** Aggregates market demand gaps (e.g. Docker, AWS) with constructive, non-punitive recommendations.
6. **Daily Career Brief:** Displays daily matching opportunity counts, strongest career direction badge (e.g. *Data Science 92% Alignment*), identified gaps, and approaching deadlines.
7. **Ask VIGNAI Career Domain:** Supports `CAREER_STRENGTHS`, `CAREER_DOMAIN_EXPLAIN`, `CAREER_PRIORITIZATION`, `CAREER_MATCHED_OPPORTUNITIES`, `CAREER_SKILL_GAPS`, `CAREER_CLOSING_SOON`, `CAREER_SKILL_SEARCH`, `CAREER_ACADEMIC_HYBRID`, and `CAMPUS_PLACEMENT_INFO` with strict `GENERAL_KNOWLEDGE` separation (*"What is Docker?"* vs *"Which internships require Docker?"*).
8. **Role Privacy Isolation:** Career profiles and uploaded resumes are private to the student owner. Faculty and Management are denied access (403).
9. **Opportunity Connector & Aggregation Architecture:**
   - `OpportunityConnector` abstraction standardizes fetching and deterministic normalization across `INSTITUTION_CURATED`, `AUTHORIZED_COORDINATOR`, `APPROVED_API`, and `PUBLIC_FEED`.
   - `MockVIITPlacementConnector` (development) and `LiveVIITPlacementConnector` (production interface ready for API keys).
   - Authorized Coordinator Intake: Placement coordinators paste circulars $\rightarrow$ parsed into `DRAFT` $\rightarrow$ human verified before appearing in student feeds.
   - Deterministic SHA-256 Deduplication: Identifies identical opportunities across recurring syncs.
   - Source Health Tracking: Records `HEALTHY`, `DEGRADED`, `OFFLINE` status without purging existing verified records during outages.
10. **VIIT Duvvada Contextualization Layer (Phase 8B):**
    - **Centralized Institutional Knowledge:** `backend/app/services/viit/context.py` encapsulates canonical VIIT institutional data (Vignan's Institute of Information Technology, Autonomous, Duvvada, Visakhapatnam, NAAC 'A+' Grade, NBA Accredited).
    - **Official Department Catalog:** 14 normalized departments (CSE, AI&DS, CSM, CSD, CSC, IT, ECE, EEE, ECM, MECH, CIVIL, BS&H, MCA, MBA) with alias resolution.
    - **Autonomous Exam Terminology:** Normalized CIE (Mid-1, Mid-2, assignments, 30%/40% weightage), SEE (Semester End Examination, 70%/60% weightage), Lab Internals, and Lab Externals.
    - **Academic Regulations:** VR20, VR22, VR23 support with fallback to `Regulation: UNKNOWN`.
    - **Attendance Policy Context:** $\ge 75\%$ Normal Attendance, $65\%-74.9\%$ Condonation Range, $<65\%$ Detention Warning with standard institutional disclaimer (*"Based on the configured VIIT attendance policy context. Official eligibility should be confirmed by the institution."*).
    - **Campus Infrastructure & Navigation:** APJ Abdul Kalam Block, Sir MV Block, Ramanujan Block, Aryabhata Block, Vignan Dhara Central Library, Dharitri Central Seminar Hall, Priyadarshini Girls Hostel, Boys Hostel Complex, Canteen, and Sports Grounds.
    - **Statutory & Grievance Context:** Anti-Ragging Committee, Internal Complaints Committee (ICC), Women Protection Cell (WPC), Central Grievance Redressal Committee (CGRC), SC/ST Cell, Dean Student Affairs.
    - **Transport & Placement Context:** 50+ bus fleet routes covering Maddilapalem, MVP Colony, Gajuwaka, Anakapalle, Steel Plant, Kurmannapalem; T&P Cell and CRT framework.
    - **Truthful Refusal & Provenance:** Refuses unverified live telemetry (live bus GPS, real-time book stock, faculty personal phone numbers) stating connector status `NOT CONFIGURED` under `VIIT CONTEXT` provenance.
    - **Connector Abstractions:** `IEcapConnector`, `ICoeConnector`, `ILmsConnector`, `ILibraryConnector`, `ITransportConnector` with mock connector `MockVIITContextConnector`.

11. **Cross-Domain Intelligence & Proactive Insight Engine (Phase 9):**
    - **Centralized Insight Engine:** `backend/app/services/intelligence/insight_engine.py` acts as an orchestrator correlating signals across Academics, Career Intelligence, Complaints, Proactive Alerts, and What-If Decision Lab.
    - **Deterministic Cross-Domain Rules:**
      - *Rule A (Academic $\rightarrow$ Career Alignment):* Coursework scores ($\ge 80\%$) + verified skills $\rightarrow$ `CAREER_ALIGNMENT`
      - *Rule B (Academic Risk):* Declining attendance ($\le 75\%$ or 14-session drop) $\rightarrow$ `ACADEMIC_RISK`
      - *Rule C (Career Skill Gap):* Missing skill required by target opportunities (e.g. Docker) $\rightarrow$ `PREVENTIVE_ACTION`
      - *Rule D (Campus Complaint Cluster):* $\ge 3$ incident reports with spatial concentration $\rightarrow$ `CAMPUS_PATTERN`
      - *Rule E (Complaint $\rightarrow$ What-If):* High/Critical cluster reaching operational threshold $\rightarrow$ Deep-links to What-If simulation (`/management/what-if?location=...`)
      - *Rule F (Career Opportunity & Multi-Domain):* High profile fit ($\ge 70\%$) + eligible + closing deadline ($\le 3$ days) $\rightarrow$ `CROSS_DOMAIN` ("High-fit [Domain] opportunity closing soon")
    - **Evidence-First Guarantee:** Every `VignaiInsight` contains structured signals, metrics, sources, and responsible AI analytical conclusions.
    - **Lifecycle & Deduplication:** Deterministic `deduplication_key` ensures zero spam across periodic syncs; status transitions `NEW` $\rightarrow$ `SEEN` $\rightarrow$ `ACTIONED` / `DISMISSED` / `EXPIRED`.
    - **Dashboard & Ask VIGNAI Integration:** Native interactive `VignaiInsightPanel` embedded on Student, Faculty, and Management dashboards; natural query routing for *"What should I focus on?"*, *"What insights do you have for me?"*, *"Why did VIGNAI recommend this?"*.

12. **VIGNAI Action Intelligence — "From Insights to Decisions" (Phase 10):**
    - **Centralized Action Engine:** `backend/app/services/intelligence/action_engine.py` orchestrates verified insights, academic signals, career fit, and incident clusters into an actionable, prioritized decision-support deck.
    - **Deterministic Priority Formula:**
      $$\text{PriorityScore} = (\text{Urgency} \times 0.35) + (\text{Impact} \times 0.30) + (\text{EvidenceStrength} \times 0.20) + (\text{Relevance} \times 0.15)$$
      Normalized into `CRITICAL` ($\ge 0.85$), `HIGH` ($\ge 0.65$), `MEDIUM` ($\ge 0.40$), and `LOW` ($< 0.40$).
    - **Action Centers & Daily Summaries:**
      - *Student Action Center ("YOUR PRIORITIES"):* Max 3–5 prioritized actions (Academic attendance recovery, closing high-fit opportunities, missing skill gaps, domain exploration) with [Why first?], [Ask VIGNAI], and direct route execution.
      - *Faculty Action Center ("TODAY'S DEPARTMENT PRIORITIES"):* Department incident cluster triage and non-punitive teaching improvement items (class attendance trajectories, unit assessment reviews).
      - *Management Action Center ("TODAY'S INSTITUTIONAL PRIORITIES"):* Campus-wide operational hotspots and direct `[Run What-If Analysis]` simulation triggers.
    - **Transparent Explainability (`[Why first?]`):** Displays Urgency, Impact, Evidence Strength, Relevance, signal timeline, and analytical conclusion.
    - **Ask VIGNAI Action Queries:** Routes *"What should I focus on?"*, *"What should I do first?"*, *"What needs my attention?"*, *"What are my priorities today?"*, *"Why is this my priority?"* through intent `ACTION_PRIORITIES`.
    - **Decision Support Principle:** VIGNAI recommends and prioritizes actions but never autonomously executes consequential institutional, grading, hiring, or disciplinary decisions.

13. **Final End-to-End Experience Audit (Phase 11):**
    - **Full-Journey Multi-Tenant Audit:** Verified complete real-world user journeys across Student, Faculty, and Management roles with 100% success rate across all 26 evaluation dimensions.
    - **Grounded AI Answers:** Verified Ask VIGNAI resolves immediately without stuck states or blank responses across General Knowledge, Academics, Career, Campus Intelligence, Complaints, Scenarios, Cross-Domain, and Action Priorities.
    - **Deterministic Mathematical Guarantees:** Priorities, attendance, and simulation projections are computed entirely through deterministic algorithms; LLM is restricted to phrasing and explanation synthesis.
    - **Total Verified Baseline:** 190 / 190 Backend Tests Passing • Frontend Production Build Passing (1678 modules, 0 errors).
    - **Verdict:** **EXPO READY**.

---

## 11. CURRENT TESTING & VERIFICATION STATUS

### 1. Automated Backend Test Suite
Executed via `pytest tests/ -v`:
- **Total Tests:** **190 / 190 PASSED (100% Success Rate)**
- `tests/test_architecture_hardening.py` (13 tests) — Taxonomy mappings, heuristic conduct classification, routing policy non-fallthrough, sensitive grievance isolation.
- `tests/test_auth_endpoints.py` (11 tests) — Database users, role logins, `/api/auth/me`, invalid password rejection, Roll Number/Faculty ID/Management ID logins, normalized whitespace/case handling, first-login password change flow, and server-side validation rules.
- `tests/test_intelligence_correction.py` (8 tests) — Dual query modes, Block A grouping, priority sorting, tie-breaking hierarchy.
- `tests/test_academic_6a.py` (19 tests) — Academic data models, attendance math, assessment tracking, timetable conflict detection, cross-role security.
- `tests/test_academic_6b_student.py` (9 tests) — Student Ask VIGNAI intents, domain isolation, workload calculation, non-punitive language.
- `tests/test_academic_6c_faculty.py` (11 tests) — Class-level authorization, 403 unauthorized class rejection, attendance/assignment math, class AI insights.
- `tests/test_academic_6d_management.py` (10 tests) — Management institutional endpoints, 403 student/faculty rejection, department breakdown metrics.
- `tests/test_academic_6e_cross_domain.py` (22 tests) — Cross-domain routing across 6 domains, general knowledge isolation, universal role queries, privacy refusal, allegation neutrality, scenario analysis.
- `tests/test_proactive_alerts.py` (10 tests) — Proactive priority alert discovery, deterministic threshold evaluation, duplicate alert suppression, student/faculty authorization isolation, protected identity leak prevention, lifecycle acknowledge/dismiss flows, and Ask VIGNAI priority alerts query routing.
- `tests/test_career_intelligence.py` (12 tests) — Student career profile retrieval, 403 privacy rejection for Faculty/Management, deterministic 75/15/10 match scoring, explainability breakdown, skill gap diagnostics, daily brief metrics, resume PDF/DOCX pipeline, Ask VIGNAI career matched opportunities, skill gaps, closing soon, general knowledge isolation, career+academic hybrid routing, and placement context refusal.
- `tests/test_career_aggregation.py` (7 tests) — Connector fetch & normalization, deterministic SHA-256 deduplication, coordinator intake text extraction, draft isolation from student recommendations, management verification workflow, opportunity rejection workflow, and connector failure degradation resilience.
- `tests/test_career_fit.py` (11 tests) — Academic subject to career domain taxonomy mapping, career strength deterministic multi-factor calculation, multi-domain profile support, deterministic eligibility filtering, personalized profile fit ranking formula, structured why-recommended evidence validation, privacy 403 isolation, Ask VIGNAI career strengths/explain/prioritization intents, and LLM-unavailable deterministic fallback.
- `tests/test_viit_context.py` (12 tests) — Department alias normalization, examination terminology mappings, VR20/VR22/VR23 regulation context, attendance policy thresholds and disclaimers, campus locations and building alias matching, statutory/grievance cells, transport routes and T&P context, Ask VIGNAI CIE/SEE intent, Ask VIGNAI campus locations intent, Ask VIGNAI department catalog intent, Ask VIGNAI truthful live data refusal, and VIIT REST API endpoints & connector statuses.
- `tests/test_insight_engine.py` (15 tests) — Academic career alignment rule, academic risk detection, career skill gap preventive action, verified opportunity closing soon, complaint pattern & What-If deep link action, duplicate insight suppression, student privacy isolation (403), faculty department isolation, lifecycle state transitions (NEW/SEEN/ACTIONED/DISMISSED), auto-expiration on resolved conditions, domain failure resilience, notification deduplication on high severity, Ask VIGNAI cross-domain insights intent, management campus scope aggregation, and multi-question phrasing variations.
- `tests/test_action_engine.py` (20 tests) — Student academic priority, student career priority, student skill gap priority, faculty department priority, management campus priority, cross-domain action correlation, deterministic priority formula, evidence presence & why-first payload, deduplication, auto-expiration past deadlines, student privacy isolation (403), faculty department isolation, management institutional scope, notification deduplication on high severity, Ask VIGNAI action priorities intent routing, What-If deep-link prepopulation, AI unavailable fallback, domain failure resilience, resolved insight expires action, and closing opportunity deadline expiration.

### 2. Frontend Production Build
Executed via `npm run build` in `frontend/`:
- **Build Status:** **1678 modules transformed, 0 TypeScript errors, 0 build warnings.**

---

## 12. KNOWN LIMITATIONS & ROADMAP

1. **General Knowledge Fallback:** Offline GK mode uses structured pedagogical response templates for core STEM/networking subjects; online Gemini mode handles arbitrary general knowledge queries.
2. **Semantic Duplicate Scanning:** In-memory keyword and Jaccard similarity scoring operates across active complaints; vector embeddings (pgvector/Chroma) planned for enterprise scaling.
3. **Database Migration to PostgreSQL:** Development currently runs on SQLite; production deployment will target PostgreSQL with identical SQLAlchemy schemas.

---

## 12. SUMMARY OF CORE PRINCIPLES

1. **AI is an Assistant, Not the Authority:** AI organizes, extracts, explains, and models; authorized humans make consequential operational decisions.
2. **Zero Truth Adjudication:** AI never declares allegations as absolute facts or determines guilt.
3. **Deterministic Authority:** Access control, routing, privacy concealment, and simulation math are strictly governed by deterministic Python backend rules.
4. **Student Privacy Protection:** Student identities under protected status remain strictly concealed across analytical and handler views.
5. **Single Source of Truth:** Every case exists as exactly one canonical record propagating live across all workspaces.
