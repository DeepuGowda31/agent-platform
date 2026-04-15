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

_agent_graph = None


def get_graph():
    global _agent_graph
    if _agent_graph is None:
        graph = StateGraph(AgentState)
        graph.add_node("supervisor", supervisor_node)
        graph.add_node("research", research_node)
        graph.add_node("data", data_node)
        graph.add_node("general", general_node)
        graph.add_node("memory", memory_node)
        graph.set_entry_point("supervisor")
        graph.add_conditional_edges(
            "supervisor",
            route_to_agent,
            {"research": "research", "data": "data", "general": "general"},
        )
        graph.add_edge("research", "memory")
        graph.add_edge("data", "memory")
        graph.add_edge("general", "memory")
        graph.add_edge("memory", END)
        _agent_graph = graph.compile()
    return _agent_graph
