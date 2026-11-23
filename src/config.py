"""
Configuration constants for the Student Performance & Career Advisory System.
"""
import os

# ──────────────────────────────────────────────
# Paths
# ──────────────────────────────────────────────
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(PROJECT_ROOT, "data")
RAW_DATA_PATH = os.path.join(DATA_DIR, "student_data.csv")
MODELS_DIR = os.path.join(PROJECT_ROOT, "models")
PLOTS_DIR = os.path.join(PROJECT_ROOT, "plots")
RESULTS_DIR = os.path.join(PROJECT_ROOT, "results")

# ──────────────────────────────────────────────
# Reproducibility
# ──────────────────────────────────────────────
RANDOM_SEED = 42
TEST_SIZE = 0.20          # 80-20 stratified split
CV_FOLDS = 5              # Repeated stratified K-Fold
CV_REPEATS = 3            # Number of repeats

# ──────────────────────────────────────────────
# Target column
# ──────────────────────────────────────────────
TARGET_COL = "career_recommendation"

# ──────────────────────────────────────────────
# Career labels (mapped from predicted cluster)
# ──────────────────────────────────────────────
CAREER_LABELS = {
    0: "Data Science / AI",
    1: "Software Engineering",
    2: "Business / Management",
    3: "Research / Academia",
    4: "Creative Arts / Design",
}

# Ensure output directories exist
for d in [MODELS_DIR, PLOTS_DIR, RESULTS_DIR]:
    os.makedirs(d, exist_ok=True)
