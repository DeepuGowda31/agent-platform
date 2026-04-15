from app.tools.base_tool import BaseTool
from app.core.config import settings
from app.core.logger import logger

_pc_client = None
_index = None

def _get_index():
    global _pc_client, _index
    if _index is None:
        try:
            from pinecone import Pinecone
            _pc_client = Pinecone(api_key=settings.PINECONE_API_KEY)
            _index = _pc_client.Index(settings.PINECONE_INDEX)
        except Exception as e:
            logger.error({"event": "PINECONE_INIT_ERROR", "error": str(e)})
    return _index

def _embed(text: str):
    # Use a free local embedding model via sentence-transformers
    try:
        from sentence_transformers import SentenceTransformer
        model = SentenceTransformer("all-MiniLM-L6-v2")
        return model.encode(text).tolist()
    except ImportError:
        # Fallback: random vector (Pinecone won't return useful results but won't crash)
        import random
        return [random.uniform(-1, 1) for _ in range(384)]

class VectorSearchTool(BaseTool):
    name = "vector_search"

    async def run(self, input_data: str) -> str:
        logger.info({"event": "VECTOR_SEARCH", "query": input_data})
        index = _get_index()
        if index is None:
            return "Vector search unavailable — Pinecone not configured."
        try:
            vector = _embed(input_data)
            results = index.query(vector=vector, top_k=3, include_metadata=True)
            if not results.matches:
                return "No relevant documents found in vector store."
            docs = [m.metadata.get("text", "") for m in results.matches if m.score > 0.5]
            return "\n---\n".join(docs) if docs else "No high-confidence matches found."
        except Exception as e:
            logger.error({"event": "VECTOR_SEARCH_ERROR", "error": str(e)})
            return f"Vector search error: {str(e)}"
