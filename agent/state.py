from typing import TypedDict


class State(TypedDict):
    transaction: dict
    root_cause: str
    confidence: float
    reason: str
    recommended_action: str
    recovery_probability: float
    recovery_decision: str
    decision_reason: str
    recovered: bool
    recovery_attempts: int