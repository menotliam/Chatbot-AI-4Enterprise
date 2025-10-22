from pydantic import BaseModel, Field, ConfigDict
from typing import List, Dict, Any, Optional
from datetime import datetime
import uuid

class Message(BaseModel):
    """
    Represents a single message in a chat conversation.
    """
    role: str  
    content: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class ChatHistory(BaseModel):
    """
    Represents the entire chat history for a session.
    This model can be used for MongoDB documents.
    """
    
    id: Optional[str] = Field(alias="_id", default=None)
    session_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str 
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    messages: List[Message] = []
    metadata: Optional[Dict[str, Any]] = None  

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={
            datetime: lambda dt: dt.isoformat()
        }
    )