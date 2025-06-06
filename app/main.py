from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import uuid
from app.agents.qa_agent import ConversationalAgent
from app.config import CORS_ORIGINS
from app.auth.supabase import auth
import traceback
from dotenv import load_dotenv
import os
import io
from contextlib import redirect_stdout

app = FastAPI(title="Business Consultant Chat API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize the agent
agent = ConversationalAgent()

class ChatMessage(BaseModel):
    message: str
    session_id: Optional[str] = None
    user_id: Optional[str] = None

@app.get("/")
async def root():
    """Get a new session ID and usage instructions."""
    session_id = str(uuid.uuid4())
    return {
        "message": "Welcome to the Business Consultant Chat API",
        "session_id": session_id,
        "usage": "Send a POST request to /chat with your message and session_id"
    }

@app.post("/chat")
async def chat(payload: dict, request: Request, current_user=Depends(auth.get_current_user)):
    """Chat with the business consultant agent."""
    try:
        # Get JWT token from Authorization header
        jwt_token = request.headers.get("authorization", "").replace("Bearer ", "")
        user_id = current_user.user.id
        
        # Generate a new session ID if not provided
        session_id = payload["session_id"] or str(uuid.uuid4())
        
        # Capture agent debug output
        f = io.StringIO()
        with redirect_stdout(f):
            response = await agent.run(
                user_message=payload["message"],
                user_id=user_id,
                session_id=session_id,
                jwt_token=jwt_token
            )
        debug_output = f.getvalue()
        
        # Return the agent's reply and debug output
        return {
            "reply": response["reply"],
            "session_id": session_id,
            "debug_output": debug_output
        }
    except Exception as e:
        print("Exception in /chat:", e)
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "environment": "production"
    }

@app.post("/dev_login")
async def dev_login():
    """Authenticate using Supabase email/password from .env and return JWT/user_id."""
    SUPABASE_URL = os.getenv("SUPABASE_URL")
    SUPABASE_KEY = os.getenv("SUPABASE_KEY")
    SUPABASE_EMAIL = os.getenv("SUPABASE_EMAIL")
    SUPABASE_PASSWORD = os.getenv("SUPABASE_PASSWORD")
    if not SUPABASE_URL or not SUPABASE_KEY or not SUPABASE_EMAIL or not SUPABASE_PASSWORD:
        raise HTTPException(status_code=500, detail="Supabase credentials not set in .env")
    try:
        from supabase import create_client
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        response = supabase.auth.sign_in_with_password({
            "email": SUPABASE_EMAIL,
            "password": SUPABASE_PASSWORD
        })
        if not response.session or not response.session.access_token:
            raise Exception("Failed to obtain session token from Supabase")
        user_id = response.user.id
        return {
            "access_token": response.session.access_token,
            "user_id": user_id
        }
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Authentication failed: {str(e)}") 