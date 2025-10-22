from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from app.models.token_usage_model import TokenUsage
from app.api import (
    update_token_usage as api_update_token_usage,
    get_token_usage as api_get_token_usage,
    get_user_token_usage as api_get_user_token_usage
)
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="", tags=["Token Tracker"])

@router.post("/usage", response_model=TokenUsage)
async def update_token_usage(
    user_id: str,
    session_id: str,
    prompt_tokens: int,
    completion_tokens: int,
    metadata: Optional[dict] = None
):
    """
    Update token usage for a user and session.
    """
    try:
        return await api_update_token_usage(
            user_id=user_id,
            session_id=session_id,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            metadata=metadata
        )
    except Exception as e:
        logger.error(f"Error updating token usage: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/usage/{user_id}/{session_id}", response_model=TokenUsage)
async def get_token_usage(user_id: str, session_id: str):
    """
    Get token usage for a specific user and session.
    """
    try:
        usage = await api_get_token_usage(user_id, session_id)
        if not usage:
            raise HTTPException(status_code=404, detail="Token usage not found")
        return usage
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting token usage: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/usage/{user_id}", response_model=List[TokenUsage])
async def get_user_token_usage(user_id: str):
    """
    Get all token usage records for a user.
    """
    try:
        return await api_get_user_token_usage(user_id)
    except Exception as e:
        logger.error(f"Error getting user token usage: {e}")
        raise HTTPException(status_code=500, detail=str(e))
