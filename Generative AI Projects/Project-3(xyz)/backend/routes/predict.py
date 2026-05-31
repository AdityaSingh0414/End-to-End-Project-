from __future__ import annotations

from fastapi import APIRouter

from backend.models.schemas import FusionPayload, FusionResult, SymptomPayload, SymptomPrediction
from backend.services.fusion_service import fuse_decisions
from backend.services.ml_service import predict_symptoms


router = APIRouter(prefix="/api/v1/predict", tags=["Prediction"])


@router.post("/symptoms", response_model=SymptomPrediction)
async def predict_from_symptoms(payload: SymptomPayload) -> SymptomPrediction:
    return predict_symptoms(payload)


@router.post("/fusion", response_model=FusionResult)
async def predict_fusion(payload: FusionPayload) -> FusionResult:
    return fuse_decisions(payload)

