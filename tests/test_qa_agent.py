import os
from dotenv import load_dotenv
import httpx
import asyncio
from supabase import create_client
import json
import uuid

load_dotenv()

API_URL = "http://localhost:8000/chat"
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
SUPABASE_EMAIL = os.getenv("SUPABASE_EMAIL")
SUPABASE_PASSWORD = os.getenv("SUPABASE_PASSWORD")

def get_auth_info():
    """Get JWT token and user ID from Supabase using email/password authentication"""
    if not SUPABASE_URL or not SUPABASE_KEY:
        raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in .env file")
    if not SUPABASE_EMAIL or not SUPABASE_PASSWORD:
        raise ValueError("SUPABASE_EMAIL and SUPABASE_PASSWORD must be set in .env file")
    
    try:
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        response = supabase.auth.sign_in_with_password({
            "email": SUPABASE_EMAIL,
            "password": SUPABASE_PASSWORD
        })
        
        if not response.session or not response.session.access_token:
            raise Exception("Failed to obtain session token from Supabase")
            
        user_id = response.user.id  # Get the actual UUID
        print(f"[qa_agent_test] Successfully authenticated as: {SUPABASE_EMAIL}")
        print(f"[qa_agent_test] User ID: {user_id}")
        
        return {
            "token": response.session.access_token,
            "user_id": user_id
        }
        
    except Exception as e:
        print(f"[qa_agent_test] Authentication error: {str(e)}")
        raise

async def select_or_create_session(auth_info):
    JWT_TOKEN = auth_info["token"]
    USER_ID = auth_info["user_id"]
    headers = {
        "Authorization": f"Bearer {JWT_TOKEN}",
        "Content-Type": "application/json"
    }
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    while True:
        choice = input("Do you want to start a new session? (y/n): ").strip().lower()
        if choice == 'y':
            session_id = f"qatest_{uuid.uuid4()}"
            print(f"\nNew session started: {session_id}")
            return session_id
        elif choice == 'n':
            # Fetch unique session_ids from conversations table that start with 'qatest_'
            try:
                # Use the user's JWT token for RLS
                # We'll use the REST API directly for this, since supabase-py doesn't support custom headers easily
                url = f"{SUPABASE_URL}/rest/v1/conversations?select=session_id&user_id=eq.{USER_ID}&session_id=like.qatest_%25"
                async with httpx.AsyncClient() as client:
                    resp = await client.get(url, headers={"apikey": SUPABASE_KEY, "Authorization": f"Bearer {JWT_TOKEN}"})
                    if resp.status_code == 200:
                        data = resp.json()
                        session_ids = sorted(set([row["session_id"] for row in data if row["session_id"].startswith("qatest_")]))
                        if not session_ids:
                            print("No qatest_ sessions found. Starting a new one.")
                            session_id = f"qatest_{uuid.uuid4()}"
                            print(f"\nNew session started: {session_id}")
                            return session_id
                        print("\nAvailable qatest_ sessions:")
                        for idx, sid in enumerate(session_ids):
                            print(f"  {idx+1}. {sid}")
                        while True:
                            sel = input("Select a session by number: ").strip()
                            if sel.isdigit() and 1 <= int(sel) <= len(session_ids):
                                session_id = session_ids[int(sel)-1]
                                print(f"\nUsing session: {session_id}")
                                return session_id
                            else:
                                print("Invalid selection. Try again.")
                    else:
                        print(f"Error fetching sessions: {resp.text}")
                        continue
            except Exception as e:
                print(f"Error fetching sessions: {e}")
                continue
        else:
            print("Please enter 'y' or 'n'.")

async def fetch_latest_assistant_reply(session_id, jwt_token):
    url = f"{SUPABASE_URL}/rest/v1/conversations?select=content,created_at&session_id=eq.{session_id}&role=eq.assistant&order=created_at.desc&limit=1"
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {jwt_token}"
    }
    async with httpx.AsyncClient() as client:
        resp = await client.get(url, headers=headers)
        if resp.status_code == 200:
            data = resp.json()
            if data:
                return data[0]["content"]
        return None

async def chat_with_agent(session_id=None):
    """Chat with the Q&A agent using authenticated session"""
    try:
        auth_info = get_auth_info()
        JWT_TOKEN = auth_info["token"]
        USER_ID = auth_info["user_id"]
        headers = {
            "Authorization": f"Bearer {JWT_TOKEN}",
            "Content-Type": "application/json"
        }
        # Prompt for session selection/creation
        if not session_id:
            session_id = await select_or_create_session(auth_info)
        print("\nStarting conversation (type 'exit' to end)...")
        print("Type your message and press Enter to chat with the agent.")
        print("Type 'exit' to end the conversation.")
        while True:
            user_input = input("\nYou: ").strip()
            if user_input.lower() == 'exit':
                print("\nEnding conversation...")
                break
            payload = {
                "message": user_input,
                "session_id": session_id,
                "user_id": USER_ID
            }
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.post(API_URL, headers=headers, json=payload)
                    if response.status_code == 200:
                        result = response.json()
                        print(f"\nAgent: {result['reply']}")
                    else:
                        print(f"\nError: {response.text}")
                        if response.status_code == 401:
                            print("Authentication error - token may have expired")
                            break
            except httpx.RequestError as e:
                print(f"\nNetwork error: {str(e)}")
            except Exception as e:
                print(f"\nUnexpected error: {str(e)}")
    except Exception as e:
        print(f"\nFatal error: {str(e)}")
        raise

async def main():
    try:
        await chat_with_agent()
    except KeyboardInterrupt:
        print("\nConversation interrupted by user")
    except Exception as e:
        print(f"\nFatal error: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main()) 