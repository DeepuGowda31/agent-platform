import time
import uuid
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from app.api.routes import router as agent_router
from app.core.config import settings
from app.core.logger import logger
from app.observability.metrics import METRICS

limiter = Limiter(key_func=get_remote_address)

app = FastAPI(title="Agent Platform", version="1.0.0")
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# ── CORS ──────────────────────────────────────────────────────────────────────
ALLOWED_ORIGINS = settings.ALLOWED_ORIGINS
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_methods=["GET", "POST", "DELETE"],
    allow_headers=["Content-Type", "Authorization"],
)

# ── Request logger middleware ─────────────────────────────────────────────────
@app.middleware("http")
async def request_logger(request: Request, call_next):
    request_id = str(uuid.uuid4())[:8]
    start = time.time()
    logger.info({"event": "REQUEST_START", "request_id": request_id,
                 "method": request.method, "path": request.url.path})
    response = await call_next(request)
    duration_ms = round((time.time() - start) * 1000, 2)
    METRICS["requests_total"] += 1
    METRICS["total_latency_ms"] += duration_ms
    response.headers["X-Request-ID"] = request_id
    logger.info({"event": "REQUEST_DONE", "request_id": request_id,
                 "status": response.status_code, "duration_ms": duration_ms})
    return response

# ── Health ────────────────────────────────────────────────────────────────────
@app.get("/health")
def health():
    missing = [k for k in ("GROQ_API_KEY", "PINECONE_API_KEY", "TAVILY_API_KEY")
               if not getattr(settings, k)]
    if missing:
        return JSONResponse(status_code=503, content={"status": "degraded", "missing": missing})
    return {"status": "ok"}

# ── Metrics ───────────────────────────────────────────────────────────────────
@app.get("/metrics")
def metrics():
    total = METRICS["requests_total"]
    avg_latency = round(METRICS["total_latency_ms"] / total, 2) if total else 0
    return {
        "requests_total": total,
        "avg_latency_ms": avg_latency,
        "agent_calls_total": METRICS["agent_calls_total"],
        "llm_errors_total": METRICS["llm_errors_total"],
        "cache_hits_total": METRICS.get("cache_hits_total", 0),
    }

# ── Ping ──────────────────────────────────────────────────────────────────────
@app.get("/ping")
def ping():
    return {"status": "ok"}

app.include_router(agent_router)
