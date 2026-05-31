from __future__ import annotations

from backend.config.settings import get_settings
from backend.models.schemas import FusionPayload, FusionResult


def fuse_decisions(payload: FusionPayload) -> FusionResult:
    settings = get_settings()
    ml_score = payload.symptom_prediction.confidence
    dl_score = payload.xray_confidence if payload.xray_label != "not_provided" else 0.0
    final_score = settings.fusion_ml_weight * ml_score + settings.fusion_dl_weight * dl_score

    if payload.xray_label.lower() == "pneumonia" and payload.xray_confidence >= 0.85:
        decision = "Pneumonia"
        reason = "High-confidence X-ray pneumonia signal overrides weighted fusion."
    else:
        decision = payload.symptom_prediction.disease
        reason = "Decision selected from symptom ML model and adjusted by image confidence."

    return FusionResult(final_decision=decision, final_score=round(final_score, 4), explanation=reason)

