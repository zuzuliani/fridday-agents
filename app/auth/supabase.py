from supabase import create_client, Client
from ..config import settings
from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer()

class SupabaseAuth:
    def __init__(self):
        self.supabase: Client = create_client(
            settings.SUPABASE_URL,
            settings.SUPABASE_KEY
        )
    
    async def get_current_user(self, credentials: HTTPAuthorizationCredentials = Depends(security)):
        try:
            # Verify the JWT token with Supabase
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