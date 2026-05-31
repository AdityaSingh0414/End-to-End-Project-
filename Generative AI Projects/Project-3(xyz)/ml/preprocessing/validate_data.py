from __future__ import annotations

from pathlib import Path

import pandas as pd


REQUIRED_COLUMNS = {
    "patient_id": "int64",
    "age": "int64",
    "gender": "object",
    "temperature_c": "float64",
    "heart_rate": "int64",
    "spo2": "int64",
    "disease": "object",
    "risk_level": "object",
    "visit_date": "object",
}

SYMPTOM_COLUMNS = [
    "fever",
    "cough",
    "fatigue",
    "shortness_of_breath",
    "chest_pain",
    "headache",
    "nausea",
    "sore_throat",
    "body_ache",
    "runny_nose",
]


def validate_symptom_dataset(path: str | Path) -> pd.DataFrame:
    df = pd.read_csv(path)
    missing = [column for column in REQUIRED_COLUMNS if column not in df.columns]
    missing.extend(column for column in SYMPTOM_COLUMNS if column not in df.columns)
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    if df.isna().any().any():
        nulls = df.isna().sum()
        raise ValueError(f"Dataset contains null values: {nulls[nulls > 0].to_dict()}")

    for column in SYMPTOM_COLUMNS:
        invalid = set(df[column].unique()) - {0, 1}
        if invalid:
            raise ValueError(f"{column} must be binary 0/1. Invalid values: {invalid}")

    if not df["spo2"].between(50, 100).all():
        raise ValueError("spo2 must be between 50 and 100")

    if not df["age"].between(0, 120).all():
        raise ValueError("age must be between 0 and 120")

    return df


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[2]
    validate_symptom_dataset(root / "data" / "raw" / "symptom_patient_records.csv")
    print("Validation passed.")

