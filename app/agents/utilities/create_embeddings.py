from openai import OpenAI
import os

def get_embedding(text, model="text-embedding-ada-002"):
    """
    Returns the embedding vector for the given text using OpenAI.
    """
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    response = client.embeddings.create(
        input=[text],
        model=model
    )
    return response.data[0].embedding
