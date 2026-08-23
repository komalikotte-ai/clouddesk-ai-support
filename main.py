from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from backend.support_agent import SupportAgent
from backend.schemas import ChatRequest, ChatResponse


# The SupportAgent loads a sentence-transformer model and opens a
# ChromaDB client in its __init__ -- that's slow (multi-second) and
# should happen exactly once when the server starts, not on every
# request. It's stored here and created/torn down via the lifespan
# hook below.
agent: SupportAgent | None = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global agent
    agent = SupportAgent()
    yield
    agent = None


app = FastAPI(
    title="CloudDesk AI Support API",
    lifespan=lifespan
)

# The Streamlit frontend calls this API with server-side `requests`,
# not a browser fetch, so CORS isn't strictly required for that path
# -- but it's left open here in case you ever call this from a
# browser-based client too.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):

    if not request.message or not request.message.strip():
        raise HTTPException(
            status_code=400,
            detail="message must not be empty"
        )

    if agent is None:
        raise HTTPException(
            status_code=503,
            detail="Support agent is still starting up. Try again shortly."
        )

    result = agent.process_message(request.message)

    return result
