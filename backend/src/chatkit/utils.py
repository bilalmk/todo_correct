"""Utility functions for ChatKit backend: retry logic, correlation IDs, error handling.

This module provides:
- Exponential backoff retry for OpenAI Agents SDK (3 attempts, 2s/4s/8s)
- Database transaction retry (2 attempts, 1s delay)
- Correlation ID generation and propagation (thread-safe via ContextVar)
- RequestContext dataclass for tracking user identity and logging

Feature: 008-chatkit-server-backend
Phase: II (Foundational) - Utility Functions
Task Reference: T011 (retry logic), T017-T018 (correlation IDs, database retry)
"""

import asyncio
import logging
from dataclasses import dataclass
from typing import TypeVar, Callable, Awaitable
from contextvars import ContextVar
from uuid import UUID, uuid4

from sqlalchemy.exc import OperationalError, DBAPIError

logger = logging.getLogger(__name__)

# Type variable for generic retry functions
T = TypeVar('T')

# Context variable for correlation ID (thread-safe propagation)
correlation_id_var: ContextVar[str] = ContextVar("correlation_id", default=None)


@dataclass
class RequestContext:
    """HTTP request tracking context for logging and tracing.

    Attributes:
        user_id: UUID from JWT token via get_current_user dependency
        correlation_id: Generated per request for log tracing

    Usage:
        context = RequestContext(user_id=user.uuid)
        logger.info("Message received", extra={"correlation_id": context.correlation_id})
    """
    user_id: UUID
    correlation_id: str = None

    def __post_init__(self):
        """Auto-generate correlation ID if not provided."""
        if self.correlation_id is None:
            self.correlation_id = get_correlation_id()


def get_correlation_id() -> str:
    """Get or create correlation ID for current request.

    Returns:
        Correlation ID string (UUID format)

    Thread Safety:
        Uses ContextVar for async-safe propagation across await boundaries
    """
    cid = correlation_id_var.get()
    if cid is None:
        cid = str(uuid4())
        correlation_id_var.set(cid)
    return cid


async def retry_with_exponential_backoff(
    func: Callable[[], Awaitable[T]],
    max_retries: int = 3,
    backoff_delays: list[int] = None,
    correlation_id: str = None,
) -> T:
    """
    Retry async function with exponential backoff (for OpenAI Agents SDK calls).

    Implements FR-018 from spec.md: OpenAI failures retry 3x with 2s/4s/8s backoff.

    Args:
        func: Async function to retry
        max_retries: Maximum retry attempts (default 3)
        backoff_delays: Delays in seconds for each retry (default [2, 4, 8])
        correlation_id: For structured logging

    Returns:
        Result from func() on success

    Raises:
        Exception: Original exception if all retries exhausted

    Example:
        result = await retry_with_exponential_backoff(
            lambda: agent.run(message),
            correlation_id=context.correlation_id
        )
    """
    if backoff_delays is None:
        backoff_delays = [2, 4, 8]

    for attempt in range(max_retries):
        try:
            return await func()
        except Exception as e:
            if attempt < max_retries - 1:
                delay = backoff_delays[attempt]
                logger.warning(
                    f"Operation failed (attempt {attempt+1}/{max_retries}), retrying in {delay}s",
                    extra={
                        "correlation_id": correlation_id,
                        "error": str(e),
                        "error_type": type(e).__name__,
                        "retry_attempt": attempt + 1,
                    }
                )
                await asyncio.sleep(delay)
            else:
                logger.error(
                    f"Operation failed after {max_retries} attempts",
                    extra={
                        "correlation_id": correlation_id,
                        "error": str(e),
                        "error_type": type(e).__name__,
                    }
                )
                raise


async def retry_database_operation(
    func: Callable[[], Awaitable[T]],
    max_retries: int = 2,
    delay: int = 1,
    correlation_id: str = None,
) -> T:
    """
    Retry database operation with fixed delay (for transient connection errors).

    Implements FR-019 from spec.md: Database failures retry 2x with 1s delay.

    Args:
        func: Async database operation to retry
        max_retries: Maximum retry attempts (default 2)
        delay: Fixed delay in seconds between retries (default 1)
        correlation_id: For structured logging

    Returns:
        Result from func() on success

    Raises:
        OperationalError or DBAPIError: If all retries exhausted

    Catches:
        - OperationalError: Connection errors, timeouts
        - DBAPIError: Database-specific errors (deadlocks, etc.)

    Example:
        message = await retry_database_operation(
            lambda: session.execute(insert_stmt),
            correlation_id=context.correlation_id
        )
    """
    for attempt in range(max_retries):
        try:
            return await func()
        except (OperationalError, DBAPIError) as e:
            if attempt < max_retries - 1:
                logger.warning(
                    f"Database operation failed (attempt {attempt+1}/{max_retries}), retrying in {delay}s",
                    extra={
                        "correlation_id": correlation_id,
                        "error": str(e),
                        "error_type": type(e).__name__,
                        "retry_attempt": attempt + 1,
                    }
                )
                await asyncio.sleep(delay)
            else:
                logger.error(
                    f"Database operation failed after {max_retries} attempts",
                    extra={
                        "correlation_id": correlation_id,
                        "error": str(e),
                        "error_type": type(e).__name__,
                    }
                )
                raise
