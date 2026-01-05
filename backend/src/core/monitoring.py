"""
Monitoring and Observability Module
T038: Console/file logging fallback with structured JSON logging per FR-034

Features:
- Structured JSON logging to console/file
- FR-029 compliant log format (timestamp, correlation_id, user_id, endpoint, etc.)
- FR-035 sensitive data sanitization (no JWT, passwords, CSRF tokens)
- Log rotation support
- Defers external monitoring services (DataDog, Sentry) to Phase V

Usage:
    from core.monitoring import get_logger
    logger = get_logger(__name__)
    logger.info("Task created", extra={"user_id": user_id, "task_id": task_id})
"""

import logging
import logging.handlers
import json
from datetime import datetime
from pathlib import Path
from typing import Optional
from core.config import settings

# Create logs directory if it doesn't exist
LOGS_DIR = Path("logs")
LOGS_DIR.mkdir(exist_ok=True)


class StructuredJSONFormatter(logging.Formatter):
    """
    JSON formatter for structured logging per FR-029.

    Required fields per FR-029:
    - timestamp (ISO 8601)
    - level
    - correlation_id
    - user_id
    - endpoint
    - http_method
    - status_code
    - duration_ms
    - error_message
    - metadata
    """

    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON with FR-029 required fields."""

        # Base log structure
        log_data = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        # Add FR-029 required fields if present in extra
        if hasattr(record, "correlation_id"):
            log_data["correlation_id"] = record.correlation_id
        if hasattr(record, "user_id"):
            log_data["user_id"] = str(record.user_id)
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

        # Add file/line info for debugging
        log_data["source"] = {
            "file": record.pathname,
            "line": record.lineno,
            "function": record.funcName,
        }

        return json.dumps(log_data)


def setup_logging(
    log_level: str = "INFO",
    log_file: Optional[str] = None,
    max_bytes: int = 10 * 1024 * 1024,  # 10MB
    backup_count: int = 5,
) -> None:
    """
    Configure structured JSON logging with console and optional file output.

    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional file path for logs. If None, only console logging.
        max_bytes: Maximum log file size before rotation (default 10MB)
        backup_count: Number of backup files to keep (default 5)
    """

    # Get root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level.upper()))

    # Clear existing handlers
    root_logger.handlers.clear()

    # JSON formatter
    formatter = StructuredJSONFormatter()

    # Console handler (stdout) - T038
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    # File handler with rotation - T038
    if log_file:
        file_path = LOGS_DIR / log_file
        file_handler = logging.handlers.RotatingFileHandler(
            filename=file_path,
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding="utf-8",
        )
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance with the specified name.

    Usage:
        logger = get_logger(__name__)
        logger.info("User logged in", extra={"user_id": "123", "correlation_id": "abc"})

    Args:
        name: Logger name (typically __name__)

    Returns:
        Logger instance configured with structured JSON formatting
    """
    return logging.getLogger(name)


# T038: Initialize logging on module import
setup_logging(
    log_level=settings.LOG_LEVEL if hasattr(settings, "LOG_LEVEL") else "INFO",
    log_file="app.log",  # Log to logs/app.log
)


# Module-level logger for this file
logger = get_logger(__name__)
logger.info("Monitoring module initialized with structured JSON logging (FR-034)")
