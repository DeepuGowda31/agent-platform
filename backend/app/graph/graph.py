from langgraph.graph import StateGraph, END
from app.graph.state import AgentState
from app.graph.nodes import (
    supervisor_node,
    research_node,
    data_node,
    general_node,
    memory_node,
    route_to_agent,
)

def build_graph():
    graph = StateGraph(AgentState)

    # ── Register all nodes ──────────────────────────────────────────────────
    graph.add_node("supervisor", supervisor_node)
    graph.add_node("research",   research_node)
    graph.add_node("data",       data_node)
    graph.add_node("general",    general_node)
    graph.add_node("memory",     memory_node)

    # ── Entry point ─────────────────────────────────────────────────────────
    graph.set_entry_point("supervisor")

    # ── Conditional routing from supervisor ─────────────────────────────────
    graph.add_conditional_edges(
        "supervisor",
        route_to_agent,
        {
            "research": "research",
            "data":     "data",
            "general":  "general",
        }
    )

    # ── All agents flow into memory, then END ────────────────────────────────
    graph.add_edge("research", "memory")
    graph.add_edge("data",     "memory")
    graph.add_edge("general",  "memory")
    graph.add_edge("memory",   END)

    return graph.compile()

# Singleton — compiled once at startup
agent_graph = build_graph()
