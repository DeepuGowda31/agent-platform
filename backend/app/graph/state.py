from typing import TypedDict, Optional

class AgentState(TypedDict):
    query: str
    session_id: str
    history: str
    route: Optional[str]
    answer: Optional[str]
    error: Optional[str]
    steps: list  # trace of every node visited
