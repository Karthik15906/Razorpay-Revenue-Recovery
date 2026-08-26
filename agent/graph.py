from langgraph.graph import StateGraph,START,END

from .state import State
from .nodes import (predict_root_cause,get_recommended_action,get_reason,confidence_router,human_review,attempt_recovery,recovery_router)


graph = StateGraph(State)

graph.add_node('predict_root_cause',predict_root_cause)
graph.add_node('get_reason',get_reason)
graph.add_node('get_recommended_action',get_recommended_action)
graph.add_node('human_review',human_review)
graph.add_node("attempt_recovery", attempt_recovery)

graph.add_edge(START,'predict_root_cause')
graph.add_conditional_edges('predict_root_cause',confidence_router,{'process':'get_reason','human_review':'human_review'})
graph.add_edge('get_reason','get_recommended_action')
graph.add_edge("get_recommended_action","attempt_recovery")
graph.add_conditional_edges("attempt_recovery",recovery_router,{"recovered": END,"retry": "attempt_recovery","human_review": "human_review"})
graph.add_edge('human_review',END)

agent = graph.compile()
def run_agent(transaction:dict):
    state : State={
        "transaction": transaction,
        "root_cause": "",
        "confidence": 0.0,
        "reason": "",
        "recommended_action": "",
        'recovered': 0,
        'recovery_attempts': 0
    }
    return  agent.invoke(state)

