from langgraph.graph import StateGraph, START, END

from .state import State

from .nodes import (
    predict_root_cause,
    predict_recovery_probability,
    recovery_decision,
    get_reason,
    get_recommended_action,
    confidence_router,
    human_review,
    attempt_recovery,
    recovery_router,
)


graph = StateGraph(State)


# -------------------------
# Nodes
# -------------------------

graph.add_node(
    "predict_root_cause",
    predict_root_cause
)

graph.add_node(
    "predict_recovery_probability",
    predict_recovery_probability
)

graph.add_node(
    "recovery_decision",
    recovery_decision
)

graph.add_node(
    "get_reason",
    get_reason
)

graph.add_node(
    "get_recommended_action",
    get_recommended_action
)

graph.add_node(
    "attempt_recovery",
    attempt_recovery
)

graph.add_node(
    "human_review",
    human_review
)


# -------------------------
# Root cause
# -------------------------

graph.add_edge(
    START,
    "predict_root_cause"
)


graph.add_conditional_edges(
    "predict_root_cause",
    confidence_router,
    {
        "process": "predict_recovery_probability",
        "human_review": "human_review",
    }
)


# -------------------------
# Recovery probability
# -------------------------

graph.add_edge(
    "predict_recovery_probability",
    "recovery_decision"
)


# -------------------------
# Recovery decision
# -------------------------

graph.add_conditional_edges(
    "recovery_decision",
    lambda state: state["recovery_decision"],
    {
        "recover": "get_reason",
        "do_not_recover": "get_reason",
        "human_review": "human_review",
    }
)


# -------------------------
# Reason + action
# -------------------------

graph.add_edge(
    "get_reason",
    "get_recommended_action"
)


# -------------------------
# IMPORTANT
# -------------------------
# Only "recover" should reach attempt_recovery.

graph.add_conditional_edges(
    "get_recommended_action",
    lambda state: state["recovery_decision"],
    {
        "recover": "attempt_recovery",
        "do_not_recover": END,
    }
)


# -------------------------
# Recovery loop
# -------------------------

graph.add_conditional_edges(
    "attempt_recovery",
    recovery_router,
    {
        "recovered": END,
        "retry": "attempt_recovery",
        "human_review": "human_review",
    }
)


# -------------------------
# Human review
# -------------------------

graph.add_edge(
    "human_review",
    END
)


agent = graph.compile()


def run_agent(transaction: dict):

    state: State = {
        "transaction": transaction,

        "root_cause": "",
        "confidence": 0.0,

        "recovery_probability": 0.0,
        "recovery_decision": "",
        "decision_reason": "",

        "reason": "",
        "recommended_action": "",

        "recovered": False,
        "recovery_attempts": 0,
    }

    return agent.invoke(state)