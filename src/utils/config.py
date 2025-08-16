"""
Configuration management for Alignator
"""

import os
from typing import Dict, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Configuration class for Alignator"""
    
    # API Configuration
    CONGRESS_API_BASE_URL = "https://api.congress.gov/v3"
    CONGRESS_API_KEY = os.getenv('CONGRESS_API_KEY')
    
    # Rate limiting (Congress.gov allows 1000 requests per hour)
    API_RATE_LIMIT = 1000
    API_RATE_LIMIT_WINDOW = 3600  # 1 hour in seconds
    
    # Data storage
    DATA_DIR = "data"
    DATABASE_PATH = os.path.join(DATA_DIR, "alignator.db")
    
    # Analysis settings
    DEFAULT_CONGRESS = 118
    DEFAULT_CHAMBER = "both"
    MAX_BILLS_PER_REQUEST = 250
    
    # NLP settings
    SPACY_MODEL = "en_core_web_sm"
    MIN_TEXT_LENGTH = 100
    MAX_TEXT_LENGTH = 10000
    
    # Political alignment settings
    ALIGNMENT_THRESHOLD = 0.6
    TOPIC_MODEL_N_COMPONENTS = 10
    
    @classmethod
    def validate_config(cls) -> bool:
        """Validate that all required configuration is present"""
        if not cls.CONGRESS_API_KEY:
            raise ValueError("CONGRESS_API_KEY not found in environment variables")
        
        # Create data directory if it doesn't exist
        os.makedirs(cls.DATA_DIR, exist_ok=True)
        
        return True
    
    @classmethod
    def get_api_headers(cls) -> Dict[str, str]:
        """Get headers for API requests"""
        return {
            'X-API-Key': cls.CONGRESS_API_KEY,
            'Content-Type': 'application/json'
        }
    
    @classmethod
    def get_api_url(cls, endpoint: str) -> str:
        """Get full API URL for an endpoint"""
        return f"{cls.CONGRESS_API_BASE_URL}/{endpoint.lstrip('/')}"
