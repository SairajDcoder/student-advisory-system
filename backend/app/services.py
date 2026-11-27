"""
Business services for AdvisorAI:
- Recomputing ML predictions & career recommendations for a student
- Auto-generating personalized weekly Study Plans
- Generating supportive Wellbeing responses
- Context-aware LLM Chat Advisor (OpenAI / Gemini API + intelligent offline fallback)
"""
from datetime import datetime, timezone
from typing import Dict, List

import httpx
from sqlalchemy.orm import Session

from backend.app.config import (
    GEMINI_API_KEY,
    GROQ_API_KEY,
    GROQ_MODEL,
    OPENAI_API_KEY,
    OPENAI_MODEL,
)
from backend.app.models import (
    Checkin,
    Notification,
    Prediction,
    Recommendation,
    Student,
    StudyPlan,
    Subject,
)
from backend.ml.predictor import predict_student_performance
from backend.ml.recommender import recommend_10th_stream, recommend_careers

DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


def build_ml_profile(student: Student, db: Session) -> Dict:
    """Assemble student database fields into the ML feature dictionary."""
    skills_map = {s.name.lower(): s.level for s in student.skills}
    latest_checkin = (
        db.query(Checkin)
        .filter(Checkin.student_id == student.id)
        .order_by(Checkin.created_at.desc())
        .first()
    )
    stress_level = latest_checkin.stress_score if latest_checkin else 2

    # Use saved profile subject scores when available, falling back to recorded marks
    math_score = float(student.math_score) if student.math_score is not None else 70.0
    science_score = float(student.science_score) if student.science_score is not None else 65.0
    english_score = float(student.english_score) if student.english_score is not None else 72.0

    coding_interest = (
        float(student.programming_score)
        if student.programming_score is not None
        else skills_map.get("python", skills_map.get("coding", 60))
    )
    creativity_score = (
        float(student.creativity_score)
        if student.creativity_score is not None
        else skills_map.get("design", skills_map.get("creativity", 55))
    )
    communication_score = (
        float(student.communication_score)
        if student.communication_score is not None
        else skills_map.get("communication", 65)
    )
    projects_completed = (
        int(student.projects_completed)
        if student.projects_completed is not None
        else (2 if student.education_stage == "12th" else 1)
    )

    return {
        "education_stage": student.education_stage,
        "stream": student.stream,
        "attendance_pct": student.attendance_pct,
        "internal_marks_avg": student.internal_marks_avg,
        "assignment_score_avg": student.assignment_score_avg,
        "past_cgpa": student.current_cgpa,
        "study_hours_per_week": student.study_hours_per_week,
        "math_score": math_score,
        "science_score": science_score,
        "english_score": english_score,
        "coding_interest": coding_interest,
        "analytical_score": skills_map.get("analytical thinking", skills_map.get("problem solving", 72)),
        "creativity_score": creativity_score,
        "communication_score": communication_score,
        "projects_completed": projects_completed,
        "stress_level": stress_level,
    }


def refresh_student_ai(student: Student, db: Session) -> Prediction:
    """Recompute ML prediction + career recommendations and persist to DB."""
    profile = build_ml_profile(student, db)
    pred_res = predict_student_performance(profile)

    prediction = Prediction(
        student_id=student.id,
        predicted_cgpa=pred_res["predicted_cgpa"],
        pass_probability=pred_res["pass_probability"],
        risk_level=pred_res["risk_level"],
        risk_score=pred_res["risk_score"],
        top_reasons=pred_res["top_reasons"],
        ai_insights=pred_res["ai_insights"],
    )
    db.add(prediction)

    # Refresh recommendations
    db.query(Recommendation).filter(Recommendation.student_id == student.id).delete()
    skills_map = {s.name: s.level for s in student.skills}
    interests = [i.topic for i in student.interests]

    careers = recommend_careers(profile, skills_map, interests)
    for c in careers:
        db.add(
            Recommendation(
                student_id=student.id,
                rec_type="career",
                title=c["title"],
                match_pct=c["match_pct"],
                summary=c["summary"],
                required_skills=c["required_skills"],
                skill_gaps=c["skill_gaps"],
                suggested_courses=c["suggested_courses"],
            )
        )

    if student.education_stage == "10th":
        stream_rec = recommend_10th_stream(profile)
        db.add(
            Recommendation(
                student_id=student.id,
                rec_type="stream",
                title=stream_rec["title"],
                match_pct=stream_rec["match_pct"],
                summary=stream_rec["summary"],
                required_skills=["Core Concepts", "Regular Practice"],
                skill_gaps=[],
                suggested_courses=[],
            )
        )

    # Add attendance alert notification if below 75%
    if student.attendance_pct < 75:
        existing_alert = (
            db.query(Notification)
            .filter(
                Notification.user_id == student.user_id,
                Notification.title == "Attendance Watch Alert",
                Notification.is_read.is_(False),
            )
            .first()
        )
        if not existing_alert:
            db.add(
                Notification(
                    user_id=student.user_id,
                    title="Attendance Watch Alert",
                    message=f"Your attendance is {student.attendance_pct:.0f}%. Aim for 75%+ to protect exam eligibility.",
                    category="warning",
                )
            )

    db.commit()
    db.refresh(prediction)
    return prediction


def generate_study_plan(student: Student, db: Session) -> List[StudyPlan]:
    """Auto-generate a 7-day balanced weekly study plan emphasizing weak areas and upcoming exams."""
    db.query(StudyPlan).filter(StudyPlan.student_id == student.id).delete()

    subjects: List[Subject] = student.subjects
    if not subjects:
        fallback_names = (
            ["Mathematics", "Science", "English", "Computer Basics"]
            if student.education_stage == "10th"
            else ["Core Subject 1", "Core Subject 2", "Aptitude & Logic", "Communication"]
        )
        subjects = [
            Subject(student_id=student.id, code=f"SUB{idx+1}", name=nm, weak_area=(idx == 0))
            for idx, nm in enumerate(fallback_names)
        ]

    # Prioritize weak subjects and earlier exam dates
    ordered = sorted(subjects, key=lambda s: (not s.weak_area, s.exam_date))
    tasks_to_create: List[StudyPlan] = []

    task_templates = [
        ("Concept revision & key formulas", 60),
        ("Solve 15 practice problems", 75),
        ("Past board/mock paper questions", 60),
        ("Summary notes & flashcards", 45),
    ]

    idx = 0
    for day_idx, day in enumerate(DAYS):
        if day == "Sunday":
            tasks_to_create.append(
                StudyPlan(
                    student_id=student.id,
                    day_of_week=day,
                    subject="Weekly Review",
                    topic="Light recap of weak topics + plan next week",
                    duration_minutes=45,
                    priority="low",
                    completed=False,
                    order_index=0,
                )
            )
            continue

        # 2 focused blocks per weekday/Saturday
        for slot in range(2):
            subj = ordered[idx % len(ordered)]
            tpl_topic, mins = task_templates[(day_idx + slot) % len(task_templates)]
            priority = "high" if subj.weak_area else ("medium" if slot == 0 else "low")
            tasks_to_create.append(
                StudyPlan(
                    student_id=student.id,
                    day_of_week=day,
                    subject=subj.name,
                    topic=f"{tpl_topic} (Exam: {subj.exam_date})",
                    duration_minutes=mins + (15 if subj.weak_area else 0),
                    priority=priority,
                    completed=(day_idx == 0 and slot == 0),
                    order_index=slot,
                )
            )
            idx += 1

    db.add_all(tasks_to_create)
    db.commit()
    return db.query(StudyPlan).filter(StudyPlan.student_id == student.id).order_by(StudyPlan.id).all()


def build_wellbeing_support(mood: str, stress_score: int, sleep_hours: float, wants_mentor: bool) -> str:
    """Return warm, plain-language encouragement after a wellbeing check-in."""
    parts = []
    if mood in ("stressed", "overwhelmed") or stress_score >= 4:
        parts.append(
            "Thanks for checking in honestly. Feeling pressured around exams or stream choices is completely normal — take one small step at a time today."
        )
    elif mood == "okay":
        parts.append(
            "You're doing okay, and checking in helps you stay steady. A short 15-minute walk or break between study blocks can lift your energy."
        )
    else:
        parts.append(
            "Great to hear you're feeling positive! Keep this steady rhythm with regular breaks and good sleep."
        )

    if sleep_hours < 6.5:
        parts.append(
            f"You logged {sleep_hours:.1f} hrs of sleep — try aiming for 7-8 hours tonight because memory locks in while you sleep."
        )

    if wants_mentor:
        parts.append(
            "We've flagged your request so your mentor can reach out for a friendly 1-on-1 chat."
        )
    return " ".join(parts)


async def generate_advisor_reply(student: Student, user_message: str, db: Session) -> str:
    """
    Generate an AI Chat Advisor reply grounded in the student's real data.
    Uses OpenAI or Gemini API when keys are provided; otherwise uses a rich,
    context-aware local advisory engine so the chat always works cleanly.
    """
    latest_pred = (
        db.query(Prediction)
        .filter(Prediction.student_id == student.id)
        .order_by(Prediction.created_at.desc())
        .first()
    )
    recs = (
        db.query(Recommendation)
        .filter(Recommendation.student_id == student.id, Recommendation.rec_type == "career")
        .order_by(Recommendation.match_pct.desc())
        .all()
    )
    weak_subjects = [s.name for s in student.subjects if s.weak_area]
    top_career = recs[0].title if recs else "Data Analyst"
    top_match = recs[0].match_pct if recs else 84.0
    pred_cgpa = latest_pred.predicted_cgpa if latest_pred else student.current_cgpa
    risk_level = latest_pred.risk_level if latest_pred else "Low"
    first_name = student.user.full_name.split()[0]

    context_summary = (
        f"Student: {student.user.full_name} ({student.education_stage} pass-out, {student.stream}). "
        f"Current CGPA: {student.current_cgpa}/10, Predicted next CGPA: {pred_cgpa}/10, "
        f"Attendance: {student.attendance_pct}%, Risk: {risk_level}. "
        f"Weak subjects: {', '.join(weak_subjects) or 'None flagged'}. "
        f"Top career match: {top_career} ({top_match}%)."
    )

    system_prompt = (
        "You are AdvisorAI, a warm, encouraging academic and career advisor for 10th and 12th pass-out students. "
        "Speak in simple, clear, jargon-free language. Keep replies concise (3-5 bullet points or short paragraphs). "
        f"Student context: {context_summary}"
    )

    if GROQ_API_KEY:
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                resp = await client.post(
                    "https://api.groq.com/openai/v1/chat/completions",
                    headers={"Authorization": f"Bearer {GROQ_API_KEY}"},
                    json={
                        "model": GROQ_MODEL,
                        "messages": [
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": user_message},
                        ],
                        "temperature": 0.6,
                        "max_tokens": 600,
                    },
                )
                if resp.status_code == 200:
                    data = resp.json()
                    return data["choices"][0]["message"]["content"].strip()
        except Exception:
            pass

    if OPENAI_API_KEY:
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                resp = await client.post(
                    "https://api.openai.com/v1/chat/completions",
                    headers={"Authorization": f"Bearer {OPENAI_API_KEY}"},
                    json={
                        "model": OPENAI_MODEL,
                        "messages": [
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": user_message},
                        ],
                        "temperature": 0.6,
                        "max_tokens": 350,
                    },
                )
                if resp.status_code == 200:
                    data = resp.json()
                    return data["choices"][0]["message"]["content"].strip()
        except Exception:
            pass

    if GEMINI_API_KEY:
        try:
            url = (
                "https://generativelanguage.googleapis.com/v1beta/models/"
                f"gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}"
            )
            async with httpx.AsyncClient(timeout=15.0) as client:
                resp = await client.post(
                    url,
                    json={
                        "contents": [
                            {"parts": [{"text": f"{system_prompt}\n\nStudent question: {user_message}"}]}
                        ]
                    },
                )
                if resp.status_code == 200:
                    data = resp.json()
                    return data["candidates"][0]["content"]["parts"][0]["text"].strip()
        except Exception:
            pass

    # Context-aware offline advisor fallback
    q = user_message.lower()
    if "cgpa" in q or "score" in q or "marks" in q or "improve" in q:
        weak_line = (
            f"Focus first on **{', '.join(weak_subjects)}**, since lifting weak subjects gives the fastest jump."
            if weak_subjects
            else "Keep polishing your core subjects with weekly timed practice."
        )
        return (
            f"Hi {first_name}! Based on your profile (predicted CGPA **{pred_cgpa}/10**, attendance **{student.attendance_pct:.0f}%**), here are 3 easy wins:\n\n"
            f"1. **Protect attendance:** Aim for **80%+** in every subject so you never miss internal marks.\n"
            f"2. **Targeted revision:** {weak_line}\n"
            f"3. **Weekly rhythm:** Follow two 60-minute focused blocks per day in your Study Planner and finish assignments 2 days early."
        )

    if "stream" in q or "10th" in q or "12th" in q or "career" in q or "elective" in q or "degree" in q:
        all_recs = ", ".join(f"**{r.title}** ({r.match_pct:.0f}%)" for r in recs[:3]) or "**Data Analyst**"
        stage_tip = (
            "Since you just completed **10th**, focus on picking a Class 11–12 stream that matches your strengths without overloading yourself."
            if student.education_stage == "10th"
            else "Since you just completed **12th**, pick a degree + 1 practical skill track you can build projects in during your first semester."
        )
        return (
            f"Great question, {first_name}! {stage_tip}\n\n"
            f"Your top AI matches right now are: {all_recs}.\n\n"
            f"• Start with **{top_career}** — open **Career Guidance** to see the exact skill gaps and beginner courses recommended for you.\n"
            f"• If you're choosing electives, pick subjects that strengthen analytical problem-solving and hands-on projects."
        )

    if "stress" in q or "anxious" in q or "tired" in q or "overwhelm" in q or "wellbeing" in q:
        return (
            f"I hear you, {first_name}. Transitioning after **{student.education_stage}** can feel overwhelming, and it's okay to pause.\n\n"
            "• Take a 10-minute screen-free break and drink some water.\n"
            "• Pick just **one** 25-minute task from today's Study Planner instead of worrying about the whole week.\n"
            "• You can also log a quick **Wellbeing Check-in** or tap **Talk to a Mentor** anytime — your mentor is here to support you."
        )

    if "plan" in q or "study" in q or "schedule" in q or "exam" in q:
        return (
            f"Your personalized 7-day Study Plan prioritizes **{', '.join(weak_subjects) or 'your upcoming exams'}** across balanced 60–75 minute blocks.\n\n"
            "Tip: Try dragging harder topics to days when your energy is highest, and keep Sunday light for weekly recap!"
        )

    return (
        f"Hi {first_name}! Here's a quick snapshot from your AdvisorAI profile:\n\n"
        f"• **Academic Forecast:** {pred_cgpa}/10 CGPA ({risk_level} Risk) with {student.attendance_pct:.0f}% attendance.\n"
        f"• **Top Career Match:** {top_career} ({top_match:.0f}% match).\n\n"
        "Ask me anything like *\"How can I improve my CGPA?\"*, *\"Which stream/career suits me after 10th/12th?\"*, or *\"Make me an exam study tip\"*!"
    )
