"""
todo_update_task MCP tool implementation.

Updates task title and/or description for the specified user.
"""

from datetime import datetime, timezone
from sqlmodel import select

from todo_mcp.app import mcp
from todo_mcp.models.inputs import UpdateTaskInput
from todo_mcp.utils.logging import log_tool_invocation
from todo_mcp.utils.errors import task_not_found_error, database_error
from todo_mcp.utils.responses import format_task_result
from todo_mcp.database import get_db_session

# Import Task model from backend via shared module
from todo_mcp.shared_models import Task


@mcp.tool(name="todo_update_task")
async def update_task(params: UpdateTaskInput) -> str:
    """
    Update task title and/or description.

    This tool allows AI chatbot users to modify existing tasks by saying
    "Change the title of my dentist task to 'Call dentist at 3pm'" and have changes persisted.

    Args:
        params: UpdateTaskInput containing user_id (UUID), task_id (positive integer),
                and at least one of title (1-255 chars) or description (max 10k chars)

    Returns:
        JSON string with task_id, status="updated", and title

    Example:
        User says: "Update my grocery task to include vegetables"
        AI calls: todo_update_task(user_id="550e8400...", task_id=42, description="Milk, eggs, bread, vegetables")
        Returns: {"task_id": 42, "status": "updated", "title": "Buy groceries"}

    Raises:
        ValueError: If both title and description are None (validated by Pydantic)
        Exception: If database connection fails
    """
    start_time = datetime.now(timezone.utc)
    tool_name = "todo_update_task"
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

            # Update only non-None fields (partial update)
            if params.title is not None:
                task.title = params.title
            if params.description is not None:
                task.description = params.description

            task.updated_at = datetime.now(timezone.utc)
            session.add(task)
            await session.commit()
            await session.refresh(task)

        # Format success response
        response = format_task_result(task, "updated")

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
