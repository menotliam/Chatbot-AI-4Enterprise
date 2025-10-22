import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv
from typing import List
from pydantic import Field

# Load environment variables from .env file
load_dotenv()

class Settings(BaseSettings):
    # App Settings
    APP_NAME: str = "AI Chatbot"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))

    # API Settings
    API_PREFIX: str = "/api"
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Chatbot API"
    
    # CORS Settings
    CORS_ORIGINS: List[str] = ["*"]  # Allow all origins in development
    BACKEND_CORS_ORIGINS: List[str] = []
    
    # OpenAI Settings
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_ASSISTANT_ID: str = os.getenv("OPENAI_ASSISTANT_ID", "")
    
    # Database Settings
    DB_URI: str = os.getenv("DB_URI", "")
    MONGO_DB_NAME: str = os.getenv("MONGO_DB_NAME", "auth")

    
    # Security Settings
    SECRET_KEY: str = os.getenv("SECRET_KEY", "dev_secret_key_change_in_production")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Logging Settings
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    # Worker Settings
    WORKERS: int = int(os.getenv("WORKERS", "1"))
    
    
    model_config = {
        "env_file": ".env",
        "extra": "allow",  # Allow extra fields from environment variables
    }

# Create a global settings object
settings = Settings()

def get_settings() -> Settings:
    return settings