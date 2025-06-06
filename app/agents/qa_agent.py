import os
import uuid
from typing import List, Dict, Any, Optional
import httpx
from supabase import create_client, Client
from app.agents.utilities.create_embeddings import get_embedding
from app.agents.memory import memory as redis_memory
from langchain.memory import ConversationBufferMemory
from langchain_openai import ChatOpenAI
from langchain.chains import ConversationChain
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.tools import Tool
from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain_core.messages import SystemMessage
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
EMBEDDING_DIM = 1536  # Set this to your embedding size (e.g., 1536 for OpenAI Ada)

# Custom system prompt for business consulting
BUSINESS_CONSULTANT_PROMPT = """You are an expert business consultant with deep knowledge in:
- Business strategy and growth
- Market analysis and competitive positioning
- Financial planning and optimization
- Operations and process improvement
- Digital transformation and technology adoption
- Change management and organizational development

Your role is to:
1. Ask clarifying questions to understand the business context
2. Provide strategic, actionable advice
3. Consider both short-term and long-term implications
4. Reference relevant business frameworks and best practices
5. Be direct but diplomatic in your recommendations

Always maintain a professional tone and focus on delivering value through practical, implementable solutions."""

class ConversationalAgent:
    def __init__(self, llm_model="gpt-3.5-turbo"):
        self.llm = ChatOpenAI(model=llm_model)
        self.memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True
        )
        
        # Initialize tools
        self.tools = self._initialize_tools()
        
        # Create the agent with custom prompt
        self.agent = self._create_agent()
        
        # Initialize Supabase client (will be updated with JWT token)
        self.supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        
    def _initialize_tools(self) -> List[Tool]:
        """Initialize the tools available to the agent"""
        return [
            Tool(
                name="SearchSimilarConversations",
                func=self._search_similar_conversations,
                description="Search for similar past conversations to provide context-aware responses"
            ),
            Tool(
                name="GetBusinessMetrics",
                func=self._get_business_metrics,
                description="Retrieve relevant business metrics and KPIs for analysis"
            )
        ]
    
    def _create_agent(self) -> AgentExecutor:
        """Create the agent with custom prompt and tools"""
        prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content=BUSINESS_CONSULTANT_PROMPT),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])
        
        agent = create_openai_functions_agent(
            llm=self.llm,
            tools=self.tools,
            prompt=prompt
        )
        
        return AgentExecutor(
            agent=agent,
            tools=self.tools,
            memory=self.memory,
            verbose=True
        )

    def _search_similar_conversations(self, query: str) -> List[Dict[str, Any]]:
        """Search for similar conversations using embeddings"""
        query_embedding = get_embedding(query)
        
        # Search in Supabase using vector similarity
        response = self.supabase.rpc(
            'match_conversations',
            {
                'query_embedding': query_embedding,
                'match_threshold': 0.7,
                'match_count': 5
            }
        ).execute()
        
        return response.data if response.data else []

    def _get_business_metrics(self, metric_type: str) -> Dict[str, Any]:
        """Example tool for retrieving business metrics"""
        # This is a placeholder - implement actual metric retrieval logic
        return {
            "metric_type": metric_type,
            "value": "Sample metric value",
            "timestamp": "2024-03-20T12:00:00Z"
        }

    def get_or_create_session_id(self, session_id=None):
        if session_id:
            return session_id
        return str(uuid.uuid4())

    async def _rest_insert_conversation(self, insert_data, jwt_token):
        url = f"{SUPABASE_URL}/rest/v1/conversations"
        headers = {
            "apikey": SUPABASE_KEY,
            "Authorization": f"Bearer {jwt_token}",
            "Content-Type": "application/json",
            "Prefer": "return=representation"
        }
        async with httpx.AsyncClient() as client:
            resp = await client.post(url, headers=headers, json=insert_data)
            print("Insert status:", resp.status_code)
            print("Insert response text:", resp.text)
            if resp.status_code not in (200, 201):
                raise Exception(f"Insert failed: {resp.text}")
            try:
                return resp.json()
            except Exception as e:
                print("Failed to parse JSON response:", e)
                print("Raw response text:", resp.text)
                raise

    async def _rest_get_conversation_history(self, session_id, jwt_token):
        url = f"{SUPABASE_URL}/rest/v1/conversations?select=role,content&session_id=eq.{session_id}&order=id"
        headers = {
            "apikey": SUPABASE_KEY,
            "Authorization": f"Bearer {jwt_token}"
        }
        async with httpx.AsyncClient() as client:
            resp = await client.get(url, headers=headers)
            if resp.status_code != 200:
                raise Exception(f"Select failed: {resp.text}")
            data = resp.json()
            return [(msg["role"], msg["content"]) for msg in data]

    async def log_message(self, session_id, user_id, role, content, jwt_token, title=None, metadata=None, is_archived=False):
        embedding = get_embedding(content)
        insert_data = {
            "session_id": session_id,
            "user_id": user_id,
            "role": role,
            "content": content,
            "title": title or "Business Consultation",
            "metadata": metadata or {},
            "is_archived": is_archived,
            "embedding": embedding
        }
        await self._rest_insert_conversation(insert_data, jwt_token)

    async def get_conversation_history(self, session_id, jwt_token):
        return await self._rest_get_conversation_history(session_id, jwt_token)

    def update_memory(self, history):
        self.memory.clear()
        for role, content in history:
            if role == "user":
                self.memory.chat_memory.add_user_message(content)
            else:
                self.memory.chat_memory.add_ai_message(content)

    async def _rest_update_conversation(self, row_id, update_data, jwt_token):
        url = f"{SUPABASE_URL}/rest/v1/conversations?id=eq.{row_id}"
        headers = {
            "apikey": SUPABASE_KEY,
            "Authorization": f"Bearer {jwt_token}",
            "Content-Type": "application/json",
            "Prefer": "return=representation"
        }
        async with httpx.AsyncClient() as client:
            resp = await client.patch(url, headers=headers, json=update_data)
            print("Update status:", resp.status_code)
            print("Update response text:", resp.text)
            if resp.status_code not in (200, 201):
                raise Exception(f"Update failed: {resp.text}")
            try:
                return resp.json()
            except Exception as e:
                print("Failed to parse JSON response:", e)
                print("Raw response text:", resp.text)
                raise

    async def run(self, user_message, user_id, session_id=None, jwt_token=None):
        session_id = self.get_or_create_session_id(session_id)
        # Log user message
        await self.log_message(session_id, user_id, "user", user_message, jwt_token)
        # Retrieve conversation history
        history = await self.get_conversation_history(session_id, jwt_token)
        # Update Redis short-term memory
        redis_memory.set_memory(f"session:{session_id}:last_user_message", user_message, expire=3600)
        # Update LangChain memory
        self.update_memory(history)
        # Insert assistant row with status 'pending' and empty content
        pending_assistant_data = {
            "session_id": session_id,
            "user_id": user_id,
            "role": "assistant",
            "content": "",
            "title": "Business Consultation",
            "metadata": {},
            "is_archived": False,
            "embedding": [0.0] * EMBEDDING_DIM,
            "status": "pending"
        }
        pending_row = await self._rest_insert_conversation(pending_assistant_data, jwt_token)
        assistant_row_id = None
        if isinstance(pending_row, list) and pending_row:
            assistant_row_id = pending_row[0].get("id")
        elif isinstance(pending_row, dict):
            assistant_row_id = pending_row.get("id")
        # Generate agent reply using the agent executor
        agent_reply = self.agent.invoke({"input": user_message})["output"]
        # Update the assistant row with the reply and status 'complete'
        if assistant_row_id:
            update_data = {
                "content": agent_reply,
                "embedding": get_embedding(agent_reply),
                "status": "complete"
            }
            await self._rest_update_conversation(assistant_row_id, update_data, jwt_token)
        # Update Redis with agent reply
        redis_memory.set_memory(f"session:{session_id}:last_agent_reply", agent_reply, expire=3600)
        return {"reply": agent_reply, "session_id": session_id} 