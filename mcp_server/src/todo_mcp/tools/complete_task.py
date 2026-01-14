"""
todo_complete_task MCP tool implementation.

Marks a task as completed for the specified user (idempotent operation).
"""

from datetime import datetime, timezone
from sqlmodel import select

from todo_mcp.models.inputs import CompleteTaskInput
from todo_mcp.utils.logging import log_tool_invocation
from todo_mcp.utils.errors import task_not_found_error, database_error
from todo_mcp.utils.responses import format_task_result
from todo_mcp.database import get_db_session
from todo_mcp.tools_registry import register_tool

# Import Task model from backend via shared module
from todo_mcp.shared_models import Task


async def complete_task_handler(arguments: dict) -> str:
    """Handler function that accepts raw arguments dict."""
    params = CompleteTaskInput(**arguments)
    return await complete_task(params)


async def complete_task(params: CompleteTaskInput) -> str:
    """
    Mark a task as completed.

    This tool allows AI chatbot users to mark tasks as done by saying
    "Mark 'buy groceries' as complete" and have status updated.

    This is an idempotent operation - completing an already-completed task succeeds
    without error, updates updated_at timestamp, and returns success (FR-024).

    Args:
        params: CompleteTaskInput containing user_id (UUID) and task_id (positive integer)

    Returns:
        JSON string with task_id, status="completed", and title

    Example:
        User says: "Mark my dentist task as complete"
        AI calls: todo_complete_task(user_id="550e8400...", task_id=42)
        Returns: {"task_id": 42, "status": "completed", "title": "Call dentist"}

    Raises:
        Exception: If database connection fails
    """
    start_time = datetime.now(timezone.utc)
    tool_name = "todo_complete_task"
    user_id_str = str(params.user_id)

    try:
        # Fetch task with user isolation and soft delete filter
        async with get_db_session() as session:
            result = await session.execute(
                select(Task).where(
                    Task.id == params.task_id,
                    Task.user_id == params.user_id,
                    Task.deleted_at.is_(None),  # Exclude soft-deleted tasks
                )
            )
            task = result.scalar_one_or_none()

            if not task:
                # Task not found or belongs to different user
                duration_ms = (datetime.now(timezone.utc) - start_time).total_seconds() * 1000
                log_tool_invocation(
                    tool_name=tool_name,
                    user_id=user_id_str,
                    parameters=params.model_dump(mode='json'),
                    error=f"Task {params.task_id} not found",
                    duration_ms=duration_ms,
                )
                return task_not_found_error(params.task_id, user_id_str)

            # Idempotent: if already completed, just update updated_at and return success
            task.completed = True  # Set to True (redundant if already True, but explicit)
            task.updated_at = datetime.now(timezone.utc)
            session.add(task)
            await session.commit()
            await session.refresh(task)

        # Format success response
        response = format_task_result(task, "completed")

        # Log successful invocation
        duration_ms = (datetime.now(timezone.utc) - start_time).total_seconds() * 1000
        log_tool_invocation(
            tool_name=tool_name,
            user_id=user_id_str,
            parameters=params.model_dump(mode='json'),
            result=response,
            duration_ms=duration_ms,
        )

        return response

    except Exception as e:
        # Database connection error or other unexpected errors
        error_msg = f"Database error: {str(e)}"
        duration_ms = (datetime.now(timezone.utc) - start_time).total_seconds() * 1000
        log_tool_invocation(
            tool_name=tool_name,
            user_id=user_id_str,
            parameters=params.model_dump(mode='json'),
            error=error_msg,
            duration_ms=duration_ms,
        )
        return database_error()


# Register the tool handler
register_tool("todo_complete_task", complete_task_handler)
