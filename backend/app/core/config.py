import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    MODEL_NAME: str = "llama-3.3-70b-versatile"

    PINECONE_API_KEY: str = os.getenv("PINECONE_API_KEY", "")
    PINECONE_INDEX: str = os.getenv("PINECONE_INDEX", "agent-platform")

    TAVILY_API_KEY: str = os.getenv("TAVILY_API_KEY", "")

    SQLITE_PATH: str = os.getenv("SQLITE_PATH", "./data/agent.db")

    ALLOWED_ORIGINS: list = os.getenv("ALLOWED_ORIGINS", "*").split(",")

settings = Settings()
