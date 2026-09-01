# Phase 10: VIGNAI Action Intelligence
*"From Insights to Decisions"*

## 1. Overview & Architecture

VIGNAI OS Phase 10 implements **VIGNAI Action Intelligence**, transforming verified insights into an actionable, prioritized decision-support system for authenticated users.

```
                  ┌──────────────────────────────────────────────────────────┐
                  │                 VIGNAI ACTION ENGINE                     │
                  │             (Deterministic Prioritization)               │
                  └─────────┬──────────────┬───────────────┬─────────────────┘
                            │              │               │
     ┌──────────────────────▼──┐    ┌──────▼────────┐   ┌──▼─────────────────────────┐
     │      VignaiInsight      │    │  VignaiAlert  │   │   Academic/Career Signals  │
     │ - Academic Risks        │    │ - Hotspots    │   │ - Assessment Records       │
     │ - Closing Opportunities │    │ - Triage      │   │ - Attendance Trajectories  │
     │ - Skill Gaps            │    │ - Clusters    │   │ - Eligibility & Fit Scores │
     └─────────────────────────┘    └───────────────┘   └────────────────────────────┘
                            │              │               │
                            └──────────────┼───────────────┘
                                           │
                             ┌─────────────▼────────────┐
                             │       VignaiAction       │
                             │  Prioritized Action Deck │
                             └─────────────┬────────────┘
                                           │
              ┌────────────────────────────┼────────────────────────────┐
              │                            │                            │
     ┌────────▼─────────┐        ┌─────────▼────────┐        ┌──────────▼─────────┐
     │ Student Action   │        │ Faculty Action   │        │ Management Action  │
     │ Center:          │        │ Center:          │        │ Center:            │
     │ "YOUR PRIORITIES"│        │ Department &     │        │ Institutional      │
     │ Max 3-5 actions  │        │ Teaching Actions │        │ & What-If Actions  │
     └──────────────────┘        └──────────────────┘        └────────────────────┘
```

---

## 2. Action Model (`VignaiAction`)

Persisted in `backend/app/models/action.py`:
- `id`: Integer primary key
- `action_type`: `ACADEMIC_ATTENDANCE`, `ACADEMIC_ASSESSMENT`, `ACADEMIC_ASSIGNMENT`, `CAREER_OPPORTUNITY`, `CAREER_SKILL_GAP`, `CAREER_EXPLORATION`, `CAMPUS_CLUSTER`, `TEACHING_IMPROVEMENT`, `WHAT_IF_SIMULATION`, `CROSS_DOMAIN`
- `priority`: `CRITICAL`, `HIGH`, `MEDIUM`, `LOW`
- `priority_score`: Float between $0.0$ and $1.0$
- `title`: Short imperative action title (e.g. *Review CS204 Attendance*, *Apply to Junior ML Engineer*)
- `summary`: Contextual actionable explanation
- `role`: Role clearance (`student`, `faculty`, `management`, `admin`)
- `target_user_id`: Integer, ForeignKey("users.id")
- `target_department`: String (e.g. `CSE`)
- `source_insight_id`: ForeignKey("vignai_insights.id")
- `source_domain`: `ACADEMICS`, `CAREER`, `COMPLAINTS`, `CAMPUS_INTELLIGENCE`, `CROSS_DOMAIN`
- `evidence`: JSON with 4 priority dimensions (`urgency`, `impact`, `evidence_strength`, `relevance`), signals, and `why_first` reasoning
- `recommended_action`: JSON with label, url, action_type, description
- `target_route`: Route for deep-linking
- `ask_vignai_query`: Pre-crafted contextual question for Ask VIGNAI
- `status`: `NEW`, `SEEN`, `IN_PROGRESS`, `COMPLETED`, `DISMISSED`, `EXPIRED`
- `deduplication_key`: Unique index string

---

## 3. Deterministic Priority Calculation

$$	ext{PriorityScore} = (	ext{Urgency} 	imes 0.35) + (	ext{Impact} 	imes 0.30) + (	ext{EvidenceStrength} 	imes 0.20) + (	ext{Relevance} 	imes 0.15)$$

### Normalization Tiers:
- **`CRITICAL` ($\ge 0.85$):** Severe attendance drops ($<65\%$) or urgent multi-report incident hotspots requiring immediate intervention.
- **`HIGH` ($\ge 0.65$):** High-fit opportunities closing in $\le 2$ days, attendance $65\%-74.9\%$ declining, or departmental complaint clusters.
- **`MEDIUM` ($\ge 0.40$):** High-demand skill gaps (e.g. Docker, AWS), teaching attendance review, or unit performance checks.
- **`LOW` ($< 0.40$):** Long-term career domain exploration and general advisories.

---

## 4. Role Action Centers

### A. Student Action Center ("YOUR PRIORITIES")
- Renders top 3–5 prioritized actions:
  1. 🔴 **Review CS204 Attendance** (Declining/Detention warning) $ightarrow$ `[Review Attendance Logs]`
  2. 🟠 **Apply to Junior ML Engineer** (Verified high-fit closing in 2 days) $ightarrow$ `[Review Opportunity]`
  3. 🟡 **Improve Docker Skills** (Required by multiple high-fit openings) $ightarrow$ `[View Skill Gap Diagnostics]`
  4. 🔵 **Explore Software Engineering Fit** (Strong current alignment) $ightarrow$ `[Explore Career Strengths]`

### B. Faculty Action Center ("TODAY'S DEPARTMENT PRIORITIES")
- Department incident cluster triage (e.g. *Block B hardware glitches*).
- **Non-Punitive Teaching Improvement Actions:**
  - *Review Class Attendance Trajectory* (identifies aggregate engagement anomalies without faculty punishment).
  - *Review Unit Assessment Performance* (suggests topic reinforcement).
  - *Investigate Repeated Lab Infrastructure Issues*.

### C. Management Action Center ("TODAY'S INSTITUTIONAL PRIORITIES")
- Campus-wide priority clusters (e.g. *Block A Wi-Fi Instability*).
- **What-If Simulation Integration:** For urgent clusters, provides direct `[Run What-If Analysis]` deep-linking into `/management/what-if?location=...` with prepopulated parameters.

---

## 5. Decision Support & AI Boundary Principles

1. **Advisory Decision Support:** VIGNAI generates recommendations and calculates mathematical priority. VIGNAI never autonomously executes consequential institutional, grading, hiring, or disciplinary actions.
2. **Deterministic Integrity:** LLM APIs never calculate scores, deadlines, or priorities. The LLM is restricted to phrasing and explanation synthesis.
3. **Privacy Isolation:** Student actions are strictly private to the student owner. Faculty views departmental aggregates only without student PII. Management views institutional summaries.
4. **Lifecycle & Auto-Expiration:** Actions automatically transition to `EXPIRED` when underlying opportunities expire, deadlines pass, or attendance conditions resolve.
