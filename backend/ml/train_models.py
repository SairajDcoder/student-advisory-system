"""
AdvisorAI ML Training Script
============================
Generates or ingests student academic dataset (tailored for 10th & 12th pass-outs
and early-college learners) and trains:
  1. XGBoost Regressor -> next-term CGPA prediction (0-10 scale)
  2. XGBoost Classifier -> At-Risk detection (Low / Medium / High)

All preprocessing is encapsulated inside scikit-learn Pipelines to prevent
data leakage. Saves models and evaluation metrics to backend/ml_models/.
"""
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Optional

import joblib
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.metrics import accuracy_score, f1_score, mean_absolute_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import LabelEncoder, OneHotEncoder, StandardScaler
from xgboost import XGBClassifier, XGBRegressor

from backend.app.config import DATA_DIR, MODELS_DIR

DATASET_PATH = DATA_DIR / "advisorai_students.csv"
CGPA_MODEL_PATH = MODELS_DIR / "xgb_cgpa.pkl"
RISK_MODEL_PATH = MODELS_DIR / "xgb_risk.pkl"
RISK_ENCODER_PATH = MODELS_DIR / "risk_encoder.pkl"
METRICS_PATH = MODELS_DIR / "model_metrics.json"

NUMERIC_FEATURES = [
    "attendance_pct",
    "internal_marks_avg",
    "assignment_score_avg",
    "past_cgpa",
    "study_hours_per_week",
    "math_score",
    "science_score",
    "english_score",
    "coding_interest",
    "analytical_score",
    "creativity_score",
    "communication_score",
    "projects_completed",
    "stress_level",
]
CATEGORICAL_FEATURES = ["education_stage", "stream"]


def generate_sample_dataset(n_samples: int = 2400, seed: int = 42) -> pd.DataFrame:
    """Create a realistic dataset representing 10th & 12th pass-out students."""
    rng = np.random.default_rng(seed)
    stages = rng.choice(["10th", "12th"], size=n_samples, p=[0.42, 0.58])
    streams = []
    for st in stages:
        if st == "10th":
            streams.append(rng.choice(["General", "Science (PCM)", "Commerce", "Arts"]))
        else:
            streams.append(
                rng.choice(
                    ["Science (PCM)", "Science (PCB)", "Commerce", "Arts"],
                    p=[0.40, 0.20, 0.25, 0.15],
                )
            )

    attendance_pct = np.clip(rng.normal(80, 12, n_samples), 40, 100).round(1)
    internal_marks_avg = np.clip(rng.normal(73, 14, n_samples), 25, 100).round(1)
    assignment_score_avg = np.clip(rng.normal(76, 13, n_samples), 30, 100).round(1)
    past_cgpa = np.clip(rng.normal(7.6, 1.2, n_samples), 4.0, 9.9).round(2)
    study_hours_per_week = np.clip(rng.normal(19, 8, n_samples), 3, 45).round(1)
    math_score = np.clip(rng.normal(72, 16, n_samples), 25, 100).round(1)
    science_score = np.clip(rng.normal(71, 16, n_samples), 25, 100).round(1)
    english_score = np.clip(rng.normal(75, 13, n_samples), 30, 100).round(1)
    coding_interest = rng.integers(15, 100, size=n_samples)
    analytical_score = rng.integers(20, 100, size=n_samples)
    creativity_score = rng.integers(20, 100, size=n_samples)
    communication_score = rng.integers(25, 100, size=n_samples)
    projects_completed = rng.integers(0, 8, size=n_samples)
    stress_level = rng.integers(1, 6, size=n_samples)

    raw_cgpa = (
        0.48 * past_cgpa
        + 0.025 * attendance_pct
        + 0.018 * internal_marks_avg
        + 0.014 * assignment_score_avg
        + 0.032 * study_hours_per_week
        - 0.14 * (stress_level - 1)
        + rng.normal(0, 0.28, n_samples)
        - 0.7
    )
    next_cgpa = np.clip(raw_cgpa, 3.5, 10.0).round(2)

    risk_levels = []
    for att, intern, assign, cgpa, stress in zip(
        attendance_pct, internal_marks_avg, assignment_score_avg, next_cgpa, stress_level
    ):
        risk_points = 0
        if att < 70:
            risk_points += 2
        elif att < 78:
            risk_points += 1
        if intern < 55:
            risk_points += 2
        elif intern < 68:
            risk_points += 1
        if assign < 60:
            risk_points += 1
        if cgpa < 6.2:
            risk_points += 2
        elif cgpa < 7.2:
            risk_points += 1
        if stress >= 4:
            risk_points += 1

        if risk_points >= 4:
            risk_levels.append("High")
        elif risk_points >= 2:
            risk_levels.append("Medium")
        else:
            risk_levels.append("Low")

    pass_status = (next_cgpa >= 5.0).astype(int)

    return pd.DataFrame(
        {
            "education_stage": stages,
            "stream": streams,
            "attendance_pct": attendance_pct,
            "internal_marks_avg": internal_marks_avg,
            "assignment_score_avg": assignment_score_avg,
            "past_cgpa": past_cgpa,
            "study_hours_per_week": study_hours_per_week,
            "math_score": math_score,
            "science_score": science_score,
            "english_score": english_score,
            "coding_interest": coding_interest,
            "analytical_score": analytical_score,
            "creativity_score": creativity_score,
            "communication_score": communication_score,
            "projects_completed": projects_completed,
            "stress_level": stress_level,
            "next_cgpa": next_cgpa,
            "risk_level": risk_levels,
            "pass_status": pass_status,
        }
    )


def _build_preprocessor() -> ColumnTransformer:
    num_pipe = Pipeline(
        [
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
        ]
    )
    cat_pipe = Pipeline(
        [
            ("imputer", SimpleImputer(strategy="most_frequent")),
            ("encoder", OneHotEncoder(handle_unknown="ignore", sparse_output=False)),
        ]
    )
    return ColumnTransformer(
        [
            ("num", num_pipe, NUMERIC_FEATURES),
            ("cat", cat_pipe, CATEGORICAL_FEATURES),
        ],
        remainder="drop",
    )


def train_and_save_models(csv_path: Optional[Path] = None) -> Dict:
    """Train CGPA regressor and Risk classifier, evaluate on test split, and persist."""
    source_path = Path(csv_path) if csv_path else DATASET_PATH
    if not source_path.exists():
        df = generate_sample_dataset()
        df.to_csv(DATASET_PATH, index=False)
    else:
        df = pd.read_csv(source_path)

    feature_cols = NUMERIC_FEATURES + CATEGORICAL_FEATURES
    X = df[feature_cols]
    y_cgpa = df["next_cgpa"].astype(float)
    y_risk_raw = df["risk_level"].astype(str)

    risk_encoder = LabelEncoder()
    y_risk = risk_encoder.fit_transform(y_risk_raw)

    X_train, X_test, y_cgpa_train, y_cgpa_test, y_risk_train, y_risk_test = train_test_split(
        X, y_cgpa, y_risk, test_size=0.20, random_state=42, stratify=y_risk
    )

    cgpa_pipeline = Pipeline(
        [
            ("prep", _build_preprocessor()),
            (
                "model",
                XGBRegressor(
                    n_estimators=180,
                    max_depth=4,
                    learning_rate=0.07,
                    subsample=0.9,
                    colsample_bytree=0.9,
                    random_state=42,
                    n_jobs=2,
                ),
            ),
        ]
    )
    cgpa_pipeline.fit(X_train, y_cgpa_train)
    cgpa_preds = cgpa_pipeline.predict(X_test)

    risk_pipeline = Pipeline(
        [
            ("prep", _build_preprocessor()),
            (
                "model",
                XGBClassifier(
                    n_estimators=180,
                    max_depth=4,
                    learning_rate=0.07,
                    subsample=0.9,
                    colsample_bytree=0.9,
                    random_state=42,
                    eval_metric="mlogloss",
                    n_jobs=2,
                ),
            ),
        ]
    )
    risk_pipeline.fit(X_train, y_risk_train)
    risk_preds = risk_pipeline.predict(X_test)

    metrics = {
        "trained_at": datetime.now(timezone.utc).isoformat(),
        "dataset_rows": int(len(df)),
        "cgpa_r2": round(float(r2_score(y_cgpa_test, cgpa_preds)), 4),
        "cgpa_mae": round(float(mean_absolute_error(y_cgpa_test, cgpa_preds)), 4),
        "risk_accuracy": round(float(accuracy_score(y_risk_test, risk_preds)), 4),
        "risk_f1_macro": round(float(f1_score(y_risk_test, risk_preds, average="macro")), 4),
        "classes": list(risk_encoder.classes_),
    }

    joblib.dump(cgpa_pipeline, CGPA_MODEL_PATH)
    joblib.dump(risk_pipeline, RISK_MODEL_PATH)
    joblib.dump(risk_encoder, RISK_ENCODER_PATH)
    METRICS_PATH.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    return metrics


if __name__ == "__main__":
    result = train_and_save_models()
    print("Trained AdvisorAI models:", json.dumps(result, indent=2))
