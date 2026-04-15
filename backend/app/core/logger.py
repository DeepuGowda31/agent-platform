import logging
import json
import time

class JSONFormatter(logging.Formatter):
    def format(self, record):
        log = {
            "ts": time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime(record.created)),
            "level": record.levelname,
            "msg": record.getMessage(),
            "logger": record.name,
        }
        if record.exc_info:
            log["exc"] = self.formatException(record.exc_info)
        return json.dumps(log)

def _build_logger(name: str) -> logging.Logger:
    log = logging.getLogger(name)
    log.setLevel(logging.INFO)
    log.propagate = False
    if not log.handlers:
        h = logging.StreamHandler()
        h.setFormatter(JSONFormatter())
        log.addHandler(h)
    return log

logger = _build_logger("agent-platform")

# Wire uvicorn loggers to same handler so all logs appear together
for _name in ("uvicorn", "uvicorn.error", "uvicorn.access"):
    _build_logger(_name)