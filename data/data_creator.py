import numpy as np
import pandas as pd
from pathlib import Path

rng = np.random.default_rng(42)
n = 10_000

root_causes = [
    "insufficient_funds",
    "expired_card",
    "bank_server_timeout",
    "otp_cvv_mismatch",
    "issuer_bank_down",
    "transaction_limit_exceeded",
    "risk_fraud_block",
    "card_blocked",
]
probs = [0.25, 0.15, 0.15, 0.12, 0.12, 0.10, 0.06, 0.05]
cause = rng.choice(root_causes, size=n, p=probs)

df = pd.DataFrame({
    "transaction_id": [f"TXN{100000+i}" for i in range(n)],
    "timestamp": pd.Timestamp("2026-01-01") + pd.to_timedelta(
        rng.integers(0, 180*24*60*60, n), unit="s"
    ),
    "amount": np.round(np.exp(rng.normal(np.log(1800), 1.0, n)).clip(50, 100000), 2),
    "payment_method": rng.choice(["credit_card", "debit_card"], n, p=[0.55, 0.45]),
    "card_age_days": rng.integers(30, 2500, n),
    "card_expiry_days": rng.integers(30, 1200, n),
    "retry_count": rng.choice([0, 1, 2, 3], n, p=[0.58, 0.25, 0.12, 0.05]),
    "customer_tenure_days": rng.integers(7, 2500, n),
    "customer_past_success_rate": np.round(rng.beta(8, 2, n), 3),
    "gateway_response_time_ms": np.round(rng.lognormal(np.log(350), 0.45, n)).astype(int),
    "gateway_status": rng.choice(["operational", "degraded"], n, p=[0.92, 0.08]),
    "issuer_response_time_ms": np.round(rng.lognormal(np.log(300), 0.5, n)).astype(int),
    "issuer_status": rng.choice(["operational", "degraded", "down"], n, p=[0.91, 0.06, 0.03]),
    "response_code": rng.choice(
        ["GENERIC_DECLINE", "TEMPORARY_FAILURE", "AUTH_FAILURE", "LIMIT_FAILURE"],
        n
    ),
    "risk_score": np.round(rng.beta(2, 8, n), 3),
    "available_balance_ratio": np.round(rng.beta(5, 3, n), 3),
    "transaction_limit": np.round(np.exp(rng.normal(np.log(5000), 0.65, n)).clip(500, 50000), 2),
    "otp_attempts": rng.choice([0, 1, 2, 3], n, p=[0.60, 0.25, 0.10, 0.05]),
    "cvv_match": rng.choice([0, 1], n, p=[0.08, 0.92]),
    "root_cause": cause,
})

# Inject cause-specific, observable signals with overlap/noise.
for c in root_causes:
    m = df["root_cause"].eq(c)
    count = m.sum()
    if c == "expired_card":
        df.loc[m, "card_expiry_days"] = rng.integers(-900, 0, count)
        df.loc[m, "response_code"] = rng.choice(["CARD_EXPIRED", "GENERIC_DECLINE"], count, p=[0.88, 0.12])
        df.loc[m, "gateway_response_time_ms"] = np.round(rng.lognormal(np.log(320), .35, count)).astype(int)
    elif c == "card_blocked":
        df.loc[m, "response_code"] = rng.choice(["CARD_BLOCKED", "GENERIC_DECLINE"], count, p=[.86, .14])
        df.loc[m, "risk_score"] = np.round(rng.beta(3, 6, count), 3)
    elif c == "insufficient_funds":
        df.loc[m, "available_balance_ratio"] = np.round(rng.beta(1.4, 7, count), 3)
        df.loc[m, "response_code"] = rng.choice(["INSUFFICIENT_FUNDS", "GENERIC_DECLINE"], count, p=[.9, .1])
    elif c == "transaction_limit_exceeded":
        df.loc[m, "transaction_limit"] = np.maximum(
            500, df.loc[m, "amount"].to_numpy() * rng.uniform(.35, .95, count)
        )
        df.loc[m, "response_code"] = rng.choice(["LIMIT_EXCEEDED", "LIMIT_FAILURE"], count, p=[.82, .18])
    elif c == "otp_cvv_mismatch":
        df.loc[m, "cvv_match"] = rng.choice([0, 1], count, p=[.85, .15])
        df.loc[m, "otp_attempts"] = rng.choice([1, 2, 3], count, p=[.45, .4, .15])
        df.loc[m, "response_code"] = rng.choice(["OTP_CVV_MISMATCH", "AUTH_FAILURE"], count, p=[.9, .1])
    elif c == "bank_server_timeout":
        df.loc[m, "gateway_response_time_ms"] = np.round(rng.lognormal(np.log(7000), .45, count)).astype(int)
        df.loc[m, "gateway_status"] = rng.choice(["degraded", "operational"], count, p=[.82, .18])
        df.loc[m, "issuer_status"] = rng.choice(["operational", "degraded"], count, p=[.82, .18])
        df.loc[m, "response_code"] = rng.choice(["BANK_TIMEOUT", "TEMPORARY_FAILURE"], count, p=[.78, .22])
    elif c == "issuer_bank_down":
        df.loc[m, "issuer_status"] = rng.choice(["down", "degraded"], count, p=[.82, .18])
        df.loc[m, "issuer_response_time_ms"] = np.round(rng.lognormal(np.log(7000), .5, count)).astype(int)
        df.loc[m, "gateway_status"] = rng.choice(["operational", "degraded"], count, p=[.85, .15])
        df.loc[m, "response_code"] = rng.choice(["ISSUER_DOWN", "TEMPORARY_FAILURE"], count, p=[.8, .2])
    elif c == "risk_fraud_block":
        df.loc[m, "risk_score"] = np.round(rng.beta(9, 1.8, count), 3)
        df.loc[m, "response_code"] = rng.choice(["RISK_BLOCK", "GENERIC_DECLINE"], count, p=[.9, .1])
    elif c == "card_blocked":
        df.loc[m, "retry_count"] = rng.choice([0, 1, 2], count, p=[.55, .3, .15])

# Small realistic noise: a minority of signals don't perfectly agree with the label.
noise_cols = ["gateway_status", "issuer_status", "response_code", "cvv_match"]
for col in noise_cols:
    mask = rng.random(n) < 0.025
    if col == "gateway_status":
        df.loc[mask, col] = rng.choice(["operational", "degraded"], mask.sum())
    elif col == "issuer_status":
        df.loc[mask, col] = rng.choice(["operational", "degraded", "down"], mask.sum())
    elif col == "response_code":
        df.loc[mask, col] = rng.choice(
            ["GENERIC_DECLINE", "TEMPORARY_FAILURE", "AUTH_FAILURE", "LIMIT_FAILURE"], mask.sum()
        )
    else:
        df.loc[mask, col] = 1 - df.loc[mask, col].astype(int)

# Recovery outcome: based primarily on cause, retry state, and realistic randomness.
base_recovery = {
    "insufficient_funds": .42,
    "expired_card": .12,
    "bank_server_timeout": .78,
    "otp_cvv_mismatch": .52,
    "issuer_bank_down": .74,
    "transaction_limit_exceeded": .60,
    "risk_fraud_block": .03,
    "card_blocked": .08,
}
p_recover = df["root_cause"].map(base_recovery).to_numpy()
p_recover += np.where(df["retry_count"].to_numpy() == 0, .04, 0)
p_recover -= np.where(df["retry_count"].to_numpy() >= 3, .08, 0)
p_recover = np.clip(p_recover, .01, .95)
df["recovered"] = rng.binomial(1, p_recover)

# Keep schema tidy.
df["timestamp"] = pd.to_datetime(df["timestamp"]).dt.strftime("%Y-%m-%d %H:%M:%S")
df["amount"] = df["amount"].round(2)
df["transaction_limit"] = df["transaction_limit"].round(2)

out = Path("payment_failures.csv")
df.to_csv(out, index=False)

print(f"Created {out.resolve()}")
print(f"Rows: {len(df):,}")
print("\nRoot-cause distribution:")
print(df["root_cause"].value_counts())
print("\nRecovery rate by root cause:")
print(df.groupby("root_cause")["recovered"].mean().sort_values(ascending=False).round(3))
print("\nColumns:")
print(df.columns.tolist())
