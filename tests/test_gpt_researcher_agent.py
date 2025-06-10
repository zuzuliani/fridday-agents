import httpx
import uuid
import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
SUPABASE_EMAIL = os.getenv("SUPABASE_EMAIL")
SUPABASE_PASSWORD = os.getenv("SUPABASE_PASSWORD")

API_URL = "http://localhost:8000/gpt-researcher"

def get_auth_info():
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    response = supabase.auth.sign_in_with_password({
        "email": SUPABASE_EMAIL,
        "password": SUPABASE_PASSWORD
    })
    if not response.session or not response.session.access_token:
        raise Exception("Failed to obtain session token from Supabase")
    return {
        "token": response.session.access_token,
        "user_id": response.user.id
    }

def main():
    auth_info = get_auth_info()
    payload = {
        "task": "The impact of AI on education",
        "report_type": "research_report",
        "report_source": "web",
        "tone": "Formal",
        "user_id": auth_info["user_id"],
        "topic": "The impact of AI on education",
        "jwt_token": auth_info["token"],
        "headers": {
            "deep_research_breadth": 4,
            "deep_research_depth": 4,
            "deep_research_concurrency": 4,
            "verbose": True
        }
    }
    print("Sending request to:", API_URL)
    response = httpx.post(API_URL, json=payload, timeout=None)
    print("Status code:", response.status_code)
    try:
        print("Response:", response.json())
    except Exception:
        print("Raw response:", response.text)

if __name__ == "__main__":
    main() 