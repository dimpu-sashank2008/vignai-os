from app.models.user import User
from app.models.department import Department
from app.models.student import StudentProfile
from app.models.faculty import FacultyProfile
from app.models.complaint import Complaint
from app.models.evidence import Evidence
from app.models.notification import Notification
from app.models.ai_analysis import ComplaintAIAnalysis
from app.models.routing import ComplaintRouting
from app.models.routing_audit import RoutingAudit
from app.models.investigation_note import InvestigationNote
from app.models.emerging_pattern import EmergingPattern
from app.models.simulation import SavedSimulation

# Phase 6 — Academic Intelligence Models
from app.models.academic_subject import AcademicSubject
from app.models.academic_enrollment import StudentSubjectEnrollment
from app.models.attendance_record import AttendanceRecord
from app.models.assessment import Assessment, AssessmentResult
from app.models.assignment import Assignment
from app.models.timetable_entry import TimetableEntry

# Proactive Alerts Model
from app.models.alert import VignaiAlert

# Phase 9 — Cross-Domain Intelligence Insights
from app.models.insight import VignaiInsight

# Phase 10 — Action Intelligence Models
from app.models.action import VignaiAction

# Career Intelligence Models
from app.models.career import (
    CareerProfile,
    CareerSkill,
    CareerProject,
    CareerCertification,
    CareerExperience,
    Opportunity,
    OpportunitySkill,
    OpportunityMatch,
    OpportunitySource,
)

__all__ = [
    "User",
    "Department",
    "StudentProfile",
    "FacultyProfile",
    "Complaint",
    "Evidence",
    "Notification",
    "ComplaintAIAnalysis",
    "ComplaintRouting",
    "RoutingAudit",
    "InvestigationNote",
    "EmergingPattern",
    "SavedSimulation",
    # Phase 6
    "AcademicSubject",
    "StudentSubjectEnrollment",
    "AttendanceRecord",
    "Assessment",
    "AssessmentResult",
    "Assignment",
    "TimetableEntry",
    # Proactive Alerts
    "VignaiAlert",
    # Career Intelligence
    "CareerProfile",
    "CareerSkill",
    "CareerProject",
    "CareerCertification",
    "CareerExperience",
    "Opportunity",
    "OpportunitySkill",
    "OpportunityMatch",
    "OpportunitySource",
]
