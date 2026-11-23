"""
Stage 5 – Hyperparameter Tuning
================================
Uses Optuna with nested cross-validation for the best baseline model
(Random Forest by default; can be changed).

Also provides a GridSearchCV alternative for comparison.
"""
import numpy as np
import pandas as pd
import os
import joblib
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.model_selection import (
    RepeatedStratifiedKFold, cross_val_score, GridSearchCV
)

from src.config import RANDOM_SEED, CV_FOLDS, CV_REPEATS, MODELS_DIR, RESULTS_DIR, PLOTS_DIR

try:
    import optuna
    optuna.logging.set_verbosity(optuna.logging.WARNING)
    HAS_OPTUNA = True
except ImportError:
    HAS_OPTUNA = False


# ──────────────────────────────────────────────
# Optuna-based tuning (Random Forest)
# ──────────────────────────────────────────────
def _objective_rf(trial, X, y, cv):
    """Optuna objective for Random Forest."""
    params = {
        "n_estimators": trial.suggest_int("n_estimators", 100, 500, step=50),
        "max_depth": trial.suggest_int("max_depth", 5, 30),
        "min_samples_split": trial.suggest_int("min_samples_split", 2, 20),
        "min_samples_leaf": trial.suggest_int("min_samples_leaf", 1, 10),
        "max_features": trial.suggest_categorical("max_features", ["sqrt", "log2", None]),
        "random_state": RANDOM_SEED,
        "n_jobs": -1,
    }
    model = RandomForestClassifier(**params)
    scores = cross_val_score(model, X, y, cv=cv, scoring="f1_macro", n_jobs=-1)
    return scores.mean()


def tune_with_optuna(X_train, y_train, n_trials: int = 50):
    """
    Tune Random Forest using Optuna and return the best model + params.
    """
    if not HAS_OPTUNA:
        print("[tuning] Optuna not installed – falling back to GridSearchCV.")
        return tune_with_gridsearch(X_train, y_train)

    print("\n══════ Stage 5: Hyperparameter Tuning (Optuna) ══════")
    cv = RepeatedStratifiedKFold(
        n_splits=CV_FOLDS, n_repeats=CV_REPEATS, random_state=RANDOM_SEED
    )
    study = optuna.create_study(direction="maximize",
                                 sampler=optuna.samplers.TPESampler(seed=RANDOM_SEED))
    study.optimize(lambda trial: _objective_rf(trial, X_train, y_train, cv),
                   n_trials=n_trials, show_progress_bar=True)

    print(f"  Best F1-macro (CV): {study.best_value:.4f}")
    print(f"  Best params: {study.best_params}")

    # Refit with best params
    best_model = RandomForestClassifier(
        **study.best_params, random_state=RANDOM_SEED, n_jobs=-1
    )
    best_model.fit(X_train, y_train)

    # Save
    joblib.dump(best_model, os.path.join(MODELS_DIR, "best_model_rf.pkl"))
    pd.DataFrame([study.best_params]).to_csv(
        os.path.join(RESULTS_DIR, "best_params_optuna.csv"), index=False
    )

    # Plot optimisation history
    _plot_optuna_history(study)

    return best_model, study.best_params, study.best_value


# ──────────────────────────────────────────────
# GridSearchCV alternative (Gradient Boosting)
# ──────────────────────────────────────────────
def tune_with_gridsearch(X_train, y_train):
    """
    Tune Gradient Boosting with GridSearchCV as an alternative / comparison.
    """
    print("\n══════ Stage 5: Hyperparameter Tuning (GridSearchCV) ══════")
    param_grid = {
        "n_estimators": [100, 200, 300],
        "max_depth": [3, 5, 7],
        "learning_rate": [0.05, 0.1, 0.2],
        "min_samples_split": [2, 5],
    }
    cv = RepeatedStratifiedKFold(
        n_splits=CV_FOLDS, n_repeats=1, random_state=RANDOM_SEED
    )
    gs = GridSearchCV(
        GradientBoostingClassifier(random_state=RANDOM_SEED),
        param_grid, cv=cv, scoring="f1_macro",
        n_jobs=-1, verbose=0, refit=True,
    )
    gs.fit(X_train, y_train)

    print(f"  Best F1-macro (CV): {gs.best_score_:.4f}")
    print(f"  Best params: {gs.best_params_}")

    joblib.dump(gs.best_estimator_, os.path.join(MODELS_DIR, "best_model_gb.pkl"))
    pd.DataFrame([gs.best_params_]).to_csv(
        os.path.join(RESULTS_DIR, "best_params_gridsearch.csv"), index=False
    )
    return gs.best_estimator_, gs.best_params_, gs.best_score_


# ──────────────────────────────────────────────
# Visualization helpers
# ──────────────────────────────────────────────
def _plot_optuna_history(study) -> None:
    """Plot the Optuna optimisation history."""
    trials = study.trials
    vals = [t.value for t in trials]
    best_so_far = np.maximum.accumulate(vals)

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(vals, "o-", alpha=0.4, label="Trial value")
    ax.plot(best_so_far, "r-", linewidth=2, label="Best so far")
    ax.set_xlabel("Trial")
    ax.set_ylabel("F1-macro (CV)")
    ax.set_title("Optuna Hyperparameter Optimisation History")
    ax.legend()
    plt.tight_layout()
    fig.savefig(os.path.join(PLOTS_DIR, "optuna_history.png"), dpi=150)
    plt.close(fig)
    print("[tuning] Saved optuna_history.png")


if __name__ == "__main__":
    from src.preprocessing import get_preprocessed_data
    X_tr, X_te, y_tr, y_te, pp, le = get_preprocessed_data()
    tune_with_optuna(X_tr, y_tr, n_trials=30)
