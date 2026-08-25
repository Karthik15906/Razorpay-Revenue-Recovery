import joblib as jl
import pandas as pd
from .state import State

artifact = jl.load('./model/root_cause_model.pkl')

pipepline = artifact['pipeline']
label_encoder = artifact['label_encoder']
FEATURES = [
    "amount",
    "payment_method",
    "card_age_days",
    "card_expiry_days",
    "retry_count",
    "customer_tenure_days",
    "customer_past_success_rate",
    "gateway_response_time_ms",
    "gateway_status",
    "issuer_response_time_ms",
    "issuer_status",
    "risk_score",
    "available_balance_ratio",
    "transaction_limit",
    "otp_attempts",
    "cvv_match",
    "recovered"
]


def predict_root_cause(state:State):
    transaction=pd.DataFrame([state['transaction']])
    transaction=transaction[FEATURES]
    prediction = pipepline.predict(transaction)
    probabilities = pipepline.predict_proba(transaction)

    root_cause = label_encoder.inverse_transform(prediction)[0]

    confidence = float(probabilities.max())

    return    {"root_cause": root_cause,
        "confidence": confidence
    }


def get_reason(state:State):
    reasons = {
        "bank_server_timeout": "The payment gateway server did not respond within the expected time.",
        "card_blocked": "The customer's card is blocked.",
        "expired_card": "The customer's card has expired.",
        "insufficient_funds": "The available balance is insufficient for the transaction.",
        "issuer_bank_down": "The customer's issuing bank is unavailable.",
        "otp_cvv_mismatch": "The OTP or CVV verification failed.",
        "risk_fraud_block": "The transaction was blocked by the risk or fraud detection system.",
        "transaction_limit_exceeded": "The transaction exceeded the allowed transaction limit."
    }

    return {
        "reason": reasons[state["root_cause"]]
    }



def get_recommended_action(state:State):
    actions = {
        "bank_server_timeout": "Retry the transaction after the gateway recovers.",
        "card_blocked": "Ask the customer to contact their bank or use another card.",
        "expired_card": "Ask the customer to use a valid card.",
        "insufficient_funds": "Ask the customer to use another payment method or sufficient balance.",
        "issuer_bank_down": "Retry the transaction after the issuer bank recovers.",
        "otp_cvv_mismatch": "Ask the customer to re-enter the OTP or CVV.",
        "risk_fraud_block": "Send the transaction for fraud review.",
        "transaction_limit_exceeded": "Ask the customer to use a lower transaction amount."
    }

    return {
        "recommended_action": actions[state["root_cause"]]
    }


def confidence_router(state:State):
    if state["confidence"] >= 0.80:
        return "process"

    return "human_review"

def human_review(state:State):
    return {
        "recommended_action": "Send the transaction for human review."
    }