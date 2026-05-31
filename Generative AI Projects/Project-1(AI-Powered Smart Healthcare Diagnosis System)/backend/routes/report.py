from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from backend.config.database import get_session
from backend.services.llm_service import build_patient_report
from backend.services.prediction_service import get_prediction_by_id


router = APIRouter(tags=["Reports"])


@router.get("/report/{prediction_id}")
def get_patient_report(prediction_id: int, session: Session = Depends(get_session)) -> dict[str, object]:
    prediction = get_prediction_by_id(session, prediction_id)
    if prediction is None:
        raise HTTPException(status_code=404, detail="Prediction not found")
    return build_patient_report(session, prediction)
