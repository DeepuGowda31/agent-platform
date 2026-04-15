from app.graph.state import AgentState
from app.llm.gemini_client import ask_llm
from app.core.logger import logger
from app.memory.store import add_message, format_history_for_prompt

# ── Supervisor Node ─────────────────────────────────────────────────────────
def supervisor_node(state: AgentState) -> AgentState:
    logger.info({"event": "NODE_SUPERVISOR", "query": state["query"]})

    prompt = f"""You are a supervisor. Route the query to the best agent.
Agents:
- research: web search, current events, news, facts from the internet
- data: math calculations, SQL queries, numbers, statistics
- general: internal documents, company knowledge, general questions

Reply with ONE word only: research, data, or general.

Query: {state["query"]}"""

    route = ask_llm(prompt).strip().lower()

    if "research" in route:
        route = "research"
    elif "data" in route:
        route = "data"
    else:
        route = "general"

    logger.info({"event": "NODE_SUPERVISOR_ROUTE", "route": route})

    return {
        **state,
        "route": route,
        "steps": state.get("steps", []) + [f"supervisor → {route}"]
    }

# ── Research Node ───────────────────────────────────────────────────────────
async def research_node(state: AgentState) -> AgentState:
    logger.info({"event": "NODE_RESEARCH"})
    from app.tools.web_search import WebSearchTool
    from app.tools.vector_search import VectorSearchTool

    web = await WebSearchTool().run(state["query"])
    vec = await VectorSearchTool().run(state["query"])

    answer = ask_llm(
        f"Synthesize a clear answer from these sources.\n\n"
        f"Question: {state['query']}\n\n"
        f"Web: {web}\nVector Store: {vec}\n\nAnswer:"
    )
    return {
        **state,
        "answer": answer,
        "steps": state["steps"] + ["research_node: web_search + vector_search"]
    }

# ── Data Node ───────────────────────────────────────────────────────────────
async def data_node(state: AgentState) -> AgentState:
    logger.info({"event": "NODE_DATA"})
    from app.tools.calculator import CalculatorTool
    from app.tools.sql_tool import SQLTool
    import re

    decision = ask_llm(
        f"Classify as 'sql' or 'calculator'. One word only.\nQuery: {state['query']}"
    ).strip().lower()

    if "sql" in decision:
        raw = ask_llm(
            f"Convert to SQLite SELECT query. Raw SQL only, no markdown.\nQuestion: {state['query']}"
        )
        sql = re.sub(r"```[\w]*\n?", "", raw).replace("```", "").strip()
        answer = await SQLTool().run(sql)
    else:
        answer = await CalculatorTool().run(state["query"])

    return {
        **state,
        "answer": answer,
        "steps": state["steps"] + [f"data_node: {decision}"]
    }

# ── General Node ────────────────────────────────────────────────────────────
async def general_node(state: AgentState) -> AgentState:
    logger.info({"event": "NODE_GENERAL"})
    from app.tools.document_search import DocumentSearchTool

    doc = await DocumentSearchTool().run(state["query"])
    answer = ask_llm(
        f"Answer using the context below.\n\n"
        f"Question: {state['query']}\nContext: {doc}\n\nAnswer:"
    )
    return {
        **state,
        "answer": answer,
        "steps": state["steps"] + ["general_node: document_search"]
    }

# ── Memory Node ─────────────────────────────────────────────────────────────
def memory_node(state: AgentState) -> AgentState:
    logger.info({"event": "NODE_MEMORY", "session_id": state["session_id"]})
    add_message(state["session_id"], "user", state["query"])
    add_message(state["session_id"], "assistant", state.get("answer", ""))
    return {
        **state,
        "steps": state["steps"] + ["memory_node: saved"]
    }

# ── Router function (used as conditional edge) ──────────────────────────────
def route_to_agent(state: AgentState) -> str:
    return state.get("route", "general")
