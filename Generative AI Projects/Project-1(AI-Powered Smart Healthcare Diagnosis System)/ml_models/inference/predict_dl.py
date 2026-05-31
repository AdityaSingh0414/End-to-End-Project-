from backend.services.prediction_service import classify_risk, compute_risk_score


def predict(features: dict[str, float | int | str]) -> dict[str, float | str]:
    adjusted = compute_risk_score(features) * 1.03
    score = min(round(adjusted, 4), 0.99)
    return {"risk_score": score, "risk_level": classify_risk(score)}
