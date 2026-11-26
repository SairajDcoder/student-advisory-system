"""
Supabase JWT Verification & User Sync + RBAC Dependencies.
Verifies real Supabase Auth tokens via JWKS (ES256/RS256) or Supabase Auth API.
"""
from typing import Dict, Iterable, Optional

import bcrypt
import httpx
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jwt import PyJWKClient
from sqlalchemy.orm import Session

from backend.app.config import SUPABASE_ANON_KEY, SUPABASE_JWT_SECRET, SUPABASE_URL
from backend.app.database import get_db
from backend.app.models import (
    Attendance,
    ChatMessage,
    Mark,
    Mentor,
    Student,
    Subject,
    User,
)
from backend.app.services import generate_study_plan, refresh_student_ai

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/me")
_jwks_client: Optional[PyJWKClient] = None


def _get_jwks_client() -> Optional[PyJWKClient]:
    global _jwks_client
    if not SUPABASE_URL:
        return None
    if _jwks_client is None:
        _jwks_client = PyJWKClient(f"{SUPABASE_URL}/auth/v1/.well-known/jwks.json")
    return _jwks_client


def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")


def verify_supabase_token(token: str) -> Dict:
    """
    Validate a Supabase access_token and return claims containing:
    sub (supabase_uid), email, user_metadata.
    """
    if not SUPABASE_URL:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="SUPABASE_URL is not configured on the backend.",
        )

    # 1. Try JWKS asymmetric verification (ES256 / RS256)
    try:
        header = jwt.get_unverified_header(token)
        alg = header.get("alg", "ES256")
        if alg in ("ES256", "RS256"):
            jwks_client = _get_jwks_client()
            if jwks_client:
                signing_key = jwks_client.get_signing_key_from_jwt(token)
                return jwt.decode(
                    token,
                    signing_key.key,
                    algorithms=[alg],
                    audience="authenticated",
                )
        elif alg == "HS256" and SUPABASE_JWT_SECRET:
            return jwt.decode(
                token,
                SUPABASE_JWT_SECRET,
                algorithms=["HS256"],
                audience="authenticated",
            )
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Your session has expired. Please sign in again.",
        )
    except Exception:
        # Fall back to Supabase /auth/v1/user check below
        pass

    # 2. Fallback: verify directly with Supabase Auth API
    if not SUPABASE_ANON_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token.",
        )
    try:
        resp = httpx.get(
            f"{SUPABASE_URL}/auth/v1/user",
            headers={
                "apikey": SUPABASE_ANON_KEY,
                "Authorization": f"Bearer {token}",
            },
            timeout=10.0,
        )
        if resp.status_code == 200:
            data = resp.json()
            return {
                "sub": data["id"],
                "email": data.get("email", ""),
                "user_metadata": data.get("user_metadata") or {},
            }
    except Exception:
        pass

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate Supabase credentials. Please sign in again.",
        headers={"WWW-Authenticate": "Bearer"},
    )


def _default_subjects_for_stage(stage: str, stream: str):
    st_lower = stream.lower()
    if stage == "10th":
        return [
            ("MAT10", "Mathematics", False),
            ("SCI10", "Science", False),
            ("ENG10", "English", False),
            ("SOC10", "Social Studies / Aptitude", False),
        ]
    if "commerce" in st_lower:
        return [
            ("ACC12", "Accountancy", False),
            ("BST12", "Business Studies", False),
            ("ECO12", "Economics", False),
            ("ENG12", "English", False),
        ]
    if "pcb" in st_lower:
        return [
            ("BIO12", "Biology", False),
            ("CHE12", "Chemistry", False),
            ("PHY12", "Physics", False),
            ("ENG12", "English", False),
        ]
    if "art" in st_lower:
        return [
            ("HIS12", "History / Humanities", False),
            ("POL12", "Political Science / Media", False),
            ("PSY12", "Psychology / Design", False),
            ("ENG12", "English", False),
        ]
    return [
        ("MAT12", "Mathematics", False),
        ("PHY12", "Physics", False),
        ("CS12", "Computer Science / Tech", False),
        ("ENG12", "English", False),
    ]


def provision_or_sync_user(claims: Dict, db: Session) -> User:
    """Ensure the authenticated Supabase user exists in our DB with the right role profile."""
    uid = str(claims.get("sub", ""))
    email = (claims.get("email") or "").lower()
    meta = claims.get("user_metadata") or {}

    user = None
    if uid:
        user = db.query(User).filter(User.supabase_uid == uid).first()
    if not user and email:
        user = db.query(User).filter(User.email == email).first()

    if user:
        if uid and not user.supabase_uid:
            user.supabase_uid = uid
            db.commit()
        return user

    role = meta.get("role", "student")
    if role not in ("student", "mentor", "admin"):
        role = "student"

    full_name = (
        meta.get("full_name")
        or meta.get("name")
        or (email.split("@")[0].replace(".", " ").title() if email else "Student")
    )
    education_stage = meta.get("education_stage", "12th")
    stream = meta.get("stream", "Science (PCM)")
    department = meta.get("department") or f"{education_stage} Pass-Out ({stream})"

    user = User(
        supabase_uid=uid or None,
        email=email or f"{uid}@supabase.local",
        full_name=full_name,
        role=role,
        department=department,
        is_active=True,
    )
    db.add(user)
    db.flush()

    if role == "student":
        mentor = db.query(Mentor).first()
        student = Student(
            user_id=user.id,
            mentor_id=mentor.id if mentor else None,
            education_stage=education_stage,
            stream=stream,
            department=department,
            previous_grades_json=[],
            onboarding_completed=False,
        )
        db.add(student)
        db.flush()

        for code, name, weak in _default_subjects_for_stage(education_stage, stream):
            subj = Subject(student_id=student.id, code=code, name=name, weak_area=weak)
            db.add(subj)
            db.flush()
            db.add(Mark(student_id=student.id, subject_id=subj.id))
            db.add(Attendance(student_id=student.id, subject_name=name))

        db.add(
            ChatMessage(
                student_id=student.id,
                sender="assistant",
                message=(
                    f"Hi {full_name.split()[0]}! 👋 I'm AdvisorAI. "
                    f"Complete your quick 10th/12th profile setup or ask me any question about streams, marks, or careers."
                ),
            )
        )
        db.flush()
        refresh_student_ai(student, db)
        generate_study_plan(student, db)
    elif role == "mentor":
        db.add(Mentor(user_id=user.id, department=department))

    db.commit()
    db.refresh(user)
    return user


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    claims = verify_supabase_token(token)
    user = provision_or_sync_user(claims, db)
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is deactivated. Contact Admin.",
        )
    return user


def require_roles(allowed_roles: Iterable[str]):
    allowed = set(allowed_roles)

    def _checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in allowed:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to access this resource.",
            )
        return current_user

    return _checker
