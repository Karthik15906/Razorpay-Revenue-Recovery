# Razorpay Revenue Recovery

An AI-powered payment failure analysis and revenue recovery system that identifies the root cause of failed transactions, estimates recovery probability, and decides whether a transaction should be recovered, ignored, or escalated for human review.

The system combines Machine Learning, LangGraph, FastAPI, Docker, Nginx, and a web-based frontend into an end-to-end application.

---

## Overview

Payment failures can happen for many different reasons such as:

- Insufficient funds
- Card expiration
- Card blocking
- Issuer bank downtime
- Gateway timeout
- OTP/CVV mismatch
- Transaction limit exceeded
- Fraud/risk blocking

Instead of treating every failed transaction the same way, this system analyzes transaction-level information and determines:

1. Why the payment failed
2. How confident the ML model is about the root cause
3. How likely the transaction is to be recovered
4. Whether the transaction should be recovered
5. Whether human intervention is required
6. What action should be recommended

---

## System Architecture

```text
                     User
                      |
                      v
              +---------------+
              |   Frontend    |
              | HTML/CSS/JS   |
              +-------+-------+
                      |
                    /api
                      |
                      v
              +---------------+
              |     Nginx     |
              | Reverse Proxy  |
              +-------+-------+
                      |
                      v
              +---------------+
              |    FastAPI    |
              |    Backend     |
              +-------+-------+
                      |
                      v
              +---------------+
              |   LangGraph   |
              | Agent Workflow |
              +-------+-------+
                      |
          +-----------+-----------+
          |                       |
          v                       v
 +----------------+      +------------------+
 | Root Cause ML  |      | Recovery Model   |
 |     Model      |      |                  |
 +----------------+      +------------------+
          |                       |
          +-----------+-----------+
                      |
                      v
              Recovery Decision
                      |
          +-----------+-----------+
          |           |           |
          v           v           v
       Recover    Do Not      Human Review
                  Recover
```

---

### Live Demo

## Link: https://razorpay-revenue-recovery-kh2d.onrender.com/

## Features

### 1. Root Cause Prediction

The system uses a trained machine learning pipeline to predict the most likely reason for a failed payment.

Supported root causes include:

- `bank_server_timeout`
- `card_blocked`
- `expired_card`
- `insufficient_funds`
- `issuer_bank_down`
- `otp_cvv_mismatch`
- `risk_fraud_block`
- `transaction_limit_exceeded`

The model also returns a confidence score for the prediction.

---

### 2. Recovery Probability

A second machine learning pipeline estimates the probability that the failed transaction can be successfully recovered.

The recovery model considers the transaction features together with the predicted root cause.

---

### 3. Confidence-Based Routing

The LangGraph workflow checks the root cause prediction confidence.

```text
Confidence >= 80%
        |
        v
   Continue Processing

Confidence < 80%
        |
        v
   Human Review
```

This prevents low-confidence predictions from being automatically processed.

---

### 4. Recovery Decision

The system applies business rules on top of the ML predictions.

Examples:

- Transactions with too many retries are escalated.
- Fraud-related failures are sent for human review.
- Expired or blocked cards are not automatically retried.
- High-value transactions require higher recovery confidence.
- Transactions with sufficiently high recovery probability can be recovered.

---

### 5. Recovery Simulation

The system simulates a recovery attempt using the predicted recovery probability.

If the simulated recovery succeeds:

```text
Recovered
```

Otherwise, the system can retry up to the configured retry limit before escalating to human review.

---

### 6. Manual Transaction Analysis

Users can enter transaction details manually through the frontend and analyze an individual failed payment.

The interface displays:

- Root cause
- Prediction confidence
- Recovery probability
- Recovery decision
- Recovery status
- Number of recovery attempts
- Recommended action

---

### 7. Generated Dataset Analysis

The application can generate a batch of synthetic payment failure transactions and process them through the complete agent workflow.

The dashboard provides:

- Number of transactions processed
- Total transaction amount
- Money recovered
- Amount at risk
- Human review count
- Recovery rate

---

## Machine Learning Pipeline

### Root Cause Model

The root cause model is trained to classify payment failures into multiple failure categories.

Input features include:

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

The trained pipeline is stored as:

```text
model/root_cause_model.pkl
```

---

### Recovery Probability Model

The recovery probability model predicts the probability that a transaction can be successfully recovered.

The trained pipeline is stored as:

```text
model/recovery_probability_pipeline.pkl
```

---

## LangGraph Workflow

The backend uses LangGraph to coordinate the transaction analysis workflow.

Conceptually:

```text
Transaction
     |
     v
Root Cause Prediction
     |
     v
Confidence Router
     |
     +---- Low Confidence ----> Human Review
     |
     +---- High Confidence
                |
                v
       Recovery Probability
                |
                v
        Recovery Decision
                |
        +-------+-------+
        |       |       |
        v       v       v
     Recover  Do Not  Human Review
              Recover
                |
                v
        Recovery Attempt
                |
        +-------+-------+
        |               |
        v               v
    Recovered        Not Recovered
                        |
                 Retry / Human Review
```

---

## Project Structure

```text
Razorpay Revenue Recovery/
│
├── agent/
│   ├── batch_processor.py
│   ├── graph.py
│   ├── nodes.py
│   ├── state.py
│   └── test_node.py
│
├── backend/
│   ├── __init__.py
│   ├── main.py
│   └── schemas.py
│
├── data/
│   ├── data_cleaning.ipynb
│   ├── data_creator.py
│   └── payment_failures.csv
│
├── frontend/
│   ├── index.html
│   ├── script.js
│   ├── style.css
│   ├── nginx.conf
│   └── Dockerfile
│
├── model/
│   ├── recovery_prob_predictor.py
│   ├── recovery_probability_pipeline.pkl
│   ├── root_cause_model.pkl
│   └── root_cause_predictor.py
│
├── Dockerfile
├── docker-compose.yml
├── .dockerignore
├── .gitignore
├── pyproject.toml
├── uv.lock
└── README.md
```

---

## API

The backend is built with FastAPI.

### Main Endpoints

#### Predict a Transaction

```http
POST /predict
```

Analyzes a single payment failure.

#### Process Generated Transactions

```http
POST /batch?n_rows=50
```

Generates and analyzes a batch of transactions.

---

## Running Locally

### Requirements

- Python 3.14+
- Docker
- Docker Compose
- Git

---

### Run with Docker Compose

Clone the repository:

```bash
git clone https://github.com/Karthik15906/Razorpay-Revenue-Recovery.git
```

Move into the project:

```bash
cd Razorpay-Revenue-Recovery
```

Build and start the containers:

```bash
docker compose up --build
```

The application uses two containers:

```text
Frontend → Nginx
Backend  → FastAPI
```

The local services are available at:

```text
Frontend:
http://localhost:10000

Backend:
http://localhost:8000

Swagger:
http://localhost:8000/docs
```

---

### Run in Background

```bash
docker compose up -d
```

Check running containers:

```bash
docker compose ps
```

View logs:

```bash
docker compose logs
```

Stop the application:

```bash
docker compose down
```

---

## Docker Architecture

The project uses separate containers for the frontend and backend.

### Backend

The backend Docker image contains:

- Python
- uv
- FastAPI
- LangGraph
- scikit-learn
- XGBoost
- pandas
- NumPy
- Trained ML models

The backend exposes:

```text
8000
```

### Frontend

The frontend is served using Nginx.

Nginx serves the static frontend and proxies API requests to the FastAPI backend.

```text
Browser
   |
   | /api/*
   v
Nginx
   |
   v
FastAPI
```

This allows the browser to communicate with the backend without directly exposing the backend URL to the frontend JavaScript.

---

## Deployment

The backend is deployed using Render.

Production backend:

```text
https://razorpay-recovery-backend-16zf.onrender.com
```

The backend runs the Docker image and starts FastAPI using:

```bash
uv run uvicorn backend.main:app --host 0.0.0.0 --port 8000
```

The frontend is also Dockerized and can be deployed separately.

---

## Technology Stack

### Backend

- Python
- FastAPI
- Pydantic
- Uvicorn

### Machine Learning

- scikit-learn
- XGBoost
- pandas
- NumPy
- joblib

### Agent Workflow

- LangGraph

### Frontend

- HTML
- CSS
- JavaScript
- Nginx

### Deployment

- Docker
- Docker Compose
- Render

### Development

- Git
- GitHub
- uv
- VS Code

---

## Example Output

For a transaction, the system can produce a result similar to:

```text
Root Cause:
issuer_bank_down

Confidence:
98.21%

Recovery Probability:
75.95%

Decision:
RECOVER

Recovered:
Yes

Recovery Attempts:
1
```

---

## Business Logic

The system combines machine learning predictions with deterministic business rules.

For example:

```text
Retry Count >= 3
        ↓
Human Review
```

```text
Risk/Fraud Block
        ↓
Human Review
```

```text
Expired Card / Blocked Card
        ↓
Do Not Recover
```

```text
Recovery Probability >= 70%
        ↓
Recover
```

High-value transactions have additional recovery-confidence requirements.

---

## Why This Project?

A payment failure is not always a permanent failure.

Different failures require different actions.

For example:

```text
Issuer Bank Down
        ↓
Wait and Retry
```

while:

```text
Expired Card
        ↓
Ask Customer for a Valid Card
```

and:

```text
Fraud Block
        ↓
Human Review
```

The goal of this project is to demonstrate how machine learning predictions can be combined with an agent workflow and business rules to make more useful payment recovery decisions.

---

## Future Improvements

Possible future improvements include:

- Real payment gateway integration
- Persistent transaction storage
- Authentication and authorization
- Monitoring and logging
- Model monitoring
- Explainable ML predictions
- More sophisticated recovery strategies
- Real-time transaction processing
- Cloud database integration
- Automated model retraining
- Production-grade observability

---

## Author

**Karthik Chukka**

Computer Science Undergraduate
Interested in AI/ML, Data Science and intelligent backend systems.

---

## License

This project is for educational and portfolio purposes.

<img width="857" height="433" alt="image" src="https://github.com/user-attachments/assets/a0486b4d-6c43-4cc4-9d75-2d50cddc1bdf" />
<img width="727" height="415" alt="image" src="https://github.com/user-attachments/assets/8c3cffee-470c-44df-8b48-da5ad5e407ef" />
<img width="671" height="428" alt="image" src="https://github.com/user-attachments/assets/dc90a747-088d-4c5e-8b56-4181bfab50e3" />
<img width="803" height="436" alt="image" src="https://github.com/user-attachments/assets/828543ee-6be2-4c15-ba0c-a86469702b50" />
<img width="781" height="374" alt="image" src="https://github.com/user-attachments/assets/8d6cb981-b316-4755-85f1-361261533858" />
