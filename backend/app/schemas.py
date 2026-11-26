"""Pydantic request and response schemas for AdvisorAI."""
from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class AuthSyncRequest(BaseModel):
    full_name: Optional[str] = None
    role: Optional[str] = None
    education_stage: Optional[str] = None
    stream: Optional[str] = None


class OnboardingRequest(BaseModel):
    education_stage: str = "12th"
    board_name: str = "CBSE"
    stream: str = "Science (PCM)"
    board_percentage: float = Field(default=80.0, ge=30, le=100)
    attendance_pct: float = Field(default=82.0, ge=20, le=100)
    internal_marks_avg: float = Field(default=76.0, ge=20, le=100)
    assignment_score_avg: float = Field(default=78.0, ge=20, le=100)
    study_hours_per_week: float = Field(default=18.0, ge=1, le=70)
    interests: List[str] = []
    skills: Dict[str, int] = {}
    goals: str = ""
    skip: bool = False


class PredictionSimulateRequest(BaseModel):
    attendance_pct: float = Field(..., ge=0, le=100)
    internal_marks_avg: float = Field(..., ge=0, le=100)
    assignment_score_avg: float = Field(..., ge=0, le=100)
    past_cgpa: float = Field(..., ge=0, le=10)
    study_hours_per_week: float = Field(..., ge=0, le=70)


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000)


class StudyTaskUpdate(BaseModel):
    completed: Optional[bool] = None
    day_of_week: Optional[str] = None
    order_index: Optional[int] = None


class CheckinRequest(BaseModel):
    mood: str
    stress_score: int = Field(..., ge=1, le=5)
    sleep_hours: float = Field(..., ge=2, le=14)
    answers: Dict[str, str] = {}
    wants_mentor_talk: bool = False


class MentorRemarkRequest(BaseModel):
    remarks: str = Field(..., min_length=1, max_length=2000)
    next_meeting_at: Optional[str] = None


class ProfileUpdateRequest(BaseModel):
    full_name: Optional[str] = None
    department: Optional[str] = None
    education_stage: Optional[str] = None
    stream: Optional[str] = None
    attendance_pct: Optional[float] = Field(default=None, ge=0, le=100)
    internal_marks_avg: Optional[float] = Field(default=None, ge=0, le=100)
    study_hours_per_week: Optional[float] = Field(default=None, ge=0, le=70)
    goals: Optional[str] = None
    theme_preference: Optional[str] = None
    language_preference: Optional[str] = None
    notifications_enabled: Optional[bool] = None


class AdminUserCreateRequest(BaseModel):
    full_name: str
    email: str
    password: str = Field(..., min_length=6)
    role: str = "student"
    department: str = "12th Pass-Out (PCM)"


class AdminUserToggleRequest(BaseModel):
    is_active: Optional[bool] = None
    role: Optional[str] = None
