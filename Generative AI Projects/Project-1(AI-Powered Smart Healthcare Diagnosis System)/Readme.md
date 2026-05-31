# Healthcare AI Intelligence Platform

This repository has been reshaped from an AI news prototype into a healthcare AI portfolio project with a modular FastAPI backend, a stronger frontend, and supporting folders for ML, RAG, multimodal work, data, and database assets.

## Architecture

```text
healthcare-ai/
├── backend/
├── ml_models/
├── rag/
├── multimodal/
├── data/
├── notebooks/
├── database/
├── powerbi/
├── frontend/
├── tests/
├── .env
├── requirements.txt
└── main.py
```

## Backend features

- `POST /api/predict`: intake a patient profile and generate a demo risk score.
- `GET /api/report/{prediction_id}`: create a clinician-style summary for a prediction.
- `POST /api/upload`: preview uploaded CSV patient files.
- `GET /api/history`: inspect stored prediction history.
- `GET /health`: health check endpoint.

## Frontend

The frontend is a static single-page dashboard served by FastAPI from `frontend/`. It includes:

- A styled patient intake workspace
- Prediction and report panels
- Batch upload preview
- Recent history cards

## Run locally

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python main.py
```

Then open [http://localhost:8000](http://localhost:8000).

## Notes

- The ML, deep learning, RAG, PDF, notebook, and Power BI files are scaffolded for portfolio completeness.
- Risk scoring is heuristic and educational, not clinical.
- The project includes a disclaimer in generated outputs and should not be used for medical diagnosis.
