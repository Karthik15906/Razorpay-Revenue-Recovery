import joblib as jl
import pandas as pd
import random
from pathlib import Path

from .state import State


# LOAD ROOT CAUSE MODEL
MODEL_PATH = (
    Path(__file__).resolve().parents[1]
    / "model"
    / "root_cause_model.pkl"
)

artifact = jl.load(MODEL_PATH)

pipeline = artifact["pipeline"]
label_encoder = artifact["label_encoder"]


# LOAD RECOVERY MODEL

RECOVERY_MODEL_PATH = (
    Path(__file__).resolve().parents[1]
    / "model"
    / "recovery_probability_pipeline.pkl"
)

recovery_pipeline = jl.load(RECOVERY_MODEL_PATH)


# =========================================================
# FEATURES
# =========================================================

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


# 1. PREDICT ROOT CAUSE
def predict_root_cause(state: State):

    transaction = pd.DataFrame([state["transaction"]])
    transaction = transaction[FEATURES]

    prediction = pipeline.predict(transaction)
    probabilities = pipeline.predict_proba(transaction)

    root_cause = label_encoder.inverse_transform(prediction)[0]

    confidence = float(probabilities.max())

    return {
        "root_cause": root_cause,
        "confidence": confidence
    }


# 2. PREDICT RECOVERY PROBABILITY

def predict_recovery_probability(state: State):

    transaction = pd.DataFrame([state["transaction"]])

    transaction["root_cause"] = state["root_cause"]

    recovery_probability = recovery_pipeline.predict_proba(transaction)[0, 1]

    return {
        "recovery_probability": float(recovery_probability)
    }


# 3. RECOVERY DECISION

def recovery_decision(state: State):

    probability = state["recovery_probability"]
    root_cause = state["root_cause"]
    retry_count = state["transaction"]["retry_count"]
    amount = state["transaction"]["amount"]

    if retry_count >= 3:
        return {
            "recovery_decision": "human_review",
            "decision_reason":
                "Maximum retry limit has been reached."
        }

    if root_cause == "risk_fraud_block":
        return {
            "recovery_decision": "human_review",
            "decision_reason":
                "Fraud-related failure requires manual review."
        }

    if root_cause in {"expired_card", "card_blocked"}:
        return {
            "recovery_decision": "do_not_recover",
            "decision_reason":
                "This failure is unlikely to be recoverable through retry."
        }

    if amount >= 50000 and probability < 0.85:
        return {
            "recovery_decision": "human_review",
            "decision_reason":
                "High-value transaction with insufficient recovery confidence."
        }

    if probability >= 0.70:
        return {
            "recovery_decision": "recover",
            "decision_reason":
                "Recovery probability is above the recovery threshold."
        }

    return {
        "recovery_decision": "do_not_recover",
        "decision_reason":
            "Recovery probability is below the recovery threshold."
    }


# 4. GET ROOT CAUSE REASON

def get_reason(state: State):

    reasons = {
        "bank_server_timeout":
            "The payment gateway server did not respond within the expected time.",

        "card_blocked":
            "The customer's card is blocked.",

        "expired_card":
            "The customer's card has expired.",

        "insufficient_funds":
            "The available balance is insufficient for the transaction.",

        "issuer_bank_down":
            "The customer's issuing bank is unavailable.",

        "otp_cvv_mismatch":
            "The OTP or CVV verification failed.",

        "risk_fraud_block":
            "The transaction was blocked by the risk or fraud detection system.",

        "transaction_limit_exceeded":
            "The transaction exceeded the allowed transaction limit."
    }

    return {
        "reason": reasons[state["root_cause"]]
    }


# 5. RECOMMENDED ACTION
def get_recommended_action(state: State):

    decision = state["recovery_decision"]

    if decision == "human_review":
        return {
            "recommended_action":
                "Send the transaction for human review."
        }

    if decision == "do_not_recover":

        actions = {
            "bank_server_timeout":
                "Do not retry automatically. Monitor the gateway and review manually.",

            "issuer_bank_down":
                "Do not retry automatically. Wait for the issuer bank to recover.",

            "insufficient_funds":
                "Do not retry. Ask the customer to use another payment method or sufficient balance.",

            "otp_cvv_mismatch":
                "Do not retry automatically. Ask the customer to verify OTP or CVV.",

            "card_blocked":
                "Do not retry. Ask the customer to contact their bank or use another card.",

            "expired_card":
                "Do not retry. Ask the customer to use a valid card.",

            "risk_fraud_block":
                "Do not retry. Send the transaction for fraud review.",

            "transaction_limit_exceeded":
                "Do not retry. Ask the customer to use a lower transaction amount.",
        }

        return {
            "recommended_action":
                actions[state["root_cause"]]
        }


    retry_count = state["transaction"]["retry_count"]

    if retry_count >= 3:
        return {
            "recommended_action":
                "Do not retry again. Escalate the transaction for human review."
        }

    actions = {
        "bank_server_timeout":
            "Retry the transaction after the gateway recovers.",

        "issuer_bank_down":
            "Retry the transaction after the issuer bank recovers.",

        "insufficient_funds":
            "Retry after the customer adds sufficient balance.",

        "otp_cvv_mismatch":
            "Ask the customer to re-enter the OTP or CVV.",

        "card_blocked":
            "Ask the customer to contact their bank or use another card.",

        "expired_card":
            "Ask the customer to use a valid card.",

        "risk_fraud_block":
            "Send the transaction for fraud review.",

        "transaction_limit_exceeded":
            "Ask the customer to use a lower transaction amount.",
    }

    return {
        "recommended_action":
            actions[state["root_cause"]]
    }


# 6. ROOT CAUSE CONFIDENCE ROUTER

def confidence_router(state: State):

    if state["confidence"] >= 0.80:
        return "process"

    return "human_review"



# 7. HUMAN REVIEW

def human_review(state: State):

    return {
        "recovery_decision": "human_review",
        "recommended_action":
            "Send the transaction for human review."
    }


# =========================================================
# 8. ACTUAL RECOVERY SIMULATION
# =========================================================

def attempt_recovery(state: State):

    probability = state["recovery_probability"]

    recovered = random.random() < probability

    return {
        "recovered": int(recovered),
        "recovery_attempts":
            state["recovery_attempts"] + 1
    }



# 9. RECOVERY RESULT ROUTER

def recovery_router(state: State):

    if state["recovered"]:
        return "recovered"

    if state["recovery_attempts"] >= 3:
        return "human_review"

    return "retry"