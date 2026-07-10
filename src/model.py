"""
model.py — ML Model Loading & Prediction Pipeline.

Handles all model I/O (via joblib), feature engineering, and
prediction logic. Every transformation mirrors the exact training
pipeline defined in config.py.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, Tuple

import joblib
import numpy as np
import pandas as pd
import streamlit as st

import config as cfg

# ──────────────────────────────────────────────────────────────────────
# LOGGING
# ──────────────────────────────────────────────────────────────────────
logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
)


# ──────────────────────────────────────────────────────────────────────
# 1. CACHED MODEL / SCALER LOADER
# ──────────────────────────────────────────────────────────────────────
@st.cache_resource(show_spinner="Loading ML assets …")
def load_ml_assets() -> Dict[str, Any]:
    """Load all serialised models and the scaler into memory (once).

    Returns
    -------
    Dict[str, Any]
        A dictionary with keys ``"scaler"`` and one key per model
        name defined in :pydata:`cfg.MODEL_OPTIONS`.
    """
    assets: Dict[str, Any] = {}

    try:
        assets["scaler"] = joblib.load(cfg.SCALER_PATH)
        logger.info("Scaler loaded from %s", cfg.SCALER_PATH)
    except Exception as exc:
        logger.error("Failed to load scaler: %s", exc)
        raise RuntimeError(f"Cannot load scaler: {exc}") from exc

    for model_name, model_path in cfg.MODEL_OPTIONS.items():
        try:
            assets[model_name] = joblib.load(model_path)
            logger.info("Model '%s' loaded from %s", model_name, model_path)
        except Exception as exc:
            logger.error("Failed to load model '%s': %s", model_name, exc)
            raise RuntimeError(
                f"Cannot load model '{model_name}': {exc}"
            ) from exc

    return assets


# ──────────────────────────────────────────────────────────────────────
# 2. PREPROCESSING HELPERS
# ──────────────────────────────────────────────────────────────────────
def _apply_log_transforms(df: pd.DataFrame) -> pd.DataFrame:
    """Apply ``np.log1p`` to Age and Balance columns **in-place**.

    Parameters
    ----------
    df : pd.DataFrame
        Raw feature DataFrame (single row).

    Returns
    -------
    pd.DataFrame
        DataFrame with log-transformed columns.
    """
    for col in cfg.LOG1P_FEATURES:
        df[col] = np.log1p(df[col].astype(float))
    return df


def _encode_dummies(input_data: Dict[str, Any]) -> pd.DataFrame:
    """Create one-hot dummy columns matching the training schema.

    Base categories (France, Female, DIAMOND) are implicitly dropped
    because we only create columns for the non-base categories.

    Parameters
    ----------
    input_data : dict
        Raw user inputs with keys ``Geography``, ``Gender``,
        ``Card Type``.

    Returns
    -------
    pd.DataFrame
        Single-row DataFrame with exactly the dummy columns listed
        in :pydata:`cfg.DUMMY_COLUMNS`, valued 0 or 1.
    """
    dummies: Dict[str, int] = {col: 0 for col in cfg.DUMMY_COLUMNS}

    geography = input_data.get("Geography", "France")
    if geography == "Germany":
        dummies["Geography_Germany"] = 1
    elif geography == "Spain":
        dummies["Geography_Spain"] = 1

    gender = input_data.get("Gender", "Female")
    if gender == "Male":
        dummies["Gender_Male"] = 1

    card_type = input_data.get("Card Type", "DIAMOND")
    if card_type == "GOLD":
        dummies["Card Type_GOLD"] = 1
    elif card_type == "PLATINUM":
        dummies["Card Type_PLATINUM"] = 1
    elif card_type == "SILVER":
        dummies["Card Type_SILVER"] = 1

    return pd.DataFrame([dummies])


def _map_satisfaction_score(score: int) -> int:
    """Map a 1-5 Satisfaction Score to its integer code (0-4).

    Parameters
    ----------
    score : int
        Raw satisfaction score from the UI (1 through 5).

    Returns
    -------
    int
        Mapped integer code (score − 1).
    """
    return int(score) - 1


# ──────────────────────────────────────────────────────────────────────
# 3. CORE PREDICTION FUNCTION
# ──────────────────────────────────────────────────────────────────────
def predict_customer_churn(
    model_name: str,
    input_data: Dict[str, Any],
) -> Tuple[int, float]:
    """Run the full preprocessing → prediction pipeline.

    Parameters
    ----------
    model_name : str
        Key from :pydata:`cfg.MODEL_OPTIONS` (e.g. ``"Random Forest"``).
    input_data : dict
        Raw inputs captured from the Streamlit UI.

    Returns
    -------
    Tuple[int, float]
        ``(prediction_class, churn_probability)`` where
        *prediction_class* is 0 (no churn) or 1 (churn) and
        *churn_probability* is the model's confidence in class 1.

    Raises
    ------
    ValueError
        If the selected model name is not in the registry.
    RuntimeError
        If any preprocessing or prediction step fails.
    """
    # --- Load cached assets ------------------------------------------------
    assets = load_ml_assets()
    scaler = assets["scaler"]

    if model_name not in assets:
        raise ValueError(
            f"Unknown model '{model_name}'. "
            f"Available: {list(cfg.MODEL_OPTIONS.keys())}"
        )
    model = assets[model_name]

    try:
        # --- Build numeric feature DataFrame -------------------------------
        numeric_data = {
            "CreditScore": float(input_data["CreditScore"]),
            "Age": float(input_data["Age"]),
            "Tenure": int(input_data["Tenure"]),
            "Balance": float(input_data["Balance"]),
            "EstimatedSalary": float(input_data["EstimatedSalary"]),
            "Point Earned": float(input_data["Point Earned"]),
        }
        df_numeric = pd.DataFrame([numeric_data])

        # Step 1: Log-transform Age & Balance
        df_numeric = _apply_log_transforms(df_numeric)

        # Step 2: Scale the numeric columns (order guaranteed by list)
        scaled_values = scaler.transform(
            df_numeric[cfg.SCALED_NUMERIC_FEATURES]
        )
        df_scaled = pd.DataFrame(
            scaled_values, columns=cfg.SCALED_NUMERIC_FEATURES
        )

        # --- Build passthrough columns ------------------------------------
        # RowNumber & CustomerId were present during training but carry no
        # predictive signal — hardcoded to 0 so the feature schema matches.
        passthrough_data = {
            "RowNumber": 0,
            "CustomerId": 0,
            "NumOfProducts": int(input_data["NumOfProducts"]),
            "HasCrCard": int(input_data["HasCrCard"]),
            "IsActiveMember": int(input_data["IsActiveMember"]),
            "Complain": int(input_data.get("Complain", 0)),
            "Satisfaction Score": _map_satisfaction_score(
                input_data["Satisfaction Score"]
            ),
        }
        df_passthrough = pd.DataFrame([passthrough_data])

        # --- Build dummy columns -------------------------------------------
        df_dummies = _encode_dummies(input_data)

        # --- Concatenate in the exact order the model expects --------------
        df_final = pd.concat(
            [df_scaled, df_passthrough, df_dummies],
            axis=1,
        )
        df_final = df_final[cfg.FINAL_FEATURE_ORDER]

        logger.info(
            "Final feature vector shape: %s — columns: %s",
            df_final.shape,
            list(df_final.columns),
        )

        # --- Predict -------------------------------------------------------
        prediction: int = int(model.predict(df_final)[0])
        probability: float = float(model.predict_proba(df_final)[0][1])

        logger.info(
            "Model=%s | Prediction=%d | Probability=%.4f",
            model_name,
            prediction,
            probability,
        )

        return prediction, probability

    except Exception as exc:
        logger.exception("Prediction pipeline error: %s", exc)
        raise RuntimeError(
            f"Prediction failed during preprocessing: {exc}"
        ) from exc
