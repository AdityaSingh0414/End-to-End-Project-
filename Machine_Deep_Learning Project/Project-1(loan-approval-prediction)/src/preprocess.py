"""
preprocess.py — Data cleaning, encoding, and feature engineering pipeline.
Reads:  data/raw/loan_data.csv
Writes: data/processed/clean_data.csv  +  models/preprocessor.pkl
"""

import os
import sys
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
import joblib

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from src.utils import (get_logger, save_model, FEATURE_COLS,
                       CATEGORICAL_COLS, NUMERICAL_COLS,
                       TARGET_COL, LABEL_MAPS)

logger = get_logger("preprocess")

RAW_PATH       = os.path.join("data", "raw",       "loan_data.csv")
PROCESSED_PATH = os.path.join("data", "processed", "clean_data.csv")
SCALER_PATH    = os.path.join("models",            "preprocessor.pkl")


# ─── Step 1: Load ─────────────────────────────────────────────────────────────
def load_data(path: str = RAW_PATH) -> pd.DataFrame:
    logger.info(f"Loading raw data from: {path}")
    df = pd.read_csv(path)
    logger.info(f"Shape: {df.shape}  |  Columns: {list(df.columns)}")
    return df


# ─── Step 2: Drop ID column ───────────────────────────────────────────────────
def drop_id(df: pd.DataFrame) -> pd.DataFrame:
    if "Loan_ID" in df.columns:
        df = df.drop(columns=["Loan_ID"])
        logger.info("Dropped 'Loan_ID' column.")
    return df


# ─── Step 3: Handle Missing Values ────────────────────────────────────────────
def handle_missing(df: pd.DataFrame) -> pd.DataFrame:
    logger.info("Handling missing values...")
    before = df.isnull().sum().sum()

    # Categorical — fill with mode
    for col in CATEGORICAL_COLS:
        if col in df.columns and df[col].isnull().any():
            mode_val = df[col].mode()[0]
            df[col].fillna(mode_val, inplace=True)
            logger.info(f"  {col}: filled {df[col].isnull().sum()} NaN → mode='{mode_val}'")

    # Numerical — fill with median
    for col in NUMERICAL_COLS:
        if col in df.columns and df[col].isnull().any():
            median_val = df[col].median()
            df[col].fillna(median_val, inplace=True)
            logger.info(f"  {col}: filled NaN → median={median_val:.2f}")

    after = df.isnull().sum().sum()
    logger.info(f"Missing values: {before} → {after}")
    return df


# ─── Step 4: Encode Categorical Variables ─────────────────────────────────────
def encode_categoricals(df: pd.DataFrame) -> pd.DataFrame:
    logger.info("Encoding categorical columns...")
    for col, mapping in LABEL_MAPS.items():
        if col in df.columns:
            df[col] = df[col].map(mapping)
            logger.info(f"  Encoded '{col}' → {mapping}")
    return df


# ─── Step 5: Feature Engineering ──────────────────────────────────────────────
def feature_engineering(df: pd.DataFrame) -> pd.DataFrame:
    logger.info("Engineering new features...")
    df["Total_Income"] = df["ApplicantIncome"] + df["CoapplicantIncome"]
    df["Income_to_Loan_Ratio"] = df["Total_Income"] / (df["LoanAmount"] + 1)
    df["EMI"]                  = df["LoanAmount"] / (df["Loan_Amount_Term"] + 1)
    df["Balance_Income"]       = df["Total_Income"] - (df["EMI"] * 1000)
    logger.info("  Added: Total_Income, Income_to_Loan_Ratio, EMI, Balance_Income")
    return df


# ─── Step 6: Scale Numerical Features ─────────────────────────────────────────
def scale_features(df: pd.DataFrame, fit: bool = True):
    scale_cols = NUMERICAL_COLS + [
        "Total_Income", "Income_to_Loan_Ratio", "EMI", "Balance_Income"
    ]
    scale_cols = [c for c in scale_cols if c in df.columns]

    scaler = StandardScaler()
    df[scale_cols] = scaler.fit_transform(df[scale_cols]) if fit \
                     else scaler.transform(df[scale_cols])

    if fit:
        save_model({"scaler": scaler, "scale_cols": scale_cols}, SCALER_PATH)
        logger.info(f"Scaler fitted and saved → {SCALER_PATH}")
    return df, scaler


# ─── Main Pipeline ────────────────────────────────────────────────────────────
def run_preprocessing(save: bool = True):
    df = load_data()
    df = drop_id(df)
    df = handle_missing(df)
    df = encode_categoricals(df)
    df = feature_engineering(df)
    df, _ = scale_features(df, fit=True)

    if df[TARGET_COL].isnull().any():
        df.dropna(subset=[TARGET_COL], inplace=True)

    logger.info(f"Final shape: {df.shape}")
    logger.info(f"Class distribution:\n{df[TARGET_COL].value_counts()}")

    if save:
        os.makedirs("data/processed", exist_ok=True)
        df.to_csv(PROCESSED_PATH, index=False)
        logger.info(f"Clean data saved → {PROCESSED_PATH}")

    return df


if __name__ == "__main__":
    run_preprocessing()
    print("\n[OK] Preprocessing complete!")
