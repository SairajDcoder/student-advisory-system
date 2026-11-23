"""
Stages 2 & 3 – Split and Preprocessing
=======================================
- Stratified train/test split (80/20) with a fixed random seed.
- Scikit-learn Pipeline for imputation, scaling, and encoding
  to prevent data leakage.
"""
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler, OneHotEncoder, LabelEncoder
import joblib
import os

from src.config import (
    RAW_DATA_PATH, RANDOM_SEED, TEST_SIZE, TARGET_COL, MODELS_DIR
)


# ─── Identify column types ───────────────────────────────────────────
NUMERIC_FEATURES = [
    "study_hours_per_week", "attendance_pct", "previous_gpa",
    "math_score", "science_score", "english_score",
    "programming_score", "creativity_score", "communication_score",
    "leadership_score", "extracurricular_activities",
    "internship_experience", "projects_completed", "part_time_job",
]
CATEGORICAL_FEATURES = ["gender", "parental_education"]


def load_and_split(path: str = RAW_DATA_PATH):
    """
    Load CSV and perform stratified train/test split.

    Returns
    -------
    X_train, X_test, y_train, y_test, label_encoder
    """
    df = pd.read_csv(path)

    X = df.drop(columns=[TARGET_COL])
    y = df[TARGET_COL]

    # Encode the multi-class target → integers
    le = LabelEncoder()
    y_encoded = le.fit_transform(y)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y_encoded,
        test_size=TEST_SIZE,
        random_state=RANDOM_SEED,
        stratify=y_encoded,
    )
    print(f"[split] Train: {X_train.shape[0]} | Test: {X_test.shape[0]}")
    print(f"[split] Classes: {list(le.classes_)}")

    # Save the label encoder
    joblib.dump(le, os.path.join(MODELS_DIR, "label_encoder.pkl"))

    return X_train, X_test, y_train, y_test, le


def build_preprocessor() -> ColumnTransformer:
    """
    Build a ColumnTransformer that handles numeric and categorical features.

    Numeric : SimpleImputer(median) → StandardScaler
    Categorical : SimpleImputer(most_frequent) → OneHotEncoder
    """
    numeric_pipeline = Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler", StandardScaler()),
    ])
    categorical_pipeline = Pipeline([
        ("imputer", SimpleImputer(strategy="most_frequent")),
        ("encoder", OneHotEncoder(handle_unknown="ignore", sparse_output=False)),
    ])
    preprocessor = ColumnTransformer(
        transformers=[
            ("num", numeric_pipeline, NUMERIC_FEATURES),
            ("cat", categorical_pipeline, CATEGORICAL_FEATURES),
        ],
        remainder="drop",
    )
    return preprocessor


def get_preprocessed_data(path: str = RAW_DATA_PATH):
    """
    Convenience function: split + fit preprocessor on train, transform both.

    Returns
    -------
    X_train_t, X_test_t, y_train, y_test, preprocessor, label_encoder
    """
    X_train, X_test, y_train, y_test, le = load_and_split(path)
    preprocessor = build_preprocessor()
    X_train_t = preprocessor.fit_transform(X_train)
    X_test_t = preprocessor.transform(X_test)

    # Save the fitted preprocessor
    joblib.dump(preprocessor, os.path.join(MODELS_DIR, "preprocessor.pkl"))
    print(f"[preprocess] Transformed shape: {X_train_t.shape}")

    return X_train_t, X_test_t, y_train, y_test, preprocessor, le


if __name__ == "__main__":
    X_tr, X_te, y_tr, y_te, pp, le = get_preprocessed_data()
    print("Preprocessing complete.")
