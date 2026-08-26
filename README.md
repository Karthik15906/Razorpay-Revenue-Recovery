# Razorpay Revenue Recovery

An AI-powered payment failure analysis and revenue recovery system that identifies the root cause of failed transactions, recommends an action, attempts recovery, and escalates transactions to human review when recovery fails repeatedly.

## Overview

The system processes payment transactions through an ML model and a LangGraph-based workflow.

For each transaction, it:

1. Predicts the payment failure root cause.
2. Calculates prediction confidence.
3. Generates an explanation for the failure.
4. Recommends an appropriate action.
5. Attempts transaction recovery.
6. Retries recovery when it fails.
7. Escalates to human review after repeated failures.
8. Reports recovered revenue and money still at risk.

The project supports both **manual transaction analysis** and **generated batch datasets**.

---

## Architecture

```text
                    ┌─────────────────────┐
                    │      Frontend       │
                    │     HTML/CSS/JS     │
                    └──────────┬──────────┘
                               │
                               │ HTTP / JSON
                               ▼
                    ┌─────────────────────┐
                    │       FastAPI       │
                    │      Backend        │
                    └──────────┬──────────┘
                               │
                ┌──────────────┴──────────────┐
                │                             │
                ▼                             ▼
        Manual Transaction             Generated Dataset
                │                             │
                │                             ▼
                │                    Batch Processor
                │                             │
                └──────────────┬──────────────┘
                               ▼
                    ┌─────────────────────┐
                    │      LangGraph      │
                    │       Agent         │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │    XGBoost Model    │
                    │   Root Cause Model  │
                    └─────────────────────┘
```

---

## LangGraph Workflow

The transaction goes through a workflow similar to:

```text
             Transaction
                  │
                  ▼
          Predict Root Cause
                  │
                  ▼
          Confidence Router
            /           \
       High confidence   Low confidence
           │                 │
           ▼                 ▼
       Get Reason       Human Review
           │
           ▼
    Recommended Action
           │
           ▼
     Attempt Recovery
        /          \
   Recovered      Failed
      │             │
      ▼             ▼
     END       Recovery Attempts
                    │
             ┌──────┴──────┐
             │             │
            < 3           >= 3
             │             │
             ▼             ▼
           Retry      Human Review
```

---

## Machine Learning Model

The root cause classifier uses **XGBoost**.

### Root causes

The model currently predicts:

* `insufficient_funds`
* `expired_card`
* `bank_server_timeout`
* `otp_cvv_mismatch`
* `issuer_bank_down`
* `transaction_limit_exceeded`
* `risk_fraud_block`
* `card_blocked`

### Features

The model uses transaction-level observable features such as:

```text
amount
payment_method
card_age_days
card_expiry_days
retry_count
customer_tenure_days
customer_past_success_rate
gateway_response_time_ms
gateway_status
issuer_response_time_ms
issuer_status
risk_score
available_balance_ratio
transaction_limit
otp_attempts
cvv_match
```

Identifiers and fields that should not be used for root-cause prediction, such as `transaction_id`, `timestamp`, and the target `root_cause`, are excluded during training.

The trained model is stored as:

```text
model/root_cause_model.pkl
```

The model is loaded once when `nodes.py` is imported, so it remains in memory instead of being loaded for every transaction.

---

## Recovery System

Recovery is attempted after the root cause has been identified.

Each root cause has a recovery probability used to simulate realistic recovery behavior:

```python
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
```

A recovery attempt returns:

```python
{
    "recovered": 0 or 1,
    "recovery_attempts": ...
}
```

If recovery succeeds:

```text
END
```

If recovery fails:

```text
attempts < 3 → retry
attempts >= 3 → human review
```

---

## Dataset Generator

The project contains a synthetic payment failure dataset generator.

The user can specify the number of transactions to generate.

For example:

```text
10
30
100
1000
```

The generator creates realistic transaction features and cause-specific signals.

The generated data can be passed directly to the batch processor without requiring the user to manually create a CSV first.

---

## Batch Processing

The batch processor:

1. Generates the requested number of transactions.
2. Converts each row into the transaction format expected by the agent.
3. Invokes the LangGraph workflow.
4. Collects the result for every transaction.
5. Calculates revenue recovery statistics.

The final summary includes:

```text
Processed
Total Amount
Money Recovered
Amount at Risk
Human Review
Recovery Rate
```

### Recovery rate

Recovery rate is based on **money**, rather than the number of transactions:

```text
Recovery Rate =
    Money Recovered / Total Amount × 100
```

This gives a more meaningful measure of revenue recovery.

---

## API

The backend is built using **FastAPI**.

### Manual prediction

```http
POST /predict
```

The frontend sends the transaction fields directly:

```json
{
    "payment_method": "credit_card",
    "gateway_status": "operational",
    "issuer_status": "operational",
    "amount": 500,
    "card_age_days": 400,
    "card_expiry_days": 250,
    "retry_count": 1,
    "customer_tenure_days": 800,
    "customer_past_success_rate": 0.92,
    "gateway_response_time_ms": 350,
    "issuer_response_time_ms": 300,
    "risk_score": 0.15,
    "available_balance_ratio": 0.08,
    "transaction_limit": 5000,
    "otp_attempts": 1,
    "cvv_match": 1
}
```

### Batch processing

```http
POST /batch
```

The endpoint accepts the number of transactions:

```text
n_rows
```

and returns:

```json
{
    "results": [],
    "summary": {
        "processed": 30,
        "total_amount": 61750.5,
        "recovered_amount": 52990.5,
        "amount_at_risk": 8760,
        "human_review": 4,
        "recovery_rate": 85.9
    }
}
```

---

## Frontend

The frontend is built using:

* HTML
* CSS
* JavaScript

It provides two modes:

### Manual Transaction

The user enters transaction information manually and receives the analysis.

### Generated Dataset

The user enters the number of transactions:

```text
Number of transactions: 30
```

The backend generates and processes the transactions.

The dashboard displays:

```text
Processed
Total Amount
Money Recovered
Amount at Risk
Human Review
Recovery Rate
```

It also provides a transaction-level results table containing:

```text
Transaction
Root Cause
Confidence
Recovery
Attempts
Action
```

Clicking a transaction displays its detailed analysis.

---

## Project Structure

```text
Razorpay Revenue Recovery/
│
├── agent/
│   ├── __init__.py
│   ├── graph.py
│   ├── nodes.py
│   ├── state.py
│   ├── batch_processor.py
│   └── test_node.py
│
├── backend/
│   └── main.py
│
├── data/
│   ├── data_creator.py
│   └── data_cleaning.ipynb
│
├── model/
│   └── root_cause_model.pkl
│
├── frontend/
│   ├── index.html
│   ├── style.css
│   └── script.js
│
├── .gitignore
├── pyproject.toml
├── requirements.txt
├── README.md
└── uv.lock
```

---

## Running the Project

### Start the FastAPI backend

From the project root:

```bash
uvicorn backend.main:app --reload
```

The API will run on:

```text
http://127.0.0.1:8000
```

### Run batch processing directly

```bash
python -m agent.batch_processor
```

### Open the frontend

Open:

```text
frontend/index.html
```

in the browser.

The frontend communicates with:

```text
http://127.0.0.1:8000
```

---

## Technologies

```text
Python
Pandas
NumPy
Scikit-learn
XGBoost
LangGraph
LangChain
FastAPI
HTML
CSS
JavaScript
Joblib
```

---

## Current Status

### Completed

* Synthetic payment failure dataset generation
* Root-cause classification
* XGBoost model training
* Categorical feature encoding
* Model persistence with Joblib
* LangGraph workflow
* Confidence-based routing
* Root-cause explanations
* Recommended actions
* Recovery attempts
* Retry logic
* Human-review escalation
* Batch transaction processing
* Revenue recovery calculations
* FastAPI backend
* HTML/CSS/JS frontend
* Manual transaction analysis
* Generated dataset analysis
* Frontend dashboard
* Transaction-level results

### Current goal

Turn the prototype into a complete **payment failure diagnosis and revenue recovery system** that can demonstrate both ML prediction and agentic decision-making.
