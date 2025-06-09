from supabase import create_client, Client
from .config import get_supabase_config
from functools import lru_cache

@lru_cache()
def get_supabase_client() -> Client:
    """Get a cached Supabase client instance."""
    config = get_supabase_config()
    return create_client(config.supabase_url, config.supabase_key) 