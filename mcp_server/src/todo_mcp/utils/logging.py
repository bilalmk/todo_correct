"""
Structured logging utilities for Todo MCP Server.

Provides JSON structured logging with tool_name, user_id, parameters, result/error, and duration.
"""

import json
import logging
import time
from typing import Any, Dict, Optional
from contextlib import asynccontextmanager

# Configure logger
logger = logging.getLogger("todo_mcp")


def log_tool_invocation(
    tool_name: str,
    user_id: str,
    parameters: Dict[str, Any],
    result: Optional[str] = None,
    error: Optional[str] = None,
    duration_ms: Optional[float] = None,
) -> None:
    """
    Log tool invocation with structured JSON.

    Args:
        tool_name: Name of the MCP tool (e.g., "todo_add_task")
        user_id: User ID performing the action
        parameters: Tool input parameters (dict)
        result: Tool execution result (optional)
        error: Error message if tool failed (optional)
        duration_ms: Execution duration in milliseconds (optional)

    Example:
        log_tool_invocation(
            tool_name="todo_add_task",
            user_id="550e8400-e29b-41d4-a716-446655440000",
            parameters={"title": "Buy groceries", "description": "Milk, eggs, bread"},
            result='{"task_id": 42, "status": "created", "title": "Buy groceries"}',
            duration_ms=87.3
        )
    """
    log_entry = {
        "tool_name": tool_name,
        "user_id": user_id,
        "parameters": parameters,
        "status": "error" if error else "success",
    }

    if result:
        # Truncate result for log readability (first 200 characters)
        log_entry["result"] = result[:200] if len(result) > 200 else result

    if error:
        log_entry["error"] = error

    if duration_ms is not None:
        log_entry["duration_ms"] = round(duration_ms, 2)

    # Log as JSON string
    logger.info(json.dumps(log_entry))


@asynccontextmanager
async def log_tool_execution(tool_name: str, user_id: str, parameters: Dict[str, Any]):
    """
    Context manager to automatically log tool execution with timing.

    Captures execution duration, success/failure status, and any exceptions.

    Args:
        tool_name: Name of the MCP tool
        user_id: User ID performing the action
        parameters: Tool input parameters (dict)

    Usage:
        async with log_tool_execution("todo_add_task", str(params.user_id), params.model_dump()):
            # Tool implementation
            result = await some_database_operation()
            return result

    Example Log Output:
        {
          "tool_name": "todo_add_task",
          "user_id": "550e8400-e29b-41d4-a716-446655440000",
          "parameters": {"title": "Buy groceries"},
          "status": "success",
          "duration_ms": 87.3
        }
    """
    start_time = time.time()
    error = None

    try:
        yield
    except Exception as e:
        error = str(e)
        raise
    finally:
        duration_ms = (time.time() - start_time) * 1000
        log_tool_invocation(
            tool_name=tool_name,
            user_id=user_id,
            parameters=parameters,
            error=error,
            duration_ms=duration_ms,
        )
