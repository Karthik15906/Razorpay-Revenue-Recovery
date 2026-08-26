import sys
from pathlib import Path
from typing import cast

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from data.data_creator import generate_dataset
from agent.graph import agent
from agent.state import State


def process_dataset(n_rows):

    df = generate_dataset(n_rows)

    results = []

    for _, row in df.iterrows():

        transaction = {
            "payment_method": row["payment_method"],
            "gateway_status": row["gateway_status"],
            "issuer_status": row["issuer_status"],
            "amount": row["amount"],
            "card_age_days": row["card_age_days"],
            "card_expiry_days": row["card_expiry_days"],
            "retry_count": row["retry_count"],
            "customer_tenure_days": row["customer_tenure_days"],
            "customer_past_success_rate": row["customer_past_success_rate"],
            "gateway_response_time_ms": row["gateway_response_time_ms"],
            "issuer_response_time_ms": row["issuer_response_time_ms"],
            "risk_score": row["risk_score"],
            "available_balance_ratio": row["available_balance_ratio"],
            "transaction_limit": row["transaction_limit"],
            "otp_attempts": row["otp_attempts"],
            "cvv_match": row["cvv_match"],
        }

        state = {
            "transaction": transaction,
            "root_cause": "",
            "confidence": 0.0,
            "reason": "",
            "recommended_action": "",
            "recovered": False,
            "recovery_attempts": 0,
        }

        result = agent.invoke(cast(State, state))

        results.append({
            "transaction_id": row["transaction_id"],
            "amount":row['amount'],
            "predicted_root_cause": result["root_cause"],
            "confidence": result["confidence"],
            "reason": result["reason"],
            "recommended_action": result["recommended_action"],
            "recovered": result["recovered"],
            "recovery_attempts": result["recovery_attempts"],
        })

    total_amount = sum(r["amount"] for r in results)

    recovered_amount = sum(
        r["amount"]
        for r in results
        if r["recovered"]
    )
    human_review = sum(
    1
    for r in results
    if "human review" in r["recommended_action"].lower()
)

    amount_at_risk = total_amount - recovered_amount

    return {
        "results": results,
        "summary": {
            "processed": len(results),
            "total_amount": total_amount,
            "recovered_amount": recovered_amount,
            "amount_at_risk": amount_at_risk,
            "human_review": human_review,
            "recovery_rate": (
                recovered_amount / total_amount * 100
                if total_amount > 0 else 0
            ),
        }
    }
