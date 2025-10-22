from fastapi import APIRouter, Request, HTTPException, Response
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import os
import httpx
import logging
import hmac
import hashlib

router = APIRouter()

PAGE_ACCESS_TOKENS: Dict[str, str] = {
    # Add more page_id: token here
}
VERIFY_TOKEN = os.getenv("FB_VERIFY_TOKEN", "KUNNE")
APP_SECRET = os.getenv("FB_APP_SECRET")
logger = logging.getLogger(__name__)

class MessagingEvent(BaseModel):
    sender: Dict[str, str]
    recipient: Dict[str, str]
    message: Optional[Dict[str, Any]] = None

class Entry(BaseModel):
    id: Optional[str] = None
    time: Optional[int] = None
    messaging: Optional[List[MessagingEvent]] = None
    changes: Optional[List[Any]] = None

class WebhookRequest(BaseModel):
    object: str
    entry: List[Entry]

@router.get("/webhook")
async def verify_webhook(request: Request):
    params = dict(request.query_params)
    mode = params.get("hub.mode")
    token = params.get("hub.verify_token")
    challenge = params.get("hub.challenge")
    if mode and token:
        if mode == "subscribe" and token == VERIFY_TOKEN:
            logger.info("WEBHOOK_VERIFIED")
            return Response(content=challenge, status_code=200)
        else:
            return Response(status_code=403)
    return Response(status_code=400)

def verify_signature(request: Request, body: bytes):
    signature = request.headers.get("x-hub-signature-256")
    if not signature or not APP_SECRET:
        return True
    try:
        sha_name, signature_hash = signature.split("=")
        mac = hmac.new(APP_SECRET.encode(), msg=body, digestmod=hashlib.sha256)
        if not hmac.compare_digest(mac.hexdigest(), signature_hash):
            logger.warning("Invalid request signature.")
            return False
        return True
    except Exception as e:
        logger.error(f"Signature verification error: {e}")
        return False

@router.post("/webhook")
async def handle_message(request: Request):
    body = await request.body()
    if not verify_signature(request, body):
        raise HTTPException(status_code=403, detail="Invalid signature")
    try:
        data = await request.json()
    except Exception as e:
        logger.error(f"Invalid JSON in request: {e}")
        raise HTTPException(status_code=400, detail="Invalid JSON body")
    webhook = WebhookRequest.parse_obj(data)
    if webhook.object == "page":
        for entry in webhook.entry:
            if entry.messaging:
                for messaging_event in entry.messaging:
                    sender_id = messaging_event.sender.get("id")
                    page_id = messaging_event.recipient.get("id")
                    if messaging_event.message and "text" in messaging_event.message:
                        user_message = messaging_event.message["text"]
                        # Gọi chatbot để lấy câu trả lời
                        from app.models.chatbot_model import ChatRequest
                        from app.routes.chatbot import handle_chat_interaction
                        chat_req = ChatRequest(message=user_message, user_id=sender_id)
                        response = await handle_chat_interaction(chat_req)
                        reply_text = response.reply
                        await send_message_to_facebook(sender_id, reply_text, page_id)
            if entry.changes:
                logger.info(f"Received non-messaging event: {entry.changes}")
        return Response(content="EVENT_RECEIVED", status_code=200)
    else:
        return Response(status_code=404)

async def send_message_to_facebook(recipient_id, message_text, page_id):
    access_token = PAGE_ACCESS_TOKENS.get(page_id)
    if not access_token:
        logger.error(f"No access token configured for page_id: {page_id}")
        return
    url = f"https://graph.facebook.com/v21.0/me/messages?access_token={access_token}"
    payload = {
        "recipient": {"id": recipient_id},
        "message": {"text": message_text}
    }
    async with httpx.AsyncClient() as client:
        await client.post(url, json=payload)
