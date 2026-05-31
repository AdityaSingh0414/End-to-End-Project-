from __future__ import annotations

from pathlib import Path

import joblib
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.tree import DecisionTreeClassifier

import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(ROOT))

from ml.preprocessing.validate_data import SYMPTOM_COLUMNS, validate_symptom_dataset


NUMERIC_COLUMNS = ["age", "temperature_c", "heart_rate", "spo2", *SYMPTOM_COLUMNS]
CATEGORICAL_COLUMNS = ["gender"]
MODEL_PATH = ROOT / "ml" / "saved_models" / "symptom_model.joblib"
REPORT_PATH = ROOT / "ml" / "saved_models" / "symptom_model_report.txt"


def build_pipeline(model) -> Pipeline:
    preprocessor = ColumnTransformer(
        transformers=[
            ("num", StandardScaler(), NUMERIC_COLUMNS),
            ("cat", OneHotEncoder(handle_unknown="ignore"), CATEGORICAL_COLUMNS),
        ]
    )
    return Pipeline([("preprocess", preprocessor), ("model", model)])


def train() -> None:
    data_path = ROOT / "data" / "raw" / "symptom_patient_records.csv"
    df = validate_symptom_dataset(data_path)
    x = df[NUMERIC_COLUMNS + CATEGORICAL_COLUMNS]
    y = df["disease"]

    x_train, x_test, y_train, y_test = train_test_split(
        x, y, test_size=0.2, random_state=42, stratify=y
    )

    candidates = {
        "logistic_regression": LogisticRegression(max_iter=1000),
        "decision_tree": DecisionTreeClassifier(max_depth=8, random_state=42),
        "random_forest": RandomForestClassifier(n_estimators=220, random_state=42),
    }

    results = {}
    best_name = ""
    best_pipeline = None
    best_score = -1.0
    for name, model in candidates.items():
        pipeline = build_pipeline(model)
        pipeline.fit(x_train, y_train)
        preds = pipeline.predict(x_test)
        score = accuracy_score(y_test, preds)
        results[name] = score
        if score > best_score:
            best_name = name
            best_score = score
            best_pipeline = pipeline

    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(
        {
            "model_name": best_name,
            "pipeline": best_pipeline,
            "features": NUMERIC_COLUMNS + CATEGORICAL_COLUMNS,
            "labels": sorted(y.unique()),
            "scores": results,
        },
        MODEL_PATH,
    )

    report = classification_report(y_test, best_pipeline.predict(x_test))
    REPORT_PATH.write_text(
        f"Best model: {best_name}\nScores: {results}\n\n{report}",
        encoding="utf-8",
    )
    print(f"Saved {best_name} model to {MODEL_PATH}")


if __name__ == "__main__":
    train()

