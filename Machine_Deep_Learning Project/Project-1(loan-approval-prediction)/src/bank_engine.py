"""
bank_engine.py — Rule-based eligibility, DTI check, max loan,
                  conditional offers, and mortgage / collateral logic.
"""

from src.banks import BANKS


# ─── Eligibility Check ────────────────────────────────────────────────────────
def check_eligibility(user: dict, bank_name: str) -> dict:
    """
    Returns:
      {
        "eligible": bool,
        "reasons": [str, ...],           # rejection reasons (empty if eligible)
        "max_loan": float,               # 0 if ineligible
        "interest_rate": float,           # mid-range rate offered
        "collateral_required": bool,
      }
    """
    bank = BANKS[bank_name]
    reasons = []
    credit_score = user.get("credit_score", 0)
    monthly_income = user.get("monthly_income", 0)
    annual_income = monthly_income * 12
    existing_emis = user.get("existing_emis", 0)
    loan_amount = user.get("loan_amount", 0)
    age = user.get("age", 0)
    property_owned = user.get("property_owned", False)

    # --- Age gate ---
    if age < 21:
        reasons.append("Applicant must be at least 21 years old")
    if age > 65:
        reasons.append("Applicant age exceeds the upper limit of 65")

    # --- Credit score gate ---
    if credit_score < bank["min_credit_score"]:
        reasons.append(
            f"Credit score {credit_score} is below minimum requirement "
            f"of {bank['min_credit_score']}"
        )

    # --- DTI ratio ---
    dti = existing_emis / monthly_income if monthly_income > 0 else 1.0
    if dti > bank["max_dti_ratio"]:
        reasons.append(
            f"Debt-to-income ratio {dti:.0%} exceeds bank limit of "
            f"{bank['max_dti_ratio']:.0%}"
        )

    # --- Income floor (₹10,000/month) ---
    if monthly_income < 10000:
        reasons.append("Monthly income below ₹10,000 minimum threshold")

    # --- Compute max eligible loan ---
    multiplier = _get_multiplier(credit_score, bank)
    max_loan = multiplier * annual_income if multiplier > 0 else 0

    # --- Interest rate (credit-score adjusted) ---
    low, high = bank["interest_rate_range"]
    if credit_score >= 750:
        rate = low
    elif credit_score >= 700:
        rate = low + (high - low) * 0.25
    elif credit_score >= 650:
        rate = low + (high - low) * 0.55
    else:
        rate = high

    # --- Collateral logic ---
    collateral_required = credit_score < bank["collateral_score_threshold"]
    if collateral_required and not property_owned:
        # Still allow conditional but flag it
        pass

    eligible = len(reasons) == 0 and max_loan > 0
    return {
        "eligible": eligible,
        "reasons": reasons,
        "max_loan": round(max_loan, 2),
        "interest_rate": round(rate, 2),
        "collateral_required": collateral_required,
    }


# ─── Conditional Offer ────────────────────────────────────────────────────────
def conditional_offer(user: dict, bank_name: str) -> dict | None:
    """
    If user doesn't fully qualify, generate a conditional offer:
      - reduced loan amount, OR
      - require collateral/mortgage
    Returns None when no offer can be made.
    """
    bank = BANKS[bank_name]
    credit_score = user.get("credit_score", 0)
    monthly_income = user.get("monthly_income", 0)
    annual_income = monthly_income * 12
    loan_amount = user.get("loan_amount", 0)
    property_owned = user.get("property_owned", False)

    # Only offer conditional if credit score is within 80 pts of min
    score_gap = bank["min_credit_score"] - credit_score
    if score_gap > 80 or credit_score < 300:
        return None

    multiplier = _get_multiplier(credit_score, bank)
    if multiplier == 0:
        # Give lowest-tier multiplier as conditional
        multiplier = bank["loan_tiers"][-1][1] * 0.6

    max_conditional = multiplier * annual_income
    conditions = []

    if credit_score < bank["collateral_score_threshold"]:
        if property_owned:
            conditions.append("Provide property as collateral")
        else:
            conditions.append("Provide collateral (property, gold, FD, etc.)")

    if loan_amount > max_conditional:
        reduced = round(max_conditional, -3)  # round to nearest 1000
        conditions.append(f"Reduce loan amount to ₹{reduced:,.0f}")
    else:
        reduced = loan_amount

    if not conditions:
        return None

    return {
        "available": True,
        "bank": bank_name,
        "max_conditional_loan": round(reduced, 2),
        "collateral_required": credit_score < bank["collateral_score_threshold"],
        "conditions": conditions,
        "condition": " & ".join(conditions),
    }


# ─── Helpers ──────────────────────────────────────────────────────────────────
def _get_multiplier(credit_score: int, bank: dict) -> float:
    """Walk through tiered loan multipliers and return the best match."""
    for tier_score, tier_mult in bank["loan_tiers"]:
        if credit_score >= tier_score:
            return tier_mult
    return 0.0
