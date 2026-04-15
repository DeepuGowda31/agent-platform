from collections import defaultdict
from typing import List, Dict
import time

# session_id -> list of {role, content, ts}
_store: Dict[str, List[dict]] = defaultdict(list)

MAX_TURNS = 20

def add_message(session_id: str, role: str, content: str):
    _store[session_id].append({
        "role": role,
        "content": content,
        "ts": time.time()
    })
    # sliding window — trim oldest beyond MAX_TURNS
    if len(_store[session_id]) > MAX_TURNS:
        _store[session_id] = _store[session_id][-MAX_TURNS:]

def get_history(session_id: str) -> List[dict]:
    return _store.get(session_id, [])

def format_history_for_prompt(session_id: str) -> str:
    history = get_history(session_id)
    if not history:
        return ""
    lines = [f"{m['role'].upper()}: {m['content']}" for m in history]
    return "\n".join(lines)

def clear_session(session_id: str):
    _store.pop(session_id, None)
