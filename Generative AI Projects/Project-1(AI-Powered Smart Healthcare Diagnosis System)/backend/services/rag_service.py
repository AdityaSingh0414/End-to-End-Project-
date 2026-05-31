from pathlib import Path

from backend.config.settings import settings


PROMPT_PATH = Path(__file__).resolve().parent.parent.parent / "rag" / "prompts" / "medical_prompt.txt"


def _load_prompt() -> str:
    if PROMPT_PATH.exists():
        return PROMPT_PATH.read_text(encoding="utf-8")
    return "Provide safe and concise healthcare recommendations for educational demo use."


def retrieve_recommendations(features: dict[str, float | int | str], risk_level: str) -> list[str]:
    prompt_hint = _load_prompt()
    recommendations = []

    if risk_level == "High":
        recommendations.extend(
            [
                "Prioritize physician review within 24 hours.",
                "Schedule blood glucose and lipid follow-up testing.",
                "Track symptoms daily and escalate if chest pain or breathlessness appears.",
            ]
        )
    elif risk_level == "Moderate":
        recommendations.extend(
            [
                "Plan a primary care review this week.",
                "Monitor blood pressure and glucose readings at home.",
                "Adopt a structured diet and activity plan for the next 30 days.",
            ]
        )
    else:
        recommendations.extend(
            [
                "Maintain preventive screenings and annual check-ups.",
                "Continue moderate exercise and balanced nutrition.",
                "Reassess if symptoms worsen or new concerns appear.",
            ]
        )

    if float(features["bmi"]) >= 30:
        recommendations.append("Discuss weight-management goals with a clinician or dietitian.")
    if float(features["glucose_level"]) >= 180:
        recommendations.append("Review glycemic control and medication adherence.")
    if "educational demo" in prompt_hint.lower():
        recommendations.append("This output is for educational decision support and not a medical diagnosis.")

    return recommendations[:5]
