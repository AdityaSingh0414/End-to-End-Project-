from datetime import datetime
from typing import Optional

from sqlmodel import Field, SQLModel


class PredictionRecord(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    patient_id: int = Field(index=True, foreign_key="patientrecord.id")
    risk_score: float
    risk_level: str
    model_name: str
    recommendations: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
