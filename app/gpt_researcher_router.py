from fastapi import APIRouter, Body, HTTPException
from app.agents.gpt_researcher_agent import GPTResearcherAgent
import os
import logging
import threading

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

# Get WebSocket URL from environment variable with a default
WS_URL = os.getenv("GPT_RESEARCHER_WS_URL", "wss://web-production-c0ad.up.railway.app/ws")
gpt_agent = GPTResearcherAgent(WS_URL)

@router.post("/gpt-researcher")
async def gpt_researcher_endpoint(
    task: str = Body(...),
    report_type: str = Body(...),
    report_source: str = Body(...),
    tone: str = Body(...),
    user_id: str = Body(...),
    topic: str = Body(...),
    jwt_token: str = Body(...),
    headers: dict = Body(default={})
):
    try:
        logger.info(f"Starting research task: {task}")
        logger.info(f"Headers received: {headers}")
        
        # Start the research process in a separate thread
        def run_research():
            try:
                gpt_agent.run_task(
                    task=task,
                    report_type=report_type,
                    report_source=report_source,
                    tone=tone,
                    user_id=user_id,
                    topic=topic,
                    jwt_token=jwt_token
                )
            except Exception as e:
                logger.error(f"Error in research thread: {str(e)}", exc_info=True)
        
        # Start the research process in background
        thread = threading.Thread(target=run_research)
        thread.start()
        
        # Return immediately with the research ID
        return {
            "status": "process_started",
            "message": "Research process has been initiated",
            "research_id": gpt_agent.research_id
        }
        
    except Exception as e:
        logger.error(f"Error in gpt_researcher_endpoint: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        ) 