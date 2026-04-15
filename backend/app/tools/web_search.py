from app.tools.base_tool import BaseTool
from app.core.config import settings
from app.core.logger import logger

class WebSearchTool(BaseTool):
    name = "web_search"

    async def run(self, input_data: str) -> str:
        logger.info({"event": "WEB_SEARCH", "query": input_data})
        if not settings.TAVILY_API_KEY or settings.TAVILY_API_KEY == "your_tavily_api_key":
            return "Web search unavailable — TAVILY_API_KEY not configured."
        try:
            from tavily import TavilyClient
            client = TavilyClient(api_key=settings.TAVILY_API_KEY)
            response = client.search(query=input_data, max_results=3)
            results = response.get("results", [])
            if not results:
                return "No web results found."
            return "\n---\n".join(
                f"Title: {r['title']}\nURL: {r['url']}\nContent: {r['content']}"
                for r in results
            )
        except Exception as e:
            logger.error({"event": "WEB_SEARCH_ERROR", "error": str(e)})
            return f"Web search error: {str(e)}"
