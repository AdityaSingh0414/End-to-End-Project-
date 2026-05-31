"""
generate_bank_data.py — Generate synthetic training data for the
multi-bank loan approval model.

Produces 10,000 rows with features:
  credit_score, monthly_income, age, existing_emis,
  employment_type, loan_amount, property_owned,
  annual_income, dti_ratio, income_to_loan_ratio, approved (label)

The label is generated using realistic banking rules so the model
learns meaningful patterns.
"""

import os
import sys
import numpy as np
import pandas as pd

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from src.utils import get_logger

logger = get_logger("generate_bank_data")

SEED = 42
N_SAMPLES = 10_000
OUTPUT_DIR = os.path.join("data", "bank")
OUTPUT_PATH = os.path.join(OUTPUT_DIR, "bank_loan_data.csv")


def generate():
    np.random.seed(SEED)

    # ── Feature generation ────────────────────────────────────────────────
    credit_score = np.random.normal(700, 80, N_SAMPLES).clip(300, 850).astype(int)

    # Income: log-normal so we get a realistic right skew
    monthly_income = np.random.lognormal(mean=10.8, sigma=0.6, size=N_SAMPLES)
    monthly_income = np.clip(monthly_income, 8000, 500000).astype(int)

    age = np.random.normal(35, 10, N_SAMPLES).clip(21, 65).astype(int)

    # Employment type  (0=Salaried 60%, 1=Self-Employed 20%, 2=Business 12%, 3=Unemployed 5%, 4=Retired 3%)
    employment_type = np.random.choice(
        [0, 1, 2, 3, 4],
        size=N_SAMPLES,
        p=[0.60, 0.20, 0.12, 0.05, 0.03],
    )

    # Existing EMIs: proportional to income with noise
    existing_emis = (monthly_income * np.random.uniform(0, 0.45, N_SAMPLES)).astype(int)

    # Loan amount requested: 1x–8x annual income with noise
    annual_income = monthly_income * 12
    loan_mult = np.random.uniform(0.5, 7.0, N_SAMPLES)
    loan_amount = (annual_income * loan_mult / 100000).astype(int) * 100000  # round to lakhs
    loan_amount = np.clip(loan_amount, 100000, 50000000)

    # Property owned: higher probability for older / higher income
    prop_prob = 0.3 + 0.3 * (age - 21) / 44 + 0.2 * (monthly_income - 8000) / 492000
    property_owned = (np.random.rand(N_SAMPLES) < prop_prob).astype(int)

    # ── Derived features ──────────────────────────────────────────────────
    dti_ratio = np.where(monthly_income > 0, existing_emis / monthly_income, 1.0)
    income_to_loan_ratio = annual_income / (loan_amount + 1)

    # ── Label generation (realistic rules) ────────────────────────────────
    score = np.zeros(N_SAMPLES, dtype=float)

    # Credit score contribution (0–40 points)
    score += np.where(credit_score >= 750, 35, 0)
    score += np.where((credit_score >= 700) & (credit_score < 750), 25, 0)
    score += np.where((credit_score >= 650) & (credit_score < 700), 15, 0)
    score += np.where((credit_score >= 600) & (credit_score < 650), 5, 0)

    # income contribution (0–20)
    score += np.clip((monthly_income - 10000) / 50000 * 20, 0, 20)

    # DTI penalty (0 to -20)
    score -= np.clip(dti_ratio * 40, 0, 20)

    # Loan-to-income penalty (higher loan = harder)
    score -= np.clip(loan_mult * 2, 0, 15)

    # Employment bonus
    score += np.where(employment_type == 0, 8, 0)   # salaried
    score += np.where(employment_type == 1, 4, 0)   # self-employed
    score += np.where(employment_type == 2, 5, 0)   # business
    score += np.where(employment_type == 3, -10, 0)  # unemployed
    score += np.where(employment_type == 4, 2, 0)   # retired

    # Property bonus
    score += property_owned * 5

    # Age sweet-spot bonus (28-50)
    score += np.where((age >= 28) & (age <= 50), 3, 0)

    # Add noise
    score += np.random.normal(0, 5, N_SAMPLES)

    # Threshold: > 25 => approved
    approved = (score > 25).astype(int)

    logger.info(f"Approval rate: {approved.mean():.2%}")

    # ── Build DataFrame ───────────────────────────────────────────────────
    df = pd.DataFrame({
        "credit_score": credit_score,
        "monthly_income": monthly_income,
        "age": age,
        "existing_emis": existing_emis,
        "employment_type": employment_type,
        "loan_amount": loan_amount,
        "property_owned": property_owned,
        "annual_income": annual_income,
        "dti_ratio": np.round(dti_ratio, 4),
        "income_to_loan_ratio": np.round(income_to_loan_ratio, 4),
        "approved": approved,
    })

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    df.to_csv(OUTPUT_PATH, index=False)
    logger.info(f"Saved {len(df)} rows -> {OUTPUT_PATH}")
    print(f"\n[OK] Generated {len(df):,} rows -> {OUTPUT_PATH}")
    print(f"     Approval rate: {approved.mean():.2%}")
    print(f"     Features: {list(df.columns)}")
    return df


if __name__ == "__main__":
    generate()
