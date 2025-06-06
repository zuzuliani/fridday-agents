import os
from dotenv import load_dotenv
from typing import List
from pydantic_settings import BaseSettings

load_dotenv()

class Settings(BaseSettings):
    # Environment
    environment: str = os.getenv("ENVIRONMENT", "development")

    # Supabase settings
    supabase_url: str = os.getenv("SUPABASE_URL", "")
    supabase_key: str = os.getenv("SUPABASE_KEY", "")

    # Redis settings
    redis_url: str = os.getenv("REDIS_URL", "redis://localhost:6379")

    # API settings
    api_v1_str: str = os.getenv("API_V1_STR", "/api/v1")
    project_name: str = os.getenv("PROJECT_NAME", "Fridday Agents")

    # Security settings
    secret_key: str = os.getenv("SECRET_KEY", "your-secret-key-here")
    access_token_expire_minutes: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "11520"))  # 8 days

    # CORS settings
    cors_origins: List[str] = ["http://localhost:3000"]  # Default value

    # Logging
    log_level: str = os.getenv("LOG_LEVEL", "INFO")

    class Config:
        case_sensitive = True

# Create settings instance
settings = Settings()

# Update CORS_ORIGINS if provided in env
if os.getenv("CORS_ORIGINS"):
    try:
        settings.cors_origins = os.getenv("CORS_ORIGINS").split(",")
    except:
        pass  # Keep default if split fails

# For backward compatibility
CORS_ORIGINS = settings.cors_origins 