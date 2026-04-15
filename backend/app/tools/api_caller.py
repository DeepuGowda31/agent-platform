import httpx
import json
from app.tools.base_tool import BaseTool
from app.core.logger import logger

class APICallerTool(BaseTool):
    name = "api_caller"

    async def run(self, input_data: str) -> str:
        """
        Expects input_data as JSON string:
        {"url": "...", "method": "GET", "headers": {}, "body": {}}
        """
        logger.info({"event": "API_CALLER", "input": input_data[:200]})
        try:
            params = json.loads(input_data)
            url = params["url"]
            method = params.get("method", "GET").upper()
            headers = params.get("headers", {})
            body = params.get("body", None)

            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.request(method, url, headers=headers, json=body)
                response.raise_for_status()
                try:
                    return json.dumps(response.json(), indent=2)
                except Exception:
                    return response.text[:2000]
        except json.JSONDecodeError:
            return "api_caller expects JSON input: {\"url\": \"...\", \"method\": \"GET\"}"
        except httpx.HTTPStatusError as e:
            logger.error({"event": "API_CALLER_HTTP_ERROR", "error": str(e)})
            return f"HTTP {e.response.status_code}: {e.response.text[:500]}"
        except Exception as e:
            logger.error({"event": "API_CALLER_ERROR", "error": str(e)})
            return f"API call failed: {str(e)}"
