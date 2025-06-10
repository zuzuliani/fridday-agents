from pydantic_settings import BaseSettings
from functools import lru_cache
import os
import logging
from dotenv import load_dotenv

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SupabaseConfig(BaseSettings):
    supabase_url: str
    supabase_key: str
    supabase_jwt_secret: str | None = None

    class Config:
        env_file = ".env"
        env_prefix = "SUPABASE_"
        extra = "allow"

    @classmethod
    def load_config(cls):
        # Load environment variables from .env file if it exists
        load_dotenv()
        
        # Log the environment variables (without sensitive data)
        logger.info("Loading Supabase configuration...")
        logger.info(f"SUPABASE_URL is set: {bool(os.getenv('SUPABASE_URL'))}")
        logger.info(f"SUPABASE_KEY is set: {bool(os.getenv('SUPABASE_KEY'))}")
        
        try:
            config = cls()
            logger.info("Successfully loaded Supabase configuration")
            return config
        except Exception as e:
            logger.error(f"Failed to load Supabase configuration: {str(e)}")
            raise

@lru_cache()
def get_supabase_config() -> SupabaseConfig:
    return SupabaseConfig.load_config() 