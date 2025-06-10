from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from supabase import Client
from .client import get_supabase_client

security = HTTPBearer()

class SupabaseAuth:
    def __init__(self):
        self.supabase: Client = get_supabase_client()
    
    async def get_current_user(self, credentials: HTTPAuthorizationCredentials = Depends(security)):
        """Verify the JWT token and return the user."""
        try:
            user = self.supabase.auth.get_user(credentials.credentials)
            if not user:
                raise HTTPException(
                    status_code=401,
                    detail="Invalid authentication credentials"
                )
            return user
        except Exception as e:
            raise HTTPException(
                status_code=401,
                detail="Invalid authentication credentials"
            )

# Create a singleton instance
auth = SupabaseAuth() 