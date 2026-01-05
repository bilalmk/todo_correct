"""Structured JSON logging configuration with request IDs."""
import logging
import sys
import json
from datetime import datetime
from typing import Any, Dict
from contextvars import ContextVar

from .config import settings

# Context variable for correlation ID (replaces request_id for Better Auth integration)
correlation_id_var: ContextVar[str] = ContextVar("correlation_id", default="")


class JSONFormatter(logging.Formatter):
    """
    Custom JSON formatter for structured logging.

    Following fastapi-expert patterns for production logging.
    """

    def format(self, record: logging.LogRecord) -> str:
        """
        Format log record as JSON with all required fields per FR-029.

        Required fields: timestamp, level, correlation_id, user_id, endpoint, http_method,
                        status_code, duration_ms, error_message, metadata
        """
        log_data: Dict[str, Any] = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "correlation_id": correlation_id_var.get(""),
            "message": record.getMessage(),
        }

        # Add optional fields from record (FR-029 required fields)
        if hasattr(record, "user_id"):
            log_data["user_id"] = record.user_id
        if hasattr(record, "endpoint"):
            log_data["endpoint"] = record.endpoint
        if hasattr(record, "http_method"):
            log_data["http_method"] = record.http_method
        if hasattr(record, "status_code"):
            log_data["status_code"] = record.status_code
        if hasattr(record, "duration_ms"):
            log_data["duration_ms"] = record.duration_ms
        if hasattr(record, "error_message"):
            log_data["error_message"] = record.error_message
        if hasattr(record, "metadata"):
            log_data["metadata"] = record.metadata

        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

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
                "%(asctime)s - %(name)s - %(levelname)s - [%(correlation_id)s] - %(message)s",
                defaults={"correlation_id": ""},
            )
        )

    root_logger.addHandler(console_handler)

    # Set log levels for third-party libraries
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.error").setLevel(logging.INFO)


def set_correlation_id(correlation_id: str) -> None:
    """
    Set correlation ID in context for current request.

    This enables tracing requests across frontend -> backend -> external services.
    Correlation ID is propagated via X-Correlation-ID header.
    """
    correlation_id_var.set(correlation_id)


def get_correlation_id() -> str:
    """Get correlation ID from context."""
    return correlation_id_var.get("")
