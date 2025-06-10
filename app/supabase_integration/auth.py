import os
from dotenv import load_dotenv
from .config import SupabaseConfig
from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from supabase import Client
from .client import get_supabase_client

security = HTTPBearer()

class SupabaseAuth:
    def __init__(self):
        load_dotenv()
        self.config = SupabaseConfig()
        self.email = os.getenv("SUPABASE_EMAIL")
        self.password = os.getenv("SUPABASE_PASSWORD")
        
    def get_auth_info(self):
        if not self.email or not self.password:
            raise ValueError("SUPABASE_EMAIL and SUPABASE_PASSWORD must be set in environment variables")
            
        response = self.config.supabase.auth.sign_in_with_password({
            "email": self.email,
            "password": self.password
        })
        
        if not response.session or not response.session.access_token:
            raise Exception("Failed to obtain session token from Supabase")
            
        return {
            "token": response.session.access_token,
            "user_id": response.user.id
        }

# Create a function to get the auth instance instead of creating it at module level
def get_auth():
    return SupabaseAuth()

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