import joblib as jl
import pandas as pd
from .state import State
import random
from pathlib import Path

MODEL_PATH = Path(__file__).resolve().parents[1] / "model" / "root_cause_model.pkl"
artifact = jl.load(MODEL_PATH)

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



def get_recommended_action(state: State):
    retry_count = state["transaction"]["retry_count"]

    if retry_count >= 3:
        return {
            "recommended_action":
                "Do not retry again. Escalate the transaction for human review."
        }

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



RECOVERY_PROBABILITIES = {
    "insufficient_funds": 0.60,
    "bank_server_timeout": 0.75,
    "issuer_bank_down": 0.70,
    "otp_cvv_mismatch": 0.55,
    "card_blocked": 0.30,
    "expired_card": 0.20,
    "risk_fraud_block": 0.15,
    "transaction_limit_exceeded": 0.45,
}


def attempt_recovery(state:State):
    root_cause = state['root_cause']
    recovered  = random.random() < RECOVERY_PROBABILITIES[root_cause]

    return {'recovered':int(recovered),
            "recovery_attempts": state["recovery_attempts"] + 1
            }

def recovery_router(state:State):
    if state['recovered']:
        return  'recovered'

    if state['recovery_attempts']>=3:
        return 'human_review'

    return 'retry'
