"""
Stage 6 – Ablation Study
=========================
Removes one feature group at a time and measures the change in
F1-macro score using cross-validation.
"""
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import os

from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import RepeatedStratifiedKFold, cross_val_score
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler, OneHotEncoder

from src.config import RANDOM_SEED, CV_FOLDS, RESULTS_DIR, PLOTS_DIR, RAW_DATA_PATH, TARGET_COL
from src.preprocessing import NUMERIC_FEATURES, CATEGORICAL_FEATURES


FEATURE_GROUPS = {
    "Academic Scores":    ["math_score", "science_score", "english_score"],
    "Skill Scores":       ["programming_score", "creativity_score",
                           "communication_score", "leadership_score"],
    "Study Habits":       ["study_hours_per_week", "attendance_pct", "previous_gpa"],
    "Experience":         ["internship_experience", "projects_completed",
                           "extracurricular_activities"],
    "Demographics":       ["gender", "parental_education", "part_time_job"],
}


def _build_pipeline(num_feats, cat_feats):
    """Build a preprocessor + model pipeline for given features."""
    transformers = []
    if num_feats:
        transformers.append(("num", Pipeline([
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
        ]), num_feats))
    if cat_feats:
        transformers.append(("cat", Pipeline([
            ("imputer", SimpleImputer(strategy="most_frequent")),
            ("encoder", OneHotEncoder(handle_unknown="ignore", sparse_output=False)),
        ]), cat_feats))
    preprocessor = ColumnTransformer(transformers, remainder="drop")
    return Pipeline([
        ("prep", preprocessor),
        ("clf", RandomForestClassifier(
            n_estimators=200, random_state=RANDOM_SEED, n_jobs=-1
        )),
    ])


def run_ablation(X_train_raw: pd.DataFrame, y_train: np.ndarray) -> pd.DataFrame:
    """
    For each feature group, train without that group and compare to full model.

    Parameters
    ----------
    X_train_raw : raw (untransformed) training features as a DataFrame
    y_train     : encoded target array
    """
    print("\n══════ Stage 6: Ablation Study ══════")
    cv = RepeatedStratifiedKFold(n_splits=CV_FOLDS, n_repeats=2, random_state=RANDOM_SEED)

    all_num = [f for f in NUMERIC_FEATURES if f in X_train_raw.columns]
    all_cat = [f for f in CATEGORICAL_FEATURES if f in X_train_raw.columns]

    # Full-model baseline
    full_pipe = _build_pipeline(all_num, all_cat)
    full_scores = cross_val_score(full_pipe, X_train_raw, y_train,
                                   cv=cv, scoring="f1_macro", n_jobs=-1)
    full_mean = full_scores.mean()
    print(f"  Full model F1-macro: {full_mean:.4f}")

    rows = [{"Removed Group": "None (Full Model)",
             "F1-macro": round(full_mean, 4),
             "Δ F1": 0.0}]

    for group_name, group_cols in FEATURE_GROUPS.items():
        remaining_num = [f for f in all_num if f not in group_cols]
        remaining_cat = [f for f in all_cat if f not in group_cols]
        if not remaining_num and not remaining_cat:
            continue
        pipe = _build_pipeline(remaining_num, remaining_cat)
        scores = cross_val_score(pipe, X_train_raw, y_train,
                                  cv=cv, scoring="f1_macro", n_jobs=-1)
        mean_score = scores.mean()
        delta = round(mean_score - full_mean, 4)
        rows.append({
            "Removed Group": group_name,
            "F1-macro": round(mean_score, 4),
            "Δ F1": delta,
        })
        print(f"  Without {group_name}: {mean_score:.4f} (Δ={delta:+.4f})")

    ablation_df = pd.DataFrame(rows)
    csv_path = os.path.join(RESULTS_DIR, "ablation_study.csv")
    ablation_df.to_csv(csv_path, index=False)
    print(f"[ablation] Saved → {csv_path}")

    _plot_ablation(ablation_df)
    return ablation_df


def _plot_ablation(df: pd.DataFrame) -> None:
    """Horizontal bar chart of ablation results."""
    plot_df = df[df["Removed Group"] != "None (Full Model)"].copy()
    plot_df = plot_df.sort_values("Δ F1")

    fig, ax = plt.subplots(figsize=(9, 5))
    colors = ["red" if d < 0 else "green" for d in plot_df["Δ F1"]]
    ax.barh(plot_df["Removed Group"], plot_df["Δ F1"], color=colors,
            edgecolor="black")
    ax.axvline(0, color="black", linewidth=0.8)
    ax.set_xlabel("Δ F1-macro (relative to full model)")
    ax.set_title("Ablation Study – Impact of Removing Feature Groups")
    for i, (val, name) in enumerate(zip(plot_df["Δ F1"], plot_df["Removed Group"])):
        ax.text(val + 0.001 if val >= 0 else val - 0.001, i,
                f"{val:+.4f}", va="center",
                ha="left" if val >= 0 else "right", fontsize=9)
    plt.tight_layout()
    fig.savefig(os.path.join(PLOTS_DIR, "ablation_study.png"), dpi=150)
    plt.close(fig)
    print("[ablation] Saved ablation_study.png")


if __name__ == "__main__":
    from src.preprocessing import load_and_split
    X_train, X_test, y_train, y_test, le = load_and_split()
    run_ablation(X_train, y_train)
