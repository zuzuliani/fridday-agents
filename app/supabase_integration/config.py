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
        
        # Get environment variables directly
        supabase_url = os.getenv('SUPABASE_URL')
        supabase_key = os.getenv('SUPABASE_KEY')
        supabase_jwt_secret = os.getenv('SUPABASE_JWT_SECRET')
        
        # Log the environment variables (without sensitive data)
        logger.info("Loading Supabase configuration...")
        logger.info(f"SUPABASE_URL: {supabase_url[:20]}..." if supabase_url else "Not set")
        logger.info(f"SUPABASE_KEY: {'Set' if supabase_key else 'Not set'}")
        logger.info(f"SUPABASE_JWT_SECRET: {'Set' if supabase_jwt_secret else 'Not set'}")
        
        if not supabase_url or not supabase_key:
            error_msg = "Missing required Supabase environment variables"
            logger.error(error_msg)
            raise ValueError(error_msg)
        
        try:
            config = cls(
                supabase_url=supabase_url,
                supabase_key=supabase_key,
                supabase_jwt_secret=supabase_jwt_secret
            )
            logger.info("Successfully loaded Supabase configuration")
            return config
        except Exception as e:
            logger.error(f"Failed to load Supabase configuration: {str(e)}")
            raise

@lru_cache()
def get_supabase_config() -> SupabaseConfig:
    return SupabaseConfig.load_config() 