"""
Error formatting utilities for Todo MCP Server.

Provides human-readable error messages optimized for AI reformulation into natural language.
"""

import json
from typing import Any, Dict, Optional


def format_error(
    message: str,
    code: str,
    task_id: Optional[int] = None,
    user_id: Optional[str] = None,
) -> str:
    """
    Format error response for AI consumption.

    Returns consistent JSON structure with error details and context.

    Args:
        message: Human-readable error message
        code: Error code (TASK_NOT_FOUND, VALIDATION_ERROR, DATABASE_ERROR, INVALID_USER_ID)
        task_id: Optional task ID context
        user_id: Optional user ID context

    Returns:
        JSON string with error details

    Example:
        format_error(
            message="Task 42 not found for user 550e8400-e29b-41d4-a716-446655440000",
            code="TASK_NOT_FOUND",
            task_id=42,
            user_id="550e8400-e29b-41d4-a716-446655440000"
        )
        # Returns:
        # {
        #   "error": true,
        #   "message": "Task 42 not found for user 550e8400-e29b-41d4-a716-446655440000. Please verify the task ID and try again.",
        #   "code": "TASK_NOT_FOUND",
        #   "task_id": 42,
        #   "user_id": "550e8400-e29b-41d4-a716-446655440000"
        # }
    """
    result: Dict[str, Any] = {
        "error": True,
        "message": message,
        "code": code,
    }

    if task_id is not None:
        result["task_id"] = task_id

    if user_id is not None:
        result["user_id"] = user_id

    return json.dumps(result, indent=2)


def task_not_found_error(task_id: int, user_id: str) -> str:
    """
    Format task not found error.

    Args:
        task_id: Task ID that was not found
        user_id: User ID who attempted to access the task

    Returns:
        JSON error response

    Example:
        task_not_found_error(42, "550e8400-e29b-41d4-a716-446655440000")
    """
    return format_error(
        message=f"Task {task_id} not found for user {user_id}. Please verify the task ID and try again.",
        code="TASK_NOT_FOUND",
        task_id=task_id,
        user_id=user_id,
    )


def validation_error(field: str, message: str) -> str:
    """
    Format validation error.

    Args:
        field: Field name that failed validation
        message: Validation error message

    Returns:
        JSON error response

    Example:
        validation_error("title", "Task title exceeds maximum length of 255 characters")
    """
    return format_error(
        message=f"Validation error: {field} - {message}",
        code="VALIDATION_ERROR",
    )


def database_error() -> str:
    """
    Format database connection error.

    Returns:
        JSON error response

    Example:
        database_error()
    """
    return format_error(
        message="Database connection error: unable to execute operation. Please try again.",
        code="DATABASE_ERROR",
    )


def invalid_user_id_error(user_id: str) -> str:
    """
    Format invalid user_id format error.

    Args:
        user_id: Invalid user_id value

    Returns:
        JSON error response

    Example:
        invalid_user_id_error("user123")
    """
    return format_error(
        message=f"Invalid user_id format: {user_id}. Expected UUID format (8-4-4-4-12 hexadecimal pattern).",
        code="INVALID_USER_ID",
        user_id=user_id,
    )
