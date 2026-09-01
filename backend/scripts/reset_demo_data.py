"""
Development-Only Demo Data Reset Script for VIGNAI OS (Phase 7).
Resets synthetic development records to a predictable, internally consistent state for AI Expo demos.

Usage:
    python scripts/reset_demo_data.py

Safety:
    Guarded against running in production environments.
"""

import os
import sys
from datetime import datetime, date, timedelta
from pathlib import Path

# Add backend to path
BACKEND_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BACKEND_DIR))

from app.config import settings
from app.database import engine, Base, SessionLocal, run_db_migrations
from app.models.user import User
from app.models.department import Department
from app.models.student import StudentProfile
from app.models.faculty import FacultyProfile
from app.models.complaint import Complaint
from app.models.notification import Notification
from app.models.ai_analysis import ComplaintAIAnalysis
from app.models.routing import ComplaintRouting
from app.models.routing_audit import RoutingAudit
from app.models.investigation_note import InvestigationNote
from app.models.academic_subject import AcademicSubject
from app.models.academic_enrollment import StudentSubjectEnrollment
from app.models.attendance_record import AttendanceRecord, ATTENDANCE_PRESENT, ATTENDANCE_ABSENT, ATTENDANCE_OD
from app.models.assessment import Assessment, AssessmentResult, ASSESSMENT_QUIZ, ASSESSMENT_MID_EXAM, ASSESSMENT_LAB_EXAM
from app.models.assignment import Assignment, ASSIGNMENT_PENDING, ASSIGNMENT_SUBMITTED, ASSIGNMENT_OVERDUE
from app.models.timetable_entry import TimetableEntry
from app.models.alert import VignaiAlert
from app.models.career import (
    CareerProfile,
    CareerSkill,
    CareerProject,
    CareerCertification,
    CareerExperience,
    Opportunity,
    OpportunitySkill,
    OpportunityMatch, OpportunitySource,
)
from app.services.career.matching_engine import matching_engine
from app.services.career.resume_parser import resume_parser

from app.services.auth_service import hash_password
from app.services.intelligence.alert_service import alert_service
from app.services.intelligence.pattern_detection import PatternDetectionService

def reset_demo_data():
    if getattr(settings, "ENVIRONMENT", "development").lower() == "production":
        raise RuntimeError("CRITICAL: Demo reset cannot be run in a production environment!")

    print("=" * 60)
    print("VIGNAI OS — RESETTING SYNTHETIC DEMO DATA")
    print("=" * 60)

    Base.metadata.create_all(bind=engine)
    run_db_migrations()
    db = SessionLocal()

    try:
        # Clear existing transient records
        print("[1/6] Clearing old transient records...")
        db.query(Notification).delete()
        db.query(VignaiAlert).delete()
        db.query(InvestigationNote).delete()
        db.query(RoutingAudit).delete()
        db.query(ComplaintRouting).delete()
        db.query(ComplaintAIAnalysis).delete()
        db.query(Complaint).delete()
        db.query(AttendanceRecord).delete()
        db.query(AssessmentResult).delete()
        db.query(Assessment).delete()
        db.query(Assignment).delete()
        db.query(TimetableEntry).delete()
        db.query(StudentSubjectEnrollment).delete()
        db.query(AcademicSubject).delete()
        db.query(OpportunityMatch).delete()
        db.query(OpportunitySkill).delete()
        db.query(Opportunity).delete()
        db.query(OpportunitySource).delete()
        db.query(CareerExperience).delete()
        db.query(CareerCertification).delete()
        db.query(CareerProject).delete()
        db.query(CareerSkill).delete()
        db.query(CareerProfile).delete()
        db.commit()

        # 1. Ensure Standard Departments
        print("[2/6] Seeding standard departments...")
        depts = [
            ("Computer Science & Engineering", "CSE"),
            ("Electronics & Communication", "ECE"),
            ("Electrical & Electronics", "EEE"),
            ("Information Technology", "IT"),
            ("Student Affairs & Grievances", "Student Affairs"),
        ]
        dept_map = {}
        for name, code in depts:
            d = db.query(Department).filter_by(code=code).first()
            if not d:
                d = Department(name=name, code=code)
                db.add(d)
                db.commit()
                db.refresh(d)
            dept_map[code] = d

        cs_dept = db.query(Department).filter((Department.code == "CSE") | (Department.code == "CS")).first()
        if not cs_dept:
            cs_dept = dept_map["CSE"]

        # 2. Seed Standard Accounts with Default Passwords
        print("[3/6] Seeding authenticated demo users...")
        # Management
        mgmt = db.query(User).filter_by(email="management@vignex.dev").first()
        if not mgmt:
            mgmt = User(
                email="management@vignex.dev",
                management_id="MGMT-ADMIN-01",
                password_hash=hash_password("password123"),
                role="management",
                is_active=True,
                must_change_password=True,
            )
            db.add(mgmt)
        else:
            mgmt.management_id = "MGMT-ADMIN-01"
            mgmt.password_hash = hash_password("password123")
            mgmt.must_change_password = True
            mgmt.is_active = True
            mgmt.role = "management"

        # Faculty
        faculty = db.query(User).filter_by(email="faculty@vignex.dev").first()
        if not faculty:
            faculty = User(
                email="faculty@vignex.dev",
                faculty_id="FAC-CSE-001",
                password_hash=hash_password("password123"),
                role="faculty",
                is_active=True,
                must_change_password=True,
            )
            faculty.faculty_profile = FacultyProfile(
                employee_id="FAC-CSE-001",
                department_id=cs_dept.id,
                designation="Assistant Professor"
            )
            db.add(faculty)
        else:
            faculty.faculty_id = "FAC-CSE-001"
            faculty.password_hash = hash_password("password123")
            faculty.must_change_password = True
            faculty.is_active = True
            faculty.role = "faculty"
            if faculty.faculty_profile:
                faculty.faculty_profile.department_id = cs_dept.id

        # Student
        student = db.query(User).filter_by(email="student@vignex.dev").first()
        if not student:
            student = User(
                email="student@vignex.dev",
                roll_number="221FA04001",
                password_hash=hash_password("password123"),
                role="student",
                is_active=True,
                must_change_password=True,
            )
            student.student_profile = StudentProfile(enrollment_number="221FA04001", year_of_study=2)
            db.add(student)
        else:
            student.roll_number = "221FA04001"
            student.password_hash = hash_password("password123")
            student.must_change_password = True
            student.is_active = True
            student.role = "student"
            if student.student_profile:
                student.student_profile.enrollment_number = "221FA04001"

        db.commit()
        db.refresh(mgmt)
        db.refresh(faculty)
        db.refresh(student)

        # 3. Seed Internally Consistent Demo Complaints
        print("[4/6] Seeding hero demo complaint clusters...")
        now = datetime.utcnow()

        demo_complaints = [
            # Story A: Block A Wi-Fi Disruption (Cluster of 4, High Priority, Increasing Trend)
            {
                "case_id": "VX-104821",
                "title": "Block A 2nd Floor Wi-Fi Disconnecting Constantly",
                "description": "The Wi-Fi access points on the 2nd floor of Block A disconnect every 5 minutes during lectures. Students are unable to access coding portals.",
                "location": "Block A",
                "category": "Wi-Fi / Network",
                "priority": "HIGH",
                "status": "IN_PROGRESS",
                "created_at": now - timedelta(days=2, hours=3),
                "dept": "Infrastructure",
                "sensitivity": "NORMAL",
            },
            {
                "case_id": "VX-104822",
                "title": "Cannot Connect to Campus Wi-Fi in Block A Reading Hall",
                "description": "Signal drops to zero in Block A reading hall. Authentication timeout error displays repeatedly on student laptops.",
                "location": "Block A",
                "category": "Wi-Fi / Network",
                "priority": "HIGH",
                "status": "UNDER_REVIEW",
                "created_at": now - timedelta(days=1, hours=8),
                "dept": "Infrastructure",
                "sensitivity": "NORMAL",
            },
            {
                "case_id": "VX-104823",
                "title": "Wi-Fi Speed Degraded in Block A Computer Lab",
                "description": "Network latency exceeds 400ms in Block A lab. Uploading lab assignments keeps timing out.",
                "location": "Block A",
                "category": "Wi-Fi / Network",
                "priority": "HIGH",
                "status": "SUBMITTED",
                "created_at": now - timedelta(hours=14),
                "dept": "Infrastructure",
                "sensitivity": "NORMAL",
            },
            {
                "case_id": "VX-104824",
                "title": "Frequent Network Packet Drops in Block A Corridor",
                "description": "Wi-Fi signal fluctuates wildly while walking through Block A main corridor.",
                "location": "Block A",
                "category": "Wi-Fi / Network",
                "priority": "HIGH",
                "status": "SUBMITTED",
                "created_at": now - timedelta(hours=4),
                "dept": "Infrastructure",
                "sensitivity": "NORMAL",
            },

            # Story B: Route 4 Transport Delays (Cluster of 3, High Priority, Recurring)
            {
                "case_id": "VX-209101",
                "title": "Route 4 Bus Overcrowded & Delayed at North Gate",
                "description": "Route 4 bus arrived 35 minutes late this morning at North Gate. Over 80 students were waiting and could not board.",
                "location": "North Gate",
                "category": "Transport",
                "priority": "HIGH",
                "status": "IN_PROGRESS",
                "created_at": now - timedelta(days=3),
                "dept": "Campus Operations",
                "sensitivity": "NORMAL",
            },
            {
                "case_id": "VX-209102",
                "title": "Route 4 Morning Commute Headway Skipped",
                "description": "The 08:15 AM Route 4 shuttle did not arrive at the hostel stop, causing students to miss 9 AM laboratory attendance.",
                "location": "Hostels",
                "category": "Transport",
                "priority": "HIGH",
                "status": "UNDER_REVIEW",
                "created_at": now - timedelta(days=1, hours=2),
                "dept": "Campus Operations",
                "sensitivity": "NORMAL",
            },
            {
                "case_id": "VX-209103",
                "title": "Bus Frequency Insufficient on Route 4",
                "description": "Need an extra bus on Route 4 between 07:30 and 09:00 AM. Boarding queues extend past the security gate.",
                "location": "North Gate",
                "category": "Transport",
                "priority": "HIGH",
                "status": "SUBMITTED",
                "created_at": now - timedelta(hours=9),
                "dept": "Campus Operations",
                "sensitivity": "NORMAL",
            },

            # Story C: Lab 3 Equipment & Projector Issue (Cluster of 2, CSE Department)
            {
                "case_id": "VX-305411",
                "title": "Lab 3 Ceiling Projector HDMI Port Damaged",
                "description": "Projector in CSE Lab 3 flickers intermittently and turns off after 10 minutes. Faculty cannot present slides.",
                "location": "Lab 3",
                "category": "Facilities",
                "priority": "HIGH",
                "status": "UNDER_REVIEW",
                "created_at": now - timedelta(days=2),
                "dept": "CSE",
                "sensitivity": "NORMAL",
            },
            {
                "case_id": "VX-305412",
                "title": "Lab 3 Overhead Projector Overheating",
                "description": "Projector fan makes grinding noise and thermal shutdown occurs during afternoon data structures lab.",
                "location": "Lab 3",
                "category": "Facilities",
                "priority": "HIGH",
                "status": "SUBMITTED",
                "created_at": now - timedelta(days=1),
                "dept": "CSE",
                "sensitivity": "NORMAL",
            },

            # Story D: Protected Identity Case (Privacy demonstration)
            {
                "case_id": "VX-990011",
                "title": "Confidential Staff Grievance in Department Office",
                "description": "Sensitive inquiry submitted under identity protection policy regarding evaluation transparency.",
                "location": "Department Office",
                "category": "Faculty & Staff Conduct",
                "priority": "HIGH",
                "status": "UNDER_REVIEW",
                "created_at": now - timedelta(days=4),
                "dept": "Student Affairs",
                "sensitivity": "HIGH_SENSITIVITY",
                "identity_protected": True,
            },
        ]

        for spec in demo_complaints:
            c = Complaint(
                case_id=spec["case_id"],
                student_id=student.id,
                title=spec["title"],
                description=spec["description"],
                location=spec["location"],
                category=spec["category"],
                priority=spec["priority"],
                status=spec["status"],
                identity_protected=spec.get("identity_protected", False),
                created_at=spec["created_at"],
            )
            db.add(c)
            db.commit()
            db.refresh(c)

            # AI Analysis & Routing records
            ai_rec = ComplaintAIAnalysis(
                complaint_id=c.id,
                category=c.category,
                issue_summary=c.description[:80],
                location=c.location,
                suggested_priority=c.priority,
                priority_reason=f"Standard policy heuristic for {c.category}",
                department=spec["dept"],
                suggested_route_type="MANAGEMENT_ONLY" if spec.get("identity_protected") else "DEPARTMENT_AND_MANAGEMENT",
                sensitivity=spec.get("sensitivity", "NORMAL"),
                routing_reason=f"Routed deterministically to {spec['dept']}",
                processing_status="COMPLETED",
                provider="LocalHeuristicProvider",
                model="deterministic-heuristic-v1",
            )
            db.add(ai_rec)

            routing_rec = ComplaintRouting(
                complaint_id=c.id,
                recipient_type="MANAGEMENT" if spec.get("identity_protected") else "DEPARTMENT",
                department_code=spec["dept"],
                role="management" if spec.get("identity_protected") else "faculty",
                assignment_status="ASSIGNED",
                is_primary=True,
            )
            db.add(routing_rec)

            audit_rec = RoutingAudit(
                complaint_id=c.id,
                ai_suggested_route=ai_rec.suggested_route_type,
                policy_validation_result="VALIDATED",
                final_route=ai_rec.suggested_route_type,
                decision_by="SYSTEM_POLICY_ENGINE",
                decision_reason="Standard taxonomy policy approved.",
            )
            db.add(audit_rec)
            db.commit()

        # 4. Seed Academic Data (Subjects, Attendance, Assessments, Assignments, Timetable)
        print("[5/6] Seeding academic intelligence records...")
        today = date.today()
        it_dept = dept_map.get("IT", cs_dept)

        subjects_spec = [
            {"code": "CS201", "name": "Data Structures", "dept_id": cs_dept.id, "faculty_id": faculty.id, "credits": 4},
            {"code": "CS202", "name": "Operating Systems", "dept_id": cs_dept.id, "faculty_id": faculty.id, "credits": 4},
            {"code": "CS203", "name": "Database Management", "dept_id": cs_dept.id, "faculty_id": faculty.id, "credits": 3},
            {"code": "CS204", "name": "Computer Networks", "dept_id": it_dept.id, "faculty_id": None, "credits": 3},
            {"code": "MA201", "name": "Engineering Mathematics", "dept_id": cs_dept.id, "faculty_id": None, "credits": 4},
        ]

        subject_map = {}
        for s_spec in subjects_spec:
            subj = AcademicSubject(
                code=s_spec["code"],
                name=s_spec["name"],
                department_id=s_spec["dept_id"],
                faculty_user_id=s_spec["faculty_id"],
                credits=s_spec["credits"],
                data_source="SYNTHETIC DEVELOPMENT DATA",
            )
            db.add(subj)
            db.commit()
            db.refresh(subj)
            subject_map[s_spec["code"]] = subj

            # Enrollment
            db.add(StudentSubjectEnrollment(
                student_id=student.student_profile.id,
                subject_id=subj.id,
                semester=3,
                section="A",
                academic_year="2024-25",
            ))

        db.commit()

        # Attendance (30 Days with CS204 decline pattern)
        for i in range(30, 0, -1):
            cur_date = today - timedelta(days=i)
            if cur_date.weekday() >= 5:
                continue

            for code, subj in subject_map.items():
                status = ATTENDANCE_PRESENT
                if code == "CS204":
                    if i <= 14:
                        status = ATTENDANCE_ABSENT if (i % 3 == 0) else (ATTENDANCE_OD if (i % 7 == 0) else ATTENDANCE_PRESENT)
                    else:
                        status = ATTENDANCE_PRESENT if (i % 8 != 0) else ATTENDANCE_ABSENT
                else:
                    if (i + subj.id) % 9 == 0:
                        status = ATTENDANCE_ABSENT
                    elif (i + subj.id) % 13 == 0:
                        status = ATTENDANCE_OD

                db.add(AttendanceRecord(
                    student_id=student.student_profile.id,
                    subject_id=subj.id,
                    date=cur_date,
                    status=status,
                ))

        # Assessments
        for code, subj in subject_map.items():
            q1 = Assessment(
                subject_id=subj.id,
                title=f"{subj.name} - Quiz 1",
                assessment_type=ASSESSMENT_QUIZ,
                scheduled_at=datetime.combine(today - timedelta(days=18), datetime.min.time()),
                max_marks=25.0,
                duration_minutes=30,
            )
            db.add(q1)
            db.commit()
            db.refresh(q1)
            db.add(AssessmentResult(
                assessment_id=q1.id,
                student_id=student.student_profile.id,
                marks=21.0 + (subj.id % 4),
                submitted_at=datetime.combine(today - timedelta(days=18), datetime.min.time()),
            ))

            mid = Assessment(
                subject_id=subj.id,
                title=f"{subj.name} - Mid-Term Exam",
                assessment_type=ASSESSMENT_MID_EXAM,
                scheduled_at=datetime.combine(today - timedelta(days=6), datetime.min.time()),
                max_marks=100.0,
                duration_minutes=90,
            )
            db.add(mid)
            db.commit()
            db.refresh(mid)
            db.add(AssessmentResult(
                assessment_id=mid.id,
                student_id=student.student_profile.id,
                marks=78.0 + (subj.id % 10),
                submitted_at=datetime.combine(today - timedelta(days=6), datetime.min.time()),
            ))

            if code in ["CS201", "CS202"]:
                db.add(Assessment(
                    subject_id=subj.id,
                    title=f"{subj.name} - Lab Practical Evaluation",
                    assessment_type=ASSESSMENT_LAB_EXAM,
                    scheduled_at=datetime.combine(today + timedelta(days=3), datetime.min.time()),
                    max_marks=50.0,
                    duration_minutes=120,
                ))

        # Assignments
        for code, subj in subject_map.items():
            db.add(Assignment(
                subject_id=subj.id,
                student_id=student.student_profile.id,
                title=f"{subj.name} - Problem Set 1",
                description="Core theoretical algorithms and implementation.",
                due_at=datetime.combine(today - timedelta(days=12), datetime.min.time()),
                status=ASSIGNMENT_SUBMITTED,
                submitted_at=datetime.combine(today - timedelta(days=13), datetime.min.time()),
            ))
            db.add(Assignment(
                subject_id=subj.id,
                student_id=student.student_profile.id,
                title=f"{subj.name} - Module 2 Assignment",
                description="Comprehensive problem set covering module 2.",
                due_at=datetime.combine(today + timedelta(days=2), datetime.min.time()),
                status=ASSIGNMENT_PENDING,
            ))

        cs204 = subject_map.get("CS204")
        if cs204:
            db.add(Assignment(
                subject_id=cs204.id,
                student_id=student.student_profile.id,
                title="Computer Networks - Wireshark Packet Capture",
                description="Capture TCP handshake logs.",
                due_at=datetime.combine(today - timedelta(days=1), datetime.min.time()),
                status=ASSIGNMENT_OVERDUE,
            ))

        # Timetable Entries
        timetable_spec = [
            ("CS201", "Monday", "09:00", "10:00", "Room 301"),
            ("CS202", "Monday", "10:15", "11:15", "Room 302"),
            ("MA201", "Monday", "11:30", "12:30", "Room 204"),
            ("CS201", "Monday", "14:00", "16:00", "Lab 3"),
            ("CS203", "Tuesday", "09:00", "10:00", "Room 301"),
            ("CS204", "Tuesday", "10:15", "11:15", "Room 305"),
            ("CS202", "Tuesday", "11:30", "12:30", "Room 302"),
            ("CS201", "Wednesday", "09:00", "10:00", "Room 301"),
            ("CS203", "Wednesday", "10:15", "11:15", "Room 301"),
            ("MA201", "Wednesday", "11:30", "12:30", "Room 204"),
            ("CS203", "Wednesday", "14:00", "16:00", "Lab 2"),
            ("CS204", "Thursday", "09:00", "10:00", "Room 305"),
            ("CS202", "Thursday", "10:15", "11:15", "Room 302"),
            ("CS203", "Thursday", "11:30", "12:30", "Room 301"),
            ("CS201", "Friday", "09:00", "10:00", "Room 301"),
            ("CS204", "Friday", "10:15", "11:15", "Room 305"),
            ("MA201", "Friday", "11:30", "12:30", "Room 204"),
            ("CS204", "Friday", "14:00", "16:00", "Lab 1"),
        ]
        for code, day, start, end, room in timetable_spec:
            subj = subject_map.get(code)
            if subj:
                db.add(TimetableEntry(
                    subject_id=subj.id,
                    day_of_week=day,
                    start_time=start,
                    end_time=end,
                    room=room,
                ))

        db.commit()

        # 4.5 Seed Synthetic Career Opportunities and Initial Student Profile
        print("[5.5/6] Seeding synthetic career intelligence data...")
        opps_data = [
            {
                "id": "OPP-2026-001",
                "title": "Software Engineering Intern",
                "org": "VIGNAI Development Partner",
                "type": "INTERNSHIP",
                "desc": "Join full-stack engineering team to build scalable REST APIs, reactive client dashboards, and database models.",
                "location": "Remote",
                "work_mode": "REMOTE",
                "deadline": now + timedelta(days=10),
                "eligibility": "B.Tech CSE/IT/AI&DS 2nd & 3rd Year (Minimum 65% attendance)",
                "skills": [("Python", True), ("React", True), ("SQL", True), ("Docker", False)],
            },
            {
                "id": "OPP-2026-002",
                "title": "AI/ML Research Assistant",
                "org": "VIGNAI Development Partner",
                "type": "RESEARCH",
                "desc": "Investigate natural language extraction models, deterministic triage heuristics, and embedding clusters.",
                "location": "Visakhapatnam",
                "work_mode": "HYBRID",
                "deadline": now + timedelta(days=25),
                "eligibility": "B.Tech CSE/AI&DS 3rd & 4th Year with foundational linear algebra & ML",
                "skills": [("Python", True), ("Machine Learning", True), ("Data Structures", True), ("AWS", False)],
            },
            {
                "id": "OPP-2026-003",
                "title": "Frontend Web Developer Intern",
                "org": "VIGNAI Development Partner",
                "type": "INTERNSHIP",
                "desc": "Craft high-performance, accessible, and responsive user interfaces using modern component design systems.",
                "location": "Remote",
                "work_mode": "REMOTE",
                "deadline": now + timedelta(days=5),
                "eligibility": "B.Tech All Branches 2nd & 3rd Year with frontend portfolio",
                "skills": [("React", True), ("JavaScript", True), ("Tailwind CSS", True), ("TypeScript", False)],
            },
            {
                "id": "OPP-2026-004",
                "title": "Cloud & DevOps Associate",
                "org": "VIGNAI Development Partner",
                "type": "JOB",
                "desc": "Automate containerized build pipelines, configure Linux staging environments, and monitor telemetry.",
                "location": "Hyderabad / Remote",
                "work_mode": "HYBRID",
                "deadline": now + timedelta(days=18),
                "eligibility": "B.Tech Final Year / Graduating Batch",
                "skills": [("Linux", True), ("Git", True), ("Docker", True), ("Kubernetes", False), ("AWS", False)],
            },
            {
                "id": "OPP-2026-005",
                "title": "National Campus Hackathon 2026",
                "org": "VIGNAI Development Partner",
                "type": "HACKATHON",
                "desc": "48-hour innovation hackathon building AI-driven campus operations and educational tooling.",
                "location": "VIIT Duvvada / Virtual",
                "work_mode": "HYBRID",
                "deadline": now + timedelta(days=8),
                "eligibility": "All VIIT Enrolled Students (Teams of 2-4)",
                "skills": [("Python", True), ("React", True), ("Git", True), ("FastAPI", False)],
            },
            {
                "id": "OPP-2026-006",
                "title": "Cloud Practitioner Certification Track",
                "org": "VIGNAI Development Partner",
                "type": "CERTIFICATION",
                "desc": "Structured 6-week curriculum covering cloud architecture, distributed systems, and security compliance.",
                "location": "Online",
                "work_mode": "REMOTE",
                "deadline": now + timedelta(days=30),
                "eligibility": "Open to all engineering students",
                "skills": [("HTML/CSS", True), ("Linux", False)],
            },
            {
                "id": "OPP-2026-007",
                "title": "Data Analytics & SQL Specialist",
                "org": "VIGNAI Development Partner",
                "type": "INTERNSHIP",
                "desc": "Extract business intelligence metrics, formulate complex SQL queries, and synthesize reporting dashboards.",
                "location": "Visakhapatnam",
                "work_mode": "ON_SITE",
                "deadline": now + timedelta(days=12),
                "eligibility": "B.Tech CSE/IT/ECE 2nd & 3rd Year",
                "skills": [("SQL", True), ("Python", True), ("Data Structures", False), ("MongoDB", False)],
            },
        ]

        # Seed Opportunity Sources
        sources_init = [
            ("VIIT Training & Placement Cell", "INSTITUTION_CURATED", "HEALTHY", 4),
            ("Approved Public Developer Feed", "PUBLIC_FEED", "HEALTHY", 2),
            ("Live VIIT Placement Portal", "APPROVED_API", "DEGRADED", 0),
            ("Coordinator Intake Channel", "AUTHORIZED_COORDINATOR", "HEALTHY", 1),
        ]
        for s_name, s_type, s_stat, s_cnt in sources_init:
            db.add(OpportunitySource(
                source_name=s_name,
                source_type=s_type,
                status=s_stat,
                last_checked=now,
                last_success=now if s_stat == "HEALTHY" else None,
                items_found=s_cnt,
            ))
        db.commit()

        for opp_spec in opps_data:
            opp = Opportunity(
                opportunity_id=opp_spec["id"],
                title=opp_spec["title"],
                organization=opp_spec["org"],
                opportunity_type=opp_spec["type"],
                description=opp_spec["desc"],
                location=opp_spec["location"],
                work_mode=opp_spec["work_mode"],
                deadline=opp_spec["deadline"],
                eligibility=opp_spec["eligibility"],
                source_name="VIIT Training & Placement Cell" if "VIIT" in opp_spec["title"] else "VIGNAI Development Partner",
                source_type="INSTITUTION_CURATED" if "VIIT" in opp_spec["title"] else "SYNTHETIC_DEVELOPMENT",
                verification_status="VERIFIED",
                lifecycle_status="ACTIVE",
                data_source="VERIFIED FROM VIIT PLACEMENT CELL" if "VIIT" in opp_spec["title"] else "SYNTHETIC DEVELOPMENT DATA",
                is_active=True,
            )
            db.add(opp)
            db.commit()
            db.refresh(opp)

            for s_name, req in opp_spec["skills"]:
                db.add(OpportunitySkill(
                    opportunity_id=opp.id,
                    skill_name=s_name,
                    is_required=req,
                ))
            db.commit()

        # Seed initial Student Career Profile
        student_career = CareerProfile(
            student_id=student.id,
            headline="B.Tech Computer Science Student | Full-Stack & AI Enthusiast",
            summary="Passionate about building scalable web applications, REST APIs, and algorithmic intelligence. Experienced in Python, React, SQL, and FastAPI.",
            education="B.Tech in Computer Science & Engineering (CSE), Vignan's Institute of Information Technology (VIIT Duvvada) | 2022 - 2026",
            interests=["Artificial Intelligence", "Full-Stack Software Engineering", "Cloud Computing"],
            resume_file_name="resume_221FA04001.pdf",
            resume_file_path="",
            resume_file_size=1048576,
            resume_uploaded_at=now - timedelta(days=3),
            extraction_status="COMPLETED",
            data_source="VERIFIED_FROM_RESUME",
        )
        db.add(student_career)
        db.commit()
        db.refresh(student_career)

        # Seed skills
        init_skills = [
            ("Python", "TECHNICAL", "VERIFIED_FROM_RESUME", "ADVANCED"),
            ("React", "FRAMEWORK", "VERIFIED_FROM_RESUME", "INTERMEDIATE"),
            ("SQL", "DATABASE", "VERIFIED_FROM_RESUME", "ADVANCED"),
            ("FastAPI", "FRAMEWORK", "VERIFIED_FROM_RESUME", "INTERMEDIATE"),
            ("JavaScript", "TECHNICAL", "VERIFIED_FROM_RESUME", "INTERMEDIATE"),
            ("Git", "TOOL", "VERIFIED_FROM_RESUME", "INTERMEDIATE"),
            ("Data Structures", "TECHNICAL", "VERIFIED_FROM_RESUME", "ADVANCED"),
            ("Tailwind CSS", "FRAMEWORK", "VERIFIED_FROM_RESUME", "INTERMEDIATE"),
        ]
        for s_name, cat, src, prof in init_skills:
            db.add(CareerSkill(
                career_profile_id=student_career.id,
                name=s_name,
                category=cat,
                source=src,
                proficiency_level=prof,
            ))

        # Seed projects
        db.add(CareerProject(
            career_profile_id=student_career.id,
            title="Campus AI Operating System & Analytics Platform",
            description="Built role-aware grievance triage, deterministic academic intelligence, and natural language analytics.",
            technologies=["Python", "FastAPI", "React", "SQL", "Tailwind CSS"],
            source="VERIFIED_FROM_RESUME",
        ))
        db.add(CareerProject(
            career_profile_id=student_career.id,
            title="Distributed Network Latency Diagnostic Utility",
            description="Created packet stream timing analysis utility for campus Wi-Fi monitoring.",
            technologies=["Python", "Linux", "Data Structures"],
            source="VERIFIED_FROM_RESUME",
        ))

        # Seed certifications
        db.add(CareerCertification(
            career_profile_id=student_career.id,
            title="Programming in Python & Data Structures",
            issuer="NPTEL / IIT Madras",
            issue_date="2024",
            source="VERIFIED_FROM_RESUME",
        ))

        # Seed experiences
        db.add(CareerExperience(
            career_profile_id=student_career.id,
            title="Student Developer & Project Lead",
            organization="VIIT Innovation & Development Lab",
            duration="6 Months (2024)",
            description="Developed campus software solutions and automated workflow tools.",
            source="VERIFIED_FROM_RESUME",
        ))

        db.commit()

        # Compute initial matches
        matching_engine.sync_student_matches(db, student_career.id)
        print("Career Intelligence opportunities and student profile seeded.")

        
        # 5. Synchronize Emerging Patterns & Proactive Priority Alerts
        print("[6/6] Synchronizing pattern clusters and proactive alerts...")
        PatternDetectionService().detect_and_save_patterns(db)
        alerts = alert_service.evaluate_and_sync_alerts(db)
        print(f"Generated {len(alerts)} proactive priority review alerts.")

        print("=" * 60)
        print("[SUCCESS] VIGNAI OS DEMO DATA RESET COMPLETE!")
        print("Accounts:")
        print("  - Student:    student@vignex.dev (Roll No: 221FA04001 / password123)")
        print("  - Faculty:    faculty@vignex.dev (Faculty ID: FAC-CSE-001 / password123)")
        print("  - Management: management@vignex.dev (Management ID: MGMT-ADMIN-01 / password123)")
        print("Demo Clusters:")
        print("  - Block A Wi-Fi (4 reports, HIGH, Increasing)")
        print("  - Route 4 Transport (3 reports, HIGH, Recurring)")
        print("  - Lab 3 Projector (2 reports, HIGH, CSE Dept)")
        print("  - Protected Grievance (1 report, HIGH, Anonymous)")
        print("=" * 60)

    finally:
        db.close()

if __name__ == "__main__":
    reset_demo_data()
