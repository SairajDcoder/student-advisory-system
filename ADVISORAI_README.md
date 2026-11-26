# AdvisorAI – AI/ML Based Student Advisory System (10th & 12th Pass-Out Edition)

A full-stack **FastAPI + React/TypeScript + Supabase Auth + XGBoost + SHAP** advisory platform designed for **students who have just completed Class 10th or Class 12th**, as well as **Mentors/Faculty** and **Admins**.

---

## Architecture & Configuration (No Hardcoded Secrets)

* **Authentication:** Real **Supabase Auth** (`@supabase/supabase-js` on frontend, `ES256`/`RS256` JWKS + Supabase Auth API verification on FastAPI backend).
* **Database:** Uses SQLAlchemy ORM (`supabase/schema.sql` provided for Supabase PostgreSQL via `DATABASE_URL`; falls back to local `advisorai.db` SQLite if `DATABASE_URL` is not set).
* **Environment files:**
  * Frontend: `frontend/.env` (`NEXT_PUBLIC_SUPABASE_URL`, `NEXT_PUBLIC_SUPABASE_ANON_KEY`, `NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY` — see `frontend/.env.example`)
  * Backend: `backend/.env` (`SUPABASE_URL`, `SUPABASE_ANON_KEY`, optional `DATABASE_URL`, `OPENAI_API_KEY`, `GEMINI_API_KEY` — see `backend/.env.example`)

---

## How to Run Locally

### 1. (Optional) Connect Supabase PostgreSQL
1. Open your Supabase Dashboard → **SQL Editor** and run `supabase/schema.sql`.
2. Copy your Postgres connection string into `backend/.env` as `DATABASE_URL`.
3. Enable **Google** (or **GitHub**) OAuth under **Authentication → Providers** in Supabase Dashboard if using OAuth buttons.

### 2. Start FastAPI Backend
```powershell
py -m pip install -r backend/requirements.txt
py -m backend.ml.train_models
py -m uvicorn backend.app.main:app --reload --port 8000
```

### 3. Start React + TypeScript Frontend
```powershell
cd frontend
npm.cmd install
npm.cmd run dev
```
Open **http://localhost:5173**, create an account (Student 10th/12th, Mentor, or Admin) via **Supabase Auth**, and complete the 3-step onboarding wizard.
