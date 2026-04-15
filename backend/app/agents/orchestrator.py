from app.core.logger import logger
from app.graph.graph import agent_graph
from app.memory.store import format_history_for_prompt

async def run_agent(query: str, session_id: str = "default") -> dict:

    logger.info({"event": "AGENT_START", "query": query, "session_id": session_id})

    history = format_history_for_prompt(session_id)

    # Initial state fed into the graph
    initial_state = {
        "query": query,
        "session_id": session_id,
        "history": history,
        "route": None,
        "answer": None,
        "error": None,
        "steps": [],
    }

    # LangGraph executes the full graph — supervisor → agent → memory
    final_state = await agent_graph.ainvoke(initial_state)

    logger.info({
        "event": "AGENT_COMPLETE",
        "session_id": session_id,
        "route": final_state.get("route"),
        "steps": final_state.get("steps"),
    })

    return {
        "session_id": session_id,
        "query": query,
        "route": final_state.get("route"),
        "answer": final_state.get("answer", "No answer generated."),
        "steps": final_state.get("steps", []),
    }
