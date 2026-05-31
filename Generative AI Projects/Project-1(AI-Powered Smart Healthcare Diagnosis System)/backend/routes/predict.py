from fastapi import APIRouter, Depends
from sqlmodel import Session

from backend.config.database import get_session
from backend.schemas.patient_schema import PatientCreate
from backend.schemas.prediction_schema import PredictionResponse
from backend.services.prediction_service import create_prediction_record


router = APIRouter(tags=["Prediction"])


@router.post("/predict", response_model=PredictionResponse)
def predict_patient_risk(payload: PatientCreate, session: Session = Depends(get_session)) -> PredictionResponse:
    return create_prediction_record(session, payload)
