from groq import Groq
from app.core.config import settings
from app.core.logger import logger
from app.observability.metrics import METRICS

_client = Groq(api_key=settings.GROQ_API_KEY)

def ask_llm(prompt: str, retries: int = 3) -> str:

    logger.info({"event": "LLM_CALL_START"})

    for attempt in range(retries):
        try:
            res = _client.chat.completions.create(
                model=settings.MODEL_NAME,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2,
            )
            logger.info({"event": "LLM_CALL_DONE"})
            return res.choices[0].message.content

        except Exception as e:
            err = str(e)
            if ("429" in err or "rate" in err.lower()) and attempt < retries - 1:
                import time
                wait = 10 * (attempt + 1)
                logger.warning({"event": "LLM_RATE_LIMITED", "attempt": attempt + 1, "wait_s": wait})
                time.sleep(wait)
                continue

            METRICS["llm_errors_total"] += 1
            logger.error({"event": "LLM_ERROR", "error": err})
            return "LLM_ERROR"
