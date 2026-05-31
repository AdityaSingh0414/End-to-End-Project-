import csv
import io
from typing import Any

from backend.schemas.patient_schema import PatientCreate
from backend.utils.helpers import normalize_text


def _to_float(value: Any, fallback: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return fallback


def _to_int(value: Any, fallback: int = 0) -> int:
    try:
        return int(float(value))
    except (TypeError, ValueError):
        return fallback


def prepare_patient_features(payload: PatientCreate) -> dict[str, float | int | str]:
    return {
        "patient_name": normalize_text(payload.patient_name),
        "age": payload.age,
        "gender": payload.gender,
        "glucose_level": payload.glucose_level,
        "blood_pressure": payload.blood_pressure,
        "cholesterol": payload.cholesterol,
        "bmi": payload.bmi,
        "symptom_severity": payload.symptom_severity,
        "activity_level": payload.activity_level,
        "has_diabetes_history": int(payload.has_diabetes_history),
        "has_hypertension_history": int(payload.has_hypertension_history),
        "notes": payload.notes.strip(),
    }


def parse_uploaded_csv(filename: str, content: bytes) -> dict[str, object]:
    text_stream = io.StringIO(content.decode("utf-8"))
    reader = csv.DictReader(text_stream)
    rows = []
    for row in reader:
        rows.append(
            {
                "patient_name": normalize_text(row.get("patient_name", "Unknown")),
                "age": _to_int(row.get("age"), 0),
                "gender": normalize_text(row.get("gender", "Unknown")),
                "glucose_level": _to_float(row.get("glucose_level"), 0.0),
                "blood_pressure": _to_float(row.get("blood_pressure"), 0.0),
                "cholesterol": _to_float(row.get("cholesterol"), 0.0),
                "bmi": _to_float(row.get("bmi"), 0.0),
            }
        )

    return {
        "filename": filename,
        "records": len(rows),
        "preview": rows[:5],
    }
