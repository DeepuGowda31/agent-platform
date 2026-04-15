from app.core.logger import logger
from app.tools.base_tool import BaseTool

class DocumentSearchTool(BaseTool):
    name = "document_search"

    _db = {
        "sales": "Sales dropped due to supply chain issues.",
        "incident": "Checkout API latency increased due to DB lock.",
        "marketing": "Marketing campaigns improved engagement.",
    }

    async def run(self, input_data: str) -> str:
        logger.info({"event": "DOCUMENT_SEARCH", "query": input_data})
        for k, v in self._db.items():
            if k in input_data.lower():
                logger.info({"event": "DOCUMENT_MATCH", "key": k})
                return v
        logger.warning({"event": "DOCUMENT_NO_MATCH"})
        return "No relevant document found"
