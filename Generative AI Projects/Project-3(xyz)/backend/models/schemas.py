from __future__ import annotations

from pydantic import BaseModel, Field


class SymptomPayload(BaseModel):
    age: int = Field(ge=0, le=120)
    gender: str
    temperature_c: float = Field(ge=34, le=43)
    heart_rate: int = Field(ge=30, le=220)
    spo2: int = Field(ge=50, le=100)
    fever: int = Field(ge=0, le=1)
    cough: int = Field(ge=0, le=1)
    fatigue: int = Field(ge=0, le=1)
    shortness_of_breath: int = Field(ge=0, le=1)
    chest_pain: int = Field(ge=0, le=1)
    headache: int = Field(ge=0, le=1)
    nausea: int = Field(ge=0, le=1)
    sore_throat: int = Field(ge=0, le=1)
    body_ache: int = Field(ge=0, le=1)
    runny_nose: int = Field(ge=0, le=1)


class SymptomPrediction(BaseModel):
    disease: str
    confidence: float
    probabilities: dict[str, float]


class FusionPayload(BaseModel):
    symptom_prediction: SymptomPrediction
    xray_label: str = "not_provided"
    xray_confidence: float = Field(default=0.0, ge=0.0, le=1.0)


class FusionResult(BaseModel):
    final_decision: str
    final_score: float
    explanation: str


class ChatPayload(BaseModel):
    query: str = Field(min_length=3, max_length=1000)

