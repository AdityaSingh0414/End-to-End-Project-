"""
predict.py — Inference helpers for single applicant prediction.
Used by Flask app.py.
"""

import os
import sys
import numpy as np
import pandas as pd

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from src.utils import (get_logger, load_model, FEATURE_COLS,
                       CATEGORICAL_COLS, NUMERICAL_COLS, LABEL_MAPS)

logger = get_logger("predict")

MODEL_PATH      = os.path.join("models", "loan_model.pkl")
SCALER_PATH     = os.path.join("models", "preprocessor.pkl")
FEAT_IMP_PATH   = os.path.join("models", "feature_importance.pkl")

_model       = None
_scaler_info = None
_feat_imp    = None


def _load_artifacts():
    global _model, _scaler_info, _feat_imp
    if _model is None:
        _model       = load_model(MODEL_PATH)
        _scaler_info = load_model(SCALER_PATH)
        _feat_imp    = load_model(FEAT_IMP_PATH)
        logger.info("Model artifacts loaded.")


def _encode(raw: dict) -> dict:
    """Encode raw string inputs to numeric values."""
    encoded = {}
    for col in FEATURE_COLS:
        val = raw.get(col)
        if col in LABEL_MAPS:
            key = str(val).strip()
            encoded[col] = LABEL_MAPS[col].get(key, 0)
        else:
            try:
                encoded[col] = float(val)
            except (TypeError, ValueError):
                encoded[col] = 0.0
    return encoded


def _engineer(df: pd.DataFrame) -> pd.DataFrame:
    """Replicate the same feature engineering done during training."""
    df["Total_Income"]         = df["ApplicantIncome"] + df["CoapplicantIncome"]
    df["Income_to_Loan_Ratio"] = df["Total_Income"] / (df["LoanAmount"] + 1)
    df["EMI"]                  = df["LoanAmount"] / (df["Loan_Amount_Term"] + 1)
    df["Balance_Income"]       = df["Total_Income"] - (df["EMI"] * 1000)
    return df


def _scale(df: pd.DataFrame) -> pd.DataFrame:
    """Apply the fitted StandardScaler to numeric columns."""
    scaler     = _scaler_info["scaler"]
    scale_cols = [c for c in _scaler_info["scale_cols"] if c in df.columns]
    df[scale_cols] = scaler.transform(df[scale_cols])
    return df


def predict_single(raw_input: dict) -> dict:
    """
    Accepts a raw dict from the form/API, returns prediction dict:
    {
        "decision":    "Approved" | "Rejected",
        "probability": 0.0 – 1.0,
        "confidence":  "High" | "Medium" | "Low",
        "top_factors": [{"feature": str, "importance": float}, ...],
        "recommendation": str
    }
    """
    _load_artifacts()

    # 1. Encode
    encoded = _encode(raw_input)
    df = pd.DataFrame([encoded])

    # 2. Feature engineering
    df = _engineer(df)

    # 3. Scale
    df = _scale(df)

    # 4. Predict
    prob   = float(_model.predict_proba(df)[0][1])
    label  = int(_model.predict(df)[0])
    decision = "Approved" if label == 1 else "Rejected"

    # 5. Confidence tier
    if prob >= 0.75 or prob <= 0.25:
        confidence = "High"
    elif prob >= 0.60 or prob <= 0.40:
        confidence = "Medium"
    else:
        confidence = "Low"

    # 6. Top 3 contributing factors
    top_factors = [
        {"feature": feat, "importance": round(float(imp), 4)}
        for feat, imp in list(_feat_imp.items())[:3]
    ]

    # 7. Recommendation
    rejection_tips = []
    enc = encoded
    if enc.get("Credit_History", 1) == 0:
        rejection_tips.append("Improve your credit history — it is the strongest predictor.")
    if (enc.get("ApplicantIncome", 0) + enc.get("CoapplicantIncome", 0)) < 5000:
        rejection_tips.append("Increase income or add a co-applicant.")
    if enc.get("LoanAmount", 0) > 300:
        rejection_tips.append("Consider requesting a lower loan amount.")

    if decision == "Approved":
        recommendation = "Congratulations! Maintain your credit score and repay on time."
    elif rejection_tips:
        recommendation = " | ".join(rejection_tips)
    else:
        recommendation = ("Your application was not approved at this time. "
                          "Consider reviewing your income-to-debt ratio.")

    return {
        "decision":       decision,
        "probability":    round(prob * 100, 1),
        "confidence":     confidence,
        "top_factors":    top_factors,
        "recommendation": recommendation,
    }
