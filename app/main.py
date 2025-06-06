from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import uuid
from app.agents.qa_agent import ConversationalAgent
from app.config import CORS_ORIGINS
from app.auth.supabase import auth
import traceback

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
        
        # Await the async agent.run method
        response = await agent.run(
            user_message=payload["message"],
            user_id=user_id,
            session_id=session_id,
            jwt_token=jwt_token
        )
        
        # Return the agent's reply directly
        return {
            "reply": response["reply"],
            "session_id": session_id
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