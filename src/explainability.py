"""
Stage 8a – Model Explainability
================================
Feature importance (from tree model) and SHAP summary plot.
"""
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import os

from src.config import PLOTS_DIR, RESULTS_DIR
from src.preprocessing import NUMERIC_FEATURES, CATEGORICAL_FEATURES


def get_feature_names(preprocessor) -> list:
    """Extract feature names from a fitted ColumnTransformer."""
    names = list(NUMERIC_FEATURES)
    try:
        ohe = preprocessor.named_transformers_["cat"].named_steps["encoder"]
        cat_names = list(ohe.get_feature_names_out(CATEGORICAL_FEATURES))
        names.extend(cat_names)
    except Exception:
        pass
    return names


def plot_feature_importance(model, preprocessor) -> None:
    """Bar chart of feature importances from a tree-based model."""
    if not hasattr(model, "feature_importances_"):
        print("[explain] Model has no feature_importances_ – skipping.")
        return

    names = get_feature_names(preprocessor)
    importances = model.feature_importances_
    if len(names) != len(importances):
        names = [f"feature_{i}" for i in range(len(importances))]

    idx = np.argsort(importances)[::-1][:20]  # top 20
    fig, ax = plt.subplots(figsize=(10, 7))
    ax.barh([names[i] for i in idx][::-1],
            [importances[i] for i in idx][::-1],
            color="steelblue", edgecolor="black")
    ax.set_xlabel("Importance")
    ax.set_title("Top 20 Feature Importances (Random Forest)")
    plt.tight_layout()
    fig.savefig(os.path.join(PLOTS_DIR, "feature_importance.png"), dpi=150)
    plt.close(fig)
    print("[explain] Saved feature_importance.png")

    # Save to CSV
    fi_df = pd.DataFrame({"Feature": names, "Importance": importances})
    fi_df = fi_df.sort_values("Importance", ascending=False)
    fi_df.to_csv(os.path.join(RESULTS_DIR, "feature_importances.csv"), index=False)


def plot_shap_summary(model, X_test, preprocessor) -> None:
    """Generate a SHAP summary plot (beeswarm)."""
    try:
        import shap
    except ImportError:
        print("[explain] shap not installed – skipping SHAP plot.")
        return

    names = get_feature_names(preprocessor)
    if len(names) != X_test.shape[1]:
        names = [f"feature_{i}" for i in range(X_test.shape[1])]

    explainer = shap.TreeExplainer(model)
    shap_values = explainer.shap_values(X_test[:200])  # sample for speed

    fig, ax = plt.subplots(figsize=(12, 8))
    # For multi-class: shap_values is a list; use mean absolute
    if isinstance(shap_values, list):
        mean_abs = np.mean([np.abs(sv) for sv in shap_values], axis=0)
        mean_importance = mean_abs.mean(axis=0)
        idx = np.argsort(mean_importance)[::-1][:15]
        ax.barh([names[i] for i in idx][::-1],
                [mean_importance[i] for i in idx][::-1],
                color="coral", edgecolor="black")
        ax.set_xlabel("Mean |SHAP value|")
        ax.set_title("SHAP Feature Importance (Mean across classes)")
    else:
        shap.summary_plot(shap_values, X_test[:200], feature_names=names,
                          show=False)
    plt.tight_layout()
    fig.savefig(os.path.join(PLOTS_DIR, "shap_summary.png"), dpi=150)
    plt.close(fig)
    print("[explain] Saved shap_summary.png")


if __name__ == "__main__":
    import joblib
    from src.preprocessing import get_preprocessed_data
    from src.config import MODELS_DIR
    X_tr, X_te, y_tr, y_te, pp, le = get_preprocessed_data()
    model = joblib.load(os.path.join(MODELS_DIR, "best_model_rf.pkl"))
    plot_feature_importance(model, pp)
    plot_shap_summary(model, X_te, pp)
