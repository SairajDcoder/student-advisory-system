"""SQLAlchemy database engine and session management."""
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import declarative_base, sessionmaker

from backend.app.config import DATABASE_URL

connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(DATABASE_URL, connect_args=connect_args, future=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, future=True)
Base = declarative_base()

_STUDENT_MIGRATION_COLUMNS = {
    "previous_gpa": ("FLOAT DEFAULT 3.2", "DOUBLE PRECISION DEFAULT 3.2"),
    "math_score": ("FLOAT DEFAULT 70.0", "DOUBLE PRECISION DEFAULT 70.0"),
    "science_score": ("FLOAT DEFAULT 65.0", "DOUBLE PRECISION DEFAULT 65.0"),
    "english_score": ("FLOAT DEFAULT 72.0", "DOUBLE PRECISION DEFAULT 72.0"),
    "programming_score": ("FLOAT DEFAULT 60.0", "DOUBLE PRECISION DEFAULT 60.0"),
    "creativity_score": ("FLOAT DEFAULT 55.0", "DOUBLE PRECISION DEFAULT 55.0"),
    "communication_score": ("FLOAT DEFAULT 65.0", "DOUBLE PRECISION DEFAULT 65.0"),
    "leadership_score": ("FLOAT DEFAULT 50.0", "DOUBLE PRECISION DEFAULT 50.0"),
    "extracurricular_activities": ("INTEGER DEFAULT 2", "INTEGER DEFAULT 2"),
    "internship_experience": ("INTEGER DEFAULT 0", "INTEGER DEFAULT 0"),
    "projects_completed": ("INTEGER DEFAULT 3", "INTEGER DEFAULT 3"),
    "gender": ("VARCHAR(20) DEFAULT 'Male'", "VARCHAR(20) DEFAULT 'Male'"),
    "parental_education": ("VARCHAR(40) DEFAULT 'High School'", "VARCHAR(40) DEFAULT 'High School'"),
    "part_time_job": ("INTEGER DEFAULT 0", "INTEGER DEFAULT 0"),
}


def ensure_schema_columns():
    """Safely add newly introduced columns to existing SQLite or Postgres tables."""
    inspector = inspect(engine)
    if "advisorai_students" not in inspector.get_table_names():
        return
    existing = {col["name"] for col in inspector.get_columns("advisorai_students")}
    is_sqlite = DATABASE_URL.startswith("sqlite")
    with engine.begin() as conn:
        for col_name, (sqlite_def, pg_def) in _STUDENT_MIGRATION_COLUMNS.items():
            if col_name not in existing:
                col_def = sqlite_def if is_sqlite else pg_def
                conn.execute(text(f"ALTER TABLE advisorai_students ADD COLUMN {col_name} {col_def}"))


def get_db():
    """FastAPI dependency yielding a scoped DB session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
