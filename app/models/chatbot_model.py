from pydantic import BaseModel
from typing import List, Optional
from .chat_history_model import Message

class ChatRequest(BaseModel):
    session_id: Optional[str] = None
    user_id: str
    message: str

class ChatResponse(BaseModel):
    session_id: str
    reply: str
    history: List[Message] 