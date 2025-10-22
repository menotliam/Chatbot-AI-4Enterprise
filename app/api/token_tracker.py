from typing import Optional, List, Dict
from datetime import datetime, timezone
from app.models.token_usage_model import TokenUsage
from app.database import get_token_usage_collection
import logging
from bson import ObjectId

logger = logging.getLogger(__name__)

async def create_or_get_token_usage(user_id: str, session_id: str) -> TokenUsage:
    """Create or get token usage record for a user and session"""
    collection = get_token_usage_collection()
    
    # Try to find existing record
    existing = collection.find_one({
        "user_id": user_id,
        "session_id": session_id
    })
    
    if existing:
        return TokenUsage.from_mongo(existing)
    
    # Create new token usage record
    new_usage = TokenUsage(
        user_id=user_id,
        session_id=session_id,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )
    
    # Insert into MongoDB
    usage_dict = new_usage.model_dump(by_alias=True)
    if '_id' in usage_dict:
        del usage_dict['_id']  # Remove _id to let MongoDB generate it
    
    result = collection.insert_one(usage_dict)
    new_usage.id = str(result.inserted_id)  # Convert ObjectId to string
    return new_usage

async def update_token_usage(
    user_id: str,
    session_id: str,
    prompt_tokens: int,
    completion_tokens: int,
    metadata: Optional[Dict] = None
) -> TokenUsage:
    """Update token usage for a user and session"""
    collection = get_token_usage_collection()
    
    # Get current usage
    usage = await create_or_get_token_usage(user_id, session_id)
    
    # Update fields
    usage.prompt_tokens += prompt_tokens
    usage.completion_tokens += completion_tokens
    usage.total_tokens = usage.prompt_tokens + usage.completion_tokens
    usage.updated_at = datetime.now(timezone.utc)
    if metadata:
        usage.metadata = metadata
    
    # Update in MongoDB
    update_data = usage.model_dump(by_alias=True)
    if "_id" in update_data:
        del update_data["_id"]  # Remove _id from update data
    
    # Use findOneAndUpdate with upsert to handle both insert and update cases
    result = collection.find_one_and_update(
        {"user_id": user_id, "session_id": session_id},
        {"$set": update_data},
        upsert=True,
        return_document=True
    )
    
    if result:
        return TokenUsage.from_mongo(result)
    return usage

async def get_token_usage(user_id: str, session_id: str) -> Optional[TokenUsage]:
    """Get token usage for a user and session"""
    collection = get_token_usage_collection()
    result = collection.find_one({
        "user_id": user_id,
        "session_id": session_id
    })
    
    return TokenUsage.from_mongo(result) if result else None

async def get_user_token_usage(user_id: str) -> List[TokenUsage]:
    """Get all token usage records for a user"""
    collection = get_token_usage_collection()
    cursor = collection.find({"user_id": user_id})
    
    return [TokenUsage.from_mongo(doc) for doc in cursor if doc]