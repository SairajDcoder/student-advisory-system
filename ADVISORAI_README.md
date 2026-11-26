# AdvisorAI – AI/ML Based Student Advisory System (10th & 12th Pass-Out Edition)

A full-stack **FastAPI + React/TypeScript + XGBoost + SHAP** advisory platform designed for **students who have just completed Class 10th or Class 12th**, as well as **Mentors/Faculty** and **Admins**.

---

## Architecture & Folder Structure

```
student-advisory-system/
├── backend/
│   ├── app/
│   │   ├── config.py        # Env config (SQLite default, PostgreSQL via DATABASE_URL, LLM keys)
│   │   ├── database.py      # SQLAlchemy engine & session dependency
│   │   ├── models.py        # 14 ORM tables (Users, Students, Mentors, Subjects, Marks, Attendance,
│   │   │                    #   Skills, Interests, Predictions, Recommendations, ChatMessages,
│   │   │                    #   StudyPlans, Notifications, Checkins)
│   │   ├── schemas.py       # Pydantic v2 request/response contracts
│   │   ├── auth.py          # Bcrypt password hashing, JWT tokens, RBAC dependencies
│   │   ├── services.py      # ML refresh, study plan builder, wellbeing coach, LLM chat advisor
│   │   ├── seed.py          # 10th & 12th pass-out student, mentor, and admin seed records
│   │   └── main.py          # FastAPI REST API server
│   ├── ml/
│   │   ├── train_models.py  # Sample dataset generator + XGBoost CGPA & Risk training pipeline
│   │   ├── predictor.py     # Prediction inference + SHAP plain-English explanations
│   │   └── recommender.py   # Content-based 10th stream, 12th career, skill-gap & course matcher
│   └── requirements.txt
└── frontend/
    ├── src/
    │   ├── components/
    │   │   ├── AppShell.tsx         # Desktop sidebar + top bar + mobile bottom bar + alerts
    │   │   ├── OnboardingWizard.tsx # 3-step welcome wizard with Skip option
    │   │   └── ui.tsx               # Accessible cards, risk badges, skeleton loaders, error banner
    │   ├── context/AuthContext.tsx  # JWT session + Light/Dark theme persistence
    │   ├── lib/api.ts               # Fetch wrapper with Bearer token handling
    │   ├── pages/
    │   │   ├── LoginPage.tsx        # Screen A: Login / Register + role switch + Google Demo
    │   │   ├── StudentDashboard.tsx # Screen B: Greeting, 4 KPIs, trend chart, 3 AI insights
    │   │   ├── PerformancePage.tsx  # Screen C: CGPA gauge, subject chart, SHAP explanations, simulator
    │   │   ├── CareerGuidancePage.tsx # Screen D: 10th stream match + top 3 career & skill-gap cards
    │   │   ├── ChatAdvisorPage.tsx  # Screen E: WhatsApp-style AI chat, chips, voice input
    │   │   ├── StudyPlannerPage.tsx # Screen F: 7-day calendar, drag-and-drop tasks, progress ring
    │   │   ├── WellbeingPage.tsx    # Screen G: Emoji mood check-in, 5 questions, talk to mentor
    │   │   ├── MentorDashboard.tsx  # Screen H: Student risk table, detail drawer, remarks, meeting
    │   │   ├── AdminDashboard.tsx   # Screen I: Users, department analytics, CSV upload & retrain
    │   │   └── SettingsPage.tsx     # Screen J: Profile, 10th/12th stage, theme, language, alerts
    │   └── types/index.ts
    └── package.json
```

---

## Sample Dataset Columns (`backend/ml/train_models.py`)

`education_stage`, `stream`, `attendance_pct`, `internal_marks_avg`, `assignment_score_avg`, `past_cgpa`, `study_hours_per_week`, `math_score`, `science_score`, `english_score`, `coding_interest`, `analytical_score`, `creativity_score`, `communication_score`, `projects_completed`, `stress_level`, `next_cgpa`, `risk_level`, `pass_status`.

---

## How to Run Locally

### 1. Train ML Models & Start FastAPI Backend
```powershell
py -m pip install -r backend/requirements.txt
py -m backend.ml.train_models
py -m uvicorn backend.app.main:app --reload --port 8000
```
*(Optional env vars: `DATABASE_URL` for PostgreSQL, `OPENAI_API_KEY` or `GEMINI_API_KEY` for external LLM chat; works out-of-the-box with SQLite + built-in context-aware AI fallback.)*

### 2. Start React + TypeScript Frontend
```powershell
cd frontend
npm.cmd install
npm.cmd run dev
```
Open **http://localhost:5173** in your browser.

---

## Demo Accounts
| Role | Email | Password |
|---|---|---|
| Student (12th Pass-Out) | `aman@advisorai.edu` | `aman123` |
| Student (10th Pass-Out) | `priya@advisorai.edu` | `priya123` |
| Student (At-Risk Watch) | `rohan@advisorai.edu` | `rohan123` |
| Mentor / Faculty | `mentor@advisorai.edu` | `mentor123` |
| Admin | `admin@advisorai.edu` | `admin123` |

---

## Future Improvements
1. Connect real CBSE/ICSE/State Board marksheet OCR (PDF/image upload) during onboarding.
2. Add scholarship & entrance exam deadline feeds (JEE, NEET, CUET, CLAT, Polytechnic dates).
3. Deploy with managed PostgreSQL, Redis rate-limiting, and OAuth2 Google Client ID verification.
