-- AdvisorAI Supabase PostgreSQL Schema (14 Core Entities)
-- Uses `advisorai_*` table names so they never collide with any existing
-- `public.users` (UUID) or other project tables in your Supabase database.

CREATE TABLE IF NOT EXISTS advisorai_users (
  id SERIAL PRIMARY KEY,
  supabase_uid VARCHAR(64) UNIQUE,
  email VARCHAR(255) UNIQUE NOT NULL,
  full_name VARCHAR(120) NOT NULL,
  password_hash VARCHAR(255),
  role VARCHAR(30) NOT NULL DEFAULT 'student',
  department VARCHAR(80) DEFAULT '12th Pass-Out (Science PCM)',
  is_active BOOLEAN DEFAULT TRUE,
  theme_preference VARCHAR(20) DEFAULT 'light',
  language_preference VARCHAR(20) DEFAULT 'en',
  notifications_enabled BOOLEAN DEFAULT TRUE,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS advisorai_mentors (
  id SERIAL PRIMARY KEY,
  user_id INTEGER UNIQUE NOT NULL REFERENCES advisorai_users(id) ON DELETE CASCADE,
  specialization VARCHAR(120) DEFAULT '10th/12th Stream & Career Counseling',
  department VARCHAR(80) DEFAULT 'Academic Advisory',
  bio TEXT DEFAULT '',
  office_hours VARCHAR(100) DEFAULT 'Mon-Fri, 4:00 PM - 6:00 PM'
);

CREATE TABLE IF NOT EXISTS advisorai_students (
  id SERIAL PRIMARY KEY,
  user_id INTEGER UNIQUE NOT NULL REFERENCES advisorai_users(id) ON DELETE CASCADE,
  mentor_id INTEGER REFERENCES advisorai_mentors(id) ON DELETE SET NULL,
  education_stage VARCHAR(20) DEFAULT '12th',
  board_name VARCHAR(40) DEFAULT 'CBSE',
  stream VARCHAR(60) DEFAULT 'Science (PCM)',
  department VARCHAR(80) DEFAULT '12th Pass-Out (PCM)',
  current_semester INTEGER DEFAULT 1,
  board_percentage DOUBLE PRECISION DEFAULT 75.0,
  current_cgpa DOUBLE PRECISION DEFAULT 7.5,
  attendance_pct DOUBLE PRECISION DEFAULT 80.0,
  internal_marks_avg DOUBLE PRECISION DEFAULT 75.0,
  assignment_score_avg DOUBLE PRECISION DEFAULT 75.0,
  study_hours_per_week DOUBLE PRECISION DEFAULT 18.0,
  previous_grades_json JSONB DEFAULT '[]'::jsonb,
  goals TEXT DEFAULT '',
  onboarding_completed BOOLEAN DEFAULT FALSE,
  mentor_remarks TEXT DEFAULT '',
  next_meeting_at VARCHAR(80) DEFAULT '',
  upcoming_deadlines_count INTEGER DEFAULT 2
);

CREATE TABLE IF NOT EXISTS advisorai_subjects (
  id SERIAL PRIMARY KEY,
  student_id INTEGER NOT NULL REFERENCES advisorai_students(id) ON DELETE CASCADE,
  code VARCHAR(30) NOT NULL,
  name VARCHAR(120) NOT NULL,
  credits INTEGER DEFAULT 4,
  exam_date VARCHAR(30) DEFAULT '2026-12-18',
  weak_area BOOLEAN DEFAULT FALSE
);

CREATE TABLE IF NOT EXISTS advisorai_marks (
  id SERIAL PRIMARY KEY,
  student_id INTEGER NOT NULL REFERENCES advisorai_students(id) ON DELETE CASCADE,
  subject_id INTEGER NOT NULL REFERENCES advisorai_subjects(id) ON DELETE CASCADE,
  internal_score DOUBLE PRECISION DEFAULT 75.0,
  assignment_score DOUBLE PRECISION DEFAULT 75.0,
  exam_score DOUBLE PRECISION DEFAULT 75.0,
  max_score DOUBLE PRECISION DEFAULT 100.0,
  semester INTEGER DEFAULT 1
);

CREATE TABLE IF NOT EXISTS advisorai_attendance (
  id SERIAL PRIMARY KEY,
  student_id INTEGER NOT NULL REFERENCES advisorai_students(id) ON DELETE CASCADE,
  subject_name VARCHAR(120) NOT NULL,
  classes_attended INTEGER DEFAULT 24,
  total_classes INTEGER DEFAULT 30,
  percentage DOUBLE PRECISION DEFAULT 80.0,
  recorded_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS advisorai_skills (
  id SERIAL PRIMARY KEY,
  student_id INTEGER NOT NULL REFERENCES advisorai_students(id) ON DELETE CASCADE,
  name VARCHAR(80) NOT NULL,
  level INTEGER DEFAULT 60
);

CREATE TABLE IF NOT EXISTS advisorai_interests (
  id SERIAL PRIMARY KEY,
  student_id INTEGER NOT NULL REFERENCES advisorai_students(id) ON DELETE CASCADE,
  topic VARCHAR(80) NOT NULL,
  weight INTEGER DEFAULT 80
);

CREATE TABLE IF NOT EXISTS advisorai_predictions (
  id SERIAL PRIMARY KEY,
  student_id INTEGER NOT NULL REFERENCES advisorai_students(id) ON DELETE CASCADE,
  predicted_cgpa DOUBLE PRECISION NOT NULL,
  pass_probability DOUBLE PRECISION NOT NULL,
  risk_level VARCHAR(20) NOT NULL,
  risk_score DOUBLE PRECISION NOT NULL,
  top_reasons JSONB DEFAULT '[]'::jsonb,
  ai_insights JSONB DEFAULT '[]'::jsonb,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS advisorai_recommendations (
  id SERIAL PRIMARY KEY,
  student_id INTEGER NOT NULL REFERENCES advisorai_students(id) ON DELETE CASCADE,
  rec_type VARCHAR(30) NOT NULL,
  title VARCHAR(120) NOT NULL,
  match_pct DOUBLE PRECISION NOT NULL,
  summary TEXT NOT NULL,
  required_skills JSONB DEFAULT '[]'::jsonb,
  skill_gaps JSONB DEFAULT '[]'::jsonb,
  suggested_courses JSONB DEFAULT '[]'::jsonb,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS advisorai_chat_messages (
  id SERIAL PRIMARY KEY,
  student_id INTEGER NOT NULL REFERENCES advisorai_students(id) ON DELETE CASCADE,
  sender VARCHAR(20) NOT NULL,
  message TEXT NOT NULL,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS advisorai_study_plans (
  id SERIAL PRIMARY KEY,
  student_id INTEGER NOT NULL REFERENCES advisorai_students(id) ON DELETE CASCADE,
  day_of_week VARCHAR(20) NOT NULL,
  subject VARCHAR(120) NOT NULL,
  topic VARCHAR(160) NOT NULL,
  duration_minutes INTEGER DEFAULT 60,
  priority VARCHAR(20) DEFAULT 'medium',
  completed BOOLEAN DEFAULT FALSE,
  order_index INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS advisorai_notifications (
  id SERIAL PRIMARY KEY,
  user_id INTEGER NOT NULL REFERENCES advisorai_users(id) ON DELETE CASCADE,
  title VARCHAR(120) NOT NULL,
  message TEXT NOT NULL,
  category VARCHAR(30) DEFAULT 'info',
  is_read BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS advisorai_checkins (
  id SERIAL PRIMARY KEY,
  student_id INTEGER NOT NULL REFERENCES advisorai_students(id) ON DELETE CASCADE,
  mood VARCHAR(30) NOT NULL,
  stress_score INTEGER DEFAULT 3,
  sleep_hours DOUBLE PRECISION DEFAULT 7.0,
  answers JSONB DEFAULT '{}'::jsonb,
  supportive_message TEXT DEFAULT '',
  wants_mentor_talk BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMPTZ DEFAULT NOW()
);
