from langgraph.graph import StateGraph,START,END

from .state import State
from .nodes import (predict_root_cause,get_recommended_action,get_reason,confidence_router,human_review)


graph = StateGraph(State)

graph.add_node('predict_root_cause',predict_root_cause)
graph.add_node('get_reason',get_reason)
graph.add_node('get_recommended_action',get_recommended_action)
graph.add_node('human_review',human_review)

graph.add_edge(START,'predict_root_cause')
graph.add_conditional_edges('predict_root_cause',confidence_router,{'process':'get_reason','human_review':'human_review'})
graph.add_edge('get_reason','get_recommended_action')
graph.add_edge('get_recommended_action',END)
graph.add_edge('human_review',END)

agent = graph.compile()
def run_agent(transaction:dict):
    state={
        "transaction": transaction,
        "root_cause": "",
        "confidence": 0.0,
        "reason": "",
        "recommended_action": ""
    }
    result = agent.invoke(state)

    return {
        "root_cause": result["root_cause"],
        "confidence": result["confidence"],
        "reason": result["reason"],
        "recommended_action": result["recommended_action"]
    }