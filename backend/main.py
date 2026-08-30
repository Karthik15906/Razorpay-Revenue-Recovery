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



@app.post("/predict")
def predict(transaction: Transaction):

    result = run_agent(transaction.model_dump())

    return {
        "transaction_id": "MANUAL",
        "transaction": transaction.model_dump(),

        "predicted_root_cause":
            result["root_cause"],

        "confidence":
            result["confidence"],

        "recovery_probability":
            result["recovery_probability"],

        "recovery_decision":
            result["recovery_decision"],

        "decision_reason":
            result["decision_reason"],

        "reason":
            result["reason"],

        "recommended_action":
            result["recommended_action"],

        "recovered":
            result["recovered"],

        "recovery_attempts":
            result["recovery_attempts"],
    }

@app.post('/batch')
def batch(n_rows: int):
    return process_dataset(n_rows)
