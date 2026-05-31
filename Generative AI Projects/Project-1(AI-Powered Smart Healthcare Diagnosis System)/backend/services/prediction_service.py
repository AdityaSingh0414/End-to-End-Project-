from datetime import datetime

from sqlmodel import Session, select

from backend.models.patient_model import PatientRecord
from backend.models.prediction_model import PredictionRecord
from backend.schemas.patient_schema import PatientCreate
from backend.schemas.prediction_schema import PredictionResponse
from backend.services.data_processing import prepare_patient_features
from backend.services.rag_service import retrieve_recommendations


def compute_risk_score(features: dict[str, float | int | str]) -> float:
    score = 0.0
    score += min(float(features["age"]) / 100.0, 1.0) * 0.14
    score += min(float(features["glucose_level"]) / 220.0, 1.0) * 0.24
    score += min(float(features["blood_pressure"]) / 180.0, 1.0) * 0.16
    score += min(float(features["cholesterol"]) / 300.0, 1.0) * 0.16
    score += min(float(features["bmi"]) / 45.0, 1.0) * 0.12
    score += min(float(features["symptom_severity"]) / 10.0, 1.0) * 0.10
    score += (10.0 - float(features["activity_level"])) / 10.0 * 0.04
    score += float(features["has_diabetes_history"]) * 0.02
    score += float(features["has_hypertension_history"]) * 0.02
    return round(min(score, 0.99), 4)


def classify_risk(score: float) -> str:
    if score >= 0.75:
        return "High"
    if score >= 0.45:
        return "Moderate"
    return "Low"


def create_prediction_record(session: Session, payload: PatientCreate) -> PredictionResponse:
    features = prepare_patient_features(payload)
    score = compute_risk_score(features)
    risk_level = classify_risk(score)
    recommendations = retrieve_recommendations(features, risk_level)

    patient = PatientRecord(**payload.model_dump())
    session.add(patient)
    session.commit()
    session.refresh(patient)

    prediction = PredictionRecord(
        patient_id=patient.id,
        risk_score=score,
        risk_level=risk_level,
        model_name="hybrid_clinical_v1",
        recommendations=" | ".join(recommendations),
        created_at=datetime.utcnow(),
    )
    session.add(prediction)
    session.commit()
    session.refresh(prediction)

    return PredictionResponse(
        prediction_id=prediction.id,
        patient_id=patient.id,
        patient_name=patient.patient_name,
        risk_score=score,
        risk_level=risk_level,
        recommendations=recommendations,
        created_at=prediction.created_at,
    )


def get_prediction_by_id(session: Session, prediction_id: int) -> PredictionRecord | None:
    return session.get(PredictionRecord, prediction_id)


def list_prediction_history(session: Session) -> list[dict[str, object]]:
    statement = (
        select(PredictionRecord, PatientRecord)
        .join(PatientRecord, PredictionRecord.patient_id == PatientRecord.id)
        .order_by(PredictionRecord.created_at.desc())
    )
    rows = session.exec(statement).all()
    history = []
    for prediction, patient in rows:
        history.append(
            {
                "prediction_id": prediction.id,
                "patient_name": patient.patient_name,
                "age": patient.age,
                "risk_level": prediction.risk_level,
                "risk_score": prediction.risk_score,
                "model_name": prediction.model_name,
                "created_at": prediction.created_at,
            }
        )
    return history
