from fastapi import APIRouter, Body
from app.agents.gpt_researcher_agent import GPTResearcherAgent

router = APIRouter()
gpt_agent = GPTResearcherAgent("wss://web-production-c0ad.up.railway.app/ws")

@router.post("/gpt-researcher")
def gpt_researcher_endpoint(
    task: str = Body(...),
    report_type: str = Body(...),
    report_source: str = Body(...),
    tone: str = Body(...),
    user_id: str = Body(...),
    topic: str = Body(...),
    jwt_token: str = Body(...)
):
    result = gpt_agent.run_task(task, report_type, report_source, tone, user_id, topic, jwt_token)
    return {"result": result} 