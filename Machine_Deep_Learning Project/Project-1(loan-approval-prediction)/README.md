# Loan Approval Prediction System 🏦

> **ML Internship Project** — An industry-grade, end-to-end machine learning system for predicting loan approvals, deployed as a web application with a Flask backend and premium dark-mode UI.

---

## 📂 Project Structure

```
loan-approval-prediction/
├── data/
│   ├── raw/loan_data.csv          # Synthetic raw dataset (5,000 rows)
│   └── processed/clean_data.csv   # Cleaned & encoded data
├── notebooks/
│   ├── eda.ipynb                  # Exploratory Data Analysis
│   ├── preprocessing.ipynb        # Preprocessing walkthrough
│   └── model_training.ipynb       # Model training walkthrough
├── src/
│   ├── generate_data.py           # Synthetic data generator
│   ├── preprocess.py              # Cleaning, encoding, scaling pipeline
│   ├── train.py                   # Model training & comparison
│   ├── predict.py                 # Inference engine
│   └── utils.py                   # Shared utilities
├── models/
│   ├── loan_model.pkl             # Best trained model
│   ├── preprocessor.pkl           # Fitted StandardScaler
│   ├── feature_importance.pkl     # Feature importance scores
│   └── metrics.json               # Model performance metrics
│   └── reports/                   # Saved plots (confusion matrix, etc.)
├── app/
│   ├── app.py                     # Flask application
│   ├── templates/index.html       # Premium frontend UI
│   └── static/
│       ├── style.css              # Dark-mode design system
│       └── script.js              # Charts, API calls, form logic
├── requirements.txt
├── README.md
└── .gitignore
```

---

## 🔄 End-to-End Workflow

```
Raw Data (loan_data.csv)
       ↓
[preprocess.py] → Handle missing values, encode, scale
       ↓
[train.py] → Compare 4 models → Select best → Save .pkl
       ↓
[Flask app.py] → REST API
       ↓
[index.html / script.js] → User Interface
       ↓
[predict.py] → Real-time Prediction → Show Result
```

---

## 🚀 Quick Start

### 1. Install Dependencies

```bash
cd loan-approval-prediction
pip install -r requirements.txt
```

### 2. Generate Dataset

```bash
python src/generate_data.py
```

### 3. Preprocess Data

```bash
python src/preprocess.py
```

### 4. Train the Model

```bash
python src/train.py
```
> ✅ Expected: Accuracy ≥ 85%, F1 ≥ 0.87

### 5. Start the Flask App

```bash
cd app
python app.py
```

### 6. Open in Browser

Visit: **http://localhost:5000**

---

## 📊 Features

| Feature | Description |
|---|---|
| **ML Pipeline** | 4-model comparison (LR, RF, GBM, XGBoost) with 5-fold CV |
| **Feature Engineering** | EMI, Total Income, Income-to-Loan Ratio, Balance Income |
| **Explainable AI** | Top-3 feature importance per prediction |
| **Recommendations** | Personalized rejection/approval advice |
| **Dashboard** | Live accuracy, F1, ROC-AUC, confusion matrix |
| **Analytics** | Feature importance chart, model comparison, approval donut |
| **REST API** | `/predict`, `/api/metrics`, `/api/feature-importance`, `/api/stats` |

---

## 🤖 Model Performance

| Model | CV F1 Score |
|---|---|
| Logistic Regression | ~0.84 |
| **Random Forest** | **~0.91** ← Selected |
| Gradient Boosting | ~0.90 |
| XGBoost | ~0.90 |

### Top 3 Features Influencing Approval

1. 🥇 **Credit History** — Strongest predictor (3-5× impact)
2. 🥈 **Total Income** (Applicant + Co-applicant)
3. 🥉 **Loan Amount** (normalized against income)

---

## 🌐 API Reference

| Endpoint | Method | Description |
|---|---|---|
| `/` | GET | Frontend UI |
| `/predict` | POST | Prediction from JSON payload |
| `/api/metrics` | GET | Model performance metrics |
| `/api/feature-importance` | GET | Feature importance scores |
| `/api/stats` | GET | Dataset statistics |
| `/health` | GET | Health check |

### Sample `/predict` Request

```json
{
  "Gender": "Male",
  "Married": "Yes",
  "Dependents": "1",
  "Education": "Graduate",
  "Self_Employed": "No",
  "ApplicantIncome": 55000,
  "CoapplicantIncome": 15000,
  "LoanAmount": 180,
  "Loan_Amount_Term": 360,
  "Credit_History": "1.0",
  "Property_Area": "Semiurban"
}
```

### Sample Response

```json
{
  "status": "success",
  "data": {
    "decision": "Approved",
    "probability": 91.3,
    "confidence": "High",
    "top_factors": [
      {"feature": "Credit_History", "importance": 0.3412},
      {"feature": "Total_Income",   "importance": 0.1823},
      {"feature": "LoanAmount",     "importance": 0.1105}
    ],
    "recommendation": "Congratulations! Maintain your credit score and repay on time."
  }
}
```

---

## 🎯 Interview Explanation

> *"I built an end-to-end ML system where raw loan data is preprocessed — handling missing values, encoding categorical features, and engineering derived features like EMI and Balance Income. I then trained and compared four classification models using 5-fold cross-validation, with Random Forest achieving the best F1 score of ~91%. The trained model is deployed via Flask REST API, where users submit their details through a modern web interface and receive real-time predictions with confidence scores, top 3 contributing factors, and personalized recommendations. The system also includes a live analytics dashboard showing model metrics and feature importance visualizations."*

---

## 🛠 Tech Stack

| Layer | Technology |
|---|---|
| Language | Python 3.10+ |
| ML | Scikit-learn, XGBoost |
| Data | Pandas, NumPy |
| Visualization | Matplotlib, Seaborn |
| Backend | Flask, Flask-CORS |
| Frontend | HTML5, CSS3 (Dark Mode), Vanilla JS, Chart.js |
| Serialization | Joblib |
| Deployment | Gunicorn (Render/Heroku ready) |

---

*Built for ML Internship 2026 — Educational Use Only*
