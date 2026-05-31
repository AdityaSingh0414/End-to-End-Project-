from fastapi import APIRouter, Depends
from sqlmodel import Session

from backend.config.database import get_session
from backend.services.prediction_service import list_prediction_history


router = APIRouter(tags=["History"])


@router.get("/history")
def get_prediction_history(session: Session = Depends(get_session)) -> list[dict[str, object]]:
    return list_prediction_history(session)
