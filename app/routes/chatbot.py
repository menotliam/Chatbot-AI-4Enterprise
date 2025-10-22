from fastapi import APIRouter, HTTPException, Body, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel as PydanticBaseModel, Field, validator
from typing import List, Optional
import uuid
import logging
from app.api import (
    update_token_usage,
    create_or_get_session,
    add_message_to_session,
    process_message_with_assistant_tool
)
from ..models.chat_history_model import Message

logger = logging.getLogger(__name__)
router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

# Request/Response Models
class ChatRequest(PydanticBaseModel):
    session_id: Optional[str] = None
    user_id: str
    message: str = Field(..., min_length=1, max_length=4000)
    enhance_response: Optional[bool] = True

    @validator('message')
    def validate_message(cls, v):
        if not v.strip():
            raise ValueError('Message cannot be empty or contain only whitespace')
        return v

class ChatResponse(PydanticBaseModel):
    session_id: str
    reply: str
    history: List[Message]

# Routes
@router.post("/interact", response_model=ChatResponse)
async def handle_chat_interaction(request: ChatRequest = Body(...)):
    """Handle chat interaction with product search integration"""
    session_id = request.session_id or str(uuid.uuid4())

    try:
        # Load or create chat session
        chat_session = create_or_get_session(
            session_id=session_id, 
            user_id=request.user_id
        )
       
        # Add user message
        user_message = Message(role="user", content=request.message)
        chat_session = add_message_to_session(
            session_id, 
            request.user_id, 
            user_message
        )
       
        # Process message and get response with session context
        enhance_response_value = getattr(request, 'enhance_response', True)
        logger.info(f"Chat request with enhance_response={enhance_response_value}")
        
        bot_reply_content, token_usage = await process_message_with_assistant_tool(
            message=request.message,
            session_id=session_id,
            enhance_response=enhance_response_value
        )
        
        # Add bot's reply to history
        bot_message = Message(role="assistant", content=bot_reply_content)
        chat_session = add_message_to_session(
            session_id, 
            request.user_id, 
            bot_message
        )

        # Track token usage
        await update_token_usage(
            user_id=request.user_id,
            session_id=session_id,
            prompt_tokens=token_usage["prompt_tokens"],
            completion_tokens=token_usage["completion_tokens"],
            metadata={
                "model": "gpt-4.1",
                "interaction_type": "chat",
                "message_count": len(chat_session.messages)
            }
        )

        return ChatResponse(
            session_id=chat_session.session_id,
            reply=bot_reply_content,
            history=chat_session.messages
        )

    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error in /chatbot/interact: {e}")
        raise HTTPException(status_code=500, detail="An internal server error occurred.")

#Renders the main chat interface (HTML page) for the user.

@router.get("/", response_class=HTMLResponse)
async def chat_page(request: Request):
    """Render the chat interface"""
    return templates.TemplateResponse(
        "chat.html",
        {"request": request}
    )

#Renders a page listing all available products.
