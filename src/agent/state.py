from typing import TypedDict

class State(TypedDict):
    transaction:dict
    root_cause:str
    confidence:float
    reason:str
    recomended_action:str
    