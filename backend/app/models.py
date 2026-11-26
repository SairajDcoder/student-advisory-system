"""
SQLAlchemy ORM Data Model for AdvisorAI.
Includes all 14 core entities + supabase_uid linkage for Supabase Auth.
"""
from datetime import datetime, timezone
from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    JSON,
    String,
    Text,
)
from sqlalchemy.orm import relationship

from backend.app.database import Base


def utcnow():
    return datetime.now(timezone.utc)


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    supabase_uid = Column(String(64), unique=True, index=True, nullable=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    full_name = Column(String(120), nullable=False)
    password_hash = Column(String(255), nullable=True)
    role = Column(String(30), nullable=False, default="student")  # student | mentor | admin
    department = Column(String(80), default="12th Pass-Out (Science PCM)")
    is_active = Column(Boolean, default=True)
    theme_preference = Column(String(20), default="light")
    language_preference = Column(String(20), default="en")
    notifications_enabled = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), default=utcnow)

    student_profile = relationship("Student", back_populates="user", uselist=False, cascade="all, delete-orphan")
    mentor_profile = relationship("Mentor", back_populates="user", uselist=False, cascade="all, delete-orphan")
    notifications = relationship("Notification", back_populates="user", cascade="all, delete-orphan")


class Mentor(Base):
    __tablename__ = "mentors"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    specialization = Column(String(120), default="10th/12th Stream & Career Counseling")
    department = Column(String(80), default="Academic Advisory")
    bio = Column(Text, default="")
    office_hours = Column(String(100), default="Mon-Fri, 4:00 PM - 6:00 PM")

    user = relationship("User", back_populates="mentor_profile")
    students = relationship("Student", back_populates="mentor")


class Student(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    mentor_id = Column(Integer, ForeignKey("mentors.id", ondelete="SET NULL"), nullable=True)

    education_stage = Column(String(20), default="12th")  # "10th" | "12th" | "college"
    board_name = Column(String(40), default="CBSE")
    stream = Column(String(60), default="Science (PCM)")
    department = Column(String(80), default="12th Pass-Out (PCM)")
    current_semester = Column(Integer, default=1)
    board_percentage = Column(Float, default=75.0)
    current_cgpa = Column(Float, default=7.5)
    attendance_pct = Column(Float, default=80.0)
    internal_marks_avg = Column(Float, default=75.0)
    assignment_score_avg = Column(Float, default=75.0)
    study_hours_per_week = Column(Float, default=18.0)
    previous_grades_json = Column(JSON, default=list)
    goals = Column(Text, default="")
    onboarding_completed = Column(Boolean, default=False)
    mentor_remarks = Column(Text, default="")
    next_meeting_at = Column(String(80), default="")
    upcoming_deadlines_count = Column(Integer, default=2)

    user = relationship("User", back_populates="student_profile")
    mentor = relationship("Mentor", back_populates="students")
    subjects = relationship("Subject", back_populates="student", cascade="all, delete-orphan")
    marks = relationship("Mark", back_populates="student", cascade="all, delete-orphan")
    attendance_records = relationship("Attendance", back_populates="student", cascade="all, delete-orphan")
    skills = relationship("Skill", back_populates="student", cascade="all, delete-orphan")
    interests = relationship("Interest", back_populates="student", cascade="all, delete-orphan")
    predictions = relationship("Prediction", back_populates="student", cascade="all, delete-orphan")
    recommendations = relationship("Recommendation", back_populates="student", cascade="all, delete-orphan")
    chat_messages = relationship("ChatMessage", back_populates="student", cascade="all, delete-orphan")
    study_plans = relationship("StudyPlan", back_populates="student", cascade="all, delete-orphan")
    checkins = relationship("Checkin", back_populates="student", cascade="all, delete-orphan")


class Subject(Base):
    __tablename__ = "subjects"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id", ondelete="CASCADE"), nullable=False)
    code = Column(String(30), nullable=False)
    name = Column(String(120), nullable=False)
    credits = Column(Integer, default=4)
    exam_date = Column(String(30), default="2026-12-18")
    weak_area = Column(Boolean, default=False)

    student = relationship("Student", back_populates="subjects")
    marks = relationship("Mark", back_populates="subject", cascade="all, delete-orphan")


class Mark(Base):
    __tablename__ = "marks"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id", ondelete="CASCADE"), nullable=False)
    subject_id = Column(Integer, ForeignKey("subjects.id", ondelete="CASCADE"), nullable=False)
    internal_score = Column(Float, default=75.0)
    assignment_score = Column(Float, default=75.0)
    exam_score = Column(Float, default=75.0)
    max_score = Column(Float, default=100.0)
    semester = Column(Integer, default=1)

    student = relationship("Student", back_populates="marks")
    subject = relationship("Subject", back_populates="marks")


class Attendance(Base):
    __tablename__ = "attendance"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id", ondelete="CASCADE"), nullable=False)
    subject_name = Column(String(120), nullable=False)
    classes_attended = Column(Integer, default=24)
    total_classes = Column(Integer, default=30)
    percentage = Column(Float, default=80.0)
    recorded_at = Column(DateTime(timezone=True), default=utcnow)

    student = relationship("Student", back_populates="attendance_records")


class Skill(Base):
    __tablename__ = "skills"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(80), nullable=False)
    level = Column(Integer, default=60)

    student = relationship("Student", back_populates="skills")


class Interest(Base):
    __tablename__ = "interests"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id", ondelete="CASCADE"), nullable=False)
    topic = Column(String(80), nullable=False)
    weight = Column(Integer, default=80)

    student = relationship("Student", back_populates="interests")


class Prediction(Base):
    __tablename__ = "predictions"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id", ondelete="CASCADE"), nullable=False)
    predicted_cgpa = Column(Float, nullable=False)
    pass_probability = Column(Float, nullable=False)
    risk_level = Column(String(20), nullable=False)
    risk_score = Column(Float, nullable=False)
    top_reasons = Column(JSON, default=list)
    ai_insights = Column(JSON, default=list)
    created_at = Column(DateTime(timezone=True), default=utcnow)

    student = relationship("Student", back_populates="predictions")


class Recommendation(Base):
    __tablename__ = "recommendations"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id", ondelete="CASCADE"), nullable=False)
    rec_type = Column(String(30), nullable=False)
    title = Column(String(120), nullable=False)
    match_pct = Column(Float, nullable=False)
    summary = Column(Text, nullable=False)
    required_skills = Column(JSON, default=list)
    skill_gaps = Column(JSON, default=list)
    suggested_courses = Column(JSON, default=list)
    created_at = Column(DateTime(timezone=True), default=utcnow)

    student = relationship("Student", back_populates="recommendations")


class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id", ondelete="CASCADE"), nullable=False)
    sender = Column(String(20), nullable=False)
    message = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), default=utcnow)

    student = relationship("Student", back_populates="chat_messages")


class StudyPlan(Base):
    __tablename__ = "study_plans"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id", ondelete="CASCADE"), nullable=False)
    day_of_week = Column(String(20), nullable=False)
    subject = Column(String(120), nullable=False)
    topic = Column(String(160), nullable=False)
    duration_minutes = Column(Integer, default=60)
    priority = Column(String(20), default="medium")
    completed = Column(Boolean, default=False)
    order_index = Column(Integer, default=0)

    student = relationship("Student", back_populates="study_plans")


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(120), nullable=False)
    message = Column(Text, nullable=False)
    category = Column(String(30), default="info")
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), default=utcnow)

    user = relationship("User", back_populates="notifications")


class Checkin(Base):
    __tablename__ = "checkins"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id", ondelete="CASCADE"), nullable=False)
    mood = Column(String(30), nullable=False)
    stress_score = Column(Integer, default=3)
    sleep_hours = Column(Float, default=7.0)
    answers = Column(JSON, default=dict)
    supportive_message = Column(Text, default="")
    wants_mentor_talk = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), default=utcnow)

    student = relationship("Student", back_populates="checkins")
