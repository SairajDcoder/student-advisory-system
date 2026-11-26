"""
Inference + Explainable AI (SHAP) module for AdvisorAI.
Explains every CGPA and risk prediction in plain, friendly student language.
"""
import json
from typing import Dict, List

import joblib
import numpy as np
import pandas as pd
import shap

from backend.ml.train_models import (
    CATEGORICAL_FEATURES,
    CGPA_MODEL_PATH,
    METRICS_PATH,
    NUMERIC_FEATURES,
    RISK_ENCODER_PATH,
    RISK_MODEL_PATH,
    train_and_save_models,
)

FRIENDLY_NAMES = {
    "attendance_pct": "Class Attendance",
    "internal_marks_avg": "Internal Test Marks",
    "assignment_score_avg": "Assignments & Homework",
    "past_cgpa": "Previous Grades",
    "study_hours_per_week": "Weekly Study Hours",
    "math_score": "Mathematics Score",
    "science_score": "Science Score",
    "english_score": "English & Communication",
    "coding_interest": "Technical / Coding Practice",
    "analytical_score": "Analytical Reasoning",
    "creativity_score": "Creative Thinking",
    "communication_score": "Presentation & Communication",
    "projects_completed": "Hands-on Projects",
    "stress_level": "Stress Load",
}

_CACHE = {}


def ensure_models_loaded():
    """Load trained models into memory, training them automatically on first run."""
    if not (CGPA_MODEL_PATH.exists() and RISK_MODEL_PATH.exists() and RISK_ENCODER_PATH.exists()):
        train_and_save_models()

    if "cgpa" not in _CACHE:
        _CACHE["cgpa"] = joblib.load(CGPA_MODEL_PATH)
        _CACHE["risk"] = joblib.load(RISK_MODEL_PATH)
        _CACHE["encoder"] = joblib.load(RISK_ENCODER_PATH)
        _CACHE["explainer"] = shap.TreeExplainer(_CACHE["cgpa"].named_steps["model"])
    return _CACHE["cgpa"], _CACHE["risk"], _CACHE["encoder"], _CACHE["explainer"]


def reload_models():
    """Clear cached models after retraining."""
    _CACHE.clear()
    return ensure_models_loaded()


def get_model_metrics() -> Dict:
    ensure_models_loaded()
    if METRICS_PATH.exists():
        return json.loads(METRICS_PATH.read_text(encoding="utf-8"))
    return {}


def _plain_reason(feature: str, value: float, shap_val: float) -> str:
    """Turn a numeric feature + SHAP contribution into plain student-friendly language."""
    if feature == "attendance_pct":
        if value < 70:
            return f"Attendance is {value:.0f}% (below 75%), which pulls your score down."
        if value < 78:
            return f"Attendance is {value:.0f}% — reaching 85% will give a clear boost."
        return f"Strong attendance ({value:.0f}%) is keeping you safely on track."
    if feature == "internal_marks_avg":
        if value < 60:
            return f"Internal test average ({value:.0f}%) is low; revising weak chapters helps most."
        return f"Solid internal test marks ({value:.0f}%) strongly support your target grade."
    if feature == "assignment_score_avg":
        if value < 65:
            return f"Assignment scores ({value:.0f}%) are below target; timely submissions add easy marks."
        return f"Consistent assignment score ({value:.0f}%) is boosting your stability."
    if feature == "past_cgpa":
        if value < 6.5:
            return f"Past grade baseline ({value:.1f}/10) means steady weekly practice is key."
        return f"Strong past academic record ({value:.1f}/10) gives you a healthy head start."
    if feature == "study_hours_per_week":
        if value < 12:
            return f"Only {value:.0f} study hrs/week logged — adding 4-5 focused hours can lift CGPA."
        return f"{value:.0f} study hours/week shows steady preparation."
    if feature == "stress_level":
        if value >= 4:
            return "High stress level may affect exam focus; shorter daily blocks and rest will help."
        return "Balanced stress level is helping you retain concepts better."

    label = FRIENDLY_NAMES.get(feature, feature.replace("_", " ").title())
    direction = "helping" if shap_val >= 0 else "holding back"
    return f"{label} ({value:.0f}) is {direction} your overall forecast."


def predict_student_performance(profile: Dict) -> Dict:
    """Predict next CGPA, pass probability, risk level, and plain-English SHAP reasons."""
    cgpa_pipe, risk_pipe, risk_encoder, explainer = ensure_models_loaded()

    row = {
        "education_stage": profile.get("education_stage", "12th"),
        "stream": profile.get("stream", "Science (PCM)"),
        "attendance_pct": float(profile.get("attendance_pct", 80.0)),
        "internal_marks_avg": float(profile.get("internal_marks_avg", 75.0)),
        "assignment_score_avg": float(profile.get("assignment_score_avg", 78.0)),
        "past_cgpa": float(profile.get("past_cgpa", 7.8)),
        "study_hours_per_week": float(profile.get("study_hours_per_week", 20.0)),
        "math_score": float(profile.get("math_score", 75.0)),
        "science_score": float(profile.get("science_score", 72.0)),
        "english_score": float(profile.get("english_score", 76.0)),
        "coding_interest": float(profile.get("coding_interest", 70.0)),
        "analytical_score": float(profile.get("analytical_score", 72.0)),
        "creativity_score": float(profile.get("creativity_score", 65.0)),
        "communication_score": float(profile.get("communication_score", 70.0)),
        "projects_completed": float(profile.get("projects_completed", 2.0)),
        "stress_level": float(profile.get("stress_level", 2.0)),
    }

    df_one = pd.DataFrame([row])[NUMERIC_FEATURES + CATEGORICAL_FEATURES]
    predicted_cgpa = float(np.clip(cgpa_pipe.predict(df_one)[0], 3.5, 10.0))

    risk_probs = risk_pipe.predict_proba(df_one)[0]
    risk_idx = int(np.argmax(risk_probs))
    risk_level = str(risk_encoder.inverse_transform([risk_idx])[0])

    class_probs = {
        str(cls): float(prob) for cls, prob in zip(risk_encoder.classes_, risk_probs)
    }
    risk_score = round(
        class_probs.get("High", 0.0) * 90.0
        + class_probs.get("Medium", 0.0) * 50.0
        + class_probs.get("Low", 0.0) * 12.0,
        1,
    )
    pass_probability = round(float(np.clip(100.0 - risk_score * 0.55, 45.0, 99.5)), 1)

    prep = cgpa_pipe.named_steps["prep"]
    X_trans = prep.transform(df_one)
    shap_vals = explainer.shap_values(X_trans)[0]

    factor_items: List[Dict] = []
    num_shap = shap_vals[: len(NUMERIC_FEATURES)]
    total_abs = float(np.sum(np.abs(num_shap))) or 1.0

    for idx, feat in enumerate(NUMERIC_FEATURES):
        sv = float(num_shap[idx])
        impact_pct = round(abs(sv) / total_abs * 100.0, 1)
        factor_items.append(
            {
                "key": feat,
                "factor": FRIENDLY_NAMES.get(feat, feat),
                "value": round(row[feat], 1),
                "impact": impact_pct,
                "signed_shap": round(sv, 3),
                "direction": "positive" if sv >= 0 else "negative",
                "plain_text": _plain_reason(feat, row[feat], sv),
            }
        )

    factor_items.sort(key=lambda item: item["impact"], reverse=True)
    top_reasons = factor_items[:6]

    insights: List[str] = []
    if row["attendance_pct"] < 75:
        insights.append(
            f"Raise attendance from {row['attendance_pct']:.0f}% to 80%+ — attending 4 extra classes a month protects exam eligibility."
        )
    if row["internal_marks_avg"] < 70:
        insights.append(
            "Focus on your 2 lowest-scoring subjects with 45-minute practice quizzes twice a week to lift internal marks."
        )
    if row["study_hours_per_week"] < 15:
        insights.append(
            "Add one 60-minute distraction-free study block after dinner to reach 16+ focused hours per week."
        )
    if row["stress_level"] >= 4:
        insights.append(
            "Your stress rating is high — break exam prep into 25-minute blocks and aim for 7+ hours of sleep."
        )
    if not insights:
        insights.append(
            f"Your academic momentum is steady ({predicted_cgpa:.2f} forecast). Keep submitting assignments early and build 1 mini-project."
        )
    fallbacks = [
        "Review weak topics every Sunday using your Study Planner so nothing piles up before exams.",
        "Check your top career matches and close your #1 skill gap with a guided beginner course.",
        "Book a quick 15-minute check-in with your mentor every two weeks to stay confident.",
    ]
    for fb in fallbacks:
        if len(insights) < 3 and fb not in insights:
            insights.append(fb)

    return {
        "predicted_cgpa": round(predicted_cgpa, 2),
        "pass_probability": pass_probability,
        "risk_level": risk_level,
        "risk_score": risk_score,
        "top_reasons": top_reasons,
        "ai_insights": insights[:3],
    }
