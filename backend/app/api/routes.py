from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, field_validator
from typing import Optional
from app.services.agent_service import AgentService
from app.memory.store import get_history, clear_session
from app.core.logger import logger
from app.observability.metrics import METRICS

router = APIRouter()
service = AgentService()

class QueryRequest(BaseModel):
    query: str
    session_id: Optional[str] = "default"

    @field_validator("query")
    @classmethod
    def validate_query(cls, v):
        if not v or not v.strip():
            raise ValueError("query must not be empty")
        if len(v) > 5000:
            raise ValueError("query must not exceed 5000 characters")
        return v.strip()

@router.post("/agent/query")
async def agent_query(req: QueryRequest):
    logger.info({"event": "API_REQUEST", "session_id": req.session_id})
    try:
        return await service.handle_query(req.query, req.session_id)
    except Exception as e:
        METRICS["llm_errors_total"] += 1
        logger.error({"event": "AGENT_ERROR", "error": str(e)})
        raise HTTPException(status_code=500, detail="Agent failed to process the request")

@router.get("/agent/history/{session_id}")
def get_session_history(session_id: str):
    return {"session_id": session_id, "history": get_history(session_id)}

@router.delete("/agent/history/{session_id}")
def clear_session_history(session_id: str):
    clear_session(session_id)
    return {"session_id": session_id, "status": "cleared"}
