from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from agent.graph import run_agent
from .schemas import Transaction
from agent.batch_processor import process_dataset


import pandas as pd
from pathlib import Path

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

DATA_PATH = Path(__file__).resolve().parents[1] / "data" / "payment_failures.csv"


def get_random_transaction():
    df = pd.read_csv(DATA_PATH)
    row = df.sample(1).iloc[0]

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
        "recovered": row["recovered"],
    }

    return Transaction(**transaction)

@app.post("/predict")
def predict(transaction: Transaction):
    return run_agent(transaction.model_dump())


@app.post('/predict/random')
def predict_random():
    transaction = get_random_transaction()
    return run_agent(transaction.model_dump())

@app.post('/batch')
def batch(n_rows: int):
    return process_dataset(n_rows)
