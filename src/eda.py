"""
Stage 1 – Exploratory Data Analysis (EDA)
==========================================
Loads the raw CSV generated in Stage 0, produces summary statistics,
missing-value reports, class-balance bar chart, correlation heatmap,
and feature distribution plots. All figures are saved to `plots/`.
"""
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
import os

from src.config import RAW_DATA_PATH, PLOTS_DIR, TARGET_COL


def load_data(path: str = RAW_DATA_PATH) -> pd.DataFrame:
    """Load the student dataset."""
    df = pd.read_csv(path)
    print(f"[EDA] Loaded {df.shape[0]} rows × {df.shape[1]} columns from {path}")
    return df


def summary_statistics(df: pd.DataFrame) -> pd.DataFrame:
    """Print and return descriptive statistics."""
    desc = df.describe(include="all").T
    print("\n── Summary Statistics ──")
    print(desc.to_string())
    return desc


def missing_value_report(df: pd.DataFrame) -> pd.DataFrame:
    """Report columns with missing values."""
    mv = df.isnull().sum()
    mv = mv[mv > 0].sort_values(ascending=False)
    pct = (mv / len(df) * 100).round(2)
    report = pd.DataFrame({"missing_count": mv, "missing_pct": pct})
    print("\n── Missing Values ──")
    print(report.to_string())
    return report


def plot_class_balance(df: pd.DataFrame) -> None:
    """Bar chart of target variable distribution."""
    fig, ax = plt.subplots(figsize=(8, 5))
    counts = df[TARGET_COL].value_counts()
    counts.plot.bar(ax=ax, color=sns.color_palette("Set2", len(counts)))
    ax.set_title("Class Distribution – Career Recommendation", fontsize=14)
    ax.set_xlabel("Career Category")
    ax.set_ylabel("Count")
    for i, v in enumerate(counts.values):
        ax.text(i, v + 10, str(v), ha="center", fontweight="bold")
    plt.tight_layout()
    fig.savefig(os.path.join(PLOTS_DIR, "class_balance.png"), dpi=150)
    plt.close(fig)
    print("[EDA] Saved class_balance.png")


def plot_correlation_heatmap(df: pd.DataFrame) -> None:
    """Correlation heatmap for numeric features."""
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    corr = df[numeric_cols].corr()
    fig, ax = plt.subplots(figsize=(12, 10))
    sns.heatmap(corr, annot=True, fmt=".2f", cmap="coolwarm", ax=ax,
                linewidths=0.5, square=True, cbar_kws={"shrink": 0.8})
    ax.set_title("Feature Correlation Heatmap", fontsize=14)
    plt.tight_layout()
    fig.savefig(os.path.join(PLOTS_DIR, "correlation_heatmap.png"), dpi=150)
    plt.close(fig)
    print("[EDA] Saved correlation_heatmap.png")


def plot_feature_distributions(df: pd.DataFrame) -> None:
    """Histograms for all numeric features, coloured by career target."""
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    n = len(numeric_cols)
    cols = 4
    rows = (n + cols - 1) // cols
    fig, axes = plt.subplots(rows, cols, figsize=(5 * cols, 4 * rows))
    axes = axes.flatten()
    for i, col in enumerate(numeric_cols):
        for label in df[TARGET_COL].unique():
            subset = df[df[TARGET_COL] == label][col].dropna()
            axes[i].hist(subset, bins=20, alpha=0.5, label=label)
        axes[i].set_title(col, fontsize=10)
        axes[i].tick_params(labelsize=8)
    # hide unused axes
    for j in range(i + 1, len(axes)):
        axes[j].set_visible(False)
    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="lower center", ncol=3, fontsize=9)
    fig.suptitle("Feature Distributions by Career Category", fontsize=14, y=1.01)
    plt.tight_layout()
    fig.savefig(os.path.join(PLOTS_DIR, "feature_distributions.png"), dpi=150)
    plt.close(fig)
    print("[EDA] Saved feature_distributions.png")


def plot_boxplots(df: pd.DataFrame) -> None:
    """Box-plots of key scores grouped by career category."""
    score_cols = ["math_score", "science_score", "programming_score",
                  "creativity_score", "communication_score", "leadership_score"]
    fig, axes = plt.subplots(2, 3, figsize=(18, 10))
    axes = axes.flatten()
    for i, col in enumerate(score_cols):
        sns.boxplot(x=TARGET_COL, y=col, data=df, ax=axes[i],
                    palette="Set2")
        axes[i].set_title(col, fontsize=11)
        axes[i].set_xlabel("")
        axes[i].tick_params(axis="x", rotation=30, labelsize=8)
    fig.suptitle("Score Distributions by Career Category", fontsize=14)
    plt.tight_layout()
    fig.savefig(os.path.join(PLOTS_DIR, "boxplots_by_career.png"), dpi=150)
    plt.close(fig)
    print("[EDA] Saved boxplots_by_career.png")


def run_eda() -> pd.DataFrame:
    """Run the full EDA pipeline and return the loaded DataFrame."""
    df = load_data()
    summary_statistics(df)
    missing_value_report(df)
    plot_class_balance(df)
    plot_correlation_heatmap(df)
    plot_feature_distributions(df)
    plot_boxplots(df)
    return df


if __name__ == "__main__":
    run_eda()
