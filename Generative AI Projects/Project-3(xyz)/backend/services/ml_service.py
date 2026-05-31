from __future__ import annotations

from functools import lru_cache
from pathlib import Path

import joblib
import pandas as pd

from backend.config.settings import get_settings
from backend.models.schemas import SymptomPayload, SymptomPrediction


@lru_cache
def load_model_bundle() -> dict:
    path = Path(get_settings().ml_model_path)
    if not path.exists():
        raise FileNotFoundError(
            f"ML model not found at {path}. Run python ml/training/train_symptom_model.py first."
        )
    return joblib.load(path)


def predict_symptoms(payload: SymptomPayload) -> SymptomPrediction:
    bundle = load_model_bundle()
    features = bundle["features"]
    frame = pd.DataFrame([payload.model_dump()])[features]
    pipeline = bundle["pipeline"]
    probabilities = pipeline.predict_proba(frame)[0]
    classes = pipeline.classes_
    scored = {label: float(prob) for label, prob in zip(classes, probabilities)}
    disease = max(scored, key=scored.get)
    return SymptomPrediction(
        disease=disease,
        confidence=scored[disease],
        probabilities=scored,
    )

