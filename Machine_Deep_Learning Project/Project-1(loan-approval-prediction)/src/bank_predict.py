"""
bank_predict.py — Hybrid ML + rule-based prediction for multi-bank system.

Loads the trained bank_model once at module level for performance.
Combines ML approval probability with per-bank risk adjustments.
"""

import os
import numpy as np
import pandas as pd
import joblib

from src.utils import get_logger

logger = get_logger("bank_predict")

MODEL_PATH = os.path.join("models", "bank_model.pkl")
PREPROCESSOR_PATH = os.path.join("models", "bank_preprocessor.pkl")

# Module-level singletons — loaded once
_model = None
_preprocessor = None


def _load_model():
    """Load model and preprocessor once into module-level cache."""
    global _model, _preprocessor
    if _model is None:
        if not os.path.exists(MODEL_PATH):
            raise FileNotFoundError(
                f"Bank model not found: {MODEL_PATH}. "
                "Run train_bank_model.py first."
            )
        _model = joblib.load(MODEL_PATH)
        _preprocessor = joblib.load(PREPROCESSOR_PATH)
        logger.info("Bank model artifacts loaded (cached).")


# Risk multipliers adjust ML probability per bank risk tolerance
RISK_MULT = {"low": 0.90, "medium": 1.00, "high": 1.10}

EMPLOYMENT_MAP = {
    "Salaried": 0,
    "Self-Employed": 1,
    "Business": 2,
    "Unemployed": 3,
    "Retired": 4,
}


def predict_approval(user: dict, bank: dict) -> float:
    """
    Return approval probability (0.0–1.0) for a user at a specific bank.

    Pipeline:
      1. Build feature vector
      2. Scale with saved preprocessor
      3. Get base probability from ML model
      4. Adjust by bank risk tolerance
      5. Clamp to [0, 1]
    """
    _load_model()

    features = _build_features(user)
    df = pd.DataFrame([features])

    # Scale numerical columns
    scale_cols = _preprocessor["scale_cols"]
    present = [c for c in scale_cols if c in df.columns]
    df[present] = _preprocessor["scaler"].transform(df[present])

    # ML probability
    base_prob = float(_model.predict_proba(df)[0][1])

    # Adjust by bank risk tolerance
    risk = bank.get("risk_tolerance", "medium")
    adjusted = base_prob * RISK_MULT.get(risk, 1.0)

    # Credit score bonus (small nudge for excellent scores)
    cs = user.get("credit_score", 0)
    if cs >= 800:
        adjusted += 0.05
    elif cs >= 750:
        adjusted += 0.02

    return round(min(max(adjusted, 0.0), 1.0), 4)


def get_top_features(user: dict, n: int = 5) -> list:
    """
    Return top-N feature importances from the trained model.
    """
    _load_model()
    feature_names = [
        "credit_score", "monthly_income", "age",
        "existing_emis", "employment_type",
        "loan_amount", "property_owned",
        "annual_income", "dti_ratio",
        "income_to_loan_ratio",
    ]
    if hasattr(_model, "feature_importances_"):
        importances = _model.feature_importances_
    else:
        importances = np.abs(_model.coef_[0])

    pairs = sorted(
        zip(feature_names, importances), key=lambda x: x[1], reverse=True
    )
    return [{"feature": f, "importance": round(float(v), 4)} for f, v in pairs[:n]]


def _build_features(user: dict) -> dict:
    """Build the feature dict expected by the model."""
    monthly_income = user.get("monthly_income", 0)
    annual_income = monthly_income * 12
    existing_emis = user.get("existing_emis", 0)
    loan_amount = user.get("loan_amount", 0)
    dti = existing_emis / monthly_income if monthly_income > 0 else 1.0
    itl = annual_income / (loan_amount + 1)

    return {
        "credit_score": user.get("credit_score", 0),
        "monthly_income": monthly_income,
        "age": user.get("age", 0),
        "existing_emis": existing_emis,
        "employment_type": EMPLOYMENT_MAP.get(
            user.get("employment_type", "Salaried"), 0
        ),
        "loan_amount": loan_amount,
        "property_owned": 1 if user.get("property_owned", False) else 0,
        "annual_income": annual_income,
        "dti_ratio": round(dti, 4),
        "income_to_loan_ratio": round(itl, 4),
    }
