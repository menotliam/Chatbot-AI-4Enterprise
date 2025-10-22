import os
import logging
from typing import Optional
from pymongo import MongoClient
from pymongo.database import Database
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
from dotenv import load_dotenv
from pymongo.collection import Collection

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv(".env", override=True)

class MongoDB:
    _instance = None
    _client = None
    _db = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(MongoDB, cls).__new__(cls)
            cls._instance._connect()
        return cls._instance

    def _connect(self):
        """Establish connection to MongoDB"""
        try:
            # Get connection URI directly from environment
            uri = os.getenv("DB_URI")
            database = os.getenv("MONGO_DB_NAME", "auth")
            
            
            
            logger.info(f"Connecting to MongoDB using URI: {uri}")
            
            # Create MongoDB client with connection pooling
            self._client = MongoClient(
                uri,
                maxPoolSize=50,
                minPoolSize=10,
                maxIdleTimeMS=30000,
                waitQueueTimeoutMS=2500,
                serverSelectionTimeoutMS=5000
            )
            
            # Test connection
            self._client.admin.command('ping')
            logger.info("Successfully connected to MongoDB")
            
            # Get database instance
            self._db = self._client[database]
            logger.info(f"Connected to database: {database}")
            
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            self._client = None
            self._db = None
            raise

    def close(self):
        """Close MongoDB connection"""
        if self._client:
            self._client.close()
            self._client = None
            self._db = None
            logger.info("MongoDB connection closed")

    @property
    def db(self) -> Database:
        """Get database instance"""
        if self._db is None:
            self._connect()
        return self._db

def get_db() -> Database:
    """Get database instance"""
    return MongoDB().db

def get_collection(collection_name: str) -> Collection:
    """Get collection instance"""
    db = get_db()
    if db is None:
        raise ConnectionError("Failed to connect to database")
    return db[collection_name]

# Add specific collection getters
def get_chat_history_collection() -> Collection:
    """Get chat history collection"""
    return get_collection("chat_history")

def get_users_collection() -> Collection:
    """Get users collection"""
    return get_collection("users")

def get_products_collection() -> Collection:
    """Get products collection"""
    return get_collection("products")

def get_token_usage_collection() -> Collection:
    """Get token usage collection"""
    return get_collection("token_usage")
