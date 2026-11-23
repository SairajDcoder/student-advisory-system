"""
Stage 0 – Synthetic Data Generation
====================================
Generates a realistic synthetic dataset of 2 000 students with features that
influence academic performance and career suitability.

Features
--------
- study_hours_per_week      : float  (5-50)
- attendance_pct            : float  (40-100)
- previous_gpa              : float  (2.0-4.0)
- math_score                : int    (30-100)
- science_score             : int    (30-100)
- english_score             : int    (30-100)
- programming_score         : int    (0-100)
- creativity_score          : int    (0-100)
- communication_score       : int    (0-100)
- leadership_score          : int    (0-100)
- extracurricular_activities: int    (0-5)
- internship_experience     : int    (0/1 binary)
- projects_completed        : int    (0-10)
- gender                    : str    (Male / Female / Other)
- parental_education        : str    (High School / Bachelor / Master / PhD)
- part_time_job             : int    (0/1 binary)

Target
------
- career_recommendation     : str    (one of 5 categories)
"""
import numpy as np
import pandas as pd
import os
from src.config import RAW_DATA_PATH, DATA_DIR, RANDOM_SEED, CAREER_LABELS

np.random.seed(RANDOM_SEED)
N = 2000


def _generate() -> pd.DataFrame:
    """Return a synthetic DataFrame."""
    data = {
        "study_hours_per_week": np.round(np.random.uniform(5, 50, N), 1),
        "attendance_pct": np.round(np.random.uniform(40, 100, N), 1),
        "previous_gpa": np.round(np.random.uniform(2.0, 4.0, N), 2),
        "math_score": np.random.randint(30, 101, N),
        "science_score": np.random.randint(30, 101, N),
        "english_score": np.random.randint(30, 101, N),
        "programming_score": np.random.randint(0, 101, N),
        "creativity_score": np.random.randint(0, 101, N),
        "communication_score": np.random.randint(0, 101, N),
        "leadership_score": np.random.randint(0, 101, N),
        "extracurricular_activities": np.random.randint(0, 6, N),
        "internship_experience": np.random.randint(0, 2, N),
        "projects_completed": np.random.randint(0, 11, N),
        "gender": np.random.choice(["Male", "Female", "Other"], N, p=[0.48, 0.48, 0.04]),
        "parental_education": np.random.choice(
            ["High School", "Bachelor", "Master", "PhD"], N, p=[0.30, 0.35, 0.25, 0.10]
        ),
        "part_time_job": np.random.randint(0, 2, N),
    }
    df = pd.DataFrame(data)

    # ── Build a rule-based target so models have a learnable pattern ──
    scores = df[["math_score", "science_score", "programming_score",
                 "creativity_score", "communication_score", "leadership_score"]].values
    # Weighted combination → career bucket
    weights = np.array([
        [0.30, 0.25, 0.35, 0.00, 0.05, 0.05],   # Data Science / AI
        [0.20, 0.10, 0.45, 0.05, 0.10, 0.10],   # Software Engineering
        [0.10, 0.05, 0.05, 0.10, 0.35, 0.35],   # Business / Management
        [0.30, 0.35, 0.15, 0.05, 0.10, 0.05],   # Research / Academia
        [0.05, 0.05, 0.05, 0.40, 0.25, 0.20],   # Creative Arts / Design
    ])
    affinity = scores @ weights.T                     # (N, 5)
    # Add noise to make it non-trivial
    affinity += np.random.normal(0, 8, affinity.shape)
    labels = affinity.argmax(axis=1)
    df["career_recommendation"] = [CAREER_LABELS[l] for l in labels]

    # ── Inject ~3 % missing values in selected columns ──
    for col in ["attendance_pct", "previous_gpa", "math_score", "english_score"]:
        mask = np.random.rand(N) < 0.03
        df.loc[mask, col] = np.nan

    return df


def generate_and_save() -> str:
    """Generate data, save to CSV, and return the path."""
    os.makedirs(DATA_DIR, exist_ok=True)
    df = _generate()
    df.to_csv(RAW_DATA_PATH, index=False)
    print(f"[data_generation] Saved {len(df)} rows → {RAW_DATA_PATH}")
    return RAW_DATA_PATH


if __name__ == "__main__":
    generate_and_save()
