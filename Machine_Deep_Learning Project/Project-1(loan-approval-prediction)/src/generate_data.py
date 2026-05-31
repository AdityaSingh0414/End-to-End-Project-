"""
generate_data.py — Generates a realistic synthetic loan dataset (loan_data.csv).
Run once to create: data/raw/loan_data.csv
"""

import os
import numpy as np
import pandas as pd

SEED = 42
N = 5000

def generate_loan_data(n: int = N, seed: int = SEED) -> pd.DataFrame:
    rng = np.random.default_rng(seed)

    gender         = rng.choice(["Male", "Female"], n, p=[0.80, 0.20])
    married        = rng.choice(["Yes", "No"],      n, p=[0.65, 0.35])
    dependents     = rng.choice(["0", "1", "2", "3+"], n, p=[0.57, 0.17, 0.16, 0.10])
    education      = rng.choice(["Graduate", "Not Graduate"], n, p=[0.78, 0.22])
    self_employed  = rng.choice(["Yes", "No"], n, p=[0.14, 0.86])
    property_area  = rng.choice(["Urban", "Semiurban", "Rural"], n, p=[0.39, 0.38, 0.23])

    # Income — log-normal to mimic real-world skew
    applicant_income   = np.round(rng.lognormal(mean=8.7, sigma=0.6, size=n)).astype(int)
    coapplicant_income = np.where(
        married == "Yes",
        np.round(rng.lognormal(mean=7.5, sigma=0.8, size=n)).astype(int),
        0
    )

    loan_amount      = np.round(rng.lognormal(mean=4.9, sigma=0.4, size=n)).astype(int)
    loan_amount_term = rng.choice([12, 36, 60, 84, 120, 180, 240, 300, 360, 480], n,
                                   p=[0.01, 0.02, 0.02, 0.02, 0.03, 0.05, 0.04, 0.09, 0.68, 0.04])
    credit_history   = rng.choice([1.0, 0.0], n, p=[0.84, 0.16])

    # Convert integer arrays to float so NaN can be assigned later
    applicant_income = applicant_income.astype(float)
    loan_amount      = loan_amount.astype(float)

    # ── Approval Logic (simulate a real credit decision) ─────────────────────
    score = np.zeros(n)
    score += np.where(credit_history == 1.0, 35, -30)
    score += np.where(education == "Graduate", 10, -5)
    score += np.where(married == "Yes", 5, 0)
    score += np.where(property_area == "Semiurban", 5,
              np.where(property_area == "Urban", 3, 0))
    score += np.clip((applicant_income + coapplicant_income * 0.5) / 5000, 0, 20)
    score -= np.clip(loan_amount / 50, 0, 20)
    score += rng.normal(0, 5, n)          # noise

    loan_status = np.where(score > 10, "Y", "N")

    # Reintroduce NaN for missing simulation
    nan_mask = rng.random(n) < 0.04
    loan_amount_f = loan_amount.astype(float)
    loan_amount_f[nan_mask] = np.nan

    gender_m = gender.copy().astype(object)
    gender_m[rng.random(n) < 0.02] = np.nan

    dep_m = dependents.copy().astype(object)
    dep_m[rng.random(n) < 0.02] = np.nan

    se_m = self_employed.copy().astype(object)
    se_m[rng.random(n) < 0.03] = np.nan

    ch_m = credit_history.copy()
    ch_m[rng.random(n) < 0.07] = np.nan

    df = pd.DataFrame({
        "Loan_ID":            [f"LP{str(i).zfill(6)}" for i in range(1, n + 1)],
        "Gender":             gender_m,
        "Married":            married,
        "Dependents":         dep_m,
        "Education":          education,
        "Self_Employed":      se_m,
        "ApplicantIncome":    applicant_income,
        "CoapplicantIncome":  coapplicant_income,
        "LoanAmount":         loan_amount_f,
        "Loan_Amount_Term":   loan_amount_term.astype(float),
        "Credit_History":     ch_m,
        "Property_Area":      property_area,
        "Loan_Status":        loan_status,
    })
    return df


if __name__ == "__main__":
    os.makedirs("data/raw", exist_ok=True)
    df = generate_loan_data()
    out = "data/raw/loan_data.csv"
    df.to_csv(out, index=False)
    print(f"[OK] Dataset saved -> {out}  ({len(df):,} rows x {df.shape[1]} cols)")
    print(f"    Approval rate : {(df['Loan_Status'] == 'Y').mean():.1%}")
    print(f"    Missing values:\n{df.isnull().sum().to_string()}")
