from fastapi import APIRouter, Depends, HTTPException, Header
from typing import Optional
from .supabase import auth
from ..config import settings
import jwt
from datetime import datetime, timedelta
import logging

router = APIRouter(prefix="/auth", tags=["auth"])

async def get_current_user(authorization: str = Header(None)):
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    logger.info("[get_current_user] Called with authorization header: %s", authorization)
    if not authorization:
        logger.warning("[get_current_user] No authorization header provided")
        raise HTTPException(
            status_code=401,
            detail="No authorization header"
        )
    
    try:
        # Remove 'Bearer ' prefix if present
        token = authorization.replace('Bearer ', '')
        
        # Verify the token with Supabase
        user = auth.supabase.auth.get_user(token)
        if not user:
            logger.warning("[get_current_user] Invalid token")
            raise HTTPException(
                status_code=401,
                detail="Invalid token"
            )
        logger.info("[get_current_user] Authenticated user: %s", getattr(user, 'id', 'unknown'))
        return user
    except Exception as e:
        logger.error("[get_current_user] Exception: %s", str(e))
        raise HTTPException(
            status_code=401,
            detail=f"Invalid authentication credentials: {str(e)}"
        )

@router.get("/me")
async def get_user_info(user = Depends(get_current_user)):
    """Get current user information"""
    return {
        "id": user.id,
        "email": user.email,
        "user_metadata": user.user_metadata
    }

# Development only endpoints
@router.post("/dev/token")
async def create_dev_token(email: str, password: str):
    """Create a development token (only available in development)"""
    if settings.ENVIRONMENT != "development":
        raise HTTPException(
            status_code=403,
            detail="This endpoint is only available in development"
        )
    
    try:
        # Sign in with Supabase
        response = auth.supabase.auth.sign_in_with_password({
            "email": email,
            "password": password
        })
        
        return {
            "access_token": response.session.access_token,
            "refresh_token": response.session.refresh_token,
            "expires_in": response.session.expires_in,
            "token_type": "bearer"
        }
    except Exception as e:
        raise HTTPException(
            status_code=401,
            detail=f"Authentication failed: {str(e)}"
        )

@router.post("/dev/refresh")
async def refresh_dev_token(refresh_token: str):
    """Refresh a development token (only available in development)"""
    if settings.ENVIRONMENT != "development":
        raise HTTPException(
            status_code=403,
            detail="This endpoint is only available in development"
        )
    
    try:
        # Refresh the token with Supabase
        response = auth.supabase.auth.refresh_session({
            "refresh_token": refresh_token
        })
        
        return {
            "access_token": response.session.access_token,
            "refresh_token": response.session.refresh_token,
            "expires_in": response.session.expires_in,
            "token_type": "bearer"
        }
    except Exception as e:
        raise HTTPException(
            status_code=401,
            detail=f"Token refresh failed: {str(e)}"
        ) 