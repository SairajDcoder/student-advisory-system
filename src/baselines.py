"""
Stage 4 – Baseline Models
==========================
Trains 3+ classifiers plus a simple baseline (most-frequent / dummy)
using Repeated Stratified K-Fold cross-validation.
Outputs a comparison table with mean ± std for multiple metrics.
"""
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import os

from sklearn.dummy import DummyClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import (
    RandomForestClassifier, GradientBoostingClassifier
)
from sklearn.svm import SVC
from sklearn.neighbors import KNeighborsClassifier
from sklearn.model_selection import RepeatedStratifiedKFold, cross_validate

from src.config import RANDOM_SEED, CV_FOLDS, CV_REPEATS, RESULTS_DIR, PLOTS_DIR


MODELS = {
    "Dummy (Most Frequent)": DummyClassifier(strategy="most_frequent"),
    "Logistic Regression": LogisticRegression(
        max_iter=1000, random_state=RANDOM_SEED
    ),
    "K-Nearest Neighbors": KNeighborsClassifier(n_neighbors=7),
    "Support Vector Machine": SVC(kernel="rbf", random_state=RANDOM_SEED),
    "Random Forest": RandomForestClassifier(
        n_estimators=200, random_state=RANDOM_SEED, n_jobs=-1
    ),
    "Gradient Boosting": GradientBoostingClassifier(
        n_estimators=200, random_state=RANDOM_SEED
    ),
}

SCORING = {
    "accuracy": "accuracy",
    "f1_macro": "f1_macro",
    "precision_macro": "precision_macro",
    "recall_macro": "recall_macro",
}


def evaluate_baselines(X_train, y_train) -> pd.DataFrame:
    """
    Run Repeated Stratified K-Fold CV for every model in MODELS.

    Returns a DataFrame: model | metric | mean | std
    """
    cv = RepeatedStratifiedKFold(
        n_splits=CV_FOLDS, n_repeats=CV_REPEATS, random_state=RANDOM_SEED
    )
    rows = []
    for name, model in MODELS.items():
        print(f"  → Evaluating {name} …")
        cv_results = cross_validate(
            model, X_train, y_train, cv=cv, scoring=SCORING, n_jobs=-1
        )
        for metric_key, scorer_name in SCORING.items():
            scores = cv_results[f"test_{metric_key}"]
            rows.append({
                "Model": name,
                "Metric": metric_key,
                "Mean": round(scores.mean(), 4),
                "Std": round(scores.std(), 4),
                "Mean ± Std": f"{scores.mean():.4f} ± {scores.std():.4f}",
            })

    results_df = pd.DataFrame(rows)
    csv_path = os.path.join(RESULTS_DIR, "baseline_comparison.csv")
    results_df.to_csv(csv_path, index=False)
    print(f"[baselines] Saved comparison → {csv_path}")
    return results_df


def plot_baseline_comparison(results_df: pd.DataFrame) -> None:
    """Bar chart comparing model accuracy (mean ± std)."""
    acc = results_df[results_df["Metric"] == "accuracy"].copy()
    acc = acc.sort_values("Mean", ascending=True)

    fig, ax = plt.subplots(figsize=(10, 6))
    bars = ax.barh(acc["Model"], acc["Mean"], xerr=acc["Std"],
                   color=plt.cm.Set2(np.linspace(0, 1, len(acc))),
                   edgecolor="black", capsize=4)
    ax.set_xlabel("Accuracy (mean ± std)")
    ax.set_title("Baseline Model Comparison – Accuracy", fontsize=14)
    ax.set_xlim(0, 1.05)
    for bar, val in zip(bars, acc["Mean"]):
        ax.text(bar.get_width() + 0.01, bar.get_y() + bar.get_height() / 2,
                f"{val:.3f}", va="center", fontsize=9)
    plt.tight_layout()
    fig.savefig(os.path.join(PLOTS_DIR, "baseline_comparison.png"), dpi=150)
    plt.close(fig)
    print("[baselines] Saved baseline_comparison.png")


def run_baselines(X_train, y_train) -> pd.DataFrame:
    """Full Stage 4 pipeline."""
    print("\n══════ Stage 4: Baseline Models ══════")
    results = evaluate_baselines(X_train, y_train)
    plot_baseline_comparison(results)
    # Print nice summary table (accuracy only)
    acc = results[results["Metric"] == "accuracy"][["Model", "Mean ± Std"]]
    print("\n── Accuracy Summary ──")
    print(acc.to_string(index=False))
    return results


if __name__ == "__main__":
    from src.preprocessing import get_preprocessed_data
    X_tr, X_te, y_tr, y_te, pp, le = get_preprocessed_data()
    run_baselines(X_tr, y_tr)
