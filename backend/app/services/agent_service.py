from app.agents.orchestrator import run_agent
from app.observability.metrics import METRICS

class AgentService:

    async def handle_query(self, query: str, session_id: str = "default"):
        METRICS["agent_calls_total"] += 1
        return await run_agent(query, session_id=session_id)
