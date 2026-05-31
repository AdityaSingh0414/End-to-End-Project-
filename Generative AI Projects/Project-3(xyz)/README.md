# Healthcare AI: Smart Clinical Decision Support System

This project combines four production-style healthcare AI components:

- Tabular ML disease prediction from symptoms and vitals.
- X-ray deep learning classification for pneumonia vs normal.
- RAG medical assistant with local FAISS retrieval and cited context.
- FastAPI backend that fuses ML and DL confidence into a final decision.

> Clinical safety note: this is a learning and portfolio project. It is not a medical device and must not be used for real diagnosis.

## Project Structure

```text
project 3/
├── data/
│   ├── raw/
│   ├── processed/
│   ├── interim/
│   └── external/
├── notebooks/
├── ml/
│   ├── preprocessing/
│   ├── training/
│   └── saved_models/
├── dl/
│   ├── cnn_model/
│   └── saved_models/
├── rag/
│   ├── data/
│   ├── embeddings/
│   ├── vector_db/
│   └── chatbot/
├── backend/
│   ├── routes/
│   ├── services/
│   ├── models/
│   ├── config/
│   └── main.py
├── database/
├── dashboard/
├── docker/
├── tests/
├── requirements.txt
└── README.md
```

## Quick Start

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python scripts/prepare_demo_data.py
python ml/training/train_symptom_model.py
python rag/chatbot/build_index.py
uvicorn backend.main:app --reload
```

Open API docs at `http://127.0.0.1:8000/docs`.

## Datasets

The project includes a reproducible offline demo dataset generator:

- `data/raw/symptom_patient_records.csv`: synthetic symptom, vitals, and disease labels.
- `data/raw/xray_demo/`: generated grayscale image-like samples for pipeline testing.
- `rag/data/medical_knowledge.md`: curated educational medical notes for local RAG.

For a stronger final portfolio version, replace these with:

- Disease symptoms: Kaggle disease-symptom datasets.
- X-rays: Chest X-Ray Images (Pneumonia) or NIH ChestX-ray14.
- Medical text: CDC, WHO, NIH, or hospital guideline PDFs.

## Phases

1. **Data Collection & Storage**: structured records in PostgreSQL, image/PDF storage paths, schema validation.
2. **EDA**: missing values, class distribution, correlation, feature importance, outlier checks.
3. **ML**: Logistic Regression, Decision Tree, Random Forest with persisted model bundle.
4. **DL**: CNN baseline plus transfer learning template with augmentation and Grad-CAM.
5. **RAG**: Sentence Transformer embeddings, FAISS vector DB, source citations.
6. **Backend**: FastAPI, typed input validation, cached model services, async endpoints.
7. **Dashboard**: Power BI-ready CSV exports and report plan.
8. **Integration**: weighted decision fusion: `0.6 * ML + 0.4 * DL`.

## Main API Endpoints

- `GET /health`
- `POST /api/v1/predict/symptoms`
- `POST /api/v1/predict/fusion`
- `POST /api/v1/chat/query`

## Power BI Dashboard

Use `dashboard/powerbi_model_inputs.csv` after running `scripts/prepare_demo_data.py`.
Recommended visuals:

- Disease distribution bar chart.
- Accuracy and confidence KPI cards.
- Patient trend over time.
- Drill-down table by disease, age group, gender, and risk level.

