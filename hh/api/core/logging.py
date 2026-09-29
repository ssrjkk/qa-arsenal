import logging
import json
import sys
from typing import Any, Dict
from datetime import datetime


class StructuredFormatter(logging.Formatter):
    """JSON formatter for structured logging"""
    
    def format(self, record: logging.LogRecord) -> str:
        log_record: Dict[str, Any] = {
            "timestamp": datetime.utcfromtimestamp(record.created).isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        
        if hasattr(record, "request_id"):
            log_record["request_id"] = record.request_id
        
        if hasattr(record, "test_name"):
            log_record["test_name"] = record.test_name
        
        if hasattr(record, "endpoint"):
            log_record["endpoint"] = record.endpoint
        
        if record.exc_info:
            log_record["exception"] = self.formatException(record.exc_info)
        
        return json.dumps(log_record, ensure_ascii=False)


def setup_structured_logging(
    level: str = "INFO",
    output: str = "stdout"
) -> None:
    """Setup structured logging with JSON output"""
    
    handler: logging.Handler
    if output == "stdout":
        handler = logging.StreamHandler(sys.stdout)
    elif output == "stderr":
        handler = logging.StreamHandler(sys.stderr)
    else:
        handler = logging.FileHandler(output)
    
    handler.setFormatter(StructuredFormatter())
    
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, level.upper()))
    root_logger.addHandler(handler)
    
    # Remove existing handlers to avoid duplicates
    for h in root_logger.handlers[:-1]:
        root_logger.removeHandler(h)


def mask_sensitive_data(message: str) -> str:
    """Mask sensitive data in log messages"""
    import re
    
    # Mask Bearer tokens
    message = re.sub(
        r'Bearer\s+[a-zA-Z0-9\-_\.]+',
        'Bearer ***',
        message
    )
    
    # Mask API keys
    message = re.sub(
        r'api[_-]?key[\'"]?\s*[:=]\s*[\'"]?[a-zA-Z0-9]+',
        'api_key=***',
        message,
        flags=re.IGNORECASE
    )
    
    return message
