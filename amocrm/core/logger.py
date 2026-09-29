"""Logger utilities with JSON format."""

import logging
import sys
import json
from datetime import datetime
from pathlib import Path

from core.config import get_settings


class JSONFormatter(logging.Formatter):
    """JSON formatter for Kibana parsing."""

    def format(self, record: logging.LogRecord) -> str:
        log_data = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_data)


class PlainFormatter(logging.Formatter):
    """Plain formatter for console."""

    def __init__(self):
        super().__init__(fmt="%(asctime)s | %(level)-8s | %(name)s | %(message)s", datefmt="%H:%M:%S")


def get_logger(name: str) -> logging.Logger:
    """Get configured logger."""
    settings = get_settings()
    logger = logging.getLogger(name)

    if not logger.handlers:
        logger.setLevel(getattr(logging, settings.log_level))

        # Console handler
        console = logging.StreamHandler(sys.stdout)
        console.setFormatter(PlainFormatter())
        logger.addHandler(console)

        # File handler (optional)
        try:
            log_dir = Path("logs")
            log_dir.mkdir(exist_ok=True)
            file_handler = logging.FileHandler(log_dir / "test.log")
            file_handler.setFormatter(JSONFormatter())
            logger.addHandler(file_handler)
        except Exception:
            pass

    logger.propagate = False
    return logger
