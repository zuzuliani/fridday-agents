from pydantic_settings import BaseSettings
from functools import lru_cache

class SupabaseConfig(BaseSettings):
    supabase_url: str
    supabase_key: str
    supabase_jwt_secret: str | None = None

    class Config:
        env_file = ".env"
        env_prefix = "SUPABASE_"
        extra = "allow"

@lru_cache()
def get_supabase_config() -> SupabaseConfig:
    return SupabaseConfig() 