from backend.services.prediction_service import classify_risk, compute_risk_score


def predict(features: dict[str, float | int | str]) -> dict[str, float | str]:
    score = compute_risk_score(features)
    return {"risk_score": score, "risk_level": classify_risk(score)}
