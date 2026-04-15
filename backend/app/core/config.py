import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    MODEL_NAME: str = "llama-3.3-70b-versatile"  # Groq free model

    # Pinecone
    PINECONE_API_KEY: str = os.getenv("PINECONE_API_KEY", "")
    PINECONE_INDEX: str = os.getenv("PINECONE_INDEX", "agent-platform")

    # Tavily web search
    TAVILY_API_KEY: str = os.getenv("TAVILY_API_KEY", "")

    # SQLite path (file-based, no server needed)
    SQLITE_PATH: str = os.getenv("SQLITE_PATH", "./data/agent.db")

settings = Settings()
