"""
config.py — Central Configuration for the Customer Churn Prediction App.

Defines all constants, paths, feature lists, and UI option mappings
used across the application. Ensures a single source of truth for
the data-preprocessing contract established during model training.
"""

from pathlib import Path
from typing import Dict, List

# ──────────────────────────────────────────────────────────────────────
# 1. PROJECT PATHS
# ──────────────────────────────────────────────────────────────────────
_SRC_DIR: Path = Path(__file__).resolve().parent
PROJECT_ROOT: Path = _SRC_DIR.parent
MODELS_DIR: Path = PROJECT_ROOT / "models"

SCALER_PATH: Path = MODELS_DIR / "scaler.pkl"
LOGISTIC_REGRESSION_PATH: Path = MODELS_DIR / "logistic_regression.pkl"
RANDOM_FOREST_PATH: Path = MODELS_DIR / "random_forest.pkl"
XGBOOST_PATH: Path = MODELS_DIR / "xgboost_classifier.pkl"

# ──────────────────────────────────────────────────────────────────────
# 2. MODEL REGISTRY
# ──────────────────────────────────────────────────────────────────────
MODEL_OPTIONS: Dict[str, Path] = {
    "Random Forest": RANDOM_FOREST_PATH,
    "Logistic Regression": LOGISTIC_REGRESSION_PATH,
    "XGBoost": XGBOOST_PATH,
}

DEFAULT_MODEL: str = "Random Forest"

# ──────────────────────────────────────────────────────────────────────
# 3. UI DROPDOWN / WIDGET OPTIONS
# ──────────────────────────────────────────────────────────────────────
GEOGRAPHY_OPTIONS: List[str] = ["France", "Spain", "Germany"]
GENDER_OPTIONS: List[str] = ["Female", "Male"]
CARD_TYPE_OPTIONS: List[str] = ["DIAMOND", "GOLD", "PLATINUM", "SILVER"]
SATISFACTION_SCORE_OPTIONS: List[int] = [1, 2, 3, 4, 5]
BINARY_OPTIONS: Dict[str, int] = {"Yes": 1, "No": 0}

# ──────────────────────────────────────────────────────────────────────
# 4. FEATURE ENGINEERING CONTRACT
# ──────────────────────────────────────────────────────────────────────
LOG1P_FEATURES: List[str] = ["Age", "Balance"]

SCALED_NUMERIC_FEATURES: List[str] = [
    "CreditScore",
    "Age",
    "Tenure",
    "Balance",
    "EstimatedSalary",
    "Point Earned",
]

DUMMY_COLUMNS: List[str] = [
    "Geography_Germany",
    "Geography_Spain",
    "Gender_Male",
    "Card Type_GOLD",
    "Card Type_PLATINUM",
    "Card Type_SILVER",
]

# These passthrough features are NOT scaled but are required by the model.
# RowNumber and CustomerId were present during training; they are set to 0
# at inference time (they carry no predictive signal but the model schema
# requires them).
PASSTHROUGH_FEATURES: List[str] = [
    "RowNumber",
    "CustomerId",
    "NumOfProducts",
    "HasCrCard",
    "IsActiveMember",
    "Complain",
    "Satisfaction Score",
]

# Final column order expected by model.predict()  — must match training.
FINAL_FEATURE_ORDER: List[str] = [
    "CreditScore",
    "Age",
    "Tenure",
    "Balance",
    "EstimatedSalary",
    "Point Earned",
    "RowNumber",
    "CustomerId",
    "NumOfProducts",
    "HasCrCard",
    "IsActiveMember",
    "Complain",
    "Satisfaction Score",
    "Geography_Germany",
    "Geography_Spain",
    "Gender_Male",
    "Card Type_GOLD",
    "Card Type_PLATINUM",
    "Card Type_SILVER",
]

# ──────────────────────────────────────────────────────────────────────
# 5. APP METADATA
# ──────────────────────────────────────────────────────────────────────
APP_TITLE: str = "Customer Churn Predictor"
APP_ICON: str = "🔮"
APP_DESCRIPTION: str = (
    "An AI-powered dashboard that predicts customer churn risk "
    "using state-of-the-art Machine Learning models trained on "
    "real banking data."
)
