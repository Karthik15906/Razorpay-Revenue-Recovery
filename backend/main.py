from fastapi import FastAPI
from agent.graph import run_agent
app = FastAPI()

@app.post('/')
def predict(transaction:dict):
    return run_agent(transaction)