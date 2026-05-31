from fastapi.testclient import TestClient

from backend.main import app


def test_health_endpoint():
    with TestClient(app) as client:
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "ok"


def test_prediction_flow():
    payload = {
        "patient_name": "Test Patient",
        "age": 58,
        "gender": "Female",
        "glucose_level": 175,
        "blood_pressure": 138,
        "cholesterol": 210,
        "bmi": 29.8,
        "symptom_severity": 6,
        "activity_level": 5,
        "has_diabetes_history": True,
        "has_hypertension_history": False,
        "notes": "Intermittent dizziness and fatigue",
    }
    with TestClient(app) as client:
        response = client.post("/api/predict", json=payload)
        assert response.status_code == 200
        body = response.json()
        assert body["patient_name"] == "Test Patient"
        assert body["risk_level"] in {"Low", "Moderate", "High"}

        report = client.get(f"/api/report/{body['prediction_id']}")
        assert report.status_code == 200
        assert "summary" in report.json()
