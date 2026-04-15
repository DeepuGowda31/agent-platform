from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional
from app.services.agent_service import AgentService
from app.memory.store import get_history, clear_session
from app.core.logger import logger

router = APIRouter()
service = AgentService()

class QueryRequest(BaseModel):
    query: str
    session_id: Optional[str] = "default"

@router.post("/agent/query")
async def agent_query(req: QueryRequest):
    logger.info({"event": "API_REQUEST", "session_id": req.session_id})
    return await service.handle_query(req.query, req.session_id)

@router.get("/agent/history/{session_id}")
def get_session_history(session_id: str):
    return {"session_id": session_id, "history": get_history(session_id)}

@router.delete("/agent/history/{session_id}")
def clear_session_history(session_id: str):
    clear_session(session_id)
    return {"session_id": session_id, "status": "cleared"}
