# Phase 9: Cross-Domain Intelligence & Proactive Insight Engine

## Overview & Architecture

VIGNAI OS Phase 9 elevates VIGNAI from a set of siloed intelligent modules into a unified **Cross-Domain Campus Intelligence System**. The centralized `InsightEngine` (`backend/app/services/intelligence/insight_engine.py`) continuously and deterministically correlates signals across:
- **Academics** (Coursework performance, attendance trajectories, continuous assessment)
- **Career Intelligence** (Verified resume competencies, project history, domain fit scores, closing opportunities, skill gaps)
- **Complaints & Spatial Clustering** (Incident density, recurring infrastructure failures, department priority alerts)
- **Institutional Decision Support** (What-If simulation deep links, campus health telemetry)
- **Ask VIGNAI & Navigation** (Natural language query synthesis, Command Palette shortcuts)

```
                       ┌──────────────────────────────────────────────┐
                       │           VIGNAI INSIGHT ENGINE              │
                       │ (Deterministic Cross-Domain Correlation)     │
                       └───────┬──────────────┬──────────────┬────────┘
                               │              │              │
        ┌──────────────────────▼──┐    ┌──────▼────────┐   ┌─▼────────────────────────┐
        │        ACADEMICS        │    │    CAREER     │   │       COMPLAINTS         │
        │ - Assessment Scores     │    │ - Skills      │   │ - Spatial Hotspots       │
        │ - Attendance Trajectory │    │ - Fit Scores  │   │ - Priority Clusters      │
        │ - VR22 Policies         │    │ - Deadlines   │   │ - Proactive Alerts       │
        └─────────────────────────┘    └───────────────┘   └──────────────────────────┘
                               │              │              │
                               └──────────────┼──────────────┘
                                              │
                                ┌─────────────▼────────────┐
                                │     VignaiInsight        │
                                │ Evidence-First Artifacts │
                                └─────────────┬────────────┘
                                              │
                 ┌────────────────────────────┼────────────────────────────┐
                 │                            │                            │
        ┌────────▼─────────┐        ┌─────────▼────────┐        ┌──────────▼─────────┐
        │ Student View     │        │ Faculty View     │        │ Management View    │
        │ Personal Fit &   │        │ Department Alert │        │ Campus Patterns,   │
        │ Academic Risks   │        │ Clusters         │        │ What-If Deep Links │
        └──────────────────┘        └──────────────────┘        └────────────────────┘
```

---

## Deterministic Cross-Domain Rules

| Rule Code | Domain Inputs | Output Insight Type | Deterministic Trigger | Recommended Action |
|---|---|---|---|---|
| **Rule A** | Academics + Career | `CAREER_ALIGNMENT` | Coursework scores (>=80%) + verified skills match domain taxonomy | View Domain Fit & Strengths (`/student/career#strengths`) |
| **Rule B** | Academics | `ACADEMIC_RISK` | Attendance <=75% or declining trajectory across 14-session window | Review Attendance Logs (`/student/academics#attendance`) |
| **Rule C** | Career + Opportunities | `PREVENTIVE_ACTION` | Target domain match has high-fit openings requiring missing skill (e.g. Docker) | View Skill Gap Diagnostics (`/student/career#skill-gaps`) |
| **Rule D** | Complaints + Telemetry | `CAMPUS_PATTERN` | >=3 incident reports with spatial concentration (Block A Wi-Fi) | Triage Incident Cluster (`/faculty/cases?alert=...`) |
| **Rule E** | Complaints + What-If | `COMPLAINT_PATTERN` | HIGH/CRITICAL complaint hotspot reaching operational threshold | Run What-If Simulation (`/management/what-if?location=...`) |
| **Rule F** | Career + Academics | `CROSS_DOMAIN` | High Profile Fit (>=70%) + Eligible + Closing Deadline (<=3 days) | Review Opportunity & Apply (`/student/career#opportunity-...`) |

---

## Evidence-First Structure

Every generated `VignaiInsight` enforces a strict schema requiring grounded telemetry before creation:
```json
{
  "insight_type": "CROSS_DOMAIN",
  "severity": "HIGH",
  "title": "High-Fit Opportunity Closing Soon: Junior Machine Learning Engineer",
  "summary": "A high-fit verified opportunity matching your strengths is closing in 2 day(s).",
  "source_domains": ["CAREER", "ACADEMICS"],
  "evidence": {
    "signals": [
      {
        "domain": "CAREER",
        "metric": "Junior Machine Learning Engineer Profile Fit",
        "value": "88% Personalized Fit",
        "source": "Personalized Recommendation Engine"
      },
      {
        "domain": "CAREER",
        "metric": "Eligibility Status",
        "value": "ELIGIBLE",
        "source": "Academic Eligibility Engine"
      },
      {
        "domain": "CAREER",
        "metric": "Application Deadline",
        "value": "2 day(s) remaining",
        "source": "Opportunity Intake System"
      }
    ],
    "conclusion": "Your verified skills and academic record yield an 88% fit for this closing listing."
  },
  "recommended_action": {
    "label": "Review Opportunity",
    "url": "/student/career#opportunity-4",
    "action_type": "VIEW_OPPORTUNITY",
    "description": "Inspect eligibility details and submit before deadline."
  }
}
```

---

## API Endpoints

- `GET /api/student/insights` — Returns evaluated personal academic and career insights.
- `GET /api/faculty/insights` — Returns department-scoped complaint and operational clusters.
- `GET /api/management/insights` — Returns campus-wide patterns with What-If triggers (no student PII).
- `POST /api/insights/{id}/seen` — Transitions state to `SEEN`.
- `POST /api/insights/{id}/actioned` — Transitions state to `ACTIONED`.
- `POST /api/insights/{id}/dismiss` — Transitions state to `DISMISSED`.

---

## Security, Privacy & Role Isolation

1. **Student Personal Isolation:** Students access only insights referencing their own `target_user_id`. Faculty and unauthenticated endpoints receive 403 Forbidden.
2. **Faculty Department Scope:** Faculty receives department-level alerts without protected reporter identities or individual student career profiles.
3. **Management Campus Aggregations:** Management reviews aggregated institutional patterns without student PII.
4. **Resilience & Fallback:** If any domain provider or model is offline, remaining domain rules continue generating valid grounded insights.
