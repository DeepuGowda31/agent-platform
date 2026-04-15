import aiosqlite
import os
from app.tools.base_tool import BaseTool
from app.core.config import settings
from app.core.logger import logger

# Ensure data directory exists
os.makedirs(os.path.dirname(settings.SQLITE_PATH), exist_ok=True)

_BLOCKED = ("insert", "update", "delete", "drop", "alter", "create", "truncate")

class SQLTool(BaseTool):
    name = "sql_query"

    async def run(self, input_data: str) -> str:
        logger.info({"event": "SQL_QUERY", "query": input_data})
        lower = input_data.lower().strip()

        # Block write operations — read-only agent tool
        if any(lower.startswith(kw) for kw in _BLOCKED):
            return "Only SELECT queries are allowed."

        try:
            async with aiosqlite.connect(settings.SQLITE_PATH) as db:
                db.row_factory = aiosqlite.Row
                async with db.execute(input_data) as cursor:
                    rows = await cursor.fetchall()
                    if not rows:
                        return "Query returned no results."
                    cols = [d[0] for d in cursor.description]
                    result = [dict(zip(cols, row)) for row in rows]
                    return str(result)
        except Exception as e:
            logger.error({"event": "SQL_ERROR", "error": str(e)})
            return f"SQL error: {str(e)}"
