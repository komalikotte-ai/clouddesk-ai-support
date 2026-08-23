from typing import List, Optional

from pydantic import BaseModel


class ChatRequest(BaseModel):
    message: str


class SourceItem(BaseModel):
    source: str
    distance: Optional[float] = None


class ChatResponse(BaseModel):
    message: str
    category: str
    confidence: float
    status: str
    reason: str
    answer: str
    sources: List[SourceItem] = []