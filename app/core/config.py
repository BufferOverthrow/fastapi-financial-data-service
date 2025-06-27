import os
from functools import lru_cache
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Settings:
    """
    Application settings loaded from environment variables.
    """
    finnhub_api_key: str = os.getenv("FINNHUB_API_KEY", "") # Default to empty string if not found

    def __init__(self):
        if not self.finnhub_api_key:
            print("WARNING: FINNHUB_API_KEY environment variable not set.")
            raise ValueError("FINNHUB_API_KEY environment variable not set.")

@lru_cache()
def get_settings() -> Settings:
    """
    Returns a cached Settings instance.
    This ensures that settings are loaded only once.
    """
    return Settings()

# Dependency for FastAPI endpoints
def get_api_key() -> str:
    """
    FastAPI dependency to provide the Finnhub API key.
    """
    settings = get_settings()
    if not settings.finnhub_api_key:
        raise ValueError("Finnhub API Key is not configured.") # Raise an error if the key is truly missing
    return settings.finnhub_api_key
