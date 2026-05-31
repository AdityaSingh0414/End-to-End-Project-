"""
train.py — Model training, comparison, selection, and evaluation.
Reads:  data/processed/clean_data.csv
Writes: models/loan_model.pkl  +  models/feature_importance.pkl
"""

import os
import sys
import json
import warnings
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")   # headless rendering for servers
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.model_selection import train_test_split, StratifiedKFold, cross_val_score
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.metrics import (accuracy_score, precision_score, recall_score,
                             f1_score, roc_auc_score, confusion_matrix,
                             classification_report)
from sklearn.pipeline import Pipeline
import xgboost as xgb

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from src.utils import get_logger, save_model, TARGET_COL

logger = get_logger("train")
warnings.filterwarnings("ignore")

PROCESSED_PATH     = os.path.join("data", "processed", "clean_data.csv")
MODEL_PATH         = os.path.join("models", "loan_model.pkl")
FEAT_IMP_PATH      = os.path.join("models", "feature_importance.pkl")
METRICS_PATH       = os.path.join("models", "metrics.json")
REPORTS_DIR        = os.path.join("models", "reports")
SEED               = 42


# ─── Candidate Models ─────────────────────────────────────────────────────────
def get_candidates():
    return {
        "Logistic Regression": LogisticRegression(max_iter=1000, random_state=SEED),
        "Random Forest":       RandomForestClassifier(n_estimators=200,
                                                      max_depth=10,
                                                      min_samples_split=5,
                                                      random_state=SEED),
        "Gradient Boosting":   GradientBoostingClassifier(n_estimators=150,
                                                          learning_rate=0.1,
                                                          max_depth=5,
                                                          random_state=SEED),
        "XGBoost":             xgb.XGBClassifier(n_estimators=200,
                                                  learning_rate=0.05,
                                                  max_depth=6,
                                                  subsample=0.8,
                                                  colsample_bytree=0.8,
                                                  use_label_encoder=False,
                                                  eval_metric="logloss",
                                                  random_state=SEED),
    }


# ─── Evaluate Metrics ─────────────────────────────────────────────────────────
def evaluate(model, X_test, y_test, label="") -> dict:
    y_pred = model.predict(X_test)
    y_prob = model.predict_proba(X_test)[:, 1]
    metrics = {
        "accuracy":  round(accuracy_score(y_test, y_pred),  4),
        "precision": round(precision_score(y_test, y_pred, zero_division=0), 4),
        "recall":    round(recall_score(y_test, y_pred, zero_division=0),    4),
        "f1_score":  round(f1_score(y_test, y_pred, zero_division=0),        4),
        "roc_auc":   round(roc_auc_score(y_test, y_prob),                    4),
        "confusion_matrix": confusion_matrix(y_test, y_pred).tolist(),
    }
    logger.info(f"[{label}] Acc={metrics['accuracy']:.4f} | "
                f"F1={metrics['f1_score']:.4f} | AUC={metrics['roc_auc']:.4f}")
    return metrics


# ─── Plot: Confusion Matrix ────────────────────────────────────────────────────
def plot_confusion_matrix(cm, title, save_path):
    plt.figure(figsize=(6, 5))
    sns.heatmap(cm, annot=True, fmt="d", cmap="Blues",
                xticklabels=["Rejected", "Approved"],
                yticklabels=["Rejected", "Approved"])
    plt.title(title, fontsize=14)
    plt.ylabel("Actual"); plt.xlabel("Predicted")
    plt.tight_layout()
    plt.savefig(save_path, dpi=150)
    plt.close()


# ─── Plot: Feature Importance ─────────────────────────────────────────────────
def plot_feature_importance(importances: dict, save_path: str):
    sorted_items = sorted(importances.items(), key=lambda x: x[1], reverse=True)
    features, vals = zip(*sorted_items)

    plt.figure(figsize=(10, 6))
    colors = ["#2ecc71" if i < 3 else "#3498db" for i in range(len(features))]
    bars = plt.barh(features[::-1], [v for v in vals[::-1]], color=colors[::-1])
    plt.xlabel("Importance Score")
    plt.title("Feature Importance — Random Forest", fontsize=14)
    plt.tight_layout()
    plt.savefig(save_path, dpi=150)
    plt.close()


# ─── Main Training Pipeline ────────────────────────────────────────────────────
def run_training():
    os.makedirs(REPORTS_DIR, exist_ok=True)
    os.makedirs("models", exist_ok=True)

    # 1. Load clean data
    logger.info(f"Loading: {PROCESSED_PATH}")
    df = pd.read_csv(PROCESSED_PATH)

    X = df.drop(columns=[TARGET_COL])
    y = df[TARGET_COL].astype(int)
    feature_names = list(X.columns)

    logger.info(f"Features ({len(feature_names)}): {feature_names}")
    logger.info(f"Class distribution: {dict(y.value_counts())}")

    # 2. Train / test split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, random_state=SEED, stratify=y
    )
    logger.info(f"Train: {X_train.shape}  |  Test: {X_test.shape}")

    # 3. Cross-validation on all candidates  (5-fold)
    candidates = get_candidates()
    cv_results = {}
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=SEED)

    print("\n" + "=" * 60)
    print("      MODEL COMPARISON (5-Fold Cross-Validation)")
    print("=" * 60)
    for name, model in candidates.items():
        scores = cross_val_score(model, X_train, y_train, cv=cv,
                                 scoring="f1", n_jobs=-1)
        cv_results[name] = scores.mean()
        print(f"  {name:<25}  F1 CV = {scores.mean():.4f} +/- {scores.std():.4f}")

    best_name = max(cv_results, key=cv_results.get)
    print(f"\n  *  Best model: {best_name}  (F1={cv_results[best_name]:.4f})")
    print("=" * 60 + "\n")

    # 4. Fit best model on full training set
    best_model = candidates[best_name]
    best_model.fit(X_train, y_train)

    # 5. Evaluate on hold-out test set
    metrics = evaluate(best_model, X_test, y_test, label=best_name)
    metrics["model_name"] = best_name
    metrics["feature_names"] = feature_names
    metrics["cv_scores"] = {k: round(v, 4) for k, v in cv_results.items()}

    print("\n── Hold-out Test Set Results ─────────────────────────────")
    print(f"  Accuracy  : {metrics['accuracy']:.4f}")
    print(f"  Precision : {metrics['precision']:.4f}")
    print(f"  Recall    : {metrics['recall']:.4f}")
    print(f"  F1 Score  : {metrics['f1_score']:.4f}")
    print(f"  ROC-AUC   : {metrics['roc_auc']:.4f}")
    print(f"\n{classification_report(y_test, best_model.predict(X_test), target_names=['Rejected','Approved'])}")

    if metrics["accuracy"] >= 0.85:
        print(f"  ✅ Goal achieved! Accuracy ≥ 85%")
    else:
        print(f"  ⚠️  Accuracy below 85% — consider tuning.")

    # 6. Feature Importance
    if hasattr(best_model, "feature_importances_"):
        importances = dict(zip(feature_names, best_model.feature_importances_))
    else:
        # Logistic Regression
        importances = dict(zip(feature_names, abs(best_model.coef_[0])))

    sorted_imp = dict(sorted(importances.items(), key=lambda x: x[1], reverse=True))
    top3 = list(sorted_imp.items())[:3]
    print("\n── Top 3 Feature Importances ─────────────────────────────")
    for rank, (feat, imp) in enumerate(top3, 1):
        print(f"  {rank}. {feat:<30} {imp:.4f}")

    metrics["feature_importances"] = {k: round(float(v), 6) for k, v in sorted_imp.items()}

    # 7. Save everything
    save_model(best_model,  MODEL_PATH)
    save_model(sorted_imp,  FEAT_IMP_PATH)

    with open(METRICS_PATH, "w") as f:
        json.dump(metrics, f, indent=2)

    # 8. Plots
    plot_confusion_matrix(
        metrics["confusion_matrix"], f"Confusion Matrix — {best_name}",
        os.path.join(REPORTS_DIR, "confusion_matrix.png")
    )
    plot_feature_importance(importances, os.path.join(REPORTS_DIR, "feature_importance.png"))

    logger.info("Training complete!")
    return best_model, metrics


if __name__ == "__main__":
    run_training()
