from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field, ConfigDict
from bson import ObjectId

class TokenUsage(BaseModel):
    """
    Represents token usage for a specific user and session.
    This model can be used for MongoDB documents.
    """
    
    id: Optional[str] = Field(alias="_id", default=None)
    user_id: str
    session_id: str
    total_tokens: int = 0
    prompt_tokens: int = 0
    completion_tokens: int = 0
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    metadata: Optional[Dict[str, Any]] = None

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={
            datetime: lambda dt: dt.isoformat(),
            ObjectId: str
        }
    )

    @classmethod
    def from_mongo(cls, data: dict):
        """Convert MongoDB document to TokenUsage model"""
        if not data:
            return None
        if '_id' in data:
            data['_id'] = str(data['_id'])
        return cls(**data)
