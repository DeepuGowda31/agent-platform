# Agent Platform

![CI/CD](https://github.com/DeepuGowda31/agent-platform/actions/workflows/ci.yml/badge.svg)
![Python](https://img.shields.io/badge/python-3.11-blue)
![LangGraph](https://img.shields.io/badge/LangGraph-0.2-green)
![Groq](https://img.shields.io/badge/LLM-Groq%20Llama%203.3-orange)
![License](https://img.shields.io/badge/license-MIT-blue)

A **production-grade Multi-Agent AI Platform** built with LangGraph, Groq (Llama 3.3 70B), FastAPI, and Next.js. Features autonomous agent routing, real-time web search, vector semantic search, session memory, and full observability.

---

## Architecture

```
User (Next.js Chat UI)
        │
        ▼
FastAPI Backend ──── Prometheus /metrics
        │
        ▼
LangGraph State Machine
        │
   Supervisor Node (Groq LLM)
        │
   ┌────┴────────────┐──────────────┐
   ▼                 ▼              ▼
Research Node    Data Node    General Node
web + vector    SQL + math    docs + API
   │                 │              │
   └────────┬────────┘──────────────┘
            ▼
       Memory Node
       (session store)
            │
            ▼
         Response
```

---

## Tech Stack

| Layer | Technology |
|---|---|
| LLM | Groq — Llama 3.3 70B (free, 14k req/day) |
| Agent Framework | LangGraph — StateGraph with conditional edges |
| API | FastAPI + Uvicorn |
| Frontend | Next.js 16 + Tailwind CSS |
| Vector DB | Pinecone (semantic search) |
| Web Search | Tavily API |
| Database | SQLite (async) |
| Observability | Prometheus + structured JSON logs |
| CI/CD | GitHub Actions — lint → test → deploy |
| Deployment | Railway (backend) + Vercel (frontend) |

---

## CI/CD Pipeline

```
git push
    │
    ├── Lint (ruff)
    │       │
    └── Test (pytest 4 tests)
            │
            ├── dev branch  → Deploy to Staging
            │
            └── main branch → Deploy to Production
                                    │
                              Health check /health
                                    │
                              Rollback on failure
```

---

## Quick Start

### Backend
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

### Environment Variables
```env
GROQ_API_KEY=your_groq_key
PINECONE_API_KEY=your_pinecone_key
PINECONE_INDEX=agent-platform
TAVILY_API_KEY=your_tavily_key
SQLITE_PATH=./data/agent.db
```

---

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| POST | `/agent/query` | Send query to agent |
| GET | `/agent/history/{session_id}` | Get conversation history |
| DELETE | `/agent/history/{session_id}` | Clear session memory |
| GET | `/health` | Health check |
| GET | `/metrics` | Prometheus metrics |
| GET | `/docs` | Swagger UI |

---

## Agents

- **Research Agent** — web search + Pinecone vector search + LLM synthesis
- **Data Agent** — natural language → SQL or calculator
- **General Agent** — internal document search + LLM answer

---

## License
MIT
