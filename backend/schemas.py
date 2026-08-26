from pydantic import BaseModel


class Transaction(BaseModel):
    payment_method: str
    gateway_status: str
    issuer_status: str

    amount: float
    card_age_days: int
    card_expiry_days: int
    retry_count: int

    customer_tenure_days: int
    customer_past_success_rate: float

    gateway_response_time_ms: int
    issuer_response_time_ms: int

    risk_score: float
    available_balance_ratio: float
    transaction_limit: float

    otp_attempts: int
    cvv_match: int