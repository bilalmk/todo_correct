"""
todo_delete_task MCP tool implementation.

Soft deletes a task for the specified user (sets deleted_at timestamp).
"""

from datetime import datetime, timezone
from sqlmodel import select

from todo_mcp.models.inputs import DeleteTaskInput
from todo_mcp.utils.logging import log_tool_invocation
from todo_mcp.utils.errors import task_not_found_error, database_error
from todo_mcp.utils.responses import format_task_result
from todo_mcp.database import get_db_session
from todo_mcp.tools_registry import register_tool

# Import Task model from backend via shared module
from todo_mcp.shared_models import Task


async def delete_task_handler(arguments: dict) -> str:
    """Handler function that accepts raw arguments dict."""
    params = DeleteTaskInput(**arguments)
    return await delete_task(params)


async def delete_task(params: DeleteTaskInput) -> str:
    """
    Soft delete a task (set deleted_at timestamp).

    This tool allows AI chatbot users to remove tasks by saying "Delete the buy groceries task"
    and have it soft-deleted from their task list. The task is not hard deleted from the database
    (data recovery possible).

    Args:
        params: DeleteTaskInput containing user_id (UUID) and task_id (positive integer)

    Returns:
        JSON string with task_id, status="deleted", and title

    Example:
        User says: "Delete my dentist task"
        AI calls: todo_delete_task(user_id="550e8400...", task_id=42)
        Returns: {"task_id": 42, "status": "deleted", "title": "Call dentist"}

    Raises:
        Exception: If database connection fails
    """
    start_time = datetime.now(timezone.utc)
    tool_name = "todo_delete_task"
    user_id_str = str(params.user_id)

    try:
        # Fetch task with user isolation and soft delete filter
        async with get_db_session() as session:
            result = await session.execute(
                select(Task).where(
                    Task.id == params.task_id,
                    Task.user_id == params.user_id,
                    Task.deleted_at.is_(None),  # Exclude already-deleted tasks
                )
            )
            task = result.scalar_one_or_none()

            if not task:
                # Task not found, belongs to different user, or already deleted
                duration_ms = (datetime.now(timezone.utc) - start_time).total_seconds() * 1000
                log_tool_invocation(
                    tool_name=tool_name,
                    user_id=user_id_str,
                    parameters=params.model_dump(mode='json'),
                    error=f"Task {params.task_id} not found",
                    duration_ms=duration_ms,
                )
                return task_not_found_error(params.task_id, user_id_str)

            # Soft delete: set deleted_at timestamp (NOT hard delete)
            task.deleted_at = datetime.now(timezone.utc)
            task.updated_at = datetime.now(timezone.utc)
            session.add(task)
            await session.commit()
            await session.refresh(task)

        # Format success response
        response = format_task_result(task, "deleted")

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
register_tool("todo_delete_task", delete_task_handler)
