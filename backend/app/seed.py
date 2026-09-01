import asyncio
from datetime import date, datetime, timedelta
from app.database import engine, Base, SessionLocal, safe_initialize_database
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
from app.services.auth_service import hash_password
from app.services.ai.complaint_ai import complaint_ai_service
from app.services.ai.policy.rules import CONFIGURED_DEPARTMENTS

def run_seed():
    safe_initialize_database()
    db = SessionLocal()
    try:
        print("Creating seed data...")
        # Create standard departments
        for dept_code in CONFIGURED_DEPARTMENTS:
            dept = db.query(Department).filter_by(code=dept_code).first()
            if not dept:
                name = dept_code
                if dept_code == "CSE":
                    name = "Computer Science & Engineering"
                elif dept_code == "ECE":
                    name = "Electronics & Communication"
                elif dept_code == "EEE":
                    name = "Electrical & Electronics"
                elif dept_code == "IT":
                    name = "Information Technology"
                elif dept_code == "Student Affairs":
                    name = "Student Affairs & Grievances"
                db.add(Department(name=name, code=dept_code))
        db.commit()

        cs_dept = db.query(Department).filter((Department.code == "CSE") | (Department.code == "CS")).first()
        if not cs_dept:
            cs_dept = Department(name="Computer Science & Engineering", code="CSE")
            db.add(cs_dept)
            db.commit()
            db.refresh(cs_dept)

        # Management User
        mgmt_email = "management@vignex.dev"
        mgmt = db.query(User).filter_by(email=mgmt_email).first()
        if not mgmt:
            mgmt = User(
                email=mgmt_email,
                management_id="MGMT-ADMIN-01",
                password_hash=hash_password("password123"),
                role="management",
                is_active=True,
                must_change_password=True,
            )
            db.add(mgmt)
            print("Created management user.")
        else:
            mgmt.password_hash = hash_password("password123")
            mgmt.management_id = "MGMT-ADMIN-01"
            mgmt.must_change_password = True
            mgmt.is_active = True
            mgmt.role = "management"

        # Student User
        student_email = "student@vignex.dev"
        student = db.query(User).filter_by(email=student_email).first()
        if not student:
            student = User(
                email=student_email,
                roll_number="221FA04001",
                password_hash=hash_password("password123"),
                role="student",
                is_active=True,
                must_change_password=True,
            )
            student.student_profile = StudentProfile(enrollment_number="221FA04001", year_of_study=2)
            db.add(student)
            print("Created student user.")
            db.commit()
            db.refresh(student)
        else:
            student.password_hash = hash_password("password123")
            student.roll_number = "221FA04001"
            student.must_change_password = True
            student.is_active = True
            student.role = "student"
            if student.student_profile:
                student.student_profile.enrollment_number = "221FA04001"

        # Faculty User (CSE)
        faculty_email = "faculty@vignex.dev"
        faculty = db.query(User).filter_by(email=faculty_email).first()
        if not faculty:
            faculty = User(
                email=faculty_email,
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
            print("Created faculty user.")
        else:
            faculty.password_hash = hash_password("password123")
            faculty.faculty_id = "FAC-CSE-001"
            faculty.must_change_password = True
            faculty.is_active = True
            faculty.role = "faculty"
            if faculty.faculty_profile:
                faculty.faculty_profile.employee_id = "FAC-CSE-001"
                if not faculty.faculty_profile.department_id:
                    faculty.faculty_profile.department_id = cs_dept.id

        db.commit()

        # Seed Academic Synthetic Data
        seed_academic_data(db, student, faculty, cs_dept)

        # Re-apply AI analysis and routing to all existing complaints if needed
        complaints = db.query(Complaint).all()
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        for c in complaints:
            if not c.ai_analysis or not c.routings or not c.ai_analysis.department:
                loop.run_until_complete(complaint_ai_service.analyze_and_save(db, c.id))

        print("Seed data creation and routing initialization complete.")
    finally:
        db.close()


def seed_academic_data(db, student_user: User, faculty_user: User, cs_dept: Department):
    """Seed synthetic academic development records (labeled SYNTHETIC DEVELOPMENT DATA)."""
    print("Seeding synthetic academic data...")
    it_dept = db.query(Department).filter(Department.code == "IT").first()

    student_profile = student_user.student_profile
    if not student_profile:
        return

    # 1. Subjects
    subjects_spec = [
        {"code": "CS201", "name": "Data Structures", "dept_id": cs_dept.id, "faculty_id": faculty_user.id, "credits": 4},
        {"code": "CS202", "name": "Operating Systems", "dept_id": cs_dept.id, "faculty_id": faculty_user.id, "credits": 4},
        {"code": "CS203", "name": "Database Management", "dept_id": cs_dept.id, "faculty_id": faculty_user.id, "credits": 3},
        {"code": "CS204", "name": "Computer Networks", "dept_id": it_dept.id if it_dept else cs_dept.id, "faculty_id": None, "credits": 3},
        {"code": "MA201", "name": "Engineering Mathematics", "dept_id": cs_dept.id, "faculty_id": None, "credits": 4},
    ]

    subject_map = {}
    for s_spec in subjects_spec:
        subj = db.query(AcademicSubject).filter_by(code=s_spec["code"]).first()
        if not subj:
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
        else:
            subj.faculty_user_id = s_spec["faculty_id"]
            db.commit()
        subject_map[s_spec["code"]] = subj

    # 2. Student Enrollments
    for code, subj in subject_map.items():
        enr = db.query(StudentSubjectEnrollment).filter_by(
            student_id=student_profile.id,
            subject_id=subj.id,
        ).first()
        if not enr:
            enr = StudentSubjectEnrollment(
                student_id=student_profile.id,
                subject_id=subj.id,
                semester=3,
                section="A",
                academic_year="2024-25",
            )
            db.add(enr)
    db.commit()

    # 3. Attendance Records (Past 30 days)
    today = date.today()
    existing_att_count = db.query(AttendanceRecord).filter_by(student_id=student_profile.id).count()
    if existing_att_count == 0:
        # Pattern: CS204 has a declining trend (first half 90%, second half 65%), others ~85-95%
        for i in range(30, 0, -1):
            cur_date = today - timedelta(days=i)
            if cur_date.weekday() >= 5:  # Skip weekends
                continue

            for code, subj in subject_map.items():
                status = ATTENDANCE_PRESENT
                if code == "CS204":
                    if i <= 14:
                        # Recent second half has more absences
                        status = ATTENDANCE_ABSENT if (i % 3 == 0) else (ATTENDANCE_OD if (i % 7 == 0) else ATTENDANCE_PRESENT)
                    else:
                        status = ATTENDANCE_PRESENT if (i % 8 != 0) else ATTENDANCE_ABSENT
                else:
                    if (i + subj.id) % 9 == 0:
                        status = ATTENDANCE_ABSENT
                    elif (i + subj.id) % 13 == 0:
                        status = ATTENDANCE_OD

                att = AttendanceRecord(
                    student_id=student_profile.id,
                    subject_id=subj.id,
                    date=cur_date,
                    status=status,
                )
                db.add(att)
        db.commit()

    # 4. Assessments & Results
    existing_assess_count = db.query(Assessment).count()
    if existing_assess_count == 0:
        for code, subj in subject_map.items():
            # Past Quiz 1
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
                student_id=student_profile.id,
                marks=21.0 + (subj.id % 4),
                submitted_at=datetime.combine(today - timedelta(days=18), datetime.min.time()),
            ))

            # Past Mid Exam
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
                student_id=student_profile.id,
                marks=76.0 + (subj.id % 12),
                submitted_at=datetime.combine(today - timedelta(days=6), datetime.min.time()),
            ))

            # Upcoming Lab / Quiz (in next 3-7 days)
            if code in ["CS201", "CS202"]:
                up_lab = Assessment(
                    subject_id=subj.id,
                    title=f"{subj.name} - Lab Practical Evaluation",
                    assessment_type=ASSESSMENT_LAB_EXAM,
                    scheduled_at=datetime.combine(today + timedelta(days=3), datetime.min.time()),
                    max_marks=50.0,
                    duration_minutes=120,
                )
                db.add(up_lab)
            if code in ["CS203", "CS204"]:
                up_q2 = Assessment(
                    subject_id=subj.id,
                    title=f"{subj.name} - Quiz 2 (Theory)",
                    assessment_type=ASSESSMENT_QUIZ,
                    scheduled_at=datetime.combine(today + timedelta(days=5), datetime.min.time()),
                    max_marks=25.0,
                    duration_minutes=30,
                )
                db.add(up_q2)
        db.commit()

    # 5. Assignments
    existing_assign_count = db.query(Assignment).filter_by(student_id=student_profile.id).count()
    if existing_assign_count == 0:
        for code, subj in subject_map.items():
            # 1 Submitted
            db.add(Assignment(
                subject_id=subj.id,
                student_id=student_profile.id,
                title=f"{subj.name} - Problem Set 1",
                description="Core theoretical proofs and implementation exercises.",
                due_at=datetime.combine(today - timedelta(days=12), datetime.min.time()),
                status=ASSIGNMENT_SUBMITTED,
                submitted_at=datetime.combine(today - timedelta(days=13), datetime.min.time()),
            ))

            # 1 Pending due in next 3 days
            db.add(Assignment(
                subject_id=subj.id,
                student_id=student_profile.id,
                title=f"{subj.name} - Module 2 Assignment",
                description="Comprehensive problem set covering module 2 algorithms.",
                due_at=datetime.combine(today + timedelta(days=2), datetime.min.time()),
                status=ASSIGNMENT_PENDING,
            ))

        # 1 Overdue on CS204
        cs204 = subject_map.get("CS204")
        if cs204:
            db.add(Assignment(
                subject_id=cs204.id,
                student_id=student_profile.id,
                title="Computer Networks - Wireshark Packet Analysis",
                description="Capture and analyze TCP 3-way handshake packets.",
                due_at=datetime.combine(today - timedelta(days=1), datetime.min.time()),
                status=ASSIGNMENT_OVERDUE,
            ))
        db.commit()

    # 6. Timetable Entries
    existing_tt_count = db.query(TimetableEntry).count()
    if existing_tt_count == 0:
        timetable_spec = [
            # Monday
            ("CS201", "Monday", "09:00", "10:00", "Room 301"),
            ("CS202", "Monday", "10:15", "11:15", "Room 302"),
            ("MA201", "Monday", "11:30", "12:30", "Room 204"),
            ("CS201", "Monday", "14:00", "16:00", "Lab 3"),
            # Tuesday
            ("CS203", "Tuesday", "09:00", "10:00", "Room 301"),
            ("CS204", "Tuesday", "10:15", "11:15", "Room 305"),
            ("CS202", "Tuesday", "11:30", "12:30", "Room 302"),
            # Wednesday
            ("CS201", "Wednesday", "09:00", "10:00", "Room 301"),
            ("CS203", "Wednesday", "10:15", "11:15", "Room 301"),
            ("MA201", "Wednesday", "11:30", "12:30", "Room 204"),
            ("CS203", "Wednesday", "14:00", "16:00", "Lab 2"),
            # Thursday
            ("CS204", "Thursday", "09:00", "10:00", "Room 305"),
            ("CS202", "Thursday", "10:15", "11:15", "Room 302"),
            ("CS203", "Thursday", "11:30", "12:30", "Room 301"),
            # Friday
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

    print("Synthetic academic data seeded successfully.")


if __name__ == "__main__":
    run_seed()

