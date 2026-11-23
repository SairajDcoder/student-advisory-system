"""
main.py – Run the Complete ML Pipeline (Stages 0 → 8)
======================================================
Execute:  python main.py
"""
import sys
import os
import time

# Ensure project root is on the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.config import MODELS_DIR


def main():
    start = time.time()
    print("=" * 60)
    print("  Student Performance & Career Advisory System")
    print("  Complete ML Pipeline")
    print("=" * 60)

    # ── Stage 0: Data Generation ──────────────────────────────
    print("\n══════ Stage 0: Data Generation ══════")
    from src.data_generation import generate_and_save
    generate_and_save()

    # ── Stage 1: Exploratory Data Analysis ────────────────────
    print("\n══════ Stage 1: Exploratory Data Analysis ══════")
    from src.eda import run_eda
    df = run_eda()

    # ── Stages 2 & 3: Split + Preprocessing ───────────────────
    print("\n══════ Stages 2 & 3: Split & Preprocessing ══════")
    from src.preprocessing import get_preprocessed_data, load_and_split
    X_train_t, X_test_t, y_train, y_test, preprocessor, le = get_preprocessed_data()
    # Also keep raw splits for ablation
    X_train_raw, X_test_raw, _, _, _ = load_and_split()

    # ── Stage 4: Baseline Models ──────────────────────────────
    from src.baselines import run_baselines
    baseline_results = run_baselines(X_train_t, y_train)

    # ── Stage 5: Hyperparameter Tuning ────────────────────────
    from src.tuning import tune_with_optuna, tune_with_gridsearch
    best_model, best_params, best_score = tune_with_optuna(X_train_t, y_train, n_trials=40)

    # Also run GridSearchCV for comparison
    gb_model, gb_params, gb_score = tune_with_gridsearch(X_train_t, y_train)

    # ── Stage 6: Ablation Study ───────────────────────────────
    from src.ablation import run_ablation
    ablation_results = run_ablation(X_train_raw, y_train)

    # ── Stage 7: Test-Set Evaluation ──────────────────────────
    from src.evaluation import evaluate_on_test
    metrics = evaluate_on_test(best_model, X_test_t, y_test, le)

    # ── Stage 8: Explainability ───────────────────────────────
    print("\n══════ Stage 8: Explainability & Delivery ══════")
    from src.explainability import plot_feature_importance, plot_shap_summary
    plot_feature_importance(best_model, preprocessor)
    plot_shap_summary(best_model, X_test_t, preprocessor)

    # ── Summary ───────────────────────────────────────────────
    elapsed = time.time() - start
    print("\n" + "=" * 60)
    print(f"  Pipeline complete in {elapsed:.1f} seconds")
    print(f"  Test Accuracy : {metrics['accuracy']:.4f}")
    print(f"  Test F1-macro : {metrics['f1_macro']:.4f}")
    print("=" * 60)
    print("\n  To launch the demo app:")
    print("    python app/app.py")
    print("    Open http://localhost:5000 in your browser")
    print("=" * 60)


if __name__ == "__main__":
    main()
