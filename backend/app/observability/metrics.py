from prometheus_client import Counter, Histogram, Gauge

# ── Counters ────────────────────────────────────────────────────────────────
requests_total = Counter(
    "agent_requests_total",
    "Total HTTP requests",
    ["method", "path", "status"]
)

agent_calls_total = Counter(
    "agent_calls_total",
    "Total agent invocations",
    ["route"]
)

llm_errors_total = Counter(
    "llm_errors_total",
    "Total LLM errors"
)

llm_calls_total = Counter(
    "llm_calls_total",
    "Total LLM calls"
)

# ── Histograms ───────────────────────────────────────────────────────────────
request_latency = Histogram(
    "agent_request_latency_seconds",
    "Request latency in seconds",
    ["path"],
    buckets=[0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 30.0]
)

llm_latency = Histogram(
    "llm_call_latency_seconds",
    "LLM call latency in seconds",
    buckets=[0.5, 1.0, 2.0, 5.0, 10.0, 30.0]
)

# ── Gauges ───────────────────────────────────────────────────────────────────
active_sessions = Gauge(
    "agent_active_sessions",
    "Number of active memory sessions"
)

# Legacy dict for backward compat with existing code
METRICS = {
    "requests_total": 0,
    "total_latency_ms": 0.0,
    "agent_calls_total": 0,
    "llm_errors_total": 0,
}
