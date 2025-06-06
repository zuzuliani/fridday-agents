import os
import asyncio
import httpx
from dotenv import load_dotenv

load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
API_URL = "http://localhost:8000/chat"

# Reuse get_auth_info from tests/test_qa_agent.py
from tests.test_qa_agent import get_auth_info

def print_conversation(messages):
    print("\n--- Conversation ---")
    for msg in messages:
        print(f"[{msg['role']}] {msg['content']}")
    print("-------------------")

async def fetch_conversation(session_id, jwt_token):
    url = f"{SUPABASE_URL}/rest/v1/conversations?select=role,content,created_at&session_id=eq.{session_id}&order=created_at.desc&limit=10"
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {jwt_token}"
    }
    async with httpx.AsyncClient() as client:
        resp = await client.get(url, headers=headers)
        if resp.status_code == 200:
            return list(reversed(resp.json()))
        return []

async def main():
    auth_info = get_auth_info()
    jwt_token = auth_info["token"]
    user_id = auth_info["user_id"]
    session_id = input("Enter session_id (or leave blank for new): ").strip() or f"cli_{os.urandom(4).hex()}"
    print(f"Using session_id: {session_id}")
    while True:
        messages = await fetch_conversation(session_id, jwt_token)
        print_conversation(messages)
        user_input = input("\nYou: ").strip()
        if user_input.lower() == "exit":
            break
        payload = {
            "message": user_input,
            "session_id": session_id,
            "user_id": user_id
        }
        headers = {
            "Authorization": f"Bearer {jwt_token}",
            "Content-Type": "application/json"
        }
        timeout = httpx.Timeout(30.0)  # 30 seconds
        async with httpx.AsyncClient(timeout=timeout) as client:
            await client.post(API_URL, headers=headers, json=payload)
        await asyncio.sleep(1)  # Give the agent a moment to reply

if __name__ == "__main__":
    asyncio.run(main()) 