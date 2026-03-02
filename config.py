import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Configuration class to hold all environment variables"""
    
    # Telegram API credentials
    API_ID = int(os.getenv("API_ID", 0))
    API_HASH = os.getenv("API_HASH", "")
    PHONE = os.getenv("PHONE", "")
    SESSION_STRING = os.getenv("SESSION_STRING", "")
    
    # MongoDB connection string
    MONGODB_URL = os.getenv("MONGODB_URL", "")
    
    # Server port for FastAPI
    PORT = int(os.getenv("PORT", 8000))
    
    # Validate required configuration
    @classmethod
    def validate(cls):
        """Validate that all required configuration values are set"""
        missing = []
        
        if not cls.API_ID:
            missing.append("API_ID")
            
        if not cls.API_HASH:
            missing.append("API_HASH")
            
        # Either PHONE or SESSION_STRING must be provided
        if not cls.PHONE and not cls.SESSION_STRING:
            missing.append("PHONE or SESSION_STRING")
            
        if not cls.MONGODB_URL:
            missing.append("MONGODB_URL")
            
        if missing:
            raise ValueError(f"Missing required configuration: {', '.join(missing)}")
            
# Validate configuration on import
Config.validate()