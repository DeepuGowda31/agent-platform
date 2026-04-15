import hashlib
from functools import lru_cache
from app.agents.orchestrator import run_agent
from app.observability.metrics import METRICS

_cache: dict = {}
MAX_CACHE_SIZE = 100


def _cache_key(query: str, session_id: str) -> str:
    return hashlib.md5(f"{session_id}:{query.lower().strip()}".encode()).hexdigest()


class AgentService:

    async def handle_query(self, query: str, session_id: str = "default"):
        METRICS["agent_calls_total"] += 1

        key = _cache_key(query, session_id)
        if key in _cache:
            METRICS["cache_hits_total"] = METRICS.get("cache_hits_total", 0) + 1
            return {**_cache[key], "cached": True}

        result = await run_agent(query, session_id=session_id)

        if len(_cache) >= MAX_CACHE_SIZE:
            _cache.pop(next(iter(_cache)))
        _cache[key] = result

        return {**result, "cached": False}
