from fastapi import APIRouter, HTTPException, Query
from app.models.chat_history_model import ChatHistory, Message
from app.api import (
    add_message_to_session,
    get_chat_history,
    get_user_chat_sessions,
    delete_chat_session,
    update_session_metadata
)
import logging
from typing import List

logger = logging.getLogger(__name__)

router = APIRouter(prefix="", tags=["Chat History"])

@router.post("/{session_id}", response_model=ChatHistory)
async def add_message(session_id: str, message: Message, user_id: str):
    """
    Add a message to the chat session, or create a new session if not exist.
    """
    try:
        return add_message_to_session(session_id, user_id, message)
    except Exception as e:
        logger.error(f"Error adding message to session {session_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Error adding message: {str(e)}")

@router.get("/{session_id}", response_model=ChatHistory)
async def get_history(session_id: str):
    """
    Retrieve the entire chat history of a session.
    """
    session = get_chat_history(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Chat session not found")
    return session

@router.get("/user/{user_id}", response_model=List[ChatHistory])
async def get_user_sessions(
    user_id: str,
    limit: int = Query(default=10, ge=1, le=50)
):
    """
    Get recent chat sessions for a user.
    """
    try:
        return get_user_chat_sessions(user_id, limit)
    except Exception as e:
        logger.error(f"Error getting sessions for user {user_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Error retrieving sessions: {str(e)}")

@router.delete("/{session_id}")
async def delete_session(session_id: str):
    """
    Delete a chat session.
    """
    try:
        success = delete_chat_session(session_id)
        if not success:
            raise HTTPException(status_code=404, detail="Chat session not found")
        return {"message": "Chat session deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting session {session_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Error deleting session: {str(e)}")

@router.patch("/{session_id}/metadata")
async def update_metadata(session_id: str, metadata: dict):
    """
    Update metadata for a chat session.
    """
    try:
        success = update_session_metadata(session_id, metadata)
        if not success:
            raise HTTPException(status_code=404, detail="Chat session not found")
        return {"message": "Metadata updated successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating metadata for session {session_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Error updating metadata: {str(e)}")