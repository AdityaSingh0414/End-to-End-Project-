from datetime import datetime

from pydantic import BaseModel


class PredictionResponse(BaseModel):
    prediction_id: int
    patient_id: int
    patient_name: str
    risk_score: float
    risk_level: str
    recommendations: list[str]
    created_at: datetime
