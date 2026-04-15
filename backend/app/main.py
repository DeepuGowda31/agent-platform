import time
import uuid
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from prometheus_fastapi_instrumentator import Instrumentator
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
from app.api.routes import router as agent_router
from app.core.logger import logger
from app.observability.metrics import (
    METRICS, requests_total, request_latency,
    agent_calls_total, llm_errors_total
)

app = FastAPI(title="Agent Platform", version="1.0.0")

# ── Prometheus auto-instrumentation ─────────────────────────────────────────
Instrumentator().instrument(app).expose(app, endpoint="/metrics")

# ── Request logger middleware ────────────────────────────────────────────────
@app.middleware("http")
async def request_logger(request: Request, call_next):
    request_id = str(uuid.uuid4())[:8]
    request.state.request_id = request_id
    start = time.time()

    logger.info({"event": "REQUEST_START", "request_id": request_id,
                 "method": request.method, "path": request.url.path})

    response = await call_next(request)
    duration_ms = round((time.time() - start) * 1000, 2)

    METRICS["requests_total"] += 1
    METRICS["total_latency_ms"] += duration_ms

    logger.info({"event": "REQUEST_DONE", "request_id": request_id,
                 "status": response.status_code, "duration_ms": duration_ms})
    return response

# ── CORS ─────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)

# ── Health ────────────────────────────────────────────────────────────────────
@app.get("/health")
def health():
    from app.llm.gemini_client import _client
    llm_ok = _client is not None
    return {"status": "ok" if llm_ok else "degraded", "llm": llm_ok}

# ── Ping ──────────────────────────────────────────────────────────────────────
@app.get("/ping")
def ping():
    logger.info({"event": "PING"})
    return {"status": "ok"}

app.include_router(agent_router)
