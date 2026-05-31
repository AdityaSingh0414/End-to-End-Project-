"""
banks.py — Registry of 10 major Indian banks with loan policies.

Each bank has:
  - min_credit_score: minimum score for basic eligibility
  - loan_tiers: list of (min_credit_score, max_multiplier) tuples ordered descending
  - interest_rate_range: (low, high) as floats
  - risk_tolerance: "low" | "medium" | "high"
  - processing_days: typical processing time
  - max_dti_ratio: maximum allowed debt-to-income ratio
  - collateral_score_threshold: below this, collateral is required
"""

BANKS = {
    "SBI": {
        "full_name": "State Bank of India",
        "min_credit_score": 600,
        "loan_tiers": [
            (750, 6.0),
            (700, 5.0),
            (650, 4.0),
            (600, 2.5),
        ],
        "interest_rate_range": (8.0, 11.5),
        "risk_tolerance": "medium",
        "processing_days": 7,
        "max_dti_ratio": 0.50,
        "collateral_score_threshold": 650,
    },
    "HDFC Bank": {
        "full_name": "HDFC Bank",
        "min_credit_score": 650,
        "loan_tiers": [
            (750, 5.5),
            (700, 5.0),
            (650, 3.5),
        ],
        "interest_rate_range": (8.5, 11.0),
        "risk_tolerance": "low",
        "processing_days": 5,
        "max_dti_ratio": 0.45,
        "collateral_score_threshold": 680,
    },
    "ICICI Bank": {
        "full_name": "ICICI Bank",
        "min_credit_score": 630,
        "loan_tiers": [
            (750, 5.5),
            (700, 4.5),
            (650, 3.5),
            (630, 2.5),
        ],
        "interest_rate_range": (8.75, 12.0),
        "risk_tolerance": "medium",
        "processing_days": 6,
        "max_dti_ratio": 0.50,
        "collateral_score_threshold": 660,
    },
    "Axis Bank": {
        "full_name": "Axis Bank",
        "min_credit_score": 650,
        "loan_tiers": [
            (750, 5.0),
            (700, 4.5),
            (650, 3.0),
        ],
        "interest_rate_range": (9.0, 12.5),
        "risk_tolerance": "medium",
        "processing_days": 6,
        "max_dti_ratio": 0.48,
        "collateral_score_threshold": 670,
    },
    "Punjab National Bank": {
        "full_name": "Punjab National Bank",
        "min_credit_score": 580,
        "loan_tiers": [
            (750, 5.5),
            (700, 4.5),
            (650, 3.5),
            (600, 2.5),
            (580, 2.0),
        ],
        "interest_rate_range": (8.25, 11.75),
        "risk_tolerance": "high",
        "processing_days": 10,
        "max_dti_ratio": 0.55,
        "collateral_score_threshold": 620,
    },
    "Bank of Baroda": {
        "full_name": "Bank of Baroda",
        "min_credit_score": 600,
        "loan_tiers": [
            (750, 5.5),
            (700, 4.5),
            (650, 3.5),
            (600, 2.5),
        ],
        "interest_rate_range": (8.1, 11.5),
        "risk_tolerance": "medium",
        "processing_days": 8,
        "max_dti_ratio": 0.50,
        "collateral_score_threshold": 640,
    },
    "Kotak Mahindra Bank": {
        "full_name": "Kotak Mahindra Bank",
        "min_credit_score": 680,
        "loan_tiers": [
            (750, 5.0),
            (700, 4.0),
            (680, 3.0),
        ],
        "interest_rate_range": (8.75, 11.25),
        "risk_tolerance": "low",
        "processing_days": 4,
        "max_dti_ratio": 0.45,
        "collateral_score_threshold": 700,
    },
    "Yes Bank": {
        "full_name": "Yes Bank",
        "min_credit_score": 620,
        "loan_tiers": [
            (750, 5.0),
            (700, 4.0),
            (650, 3.0),
            (620, 2.0),
        ],
        "interest_rate_range": (9.25, 13.0),
        "risk_tolerance": "high",
        "processing_days": 5,
        "max_dti_ratio": 0.55,
        "collateral_score_threshold": 650,
    },
    "IndusInd Bank": {
        "full_name": "IndusInd Bank",
        "min_credit_score": 650,
        "loan_tiers": [
            (750, 5.0),
            (700, 4.0),
            (650, 3.0),
        ],
        "interest_rate_range": (9.5, 13.5),
        "risk_tolerance": "medium",
        "processing_days": 5,
        "max_dti_ratio": 0.50,
        "collateral_score_threshold": 670,
    },
    "Union Bank of India": {
        "full_name": "Union Bank of India",
        "min_credit_score": 590,
        "loan_tiers": [
            (750, 5.5),
            (700, 4.5),
            (650, 3.5),
            (600, 2.5),
            (590, 2.0),
        ],
        "interest_rate_range": (8.3, 11.75),
        "risk_tolerance": "high",
        "processing_days": 9,
        "max_dti_ratio": 0.52,
        "collateral_score_threshold": 630,
    },
}


def get_all_banks():
    """Return list of bank dicts with name key included."""
    return [{"name": k, **v} for k, v in BANKS.items()]


def get_bank(name: str):
    """Return a single bank dict or None."""
    b = BANKS.get(name)
    if b:
        return {"name": name, **b}
    return None
