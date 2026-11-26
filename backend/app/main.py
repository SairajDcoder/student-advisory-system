"""
AdvisorAI FastAPI Application
=============================
Complete REST API supporting:
- JWT Auth & Role-Based Access (student, mentor, admin)
- 3-Step Student Onboarding Wizard
- Student Dashboard, Performance Prediction + SHAP XAI, Simulator
- Content-based Career & Stream Guidance (10th & 12th pass-outs)
- AI Chat Advisor (LLM + context-aware fallback)
- Weekly Study Planner (auto-generate, drag-reorder, toggle complete)
- Wellbeing Check-in + Mentor Talk flag
- Notifications
- Mentor Dashboard (assigned students, filter, detail drawer, remarks, schedule meeting)
- Admin Dashboard (user management, department analytics, CSV dataset upload, XGBoost retrain)
"""
import io
from contextlib import asynccontextmanager
from typing import Dict, List

import pandas as pd
from fastapi import Depends, FastAPI, File, HTTPException, UploadFile, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from backend.app.auth import (
    create_access_token,
    get_current_user,
    hash_password,
    require_roles,
    verify_password,
)
from backend.app.config import CORS_ORIGINS, DATA_DIR
from backend.app.database import Base, SessionLocal, engine, get_db
from backend.app.models import (
    ChatMessage,
    Checkin,
    Interest,
    Mentor,
    Notification,
    Prediction,
    Recommendation,
    Skill,
    Student,
    StudyPlan,
    Subject,
    User,
)
from backend.app.schemas import (
    AdminUserCreateRequest,
    AdminUserToggleRequest,
    ChatRequest,
    CheckinRequest,
    GoogleDemoRequest,
    LoginRequest,
    MentorRemarkRequest,
    OnboardingRequest,
    PredictionSimulateRequest,
    ProfileUpdateRequest,
    RegisterRequest,
    StudyTaskUpdate,
)
from backend.app.seed import seed_database
from backend.app.services import (
    build_ml_profile,
    build_wellbeing_support,
    generate_advisor_reply,
    generate_study_plan,
    refresh_student_ai,
)
from backend.ml.predictor import get_model_metrics, predict_student_performance, reload_models
from backend.ml.train_models import DATASET_PATH, NUMERIC_FEATURES, train_and_save_models


@asynccontextmanager
async def lifespan(_app: FastAPI):
    """Initialize tables, ensure ML models are trained, and seed demo data."""
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seed_database(db)
    finally:
        db.close()
    yield


app = FastAPI(
    title="AdvisorAI – Student Advisory System API",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def _get_student_for_user(user: User, db: Session) -> Student:
    student = db.query(Student).filter(Student.user_id == user.id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student profile not found.")
    return student


def _serialize_user(user: User, db: Session) -> Dict:
    student = db.query(Student).filter(Student.user_id == user.id).first()
    return {
        "id": user.id,
        "email": user.email,
        "full_name": user.full_name,
        "role": user.role,
        "department": user.department,
        "theme_preference": user.theme_preference,
        "language_preference": user.language_preference,
        "notifications_enabled": user.notifications_enabled,
        "onboarding_completed": student.onboarding_completed if student else True,
        "education_stage": student.education_stage if student else None,
        "stream": student.stream if student else None,
    }


# ─────────────────────────────────────────────────────────────────────────────
# Auth & Onboarding
# ─────────────────────────────────────────────────────────────────────────────
@app.get("/api/health")
def health():
    return {"status": "healthy", "ml_metrics": get_model_metrics()}


@app.post("/api/auth/register")
def register(payload: RegisterRequest, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == payload.email.lower()).first():
        raise HTTPException(status_code=400, detail="An account with this email already exists.")

    role = payload.role if payload.role in ("student", "mentor", "admin") else "student"
    user = User(
        email=payload.email.lower(),
        full_name=payload.full_name,
        password_hash=hash_password(payload.password),
        role=role,
        department=payload.department,
    )
    db.add(user)
    db.flush()

    if role == "student":
        mentor = db.query(Mentor).first()
        student = Student(
            user_id=user.id,
            mentor_id=mentor.id if mentor else None,
            education_stage=payload.education_stage,
            stream=payload.stream,
            department=payload.department,
            previous_grades_json=[
                {"term": "Previous Term", "cgpa": 7.6},
                {"term": "Board Score", "cgpa": 8.0},
            ],
            onboarding_completed=False,
        )
        db.add(student)
        db.flush()
        for code, name, weak in [
            ("MAT101", "Mathematics", False),
            ("SCI102", "Core Science / Tech", False),
            ("ENG103", "English & Communication", False),
            ("APT104", "Analytical Aptitude", True),
        ]:
            subj = Subject(student_id=student.id, code=code, name=name, weak_area=weak)
            db.add(subj)
        db.flush()
        db.add(
            ChatMessage(
                student_id=student.id,
                sender="assistant",
                message=f"Welcome {payload.full_name.split()[0]}! 👋 I'm AdvisorAI. Complete your quick setup or ask me any question about 10th/12th streams, CGPA, or careers!",
            )
        )
        refresh_student_ai(student, db)
        generate_study_plan(student, db)
    elif role == "mentor":
        db.add(Mentor(user_id=user.id, department=payload.department))

    db.commit()
    token = create_access_token(user)
    return {"access_token": token, "token_type": "bearer", "user": _serialize_user(user, db)}


@app.post("/api/auth/login")
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email.lower()).first()
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password.")
    if not user.is_active:
        raise HTTPException(status_code=403, detail="Account is deactivated. Contact Admin.")
    token = create_access_token(user)
    return {"access_token": token, "token_type": "bearer", "user": _serialize_user(user, db)}


@app.post("/api/auth/google-demo")
def google_demo_login(payload: GoogleDemoRequest, db: Session = Depends(get_db)):
    """Demo Google Sign-In endpoint matching role selection on the Login screen."""
    email_map = {
        "student": "aman@advisorai.edu",
        "mentor": "mentor@advisorai.edu",
        "admin": "admin@advisorai.edu",
    }
    target_email = (payload.email or email_map.get(payload.role, "aman@advisorai.edu")).lower()
    user = db.query(User).filter(User.email == target_email).first()
    if not user:
        raise HTTPException(status_code=404, detail="Demo account not found.")
    token = create_access_token(user)
    return {"access_token": token, "token_type": "bearer", "user": _serialize_user(user, db)}


@app.get("/api/auth/me")
def me(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return _serialize_user(current_user, db)


@app.post("/api/student/onboarding")
def complete_onboarding(
    payload: OnboardingRequest,
    current_user: User = Depends(require_roles(["student"])),
    db: Session = Depends(get_db),
):
    student = _get_student_for_user(current_user, db)
    if not payload.skip:
        student.education_stage = payload.education_stage
        student.board_name = payload.board_name
        student.stream = payload.stream
        student.board_percentage = payload.board_percentage
        student.current_cgpa = round(payload.board_percentage / 10.0, 2)
        student.study_hours_per_week = payload.study_hours_per_week
        student.department = f"{payload.education_stage} Pass-Out ({payload.stream})"
        current_user.department = student.department
        if payload.goals:
            student.goals = payload.goals

        if payload.interests:
            db.query(Interest).filter(Interest.student_id == student.id).delete()
            for topic in payload.interests:
                db.add(Interest(student_id=student.id, topic=topic, weight=85))

        if payload.skills:
            db.query(Skill).filter(Skill.student_id == student.id).delete()
            for sk_name, sk_lvl in payload.skills.items():
                db.add(Skill(student_id=student.id, name=sk_name, level=int(sk_lvl)))

    student.onboarding_completed = True
    db.commit()
    refresh_student_ai(student, db)
    generate_study_plan(student, db)
    return {"message": "Onboarding saved", "user": _serialize_user(current_user, db)}


# ─────────────────────────────────────────────────────────────────────────────
# Student Screens (Dashboard, Performance, Careers, Chat, Study, Wellbeing)
# ─────────────────────────────────────────────────────────────────────────────
@app.get("/api/student/dashboard")
def student_dashboard(
    current_user: User = Depends(require_roles(["student"])),
    db: Session = Depends(get_db),
):
    student = _get_student_for_user(current_user, db)
    pred = (
        db.query(Prediction)
        .filter(Prediction.student_id == student.id)
        .order_by(Prediction.created_at.desc())
        .first()
    )
    if not pred:
        pred = refresh_student_ai(student, db)

    subject_scores = []
    for subj in student.subjects:
        m = subj.marks[0] if subj.marks else None
        att = next((a for a in student.attendance_records if a.subject_name == subj.name), None)
        subject_scores.append(
            {
                "id": subj.id,
                "code": subj.code,
                "subject": subj.name,
                "internal": m.internal_score if m else 75,
                "assignment": m.assignment_score if m else 78,
                "exam": m.exam_score if m else 74,
                "attendance": att.percentage if att else student.attendance_pct,
                "weak_area": subj.weak_area,
                "exam_date": subj.exam_date,
            }
        )

    unread_notifs = (
        db.query(Notification)
        .filter(Notification.user_id == current_user.id, Notification.is_read.is_(False))
        .count()
    )

    return {
        "student": {
            "id": student.id,
            "full_name": current_user.full_name,
            "education_stage": student.education_stage,
            "board_name": student.board_name,
            "stream": student.stream,
            "department": student.department,
            "board_percentage": student.board_percentage,
            "current_cgpa": student.current_cgpa,
            "attendance_pct": student.attendance_pct,
            "internal_marks_avg": student.internal_marks_avg,
            "assignment_score_avg": student.assignment_score_avg,
            "study_hours_per_week": student.study_hours_per_week,
            "upcoming_deadlines_count": student.upcoming_deadlines_count,
            "previous_grades": student.previous_grades_json or [],
            "goals": student.goals,
            "mentor_remarks": student.mentor_remarks,
            "next_meeting_at": student.next_meeting_at,
            "onboarding_completed": student.onboarding_completed,
        },
        "prediction": {
            "predicted_cgpa": pred.predicted_cgpa,
            "pass_probability": pred.pass_probability,
            "risk_level": pred.risk_level,
            "risk_score": pred.risk_score,
            "top_reasons": pred.top_reasons,
            "ai_insights": pred.ai_insights,
        },
        "subject_scores": subject_scores,
        "unread_notifications": unread_notifs,
    }


@app.post("/api/student/predict/simulate")
def simulate_prediction(
    payload: PredictionSimulateRequest,
    current_user: User = Depends(require_roles(["student"])),
    db: Session = Depends(get_db),
):
    """Interactive what-if simulator on Performance & Prediction screen."""
    student = _get_student_for_user(current_user, db)
    profile = build_ml_profile(student, db)
    profile.update(
        {
            "attendance_pct": payload.attendance_pct,
            "internal_marks_avg": payload.internal_marks_avg,
            "assignment_score_avg": payload.assignment_score_avg,
            "past_cgpa": payload.past_cgpa,
            "study_hours_per_week": payload.study_hours_per_week,
        }
    )
    return predict_student_performance(profile)


@app.get("/api/student/careers")
def get_careers(
    current_user: User = Depends(require_roles(["student"])),
    db: Session = Depends(get_db),
):
    student = _get_student_for_user(current_user, db)
    recs = (
        db.query(Recommendation)
        .filter(Recommendation.student_id == student.id)
        .order_by(Recommendation.match_pct.desc())
        .all()
    )
    if not recs:
        refresh_student_ai(student, db)
        recs = (
            db.query(Recommendation)
            .filter(Recommendation.student_id == student.id)
            .order_by(Recommendation.match_pct.desc())
            .all()
        )

    careers = [r for r in recs if r.rec_type == "career"]
    stream_rec = next((r for r in recs if r.rec_type == "stream"), None)
    return {
        "education_stage": student.education_stage,
        "stream": student.stream,
        "stream_recommendation": (
            {
                "title": stream_rec.title,
                "match_pct": stream_rec.match_pct,
                "summary": stream_rec.summary,
            }
            if stream_rec
            else None
        ),
        "careers": [
            {
                "id": c.id,
                "title": c.title,
                "match_pct": c.match_pct,
                "summary": c.summary,
                "required_skills": c.required_skills,
                "skill_gaps": c.skill_gaps,
                "suggested_courses": c.suggested_courses,
            }
            for c in careers
        ],
    }


@app.get("/api/student/chat")
def get_chat_history(
    current_user: User = Depends(require_roles(["student"])),
    db: Session = Depends(get_db),
):
    student = _get_student_for_user(current_user, db)
    msgs = (
        db.query(ChatMessage)
        .filter(ChatMessage.student_id == student.id)
        .order_by(ChatMessage.created_at.asc(), ChatMessage.id.asc())
        .all()
    )
    return [
        {
            "id": m.id,
            "sender": m.sender,
            "message": m.message,
            "created_at": m.created_at.isoformat() if m.created_at else "",
        }
        for m in msgs
    ]


@app.post("/api/student/chat")
async def post_chat_message(
    payload: ChatRequest,
    current_user: User = Depends(require_roles(["student"])),
    db: Session = Depends(get_db),
):
    student = _get_student_for_user(current_user, db)
    user_msg = ChatMessage(student_id=student.id, sender="user", message=payload.message.strip())
    db.add(user_msg)
    db.flush()

    reply_text = await generate_advisor_reply(student, payload.message, db)
    bot_msg = ChatMessage(student_id=student.id, sender="assistant", message=reply_text)
    db.add(bot_msg)
    db.commit()
    db.refresh(user_msg)
    db.refresh(bot_msg)
    return {
        "user_message": {
            "id": user_msg.id,
            "sender": user_msg.sender,
            "message": user_msg.message,
            "created_at": user_msg.created_at.isoformat(),
        },
        "assistant_message": {
            "id": bot_msg.id,
            "sender": bot_msg.sender,
            "message": bot_msg.message,
            "created_at": bot_msg.created_at.isoformat(),
        },
    }


@app.get("/api/student/study-plan")
def get_study_plan(
    current_user: User = Depends(require_roles(["student"])),
    db: Session = Depends(get_db),
):
    student = _get_student_for_user(current_user, db)
    tasks = (
        db.query(StudyPlan)
        .filter(StudyPlan.student_id == student.id)
        .order_by(StudyPlan.order_index.asc(), StudyPlan.id.asc())
        .all()
    )
    if not tasks:
        tasks = generate_study_plan(student, db)
    return [
        {
            "id": t.id,
            "day_of_week": t.day_of_week,
            "subject": t.subject,
            "topic": t.topic,
            "duration_minutes": t.duration_minutes,
            "priority": t.priority,
            "completed": t.completed,
            "order_index": t.order_index,
        }
        for t in tasks
    ]


@app.post("/api/student/study-plan/regenerate")
def regenerate_study_plan(
    current_user: User = Depends(require_roles(["student"])),
    db: Session = Depends(get_db),
):
    student = _get_student_for_user(current_user, db)
    tasks = generate_study_plan(student, db)
    return [
        {
            "id": t.id,
            "day_of_week": t.day_of_week,
            "subject": t.subject,
            "topic": t.topic,
            "duration_minutes": t.duration_minutes,
            "priority": t.priority,
            "completed": t.completed,
            "order_index": t.order_index,
        }
        for t in tasks
    ]


@app.patch("/api/student/study-plan/{task_id}")
def update_study_task(
    task_id: int,
    payload: StudyTaskUpdate,
    current_user: User = Depends(require_roles(["student"])),
    db: Session = Depends(get_db),
):
    student = _get_student_for_user(current_user, db)
    task = (
        db.query(StudyPlan)
        .filter(StudyPlan.id == task_id, StudyPlan.student_id == student.id)
        .first()
    )
    if not task:
        raise HTTPException(status_code=404, detail="Study task not found.")
    if payload.completed is not None:
        task.completed = payload.completed
    if payload.day_of_week is not None:
        task.day_of_week = payload.day_of_week
    if payload.order_index is not None:
        task.order_index = payload.order_index
    db.commit()
    db.refresh(task)
    return {
        "id": task.id,
        "day_of_week": task.day_of_week,
        "subject": task.subject,
        "topic": task.topic,
        "duration_minutes": task.duration_minutes,
        "priority": task.priority,
        "completed": task.completed,
        "order_index": task.order_index,
    }


@app.get("/api/student/wellbeing")
def get_checkins(
    current_user: User = Depends(require_roles(["student"])),
    db: Session = Depends(get_db),
):
    student = _get_student_for_user(current_user, db)
    rows = (
        db.query(Checkin)
        .filter(Checkin.student_id == student.id)
        .order_by(Checkin.created_at.desc())
        .limit(10)
        .all()
    )
    return [
        {
            "id": r.id,
            "mood": r.mood,
            "stress_score": r.stress_score,
            "sleep_hours": r.sleep_hours,
            "answers": r.answers,
            "supportive_message": r.supportive_message,
            "wants_mentor_talk": r.wants_mentor_talk,
            "created_at": r.created_at.isoformat() if r.created_at else "",
        }
        for r in rows
    ]


@app.post("/api/student/wellbeing")
def submit_checkin(
    payload: CheckinRequest,
    current_user: User = Depends(require_roles(["student"])),
    db: Session = Depends(get_db),
):
    student = _get_student_for_user(current_user, db)
    msg = build_wellbeing_support(
        payload.mood, payload.stress_score, payload.sleep_hours, payload.wants_mentor_talk
    )
    checkin = Checkin(
        student_id=student.id,
        mood=payload.mood,
        stress_score=payload.stress_score,
        sleep_hours=payload.sleep_hours,
        answers=payload.answers,
        supportive_message=msg,
        wants_mentor_talk=payload.wants_mentor_talk,
    )
    db.add(checkin)

    if payload.wants_mentor_talk and student.mentor:
        db.add(
            Notification(
                user_id=student.mentor.user_id,
                title=f"Mentor Request: {current_user.full_name}",
                message=f"{current_user.full_name} requested a wellbeing / study chat (Mood: {payload.mood}).",
                category="warning",
            )
        )

    db.commit()
    db.refresh(checkin)
    refresh_student_ai(student, db)
    return {
        "id": checkin.id,
        "mood": checkin.mood,
        "stress_score": checkin.stress_score,
        "sleep_hours": checkin.sleep_hours,
        "supportive_message": checkin.supportive_message,
        "wants_mentor_talk": checkin.wants_mentor_talk,
        "created_at": checkin.created_at.isoformat(),
    }


# ─────────────────────────────────────────────────────────────────────────────
# Notifications & Profile Settings (All Authenticated Roles)
# ─────────────────────────────────────────────────────────────────────────────
@app.get("/api/notifications")
def list_notifications(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    items = (
        db.query(Notification)
        .filter(Notification.user_id == current_user.id)
        .order_by(Notification.created_at.desc())
        .limit(20)
        .all()
    )
    return [
        {
            "id": n.id,
            "title": n.title,
            "message": n.message,
            "category": n.category,
            "is_read": n.is_read,
            "created_at": n.created_at.isoformat() if n.created_at else "",
        }
        for n in items
    ]


@app.post("/api/notifications/{notif_id}/read")
def mark_notification_read(
    notif_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    notif = (
        db.query(Notification)
        .filter(Notification.id == notif_id, Notification.user_id == current_user.id)
        .first()
    )
    if not notif:
        raise HTTPException(status_code=404, detail="Notification not found.")
    notif.is_read = True
    db.commit()
    return {"ok": True}


@app.patch("/api/profile")
def update_profile(
    payload: ProfileUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if payload.full_name is not None:
        current_user.full_name = payload.full_name
    if payload.department is not None:
        current_user.department = payload.department
    if payload.theme_preference is not None:
        current_user.theme_preference = payload.theme_preference
    if payload.language_preference is not None:
        current_user.language_preference = payload.language_preference
    if payload.notifications_enabled is not None:
        current_user.notifications_enabled = payload.notifications_enabled

    student = db.query(Student).filter(Student.user_id == current_user.id).first()
    if student:
        if payload.education_stage is not None:
            student.education_stage = payload.education_stage
        if payload.stream is not None:
            student.stream = payload.stream
        if payload.department is not None:
            student.department = payload.department
        if payload.goals is not None:
            student.goals = payload.goals

    db.commit()
    return _serialize_user(current_user, db)


# ─────────────────────────────────────────────────────────────────────────────
# Mentor Dashboard
# ─────────────────────────────────────────────────────────────────────────────
@app.get("/api/mentor/students")
def mentor_students(
    current_user: User = Depends(require_roles(["mentor", "admin"])),
    db: Session = Depends(get_db),
):
    students = db.query(Student).all()
    results = []
    for st in students:
        pred = (
            db.query(Prediction)
            .filter(Prediction.student_id == st.id)
            .order_by(Prediction.created_at.desc())
            .first()
        )
        latest_checkin = (
            db.query(Checkin)
            .filter(Checkin.student_id == st.id)
            .order_by(Checkin.created_at.desc())
            .first()
        )
        results.append(
            {
                "student_id": st.id,
                "full_name": st.user.full_name,
                "email": st.user.email,
                "education_stage": st.education_stage,
                "stream": st.stream,
                "department": st.department,
                "current_cgpa": st.current_cgpa,
                "predicted_cgpa": pred.predicted_cgpa if pred else st.current_cgpa,
                "attendance_pct": st.attendance_pct,
                "internal_marks_avg": st.internal_marks_avg,
                "risk_level": pred.risk_level if pred else "Low",
                "risk_score": pred.risk_score if pred else 15.0,
                "top_reasons": pred.top_reasons if pred else [],
                "ai_insights": pred.ai_insights if pred else [],
                "mentor_remarks": st.mentor_remarks,
                "next_meeting_at": st.next_meeting_at,
                "wants_mentor_talk": latest_checkin.wants_mentor_talk if latest_checkin else False,
                "latest_mood": latest_checkin.mood if latest_checkin else "calm",
                "subjects": [
                    {
                        "name": subj.name,
                        "internal": subj.marks[0].internal_score if subj.marks else 75,
                        "exam": subj.marks[0].exam_score if subj.marks else 75,
                        "weak_area": subj.weak_area,
                    }
                    for subj in st.subjects
                ],
            }
        )
    return results


@app.post("/api/mentor/students/{student_id}/remarks")
def save_mentor_remarks(
    student_id: int,
    payload: MentorRemarkRequest,
    current_user: User = Depends(require_roles(["mentor", "admin"])),
    db: Session = Depends(get_db),
):
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found.")

    student.mentor_remarks = payload.remarks
    if payload.next_meeting_at:
        student.next_meeting_at = payload.next_meeting_at
        db.add(
            Notification(
                user_id=student.user_id,
                title="Mentor Meeting Scheduled",
                message=f"{current_user.full_name} scheduled a guidance session: {payload.next_meeting_at}.",
                category="success",
            )
        )
    else:
        db.add(
            Notification(
                user_id=student.user_id,
                title="New Mentor Remark",
                message=f"{current_user.full_name} added a note to your academic profile.",
                category="info",
            )
        )
    db.commit()
    return {
        "student_id": student.id,
        "mentor_remarks": student.mentor_remarks,
        "next_meeting_at": student.next_meeting_at,
    }


# ─────────────────────────────────────────────────────────────────────────────
# Admin Dashboard
# ─────────────────────────────────────────────────────────────────────────────
@app.get("/api/admin/overview")
def admin_overview(
    current_user: User = Depends(require_roles(["admin"])),
    db: Session = Depends(get_db),
):
    users = db.query(User).order_by(User.id.asc()).all()
    students = db.query(Student).all()

    dept_map: Dict[str, Dict] = {}
    risk_counts = {"Low": 0, "Medium": 0, "High": 0}
    for st in students:
        pred = (
            db.query(Prediction)
            .filter(Prediction.student_id == st.id)
            .order_by(Prediction.created_at.desc())
            .first()
        )
        risk = pred.risk_level if pred else "Low"
        risk_counts[risk] = risk_counts.get(risk, 0) + 1

        bucket = dept_map.setdefault(
            st.department, {"department": st.department, "students": 0, "avg_cgpa": 0.0, "at_risk": 0}
        )
        bucket["students"] += 1
        bucket["avg_cgpa"] += st.current_cgpa
        if risk == "High":
            bucket["at_risk"] += 1

    dept_analytics = []
    for d in dept_map.values():
        d["avg_cgpa"] = round(d["avg_cgpa"] / max(1, d["students"]), 2)
        dept_analytics.append(d)

    return {
        "users": [
            {
                "id": u.id,
                "full_name": u.full_name,
                "email": u.email,
                "role": u.role,
                "department": u.department,
                "is_active": u.is_active,
            }
            for u in users
        ],
        "department_analytics": dept_analytics,
        "risk_summary": risk_counts,
        "system_health": {
            "api_status": "Healthy",
            "database_status": "Connected",
            "total_users": len(users),
            "total_students": len(students),
            "ml_metrics": get_model_metrics(),
        },
    }


@app.post("/api/admin/users")
def admin_create_user(
    payload: AdminUserCreateRequest,
    current_user: User = Depends(require_roles(["admin"])),
    db: Session = Depends(get_db),
):
    if db.query(User).filter(User.email == payload.email.lower()).first():
        raise HTTPException(status_code=400, detail="Email already registered.")
    user = User(
        email=payload.email.lower(),
        full_name=payload.full_name,
        password_hash=hash_password(payload.password),
        role=payload.role,
        department=payload.department,
    )
    db.add(user)
    db.flush()
    if payload.role == "student":
        mentor = db.query(Mentor).first()
        st = Student(
            user_id=user.id,
            mentor_id=mentor.id if mentor else None,
            department=payload.department,
            previous_grades_json=[{"term": "Board Score", "cgpa": 7.8}],
            onboarding_completed=False,
        )
        db.add(st)
        db.flush()
        refresh_student_ai(st, db)
        generate_study_plan(st, db)
    elif payload.role == "mentor":
        db.add(Mentor(user_id=user.id, department=payload.department))
    db.commit()
    return {"id": user.id, "email": user.email, "full_name": user.full_name, "role": user.role}


@app.patch("/api/admin/users/{user_id}")
def admin_toggle_user(
    user_id: int,
    payload: AdminUserToggleRequest,
    current_user: User = Depends(require_roles(["admin"])),
    db: Session = Depends(get_db),
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
    if payload.is_active is not None:
        user.is_active = payload.is_active
    if payload.role is not None:
        user.role = payload.role
    db.commit()
    return {"id": user.id, "is_active": user.is_active, "role": user.role}


@app.post("/api/admin/dataset")
async def admin_upload_dataset(
    file: UploadFile = File(...),
    current_user: User = Depends(require_roles(["admin"])),
):
    content = await file.read()
    try:
        df = pd.read_csv(io.BytesIO(content))
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Invalid CSV file: {exc}")

    required = set(NUMERIC_FEATURES[:5] + ["next_cgpa", "risk_level"])
    missing = required - set(df.columns)
    if missing:
        raise HTTPException(
            status_code=400,
            detail=f"CSV is missing required columns: {', '.join(sorted(missing))}",
        )

    df.to_csv(DATASET_PATH, index=False)
    return {"message": f"Uploaded {len(df)} rows successfully.", "rows": len(df)}


@app.post("/api/admin/retrain")
def admin_retrain_models(
    current_user: User = Depends(require_roles(["admin"])),
    db: Session = Depends(get_db),
):
    metrics = train_and_save_models(DATASET_PATH if DATASET_PATH.exists() else None)
    reload_models()
    for st in db.query(Student).all():
        refresh_student_ai(st, db)
    return {"message": "XGBoost models retrained and predictions refreshed.", "metrics": metrics}
