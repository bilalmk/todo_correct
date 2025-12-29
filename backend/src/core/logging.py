"""Structured JSON logging configuration with request IDs."""
import logging
import sys
import json
from datetime import datetime
from typing import Any, Dict
from contextvars import ContextVar

from .config import settings

# Context variable for request ID
request_id_var: ContextVar[str] = ContextVar("request_id", default="")


class JSONFormatter(logging.Formatter):
    """
    Custom JSON formatter for structured logging.

    Following fastapi-expert patterns for production logging.
    """

    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON."""
        log_data: Dict[str, Any] = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "request_id": request_id_var.get(""),
        }

        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        # Add extra fields from record
        if hasattr(record, "user_id"):
            log_data["user_id"] = record.user_id
        if hasattr(record, "email"):
            log_data["email"] = record.email
        if hasattr(record, "endpoint"):
            log_data["endpoint"] = record.endpoint
        if hasattr(record, "status_code"):
            log_data["status_code"] = record.status_code
        if hasattr(record, "duration_ms"):
            log_data["duration_ms"] = record.duration_ms

        return json.dumps(log_data)


def setup_logging() -> None:
    """
    Configure structured JSON logging for the application.

    Following fastapi-expert best practices:
    - Structured JSON format for parsing
    - Request ID tracking
    - Configurable log level
    - Production-ready output
    """
    # Get root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, settings.LOG_LEVEL))

    # Remove existing handlers
    root_logger.handlers.clear()

    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, settings.LOG_LEVEL))

    # Use JSON formatter in production, simple format in development
    if settings.is_production:
        console_handler.setFormatter(JSONFormatter())
    else:
        console_handler.setFormatter(
            logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - [%(request_id)s] - %(message)s",
                defaults={"request_id": ""},
            )
        )

    root_logger.addHandler(console_handler)

    # Set log levels for third-party libraries
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.error").setLevel(logging.INFO)


def set_request_id(request_id: str) -> None:
    """Set request ID in context for current request."""
    request_id_var.set(request_id)


def get_request_id() -> str:
    """Get request ID from context."""
    return request_id_var.get("")
