"""
train_bank_model.py — Train the multi-bank approval prediction model.

Reads:  data/bank/bank_loan_data.csv
Writes: models/bank_model.pkl
        models/bank_preprocessor.pkl
        models/bank_metrics.json
"""

import os
import sys
import json
import warnings
import numpy as np
import pandas as pd

from sklearn.model_selection import train_test_split, StratifiedKFold, cross_val_score
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score,
    f1_score, roc_auc_score, confusion_matrix,
    classification_report,
)
import xgboost as xgb
import joblib

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from src.utils import get_logger

logger = get_logger("train_bank_model")
warnings.filterwarnings("ignore")

DATA_PATH = os.path.join("data", "bank", "bank_loan_data.csv")
MODEL_PATH = os.path.join("models", "bank_model.pkl")
PREPROCESSOR_PATH = os.path.join("models", "bank_preprocessor.pkl")
METRICS_PATH = os.path.join("models", "bank_metrics.json")
SEED = 42

FEATURE_COLS = [
    "credit_score", "monthly_income", "age",
    "existing_emis", "employment_type",
    "loan_amount", "property_owned",
    "annual_income", "dti_ratio",
    "income_to_loan_ratio",
]
TARGET = "approved"


def run():
    os.makedirs("models", exist_ok=True)

    # 1. Load
    logger.info(f"Loading {DATA_PATH}")
    df = pd.read_csv(DATA_PATH)
    X = df[FEATURE_COLS]
    y = df[TARGET].astype(int)

    logger.info(f"Shape: {X.shape}  |  Class dist: {dict(y.value_counts())}")

    # 2. Scale
    scaler = StandardScaler()
    scale_cols = [
        "credit_score", "monthly_income", "age", "existing_emis",
        "loan_amount", "annual_income", "dti_ratio", "income_to_loan_ratio",
    ]
    X_scaled = X.copy()
    X_scaled[scale_cols] = scaler.fit_transform(X[scale_cols])

    # Save preprocessor
    joblib.dump({"scaler": scaler, "scale_cols": scale_cols}, PREPROCESSOR_PATH)
    logger.info(f"Scaler saved -> {PREPROCESSOR_PATH}")

    # 3. Split
    X_train, X_test, y_train, y_test = train_test_split(
        X_scaled, y, test_size=0.20, random_state=SEED, stratify=y
    )
    logger.info(f"Train: {X_train.shape}  |  Test: {X_test.shape}")

    # 4. Candidates
    candidates = {
        "XGBoost": xgb.XGBClassifier(
            n_estimators=250, learning_rate=0.05, max_depth=6,
            subsample=0.8, colsample_bytree=0.8,
            use_label_encoder=False, eval_metric="logloss",
            random_state=SEED,
        ),
        "Gradient Boosting": GradientBoostingClassifier(
            n_estimators=200, learning_rate=0.1, max_depth=5,
            random_state=SEED,
        ),
        "Random Forest": RandomForestClassifier(
            n_estimators=250, max_depth=12,
            min_samples_split=5, random_state=SEED,
        ),
    }

    # 5. Cross-validation
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=SEED)
    cv_results = {}

    print("\n" + "=" * 60)
    print("    BANK MODEL - 5-Fold Cross-Validation")
    print("=" * 60)

    for name, model in candidates.items():
        scores = cross_val_score(model, X_train, y_train, cv=cv,
                                 scoring="f1", n_jobs=-1)
        cv_results[name] = scores.mean()
        print(f"  {name:<25}  F1 CV = {scores.mean():.4f} +/- {scores.std():.4f}")

    best_name = max(cv_results, key=cv_results.get)
    print(f"\n  *  Best: {best_name}  (F1={cv_results[best_name]:.4f})")
    print("=" * 60)

    # 6. Fit best on full train
    best_model = candidates[best_name]
    best_model.fit(X_train, y_train)

    # 7. Evaluate
    y_pred = best_model.predict(X_test)
    y_prob = best_model.predict_proba(X_test)[:, 1]

    metrics = {
        "model_name": best_name,
        "accuracy": round(accuracy_score(y_test, y_pred), 4),
        "precision": round(precision_score(y_test, y_pred, zero_division=0), 4),
        "recall": round(recall_score(y_test, y_pred, zero_division=0), 4),
        "f1_score": round(f1_score(y_test, y_pred, zero_division=0), 4),
        "roc_auc": round(roc_auc_score(y_test, y_prob), 4),
        "confusion_matrix": confusion_matrix(y_test, y_pred).tolist(),
        "cv_scores": {k: round(v, 4) for k, v in cv_results.items()},
        "feature_names": FEATURE_COLS,
    }

    # Feature importance
    if hasattr(best_model, "feature_importances_"):
        imp = dict(zip(FEATURE_COLS, best_model.feature_importances_))
    else:
        imp = dict(zip(FEATURE_COLS, np.abs(best_model.coef_[0])))
    metrics["feature_importances"] = {k: round(float(v), 6) for k, v in
                                       sorted(imp.items(), key=lambda x: x[1], reverse=True)}

    print(f"\n-- Hold-out Test Results ---------------------")
    print(f"  Accuracy  : {metrics['accuracy']:.4f}")
    print(f"  Precision : {metrics['precision']:.4f}")
    print(f"  Recall    : {metrics['recall']:.4f}")
    print(f"  F1 Score  : {metrics['f1_score']:.4f}")
    print(f"  ROC-AUC   : {metrics['roc_auc']:.4f}")
    print(f"\n{classification_report(y_test, y_pred, target_names=['Rejected', 'Approved'])}")

    if metrics["accuracy"] >= 0.85:
        print("  [OK] Accuracy >= 85% - Goal met!")
    else:
        print("  [WARN] Accuracy below 85%")

    # 8. Save
    joblib.dump(best_model, MODEL_PATH)
    with open(METRICS_PATH, "w") as f:
        json.dump(metrics, f, indent=2)

    logger.info(f"Model saved -> {MODEL_PATH}")
    logger.info(f"Metrics saved -> {METRICS_PATH}")
    print(f"\n[OK] Training complete! Model -> {MODEL_PATH}")
    return best_model, metrics


if __name__ == "__main__":
    run()
