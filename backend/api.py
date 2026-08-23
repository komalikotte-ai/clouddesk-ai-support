from fastapi import FastAPI
from pydantic import BaseModel

from backend.support_agent import SupportAgent


app = FastAPI(
    title="CloudDesk Customer Support AI Employee",
    description="Tier-1 customer support AI system for Supervity technical assessment",
    version="1.0.0"
)


# Initialize the AI Employee
agent = SupportAgent()


class ChatRequest(BaseModel):
    message: str


@app.get("/")
def root():
    return {
        "status": "online",
        "service": "CloudDesk Customer Support AI Employee"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }


@app.post("/chat")
def chat(request: ChatRequest):

    result = agent.process_message(
        request.message
    )

    return result