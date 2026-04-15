from .base_tool import BaseTool
from app.llm.gemini_client import ask_llm

class SummarizerTool(BaseTool):

    name = "summarizer"

    async def run(self, text: str) -> str:

        prompt = f"""
        Summarize the following content:

        {text}
        """

        return ask_llm(prompt)
