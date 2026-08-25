from .nodes import predict_root_cause,get_reason,get_recommended_action


transaction = {
    "payment_method": "credit_card",
    "gateway_status": "operational",
    "issuer_status": "operational",
    "amount": 500.0,
    "card_age_days": 400,
    "card_expiry_days": 250,
    "retry_count": 1,
    "customer_tenure_days": 800,
    "customer_past_success_rate": 0.92,
    "gateway_response_time_ms": 350,
    "issuer_response_time_ms": 300,
    "risk_score": 0.15,
    "available_balance_ratio": 0.08,
    "transaction_limit": 5000.0,
    "otp_attempts": 1,
    "cvv_match": 1,
    "recovered": 0
}
state={
    "transaction": transaction,
    "root_cause": "",
    "confidence": 0.0,
    "reason": "",
    "recommended_action": ""
}

result = predict_root_cause(state)
state.update(result)
result=get_reason(state)
state.update(result)
result=get_recommended_action(state)
state.update(result)

print("Root Cause:", state["root_cause"])
print("Confidence:", state["confidence"])
print("Reason:", state["reason"])
print("Action:", state["recommended_action"])