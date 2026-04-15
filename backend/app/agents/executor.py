from app.tools.document_search import DocumentSearchTool
from app.tools.vector_search import VectorSearchTool
from app.tools.web_search import WebSearchTool
from app.tools.calculator import CalculatorTool
from app.tools.sql_tool import SQLTool
from app.tools.api_caller import APICallerTool

TOOLS = {
    "document_search": DocumentSearchTool(),
    "vector_search": VectorSearchTool(),
    "web_search": WebSearchTool(),
    "calculator": CalculatorTool(),
    "sql_query": SQLTool(),
    "api_caller": APICallerTool(),
}

async def execute_tool(name: str, input_data: str) -> str:
    tool = TOOLS.get(name)
    if not tool:
        return f"Unknown tool: {name}"
    return await tool.run(input_data)
