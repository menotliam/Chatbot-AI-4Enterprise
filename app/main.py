from fastapi import FastAPI, Request, Response, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import time
import logging
import signal
import sys
from contextlib import asynccontextmanager
from app.core.config import settings
from app.core.logging import init_logging
from app.routes import (
    chatbot_router,
    chat_history_router,
    token_tracker_router,
)

from app.api.messenger_webhook import router as messenger_router
# Setup logging
init_logging()

logger = logging.getLogger(__name__)

# Global flag for graceful shutdown
shutdown_event = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for FastAPI application.
    Handles startup and shutdown events.
    """
    global shutdown_event
    shutdown_event = False
    
    # Startup
    logger.info("Starting up application...")
    yield
    
    # Shutdown
    logger.info("Shutting down application...")
    shutdown_event = True
    # Add any cleanup code here
    logger.info("Application shutdown complete")

# Middleware to log requests and responses
async def log_requests(request: Request, call_next):
    request_id = f"{request.method} {request.url}"
    logger.info(f"Request started: {request_id}")
    start_time = time.time()
    try:
        response: Response = await call_next(request)
        duration = time.time() - start_time
        logger.info(f"Request finished: {request_id} ({duration:.2f}s) Status: {response.status_code}")
        return response
    except Exception as e:
        duration = time.time() - start_time
        logger.error(f"Request failed: {request_id} ({duration:.2f}s) Error: {str(e)}")
        raise

# Application factory
def create_app() -> FastAPI:
    app = FastAPI(
        title="AI Chatbot Platform",
        description="Chatbot powered by GPT-4 Turbo with product suggestions from Shopee, TikTok, and Amazon",
        version="1.0.0",
        lifespan=lifespan,
    )
    
    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Logging middleware
    app.middleware("http")(log_requests)
    
    # Register routes
    route_configs = [
        (chatbot_router, "/api/chatbot", ["Chatbot"]),
        (chat_history_router, "/api/chat-history", ["Chat History"]),
        (token_tracker_router, "/api/token-tracker", ["Token Tracker"]),
    ]
    app.include_router(messenger_router)
    for router, prefix, tags in route_configs:
        app.include_router(router, prefix=prefix, tags=tags)

    return app

def handle_sigterm(signum, frame):
    """Handle SIGTERM signal for graceful shutdown"""
    logger.info("Received SIGTERM signal. Starting graceful shutdown...")
    sys.exit(0)

# Register signal handlers
signal.signal(signal.SIGTERM, handle_sigterm)
signal.signal(signal.SIGINT, handle_sigterm)

# App instance for Uvicorn
app = create_app()

# Run the server if executed directly
if __name__ == "__main__":
    try:
        logger.info("Starting server...")
        uvicorn.run(
            "app.main:app",
            host=settings.HOST,
            port=settings.PORT,
            reload=settings.DEBUG,
            log_level=settings.LOG_LEVEL.lower(),
            workers=settings.WORKERS
        )
    except Exception as e:
        logger.exception(f"Server failed to start: {e}")
        sys.exit(1)