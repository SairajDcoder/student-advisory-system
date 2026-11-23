"""
Stage 7 – Test-Set Evaluation
==============================
Evaluates the best tuned model on the held-out test set exactly once.
Produces:
  - Classification report (precision / recall / F1 per class)
  - Confusion matrix heatmap
  - ROC curves (one-vs-rest for multi-class)
  - Per-class metrics table
"""
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
import os

from sklearn.metrics import (
    classification_report, confusion_matrix, accuracy_score,
    f1_score, precision_score, recall_score, roc_curve, auc
)
from sklearn.preprocessing import label_binarize

from src.config import PLOTS_DIR, RESULTS_DIR


def evaluate_on_test(model, X_test, y_test, label_encoder) -> dict:
    """
    Full test-set evaluation.

    Returns a dict with key metrics.
    """
    print("\n══════ Stage 7: Test-Set Evaluation ══════")
    y_pred = model.predict(X_test)
    class_names = list(label_encoder.classes_)

    # ── Classification report ──
    report = classification_report(y_test, y_pred, target_names=class_names)
    print("\n── Classification Report ──")
    print(report)

    # Save report
    report_dict = classification_report(y_test, y_pred,
                                         target_names=class_names, output_dict=True)
    pd.DataFrame(report_dict).T.to_csv(
        os.path.join(RESULTS_DIR, "classification_report.csv")
    )

    # ── Metrics summary ──
    metrics = {
        "accuracy": accuracy_score(y_test, y_pred),
        "f1_macro": f1_score(y_test, y_pred, average="macro"),
        "f1_weighted": f1_score(y_test, y_pred, average="weighted"),
        "precision_macro": precision_score(y_test, y_pred, average="macro"),
        "recall_macro": recall_score(y_test, y_pred, average="macro"),
    }
    pd.DataFrame([metrics]).to_csv(
        os.path.join(RESULTS_DIR, "test_metrics.csv"), index=False
    )
    print("\n── Test Metrics ──")
    for k, v in metrics.items():
        print(f"  {k}: {v:.4f}")

    # ── Confusion matrix ──
    _plot_confusion_matrix(y_test, y_pred, class_names)

    # ── ROC curves (one-vs-rest) ──
    if hasattr(model, "predict_proba"):
        y_proba = model.predict_proba(X_test)
        _plot_roc_curves(y_test, y_proba, class_names)

    return metrics


def _plot_confusion_matrix(y_true, y_pred, class_names) -> None:
    cm = confusion_matrix(y_true, y_pred)
    fig, ax = plt.subplots(figsize=(8, 7))
    sns.heatmap(cm, annot=True, fmt="d", cmap="Blues",
                xticklabels=class_names, yticklabels=class_names, ax=ax)
    ax.set_xlabel("Predicted")
    ax.set_ylabel("Actual")
    ax.set_title("Confusion Matrix – Test Set")
    plt.xticks(rotation=30, ha="right")
    plt.yticks(rotation=0)
    plt.tight_layout()
    fig.savefig(os.path.join(PLOTS_DIR, "confusion_matrix.png"), dpi=150)
    plt.close(fig)
    print("[eval] Saved confusion_matrix.png")


def _plot_roc_curves(y_true, y_proba, class_names) -> None:
    n_classes = len(class_names)
    y_bin = label_binarize(y_true, classes=list(range(n_classes)))

    fig, ax = plt.subplots(figsize=(9, 7))
    for i, name in enumerate(class_names):
        fpr, tpr, _ = roc_curve(y_bin[:, i], y_proba[:, i])
        roc_auc = auc(fpr, tpr)
        ax.plot(fpr, tpr, lw=2, label=f"{name} (AUC = {roc_auc:.3f})")

    ax.plot([0, 1], [0, 1], "k--", lw=1)
    ax.set_xlabel("False Positive Rate")
    ax.set_ylabel("True Positive Rate")
    ax.set_title("ROC Curves (One-vs-Rest) – Test Set")
    ax.legend(loc="lower right", fontsize=8)
    plt.tight_layout()
    fig.savefig(os.path.join(PLOTS_DIR, "roc_curves.png"), dpi=150)
    plt.close(fig)
    print("[eval] Saved roc_curves.png")


if __name__ == "__main__":
    import joblib
    from src.preprocessing import get_preprocessed_data
    from src.config import MODELS_DIR
    X_tr, X_te, y_tr, y_te, pp, le = get_preprocessed_data()
    model = joblib.load(os.path.join(MODELS_DIR, "best_model_rf.pkl"))
    evaluate_on_test(model, X_te, y_te, le)
