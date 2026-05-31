"""
utils.py — Shared utility functions for the Loan Approval ML project.
"""

import os
import logging
import joblib
import numpy as np

# ─── Logging Setup ────────────────────────────────────────────────────────────
def get_logger(name: str) -> logging.Logger:
    """Returns a configured logger."""
    os.makedirs("logs", exist_ok=True)
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    if not logger.handlers:
        fmt = logging.Formatter("[%(asctime)s] %(levelname)s — %(name)s — %(message)s",
                                datefmt="%Y-%m-%d %H:%M:%S")
        # Console handler
        ch = logging.StreamHandler()
        ch.setFormatter(fmt)
        logger.addHandler(ch)
        # File handler
        fh = logging.FileHandler(os.path.join("logs", "project.log"))
        fh.setFormatter(fmt)
        logger.addHandler(fh)
    return logger


# ─── Model I/O ────────────────────────────────────────────────────────────────
def save_model(obj, path: str):
    """Save a model or object to disk using joblib."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    joblib.dump(obj, path)
    get_logger("utils").info(f"Saved -> {path}")


def load_model(path: str):
    """Load a model or object from disk using joblib."""
    if not os.path.exists(path):
        raise FileNotFoundError(f"Model file not found: {path}")
    return joblib.load(path)


# ─── Feature Definitions ──────────────────────────────────────────────────────
FEATURE_COLS = [
    "Gender", "Married", "Dependents", "Education", "Self_Employed",
    "ApplicantIncome", "CoapplicantIncome", "LoanAmount",
    "Loan_Amount_Term", "Credit_History", "Property_Area"
]

CATEGORICAL_COLS = [
    "Gender", "Married", "Dependents", "Education",
    "Self_Employed", "Property_Area"
]

NUMERICAL_COLS = [
    "ApplicantIncome", "CoapplicantIncome",
    "LoanAmount", "Loan_Amount_Term", "Credit_History"
]

TARGET_COL = "Loan_Status"

# ─── Label Mappings ───────────────────────────────────────────────────────────
LABEL_MAPS = {
    "Gender":        {"Male": 1, "Female": 0},
    "Married":       {"Yes": 1, "No": 0},
    "Dependents":    {"0": 0, "1": 1, "2": 2, "3+": 3},
    "Education":     {"Graduate": 1, "Not Graduate": 0},
    "Self_Employed": {"Yes": 1, "No": 0},
    "Property_Area": {"Urban": 2, "Semiurban": 1, "Rural": 0},
    "Loan_Status":   {"Y": 1, "N": 0},
}

REVERSE_LABEL_MAPS = {
    col: {v: k for k, v in mapping.items()}
    for col, mapping in LABEL_MAPS.items()
}


def encode_input(raw: dict) -> dict:
    """
    Encode a single raw input dict (from form/API) into numeric values
    ready for model inference.
    """
    encoded = {}
    for col in FEATURE_COLS:
        val = raw.get(col)
        if col in LABEL_MAPS:
            encoded[col] = LABEL_MAPS[col].get(str(val), 0)
        else:
            encoded[col] = float(val) if val is not None else 0.0
    return encoded
