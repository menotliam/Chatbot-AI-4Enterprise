from typing import Optional, List
from datetime import datetime, timezone
from app.models.chat_history_model import ChatHistory, Message
from uuid import uuid4
from app.database import get_chat_history_collection
from bson import ObjectId
import logging

logger = logging.getLogger(__name__)

def create_or_get_session(session_id: Optional[str], user_id: str) -> ChatHistory:
    """Create a new chat session or get existing one"""
    collection = get_chat_history_collection()
    
    if session_id:
        # Try to find existing session
        session_data = collection.find_one({"session_id": session_id})
        if session_data:
            # Convert MongoDB document to ChatHistory model
            session_data["_id"] = str(session_data["_id"])  # Convert ObjectId to string
            return ChatHistory(**session_data)
    
    # Create new session
    new_session_id = session_id or str(uuid4())
    new_session = ChatHistory(
        session_id=new_session_id,
        user_id=user_id,
        messages=[],
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )
    
    # Insert into MongoDB
    session_dict = new_session.model_dump(by_alias=True)
    if '_id' in session_dict:
        del session_dict['_id']

    result = collection.insert_one(session_dict)
    new_session.id = str(result.inserted_id)
    
    return new_session

def add_message_to_session(session_id: str, user_id: str, message: Message) -> ChatHistory:
    """Add a message to an existing chat session"""
    collection = get_chat_history_collection()
    
    # Get existing session
    session_data = collection.find_one({"session_id": session_id})
    if not session_data:
        # Create new session if not exists
        return create_or_get_session(session_id, user_id)
    
    # Update session with new message
    update_result = collection.update_one(
        {"session_id": session_id},
        {
            "$push": {"messages": message.dict()},
            "$set": {"updated_at": datetime.now(timezone.utc)}
        }
    )
    
    if update_result.modified_count == 0:
        logger.error(f"Failed to update session {session_id}")
        raise Exception("Failed to update chat session")
    
    # Get updated session
    updated_session = collection.find_one({"session_id": session_id})
    updated_session["_id"] = str(updated_session["_id"])
    return ChatHistory(**updated_session)

def get_chat_history(session_id: str) -> Optional[ChatHistory]:
    """Get chat history for a session"""
    collection = get_chat_history_collection()
    session_data = collection.find_one({"session_id": session_id})
    
    if session_data:
        session_data["_id"] = str(session_data["_id"])
        return ChatHistory(**session_data)
    return None

def get_user_chat_sessions(user_id: str, limit: int = 10) -> List[ChatHistory]:
    """Get recent chat sessions for a user"""
    collection = get_chat_history_collection()
    sessions = collection.find(
        {"user_id": user_id}
    ).sort("updated_at", -1).limit(limit)
    
    return [ChatHistory(**{**session, "_id": str(session["_id"])}) for session in sessions]

def delete_chat_session(session_id: str) -> bool:
    """Delete a chat session"""
    collection = get_chat_history_collection()
    result = collection.delete_one({"session_id": session_id})
    return result.deleted_count > 0

def update_session_metadata(session_id: str, metadata: dict) -> bool:
    """Update metadata for a chat session"""
    collection = get_chat_history_collection()
    result = collection.update_one(
        {"session_id": session_id},
        {"$set": {"metadata": metadata, "updated_at": datetime.now(timezone.utc)}}
    )
    return result.modified_count > 0