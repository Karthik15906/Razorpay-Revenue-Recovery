from .graph import agent
import time

transactions = [

    {
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
    },

    {
        "payment_method": "debit_card",
        "gateway_status": "degraded",
        "issuer_status": "operational",
        "amount": 2000.0,
        "card_age_days": 700,
        "card_expiry_days": 500,
        "retry_count": 0,
        "customer_tenure_days": 1200,
        "customer_past_success_rate": 0.85,
        "gateway_response_time_ms": 12000,
        "issuer_response_time_ms": 400,
        "risk_score": 0.20,
        "available_balance_ratio": 0.70,
        "transaction_limit": 5000.0,
        "otp_attempts": 1,
        "cvv_match": 1,
    },

    {
        "payment_method": "credit_card",
        "gateway_status": "operational",
        "issuer_status": "down",
        "amount": 1500.0,
        "card_age_days": 600,
        "card_expiry_days": 800,
        "retry_count": 1,
        "customer_tenure_days": 900,
        "customer_past_success_rate": 0.90,
        "gateway_response_time_ms": 300,
        "issuer_response_time_ms": 12000,
        "risk_score": 0.10,
        "available_balance_ratio": 0.80,
        "transaction_limit": 5000.0,
        "otp_attempts": 1,
        "cvv_match": 1,
    },

    {
        "payment_method": "debit_card",
        "gateway_status": "operational",
        "issuer_status": "operational",
        "amount": 1000.0,
        "card_age_days": 100,
        "card_expiry_days": 50,
        "retry_count": 0,
        "customer_tenure_days": 300,
        "customer_past_success_rate": 0.70,
        "gateway_response_time_ms": 300,
        "issuer_response_time_ms": 300,
        "risk_score": 0.20,
        "available_balance_ratio": 0.80,
        "transaction_limit": 5000.0,
        "otp_attempts": 1,
        "cvv_match": 1,
    }
]

for i, transaction in enumerate(transactions, start=1):
    start = time.time()

    state = {
        "transaction": transaction,
        "root_cause": "",
        "confidence": 0.0,
        "reason": "",
        "recommended_action": "",
        "recovered": False,
        "recovery_attempts": 0
    }

    result = agent.invoke(state)

    end = time.time()
    print(f"\n{'=' * 50}")
    print(f"TRANSACTION {i}, time_taken:{end-start}")
    print(f"{'=' * 50}")

    print("Root Cause:", result["root_cause"])
    print("Confidence:", result["confidence"])
    print("Reason:", result["reason"])
    print("Action:", result["recommended_action"])
    print("Recovered:", result["recovered"])
    print("Recovery Attempts:", result["recovery_attempts"])
