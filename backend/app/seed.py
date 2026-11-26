"""
Initializes the database with rich, realistic seed data for AdvisorAI
focused on 10th & 12th pass-out students, mentors, and an admin user.
"""
from sqlalchemy.orm import Session

from backend.app.auth import hash_password
from backend.app.models import (
    Attendance,
    ChatMessage,
    Checkin,
    Interest,
    Mark,
    Mentor,
    Notification,
    Skill,
    Student,
    Subject,
    User,
)
from backend.app.services import generate_study_plan, refresh_student_ai


def seed_database(db: Session) -> None:
    """Populate realistic sample records if the database is empty."""
    if db.query(User).count() > 0:
        return

    # 1. Admin & Mentor accounts
    admin_user = User(
        email="admin@advisorai.edu",
        full_name="Dr. Rajesh Kulkarni",
        password_hash=hash_password("admin123"),
        role="admin",
        department="Academic Administration",
    )
    mentor_user = User(
        email="mentor@advisorai.edu",
        full_name="Prof. Neha Verma",
        password_hash=hash_password("mentor123"),
        role="mentor",
        department="10th & 12th Career Advisory",
    )
    db.add_all([admin_user, mentor_user])
    db.flush()

    mentor_profile = Mentor(
        user_id=mentor_user.id,
        specialization="10th Stream Choice, 12th Career Counseling & STEM Mentoring",
        department="10th & 12th Career Advisory",
        bio="12+ years helping Class 10 and Class 12 graduates pick right streams, degrees, and study habits.",
        office_hours="Mon-Fri, 4:00 PM - 6:30 PM",
    )
    db.add(mentor_profile)
    db.flush()

    # 2. Sample 10th & 12th students
    sample_students = [
        {
            "email": "aman@advisorai.edu",
            "full_name": "Aman Sharma",
            "password": "aman123",
            "education_stage": "12th",
            "board_name": "CBSE",
            "stream": "Science (PCM)",
            "department": "12th Pass-Out (PCM)",
            "current_semester": 1,
            "board_percentage": 86.4,
            "current_cgpa": 8.4,
            "attendance_pct": 88.0,
            "internal_marks_avg": 82.0,
            "assignment_score_avg": 85.0,
            "study_hours_per_week": 24.0,
            "previous_grades_json": [
                {"term": "10th Boards", "cgpa": 8.6},
                {"term": "11th Finals", "cgpa": 7.9},
                {"term": "12th Pre-Board", "cgpa": 8.2},
                {"term": "12th Boards", "cgpa": 8.6},
                {"term": "Sem 1 Internal", "cgpa": 8.4},
            ],
            "goals": "Master Python & Machine Learning after 12th PCM and build real AI projects.",
            "onboarding_completed": True,
            "mentor_remarks": "Strong analytical base. Encourage building 2 Python data projects this month.",
            "upcoming_deadlines_count": 3,
            "subjects": [
                ("MAT101", "Mathematics & Calculus", 86, 88, 84, "2026-12-12", False),
                ("CS102", "Python & Data Logic", 90, 92, 89, "2026-12-15", False),
                ("PHY103", "Applied Physics", 71, 76, 68, "2026-12-18", True),
                ("ENG104", "Communication Skills", 80, 84, 82, "2026-12-20", False),
            ],
            "skills": {"Python": 78, "Analytical Thinking": 82, "Mathematics": 84, "Communication": 72},
            "interests": ["Artificial Intelligence", "Data Science", "Coding"],
        },
        {
            "email": "priya@advisorai.edu",
            "full_name": "Priya Nair",
            "password": "priya123",
            "education_stage": "10th",
            "board_name": "ICSE",
            "stream": "General",
            "department": "10th Pass-Out",
            "current_semester": 1,
            "board_percentage": 91.2,
            "current_cgpa": 9.1,
            "attendance_pct": 93.0,
            "internal_marks_avg": 88.0,
            "assignment_score_avg": 90.0,
            "study_hours_per_week": 26.0,
            "previous_grades_json": [
                {"term": "Class 8", "cgpa": 8.5},
                {"term": "Class 9", "cgpa": 8.8},
                {"term": "10th Mock", "cgpa": 8.9},
                {"term": "10th Boards", "cgpa": 9.1},
            ],
            "goals": "Choose the right stream after 10th (PCM vs PCB) for biotech or data science.",
            "onboarding_completed": True,
            "mentor_remarks": "Exceptional science & biology curiosity. Great fit for PCB or PCMB.",
            "upcoming_deadlines_count": 2,
            "subjects": [
                ("SCI10", "Science (Bio & Chem)", 92, 90, 94, "2026-12-10", False),
                ("MAT10", "Mathematics", 85, 86, 84, "2026-12-14", False),
                ("ENG10", "English Literature", 88, 90, 87, "2026-12-17", False),
                ("COM10", "Computer Applications", 76, 80, 74, "2026-12-21", True),
            ],
            "skills": {"Biology": 90, "Analytical Thinking": 84, "Communication": 86, "Python": 55},
            "interests": ["Biotechnology", "Healthcare", "Research"],
        },
        {
            "email": "rohan@advisorai.edu",
            "full_name": "Rohan Verma",
            "password": "rohan123",
            "education_stage": "12th",
            "board_name": "State Board",
            "stream": "Science (PCM)",
            "department": "12th Pass-Out (PCM)",
            "current_semester": 1,
            "board_percentage": 64.5,
            "current_cgpa": 6.0,
            "attendance_pct": 63.0,
            "internal_marks_avg": 52.0,
            "assignment_score_avg": 58.0,
            "study_hours_per_week": 9.0,
            "previous_grades_json": [
                {"term": "10th Boards", "cgpa": 7.1},
                {"term": "11th Finals", "cgpa": 6.4},
                {"term": "12th Pre-Board", "cgpa": 6.1},
                {"term": "12th Boards", "cgpa": 6.4},
                {"term": "Sem 1 Internal", "cgpa": 5.8},
            ],
            "goals": "Improve attendance, pass all subjects comfortably, and build web development skills.",
            "onboarding_completed": True,
            "mentor_remarks": "Attendance dropped to 63% — schedule weekly 1-on-1 check-in urgently.",
            "upcoming_deadlines_count": 4,
            "subjects": [
                ("MAT101", "Mathematics", 48, 55, 50, "2026-12-11", True),
                ("CS102", "Web & HTML/JS", 68, 72, 69, "2026-12-15", False),
                ("PHY103", "Physics Basics", 49, 54, 46, "2026-12-18", True),
                ("ENG104", "English", 64, 68, 66, "2026-12-22", False),
            ],
            "skills": {"Coding": 68, "Design": 62, "Mathematics": 48, "Communication": 60},
            "interests": ["Web Development", "UI Design", "Gaming"],
        },
        {
            "email": "sneha@advisorai.edu",
            "full_name": "Sneha Patel",
            "password": "sneha123",
            "education_stage": "12th",
            "board_name": "CBSE",
            "stream": "Commerce",
            "department": "12th Pass-Out (Commerce)",
            "current_semester": 1,
            "board_percentage": 84.0,
            "current_cgpa": 8.1,
            "attendance_pct": 76.0,
            "internal_marks_avg": 74.0,
            "assignment_score_avg": 78.0,
            "study_hours_per_week": 17.0,
            "previous_grades_json": [
                {"term": "10th Boards", "cgpa": 8.0},
                {"term": "11th Finals", "cgpa": 7.8},
                {"term": "12th Boards", "cgpa": 8.4},
                {"term": "Sem 1 Internal", "cgpa": 8.1},
            ],
            "goals": "Explore Financial Analytics, BBA Finance, or Chartered Accountancy.",
            "onboarding_completed": True,
            "mentor_remarks": "Good business sense; keep attendance above 80%.",
            "upcoming_deadlines_count": 2,
            "subjects": [
                ("ACC101", "Financial Accounting", 84, 86, 82, "2026-12-12", False),
                ("ECO102", "Business Economics", 77, 80, 75, "2026-12-16", False),
                ("MAT103", "Business Statistics", 65, 70, 64, "2026-12-19", True),
                ("ENG104", "Business Communication", 85, 88, 86, "2026-12-23", False),
            ],
            "skills": {"Accounting": 84, "Communication": 85, "Analytical Thinking": 76, "Excel": 74},
            "interests": ["Finance", "Business", "Data Analytics"],
        },
        {
            "email": "vikram@advisorai.edu",
            "full_name": "Vikram Joshi",
            "password": "vikram123",
            "education_stage": "10th",
            "board_name": "CBSE",
            "stream": "Arts",
            "department": "10th Pass-Out",
            "current_semester": 1,
            "board_percentage": 78.0,
            "current_cgpa": 7.6,
            "attendance_pct": 74.0,
            "internal_marks_avg": 71.0,
            "assignment_score_avg": 75.0,
            "study_hours_per_week": 14.0,
            "previous_grades_json": [
                {"term": "Class 8", "cgpa": 7.4},
                {"term": "Class 9", "cgpa": 7.5},
                {"term": "10th Boards", "cgpa": 7.8},
            ],
            "goals": "Combine creativity and technology into UI/UX or Media Design after 10th.",
            "onboarding_completed": True,
            "mentor_remarks": "Creative thinker; encourage Figma portfolio + attendance consistency.",
            "upcoming_deadlines_count": 3,
            "subjects": [
                ("ART10", "Visual Design & Media", 88, 90, 86, "2026-12-13", False),
                ("ENG10", "English & Storytelling", 82, 84, 80, "2026-12-16", False),
                ("MAT10", "Mathematics", 61, 65, 59, "2026-12-19", True),
                ("SOC10", "Social Studies", 75, 78, 74, "2026-12-22", False),
            ],
            "skills": {"Design": 88, "Communication": 82, "Creativity": 90, "Coding": 52},
            "interests": ["UI/UX Design", "Arts", "Web Development"],
        },
    ]

    for item in sample_students:
        user = User(
            email=item["email"],
            full_name=item["full_name"],
            password_hash=hash_password(item["password"]),
            role="student",
            department=item["department"],
        )
        db.add(user)
        db.flush()

        student = Student(
            user_id=user.id,
            mentor_id=mentor_profile.id,
            education_stage=item["education_stage"],
            board_name=item["board_name"],
            stream=item["stream"],
            department=item["department"],
            current_semester=item["current_semester"],
            board_percentage=item["board_percentage"],
            current_cgpa=item["current_cgpa"],
            attendance_pct=item["attendance_pct"],
            internal_marks_avg=item["internal_marks_avg"],
            assignment_score_avg=item["assignment_score_avg"],
            study_hours_per_week=item["study_hours_per_week"],
            previous_grades_json=item["previous_grades_json"],
            goals=item["goals"],
            onboarding_completed=item["onboarding_completed"],
            mentor_remarks=item["mentor_remarks"],
            upcoming_deadlines_count=item["upcoming_deadlines_count"],
        )
        db.add(student)
        db.flush()

        for code, name, internal_s, assign_s, exam_s, exam_date, is_weak in item["subjects"]:
            subj = Subject(
                student_id=student.id,
                code=code,
                name=name,
                credits=4,
                exam_date=exam_date,
                weak_area=is_weak,
            )
            db.add(subj)
            db.flush()
            db.add(
                Mark(
                    student_id=student.id,
                    subject_id=subj.id,
                    internal_score=internal_s,
                    assignment_score=assign_s,
                    exam_score=exam_s,
                    semester=1,
                )
            )
            att_pct = min(98.0, max(52.0, item["attendance_pct"] + (-6 if is_weak else 3)))
            attended = int(round(att_pct * 30 / 100))
            db.add(
                Attendance(
                    student_id=student.id,
                    subject_name=name,
                    classes_attended=attended,
                    total_classes=30,
                    percentage=round(att_pct, 1),
                )
            )

        for sk_name, sk_lvl in item["skills"].items():
            db.add(Skill(student_id=student.id, name=sk_name, level=sk_lvl))
        for intr in item["interests"]:
            db.add(Interest(student_id=student.id, topic=intr, weight=85))

        db.add(
            Checkin(
                student_id=student.id,
                mood="calm" if item["attendance_pct"] >= 75 else "stressed",
                stress_score=2 if item["attendance_pct"] >= 75 else 4,
                sleep_hours=7.5 if item["attendance_pct"] >= 75 else 5.5,
                answers={"focus": "Good", "workload": "Manageable"},
                supportive_message="You're making steady progress. Keep taking short breaks!",
                wants_mentor_talk=(item["attendance_pct"] < 70),
            )
        )
        db.add(
            ChatMessage(
                student_id=student.id,
                sender="assistant",
                message=(
                    f"Hi {item['full_name'].split()[0]}! 👋 I'm AdvisorAI. "
                    f"Ask me anything about your {item['education_stage']} next steps, improving your CGPA, or choosing the right career!"
                ),
            )
        )
        db.add(
            Notification(
                user_id=user.id,
                title="New AI Career Matches Ready",
                message="Your top 3 career paths and skill-gap courses have been updated based on your latest marks.",
                category="info",
            )
        )
        db.add(
            Notification(
                user_id=user.id,
                title="Upcoming Exam Deadline",
                message="First mock/internal exam starts on 12 Dec — check your Study Planner!",
                category="deadline",
            )
        )
        db.flush()

        refresh_student_ai(student, db)
        generate_study_plan(student, db)

    # Mentor notification about at-risk student
    db.add(
        Notification(
            user_id=mentor_user.id,
            title="High-Risk Alert: Rohan Verma",
            message="Rohan Verma's attendance dropped to 63% and requested a mentor talk.",
            category="warning",
        )
    )
    db.commit()
