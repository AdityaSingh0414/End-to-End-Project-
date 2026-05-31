"""
app.py — Flask REST API + HTML frontend server.

Endpoints:
    GET  /                      → Serve the fintech dashboard UI
    POST /predict               → Run original ML prediction (legacy)
    POST /recommend             → Multi-bank recommendation engine
    GET  /api/banks             → List all bank profiles
    POST /api/chatbot           → Chatbot Q&A about recommendations
    GET  /api/metrics           → Model performance metrics
    GET  /api/feature-importance → Feature importance scores
    GET  /api/stats             → Dataset-level statistics
    GET  /api/dashboard         → Aggregate dashboard data
    GET  /health                → Health check
"""

import os, sys, json, time, logging, hashlib
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from src.predict import predict_single
from src.banks import get_all_banks, get_bank
from src.recommendation import rank_banks, explain_bank

# ─── App Setup ────────────────────────────────────────────────────────────────
app = Flask(__name__, template_folder="templates", static_folder="static")
CORS(app)

logging.basicConfig(level=logging.INFO,
                    format="[%(asctime)s] %(levelname)s — %(message)s")
logger = logging.getLogger("app")

METRICS_PATH  = os.path.join(os.path.dirname(__file__), "..", "models", "metrics.json")
FEAT_IMP_PATH = os.path.join(os.path.dirname(__file__), "..", "models", "feature_importance.pkl")
BANK_METRICS  = os.path.join(os.path.dirname(__file__), "..", "models", "bank_metrics.json")

import joblib

# ─── Simple in-memory cache (TTL = 60s) ──────────────────────────────────────
_cache = {}
CACHE_TTL = 60


def _cache_key(data: dict) -> str:
    raw = json.dumps(data, sort_keys=True)
    return hashlib.md5(raw.encode()).hexdigest()


def _cache_get(key: str):
    entry = _cache.get(key)
    if entry and time.time() - entry["ts"] < CACHE_TTL:
        return entry["val"]
    return None


def _cache_set(key: str, val):
    _cache[key] = {"val": val, "ts": time.time()}
    # Evict old entries if cache grows too large
    if len(_cache) > 500:
        cutoff = time.time() - CACHE_TTL
        to_del = [k for k, v in _cache.items() if v["ts"] < cutoff]
        for k in to_del:
            del _cache[k]


def _load_json(path):
    if os.path.exists(path):
        with open(path) as f:
            return json.load(f)
    return {}


def _load_pkl(path):
    if os.path.exists(path):
        return joblib.load(path)
    return {}


# ─── Routes ───────────────────────────────────────────────────────────────────
@app.route("/")
def index():
    return render_template("index.html")


# ── Legacy predict endpoint ──────────────────────────────────────────────────
@app.route("/predict", methods=["POST"])
def predict():
    try:
        data = request.get_json(force=True)
        logger.info(f"Prediction request: {data}")
        result = predict_single(data)
        logger.info(f"Result: {result}")
        return jsonify({"status": "success", "data": result}), 200
    except FileNotFoundError as e:
        logger.error(f"Model not found: {e}")
        return jsonify({"status": "error",
                        "message": "Model not trained yet. Run train.py first."}), 503
    except Exception as e:
        logger.exception(f"Prediction error: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500


# ── Multi-bank recommendation ───────────────────────────────────────────────
@app.route("/recommend", methods=["POST"])
def recommend():
    try:
        data = request.get_json(force=True)
        logger.info(f"Recommendation request: {data}")

        # Validate required fields
        required = ["age", "monthly_income", "credit_score",
                     "employment_type", "loan_amount"]
        missing = [f for f in required if f not in data]
        if missing:
            return jsonify({
                "status": "error",
                "message": f"Missing required fields: {', '.join(missing)}"
            }), 400

        # Cast types
        user = {
            "age": int(data["age"]),
            "monthly_income": float(data["monthly_income"]),
            "credit_score": int(data["credit_score"]),
            "employment_type": data.get("employment_type", "Salaried"),
            "existing_emis": float(data.get("existing_emis", 0)),
            "loan_amount": float(data["loan_amount"]),
            "property_owned": bool(data.get("property_owned", False)),
        }

        # Check cache
        key = _cache_key(user)
        cached = _cache_get(key)
        if cached:
            logger.info("Cache hit for recommendation")
            return jsonify({"status": "success", "data": cached}), 200

        start = time.time()
        result = rank_banks(user)
        elapsed = time.time() - start
        logger.info(f"Recommendation completed in {elapsed:.3f}s")

        _cache_set(key, result)
        return jsonify({"status": "success", "data": result}), 200

    except FileNotFoundError as e:
        logger.error(f"Bank model not found: {e}")
        return jsonify({
            "status": "error",
            "message": "Bank model not trained. Run: python src/generate_bank_data.py && python src/train_bank_model.py"
        }), 503
    except Exception as e:
        logger.exception(f"Recommendation error: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500


# ── Bank profiles ────────────────────────────────────────────────────────────
@app.route("/api/banks")
def list_banks():
    banks = get_all_banks()
    # Serialize for JSON (stringify tuples)
    for b in banks:
        b["interest_rate_range"] = list(b["interest_rate_range"])
    return jsonify({"status": "success", "data": banks})


# ── Chatbot ──────────────────────────────────────────────────────────────────
@app.route("/api/chatbot", methods=["POST"])
def chatbot():
    try:
        data = request.get_json(force=True)
        question = data.get("question", "")
        context = data.get("context", {})

        if not question:
            return jsonify({"status": "error", "message": "No question provided"}), 400

        answer = explain_bank(question, context)
        return jsonify({"status": "success", "data": {"answer": answer}})

    except Exception as e:
        logger.exception(f"Chatbot error: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500


# ── Metrics (original model) ────────────────────────────────────────────────
@app.route("/api/metrics")
def get_metrics():
    metrics = _load_json(METRICS_PATH)
    if not metrics:
        return jsonify({"status": "error", "message": "metrics.json not found"}), 404
    return jsonify({"status": "success", "data": metrics})


@app.route("/api/feature-importance")
def get_feature_importance():
    fi = _load_pkl(FEAT_IMP_PATH)
    if not fi:
        return jsonify({"status": "error", "message": "Feature importance not found"}), 404
    sorted_fi = sorted(fi.items(), key=lambda x: x[1], reverse=True)
    return jsonify({"status": "success",
                    "data": [{"feature": k, "importance": round(float(v), 4)}
                             for k, v in sorted_fi]})


@app.route("/api/stats")
def get_stats():
    metrics = _load_json(METRICS_PATH)
    if not metrics:
        return jsonify({"status": "error", "message": "metrics.json not found"}), 404
    cm = metrics.get("confusion_matrix", [[0, 0], [0, 0]])
    total = sum(sum(row) for row in cm)
    approved = cm[1][1] + cm[0][1] if len(cm) > 1 else 0
    stats = {
        "total_applications": total,
        "approval_rate": round(approved / total * 100, 1) if total else 0,
        "model_name": metrics.get("model_name", "N/A"),
        "accuracy": metrics.get("accuracy", 0),
        "f1_score": metrics.get("f1_score", 0),
        "roc_auc": metrics.get("roc_auc", 0),
        "cv_scores": metrics.get("cv_scores", {}),
    }
    return jsonify({"status": "success", "data": stats})


# ── Dashboard aggregate ─────────────────────────────────────────────────────
@app.route("/api/dashboard")
def dashboard():
    bank_m = _load_json(BANK_METRICS)
    orig_m = _load_json(METRICS_PATH)
    banks = get_all_banks()
    return jsonify({
        "status": "success",
        "data": {
            "bank_model": bank_m,
            "original_model": orig_m,
            "total_banks": len(banks),
            "banks_summary": [
                {"name": b["name"], "min_score": b["min_credit_score"],
                 "rate_range": list(b["interest_rate_range"]),
                 "risk": b["risk_tolerance"]}
                for b in banks
            ],
        }
    })


@app.route("/health")
def health():
    return jsonify({"status": "ok",
                    "service": "Loan Approval & Bank Recommendation API"})


# ─── Entry Point ──────────────────────────────────────────────────────────────
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
