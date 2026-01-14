"""
todo_update_task MCP tool implementation.

Updates task title and/or description for the specified user.
"""

from datetime import datetime, timezone
from sqlmodel import select

from todo_mcp.models.inputs import UpdateTaskInput
from todo_mcp.utils.logging import log_tool_invocation
from todo_mcp.utils.errors import task_not_found_error, database_error
from todo_mcp.utils.responses import format_task_result
from todo_mcp.database import get_db_session
from todo_mcp.tools_registry import register_tool

# Import Task model from backend via shared module
from todo_mcp.shared_models import Task


async def update_task_handler(arguments: dict) -> str:
    """Handler function that accepts raw arguments dict."""
    params = UpdateTaskInput(**arguments)
    return await update_task(params)


async def update_task(params: UpdateTaskInput) -> str:
    """
    Update task fields including title, description, priority, due dates, reminders, and recurrence.

    This tool allows AI chatbot users to modify existing tasks via natural language,
    including advanced fields like priorities, due dates, and recurring patterns.

    Args:
        params: UpdateTaskInput containing:
            - user_id (UUID): User identifier
            - task_id (int): Task ID to update
            - title (str, optional): New title (1-255 chars)
            - description (str, optional): New description (max 10k chars)
            - priority (str, optional): New priority ('low', 'medium', 'high')
            - due_date (datetime, optional): New due date (ISO 8601 format)
            - reminder_at (datetime, optional): New reminder time (ISO 8601 format)
            - recurrence_pattern (str, optional): New recurrence ('daily', 'weekly', 'monthly', 'custom')
            - recurrence_config (dict, optional): New recurrence config (iCalendar RRULE format)

    Returns:
        JSON string with task_id, status="updated", and all updated fields

    Examples:
        User says: "Update my grocery task to include vegetables"
        AI calls: todo_update_task(user_id="550e8400...", task_id=42, description="Milk, eggs, bread, vegetables")
        Returns: {"task_id": 42, "status": "updated", "title": "Buy groceries"}

        User says: "Change the FastAPI project deadline to February 15th and mark it as urgent"
        AI calls: todo_update_task(
            user_id="550e8400...",
            task_id=43,
            due_date="2026-02-15T23:59:59Z",
            priority="high"
        )
        Returns: {"task_id": 43, "status": "updated", "due_date": "2026-02-15T23:59:59Z", "priority": "high"}

    Raises:
        ValueError: If no update fields provided (validated by Pydantic)
        Exception: If database connection fails or task not found
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
            if params.priority is not None:
                task.priority = params.priority
            if params.due_date is not None:
                task.due_date = params.due_date
            if params.reminder_at is not None:
                task.reminder_at = params.reminder_at
            if params.recurrence_pattern is not None:
                task.recurrence_pattern = params.recurrence_pattern
            if params.recurrence_config is not None:
                task.recurrence_config = params.recurrence_config

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


# Register the tool handler
register_tool("todo_update_task", update_task_handler)
