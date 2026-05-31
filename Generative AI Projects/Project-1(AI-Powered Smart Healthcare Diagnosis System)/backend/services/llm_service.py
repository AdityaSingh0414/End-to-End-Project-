from sqlmodel import Session

from backend.models.patient_model import PatientRecord
from backend.models.prediction_model import PredictionRecord


def build_patient_report(session: Session, prediction: PredictionRecord) -> dict[str, object]:
    patient = session.get(PatientRecord, prediction.patient_id)
    if patient is None:
        raise ValueError("Patient record missing for prediction")

    recommendations = [item.strip() for item in prediction.recommendations.split("|") if item.strip()]
    summary = (
        f"{patient.patient_name} is classified as {prediction.risk_level.lower()} risk "
        f"with a score of {prediction.risk_score:.2f}. Key clinical markers include glucose "
        f"{patient.glucose_level}, blood pressure {patient.blood_pressure}, cholesterol {patient.cholesterol}, "
        f"and BMI {patient.bmi}."
    )

    return {
        "prediction_id": prediction.id,
        "patient": {
            "name": patient.patient_name,
            "age": patient.age,
            "gender": patient.gender,
            "notes": patient.notes,
        },
        "summary": summary,
        "clinical_flags": [
            f"Symptom severity: {patient.symptom_severity}/10",
            f"Activity level: {patient.activity_level}/10",
            f"Family diabetes history: {'Yes' if patient.has_diabetes_history else 'No'}",
            f"Hypertension history: {'Yes' if patient.has_hypertension_history else 'No'}",
        ],
        "recommendations": recommendations,
        "disclaimer": "This portfolio project is an educational healthcare AI demo and not a substitute for medical advice.",
    }
