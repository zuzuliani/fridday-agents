import pytest
import os
import uuid
from supabase import create_client, Client
from app.agents.utilities.create_embeddings import get_embedding
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

@pytest.mark.asyncio
async def test_vector_similarity_search():
    # Authenticate first
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
    
    # Test data with proper UUIDs
    test_session_1 = str(uuid.uuid4())
    test_session_2 = str(uuid.uuid4())
    
    test_messages = [
        {
            "content": "I need help with my business strategy for market expansion",
            "role": "user",
            "user_id": user_id,  # Use the authenticated user's ID
            "session_id": test_session_1
        },
        {
            "content": "Here's a strategic plan for market expansion: 1) Market research 2) Competitor analysis 3) Entry strategy",
            "role": "assistant",
            "user_id": user_id,  # Use the authenticated user's ID
            "session_id": test_session_1
        },
        {
            "content": "How do I improve my customer service?",
            "role": "user",
            "user_id": user_id,  # Use the authenticated user's ID
            "session_id": test_session_2
        }
    ]
    
    # Insert test messages with embeddings
    for message in test_messages:
        embedding = get_embedding(message["content"])
        insert_data = {
            **message,
            "embedding": embedding,
            "title": "Test Conversation"
        }
        supabase.table("conversations").insert(insert_data).execute()
    
    # Test search query
    search_query = "What's the best way to expand my business?"
    query_embedding = get_embedding(search_query)
    
    # Search for similar conversations
    response = supabase.rpc(
        'match_conversations',
        {
            'query_embedding': query_embedding,
            'match_threshold': 0.7,
            'match_count': 2
        }
    ).execute()
    
    # Verify results
    assert response.data is not None, "Search returned no results"
    assert len(response.data) > 0, "No similar conversations found"
    
    # The first result should be most similar to our search query
    first_result = response.data[0]
    assert first_result["content"] == test_messages[0]["content"], "Most similar result should match our test message"
    assert first_result["similarity"] > 0.7, "Similarity score should be above threshold"
    
    # Clean up test data
    for message in test_messages:
        supabase.table("conversations").delete().eq("session_id", message["session_id"]).execute()
    
    # Sign out
    supabase.auth.sign_out() 