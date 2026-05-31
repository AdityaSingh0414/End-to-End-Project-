"""
recommendation.py — Bank ranking engine with explainable AI and chatbot helper.

Top-3 bank selection using composite score:
    50% approval probability  +  30% interest rate (inverted)  +  20% max loan coverage
"""

from src.banks import BANKS, get_all_banks
from src.bank_engine import check_eligibility, conditional_offer
from src.bank_predict import predict_approval, get_top_features


# ─── Composite Score Weights ──────────────────────────────────────────────────
W_PROB = 0.50
W_RATE = 0.30
W_LOAN = 0.20


def rank_banks(user: dict) -> dict:
    """
    Master entry-point.  Returns the full JSON response:
    {
        "best_bank": str,
        "recommended_banks": [...],
        "conditional_offer": {...} | None,
        "final_decision": "Approved" | "Conditional" | "Rejected",
        "all_banks": [...],           # every bank with eligibility info
        "top_features": [...],
    }
    """
    loan_amount = user.get("loan_amount", 0)

    eligible_banks = []
    ineligible_banks = []
    best_conditional = None

    for bank_name, bank_policy in BANKS.items():
        elig = check_eligibility(user, bank_name)
        prob = 0.0

        if elig["eligible"]:
            prob = predict_approval(user, bank_policy)

        entry = {
            "bank": bank_name,
            "eligible": elig["eligible"],
            "approval_probability": round(prob, 4),
            "max_loan": elig["max_loan"],
            "interest_rate": f"{elig['interest_rate']}%",
            "interest_rate_num": elig["interest_rate"],
            "collateral_required": elig["collateral_required"],
            "reasons": elig["reasons"],
            "processing_days": bank_policy["processing_days"],
            "risk_tolerance": bank_policy["risk_tolerance"],
        }

        if elig["eligible"] and elig["max_loan"] >= loan_amount:
            # Compute composite score
            # Interest: lower is better → invert (max 15%)
            rate_score = max(0, 1 - elig["interest_rate"] / 15.0)
            loan_score = min(elig["max_loan"] / (loan_amount + 1), 1.0)
            composite = (
                W_PROB * prob + W_RATE * rate_score + W_LOAN * loan_score
            )
            entry["composite_score"] = round(composite, 4)
            entry["reason"] = _build_reason(user, entry)
            eligible_banks.append(entry)
        elif elig["eligible"] and elig["max_loan"] < loan_amount:
            # Eligible but loan amount too high — partial
            entry["reason"] = (
                f"Eligible but max loan ₹{elig['max_loan']:,.0f} is below "
                f"requested ₹{loan_amount:,.0f}"
            )
            entry["composite_score"] = 0
            ineligible_banks.append(entry)
            # Try conditional
            cond = conditional_offer(user, bank_name)
            if cond and (
                best_conditional is None
                or cond["max_conditional_loan"] > best_conditional["max_conditional_loan"]
            ):
                best_conditional = cond
        else:
            entry["reason"] = "; ".join(elig["reasons"]) if elig["reasons"] else "Not eligible"
            entry["composite_score"] = 0
            ineligible_banks.append(entry)
            # Try conditional for ineligible
            cond = conditional_offer(user, bank_name)
            if cond and (
                best_conditional is None
                or cond["max_conditional_loan"] > best_conditional.get("max_conditional_loan", 0)
            ):
                best_conditional = cond

    # Sort eligible by composite score descending
    eligible_banks.sort(key=lambda x: x["composite_score"], reverse=True)

    top3 = eligible_banks[:3]
    # Clean up internal keys before returning
    for b in top3:
        b.pop("interest_rate_num", None)
        b.pop("composite_score", None)

    # Determine final decision
    if top3:
        best_bank = top3[0]["bank"]
        final_decision = "Approved"
    elif best_conditional:
        best_bank = best_conditional["bank"]
        final_decision = "Conditional"
    else:
        best_bank = None
        final_decision = "Rejected"

    # Feature importance
    top_features = get_top_features(user, n=5)

    # Build all_banks list (for dashboard)
    all_entries = eligible_banks + ineligible_banks
    for b in all_entries:
        b.pop("interest_rate_num", None)
        b.pop("composite_score", None)

    return {
        "best_bank": best_bank,
        "recommended_banks": top3,
        "conditional_offer": best_conditional or {"available": False},
        "final_decision": final_decision,
        "all_banks": all_entries,
        "top_features": top_features,
    }


# ─── Explanation Helpers ──────────────────────────────────────────────────────
def _build_reason(user: dict, entry: dict) -> str:
    """Generate human-readable reason why a bank is recommended."""
    parts = []
    cs = user.get("credit_score", 0)
    if cs >= 750:
        parts.append("Excellent credit score")
    elif cs >= 700:
        parts.append("Good credit score")
    else:
        parts.append("Fair credit score")

    mi = user.get("monthly_income", 0)
    if mi >= 80000:
        parts.append("high income stability")
    elif mi >= 40000:
        parts.append("stable income")
    else:
        parts.append("moderate income")

    rate = entry.get("interest_rate_num", 10)
    if rate < 9:
        parts.append("competitive interest rate")
    elif rate < 10.5:
        parts.append("reasonable interest rate")

    if not entry.get("collateral_required"):
        parts.append("no collateral needed")

    return "; ".join(parts).capitalize()


def explain_bank(question: str, result: dict) -> str:
    """
    Chatbot-style Q&A.  Accepts a free-text question and the
    recommendation result, returns a natural-language answer.
    """
    q = question.lower().strip()

    if not result.get("best_bank"):
        return (
            "Unfortunately, none of the banks can approve your loan at the current "
            "parameters. Consider improving your credit score, reducing the loan "
            "amount, or providing collateral."
        )

    best = result["best_bank"]
    top = result["recommended_banks"]
    cond = result.get("conditional_offer", {})

    # "Why is X best?"
    if "why" in q and "best" in q:
        if top:
            b = top[0]
            return (
                f"{best} is the best choice for you because: {b.get('reason', 'N/A')}. "
                f"Your approval probability is {b['approval_probability']*100:.0f}% "
                f"with an interest rate of {b['interest_rate']}."
            )

    # "What about <bank>?"
    for bank_entry in result.get("all_banks", []):
        bname = bank_entry["bank"].lower()
        if bname in q:
            if bank_entry["eligible"]:
                return (
                    f"{bank_entry['bank']} can approve your loan with a probability "
                    f"of {bank_entry['approval_probability']*100:.0f}% at "
                    f"{bank_entry['interest_rate']} interest rate. "
                    f"Max loan: ₹{bank_entry['max_loan']:,.0f}."
                )
            else:
                return (
                    f"{bank_entry['bank']} cannot approve your loan because: "
                    f"{bank_entry.get('reason', 'Not eligible')}."
                )

    # "Conditional" / "collateral"
    if "conditional" in q or "collateral" in q or "mortgage" in q:
        if cond.get("available"):
            return (
                f"A conditional offer is available from {cond['bank']}: "
                f"{cond['condition']}. "
                f"Maximum conditional loan: ₹{cond.get('max_conditional_loan', 0):,.0f}."
            )
        return "No conditional offers are available for your profile."

    # "Compare" / "comparison"
    if "compare" in q or "comparison" in q or "all" in q:
        if top:
            lines = [f"Top {len(top)} recommended banks:"]
            for i, b in enumerate(top, 1):
                lines.append(
                    f"  {i}. {b['bank']} — {b['approval_probability']*100:.0f}% "
                    f"approval, {b['interest_rate']} rate, "
                    f"max ₹{b['max_loan']:,.0f}"
                )
            return "\n".join(lines)

    # Default
    return (
        f"Based on your profile, {best} is our top recommendation with "
        f"{'an approval probability of ' + str(round(top[0]['approval_probability']*100)) + '%' if top else 'the best terms'}. "
        f"Feel free to ask about specific banks, conditional offers, "
        f"or why a bank was recommended!"
    )
