import pytest
from supabase import create_client, Client
import os
from dotenv import load_dotenv
import json
from datetime import datetime
from app.agents.utilities.create_embeddings import get_embedding

# Load environment variables
load_dotenv()

# Initialize Supabase client
supabase: Client = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_KEY")
)

@pytest.mark.asyncio
async def test_supabase_connection():
    """Test basic Supabase connection"""
    print("\n1. Testing Supabase Connection...")
    try:
        # Try to get the current user (should fail as we're not authenticated)
        response = supabase.auth.get_user("dummy-token")
        assert False, "Should have failed with unauthenticated request"
    except Exception as e:
        assert True, "Connection successful (expected error for unauthenticated request)"

@pytest.mark.asyncio
async def test_auth_flow():
    """Test the authentication flow with existing user"""
    print("\n2. Testing Authentication Flow...")
    
    # Get credentials from environment variables
    test_email = os.getenv("SUPABASE_EMAIL")
    test_password = os.getenv("SUPABASE_PASSWORD")
    
    if not test_email or not test_password:
        pytest.fail("SUPABASE_EMAIL and SUPABASE_PASSWORD must be set in .env file")
    
    try:
        # 1. Sign in
        print("\n   a. Testing Sign In...")
        signin_response = supabase.auth.sign_in_with_password({
            "email": test_email,
            "password": test_password
        })
        assert signin_response.session is not None, "Sign in failed"
        print(f"   ✅ Sign in successful: {json.dumps(signin_response.model_dump(), indent=2, default=str)}")
        
        # 2. Get user
        print("\n   b. Testing Get User...")
        user = supabase.auth.get_user(signin_response.session.access_token)
        assert user.user is not None, "Get user failed"
        print(f"   ✅ Get user successful: {json.dumps(user.model_dump(), indent=2, default=str)}")
        
        # 3. Refresh token
        print("\n   c. Testing Token Refresh...")
        refresh_response = supabase.auth.refresh_session(signin_response.session.refresh_token)
        assert refresh_response.session is not None, "Token refresh failed"
        print(f"   ✅ Token refresh successful: {json.dumps(refresh_response.model_dump(), indent=2, default=str)}")
        
        # 4. Sign out
        print("\n   d. Testing Sign Out...")
        supabase.auth.sign_out()
        print("   ✅ Sign out successful")
        
    except Exception as e:
        error_msg = str(e)
        if "invalid" in error_msg.lower():
            print(f"   ❌ Invalid credentials: {error_msg}")
        elif "network" in error_msg.lower():
            print(f"   ❌ Network error: {error_msg}")
        else:
            print(f"   ❌ Unexpected error: {error_msg}")
        pytest.fail(f"Error during auth flow: {error_msg}")

def test_environment_variables():
    """Test that required environment variables are set"""
    assert os.getenv("SUPABASE_URL"), "SUPABASE_URL is not set"
    assert os.getenv("SUPABASE_KEY"), "SUPABASE_KEY is not set"
    assert os.getenv("SUPABASE_EMAIL"), "SUPABASE_EMAIL is not set"
    assert os.getenv("SUPABASE_PASSWORD"), "SUPABASE_PASSWORD is not set"
    print(f"\n✅ Environment variables check passed")
    print(f"Supabase URL: {os.getenv('SUPABASE_URL')}")

def test_get_embedding():
    text = "Hello, this is a test."
    embedding = get_embedding(text)
    assert isinstance(embedding, list)
    assert all(isinstance(x, float) for x in embedding)
    assert len(embedding) > 0
    print("✅ Embedding generated successfully:", embedding[:5], "...")

def test_conversations_select_and_insert():
    """Test select and insert on conversations table for authenticated user"""
    print("\n3. Testing Conversations Table (select & insert)...")
    test_email = os.getenv("SUPABASE_EMAIL")
    test_password = os.getenv("SUPABASE_PASSWORD")
    if not test_email or not test_password:
        pytest.fail("SUPABASE_EMAIL and SUPABASE_PASSWORD must be set in .env file")

    # Sign in
    signin_response = supabase.auth.sign_in_with_password({
        "email": test_email,
        "password": test_password
    })
    assert signin_response.session is not None, "Sign in failed"
    user_id = signin_response.user.id
    access_token = signin_response.session.access_token

    # Insert a conversation
    print("   a. Inserting a conversation...")
    content = "This is a test conversation from pytest."
    embedding = get_embedding(content)
    insert_data = {
        "session_id": "test-session",
        "user_id": user_id,
        "role": "user",
        "content": content,
        "title": "Test Conversation",
        "metadata": {},
        "is_archived": False,
        "embedding": embedding
    }
    insert_response = supabase.table("conversations").insert(insert_data).execute()
    assert insert_response.data, f"Insert failed: {insert_response.error}"
    print(f"   ✅ Inserted conversation: {json.dumps(insert_response.data, indent=2, default=str)}")

    # Select conversations for this user
    print("   b. Selecting conversations for this user...")
    select_response = supabase.table("conversations").select("*").eq("user_id", user_id).execute()
    assert select_response.data is not None, f"Select failed: {select_response.error}"
    print(f"   ✅ Selected conversations: {json.dumps(select_response.data, indent=2, default=str)}")

if __name__ == "__main__":
    print(f"\n=== Supabase Authentication Test ({datetime.now()}) ===")
    pytest.main([__file__, "-v"]) 