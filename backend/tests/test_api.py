import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from httpx import AsyncClient, ASGITransport

# ── Mock Groq client before app loads ────────────────────────────────────────
mock_groq = MagicMock()
mock_groq.chat.completions.create.return_value = MagicMock(
    choices=[MagicMock(message=MagicMock(content="general"))]
)

with patch("groq.Groq", return_value=mock_groq):
    from app.main import app


# ── Helpers ───────────────────────────────────────────────────────────────────
async def client_get(path):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        return await ac.get(path)

async def client_post(path, json):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        return await ac.post(path, json=json)


# ── Health & Infra ────────────────────────────────────────────────────────────
@pytest.mark.asyncio
async def test_ping():
    r = await client_get("/ping")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


@pytest.mark.asyncio
async def test_health():
    r = await client_get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


@pytest.mark.asyncio
async def test_metrics_returns_expected_keys():
    r = await client_get("/metrics")
    assert r.status_code == 200
    data = r.json()
    for key in ("requests_total", "avg_latency_ms", "agent_calls_total", "llm_errors_total"):
        assert key in data


# ── Agent Query — happy path ──────────────────────────────────────────────────
@pytest.mark.asyncio
async def test_agent_query_success():
    mock_response = {"answer": "Sales dropped due to supply chain issues.", "route": "general"}
    with patch("app.services.agent_service.run_agent", new=AsyncMock(return_value=mock_response)):
        r = await client_post("/agent/query", {"query": "What happened with sales?"})
    assert r.status_code == 200
    data = r.json()
    assert "answer" in data
    assert "route" in data


@pytest.mark.asyncio
async def test_agent_query_with_session_id():
    mock_response = {"answer": "ok", "route": "general"}
    with patch("app.services.agent_service.run_agent", new=AsyncMock(return_value=mock_response)):
        r = await client_post("/agent/query", {"query": "hello", "session_id": "test-session-123"})
    assert r.status_code == 200


# ── Agent Query — guardrail tests ─────────────────────────────────────────────
@pytest.mark.asyncio
async def test_agent_query_empty_string():
    r = await client_post("/agent/query", {"query": ""})
    assert r.status_code == 422


@pytest.mark.asyncio
async def test_agent_query_missing_query_field():
    r = await client_post("/agent/query", {})
    assert r.status_code == 422


@pytest.mark.asyncio
async def test_agent_query_too_long():
    r = await client_post("/agent/query", {"query": "a" * 5001})
    assert r.status_code == 422


# ── Agent Query — fallback/error handling ────────────────────────────────────
@pytest.mark.asyncio
async def test_agent_query_llm_failure_returns_500():
    with patch("app.services.agent_service.run_agent", new=AsyncMock(side_effect=Exception("LLM timeout"))):
        r = await client_post("/agent/query", {"query": "test query"})
    assert r.status_code == 500


# ── Session History ───────────────────────────────────────────────────────────
@pytest.mark.asyncio
async def test_get_history_empty_session():
    r = await client_get("/agent/history/nonexistent-session")
    assert r.status_code == 200
    assert "history" in r.json()


@pytest.mark.asyncio
async def test_clear_session():
    r = await client_post("/agent/query", {"query": "hello", "session_id": "clear-me"}) if False else None
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        r = await ac.delete("/agent/history/clear-me")
    assert r.status_code == 200
    assert r.json()["status"] == "cleared"
