import pytest
from unittest.mock import patch, MagicMock
from httpx import AsyncClient, ASGITransport


# ── Mock Groq client before the app loads ───────────────────────────────────────
mock_groq = MagicMock()
mock_groq.chat.completions.create.return_value = MagicMock(
    choices=[MagicMock(message=MagicMock(content="general"))]
)

with patch("groq.Groq", return_value=mock_groq):
    from app.main import app


@pytest.mark.asyncio
async def test_ping():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        r = await ac.get("/ping")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


@pytest.mark.asyncio
async def test_health():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        r = await ac.get("/health")
    assert r.status_code == 200
    assert "status" in r.json()


@pytest.mark.asyncio
async def test_metrics_endpoint_exists():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        r = await ac.get("/metrics")
    # Prometheus returns text/plain format
    assert r.status_code == 200


@pytest.mark.asyncio
async def test_agent_query():
    with patch("app.llm.gemini_client.ask_llm", return_value="Sales dropped due to supply chain issues."):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            r = await ac.post("/agent/query", json={"query": "What happened with sales?"})
    assert r.status_code == 200
    data = r.json()
    assert "answer" in data
    assert "route" in data
