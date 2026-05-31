from __future__ import annotations

import csv
import math
import random
from pathlib import Path

from PIL import Image, ImageDraw


ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
PROCESSED = ROOT / "data" / "processed"
DASHBOARD = ROOT / "dashboard"
XRAY_ROOT = RAW / "xray_demo"

SYMPTOMS = [
    "fever",
    "cough",
    "fatigue",
    "shortness_of_breath",
    "chest_pain",
    "headache",
    "nausea",
    "sore_throat",
    "body_ache",
    "runny_nose",
]

DISEASE_RULES = {
    "Pneumonia": {"fever", "cough", "shortness_of_breath", "chest_pain", "fatigue"},
    "Flu": {"fever", "cough", "body_ache", "headache", "fatigue"},
    "Common Cold": {"cough", "runny_nose", "sore_throat", "headache"},
    "Migraine": {"headache", "nausea", "fatigue"},
    "Gastritis": {"nausea", "fatigue"},
}


def disease_for(row: dict[str, int]) -> str:
    scores = {
        disease: sum(row[symptom] for symptom in symptoms)
        for disease, symptoms in DISEASE_RULES.items()
    }
    return max(scores, key=scores.get)


def make_symptom_records(n: int = 500) -> list[dict[str, object]]:
    random.seed(42)
    rows: list[dict[str, object]] = []
    for patient_id in range(1, n + 1):
        base = {symptom: int(random.random() < 0.22) for symptom in SYMPTOMS}
        target = random.choice(list(DISEASE_RULES))
        for symptom in DISEASE_RULES[target]:
            base[symptom] = int(random.random() < 0.82)

        disease = disease_for(base)
        fever_boost = 2.2 if base["fever"] else 0
        breath_penalty = 4 if base["shortness_of_breath"] else 0
        row = {
            "patient_id": patient_id,
            "age": random.randint(5, 88),
            "gender": random.choice(["Female", "Male", "Other"]),
            "temperature_c": round(random.normalvariate(37 + fever_boost, 0.45), 1),
            "heart_rate": random.randint(62, 118),
            "spo2": max(82, min(100, random.randint(94, 100) - breath_penalty)),
            **base,
            "disease": disease,
            "risk_level": "High" if disease == "Pneumonia" and base["shortness_of_breath"] else "Medium",
            "visit_date": f"2026-{random.randint(1, 4):02d}-{random.randint(1, 28):02d}",
        }
        if row["spo2"] >= 97 and disease not in {"Pneumonia", "Flu"}:
            row["risk_level"] = "Low"
        rows.append(row)
    return rows


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def make_xray_demo() -> None:
    random.seed(7)
    for label in ["normal", "pneumonia"]:
        folder = XRAY_ROOT / label
        folder.mkdir(parents=True, exist_ok=True)
        for i in range(24):
            img = Image.new("L", (128, 128), 18)
            draw = ImageDraw.Draw(img)
            draw.ellipse((25, 15, 63, 115), fill=70)
            draw.ellipse((65, 15, 103, 115), fill=70)
            draw.rectangle((58, 8, 70, 120), fill=35)
            if label == "pneumonia":
                for _ in range(12):
                    x = random.randint(35, 95)
                    y = random.randint(35, 105)
                    r = random.randint(4, 10)
                    shade = random.randint(105, 170)
                    draw.ellipse((x - r, y - r, x + r, y + r), fill=shade)
            else:
                for y in range(20, 110, 12):
                    draw.arc((22, y - 15, 106, y + 15), 0, 180, fill=88)
            img.save(folder / f"{label}_{i:03d}.png")


def main() -> None:
    rows = make_symptom_records()
    write_csv(RAW / "symptom_patient_records.csv", rows)
    write_csv(PROCESSED / "symptom_patient_records_clean.csv", rows)
    write_csv(DASHBOARD / "powerbi_model_inputs.csv", rows)
    make_xray_demo()
    print(f"Created demo data under {RAW}")


if __name__ == "__main__":
    main()

