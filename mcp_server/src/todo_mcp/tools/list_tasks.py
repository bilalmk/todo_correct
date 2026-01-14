"""
todo_list_tasks MCP tool implementation.

Retrieves user's tasks with optional status filter (all/pending/completed).
"""

from datetime import datetime, timezone
from sqlmodel import select

from todo_mcp.models.inputs import ListTasksInput
from todo_mcp.utils.logging import log_tool_invocation
from todo_mcp.utils.errors import database_error
from todo_mcp.utils.responses import format_task_list
from todo_mcp.database import get_db_session
from todo_mcp.tools_registry import register_tool

# Import Task model from backend via shared module
from todo_mcp.shared_models import Task


async def list_tasks_handler(arguments: dict) -> str:
    """Handler function that accepts raw arguments dict."""
    params = ListTasksInput(**arguments)
    return await list_tasks(params)


async def list_tasks(params: ListTasksInput) -> str:
    """
    Retrieve user's tasks with optional status filter.

    This tool allows AI chatbot users to see their tasks by asking natural language questions
    like "What tasks do I have?" or "Show me my completed tasks".

    Args:
        params: ListTasksInput containing user_id (UUID) and optional status filter (all/pending/completed)

    Returns:
        JSON string with total count and array of task objects

    Example:
        User says: "Show me my completed tasks"
        AI calls: todo_list_tasks(user_id="550e8400...", status="completed")
        Returns: {
          "total": 2,
          "tasks": [
            {"task_id": 42, "title": "Buy groceries", "completed": true, ...},
            {"task_id": 43, "title": "Call dentist", "completed": true, ...}
          ]
        }

    Raises:
        Exception: If database connection fails
    """
    start_time = datetime.now(timezone.utc)
    tool_name = "todo_list_tasks"
    user_id_str = str(params.user_id)

    try:
        # Build base query with user isolation and soft delete filter
        query = select(Task).where(
            Task.user_id == params.user_id,
            Task.deleted_at.is_(None),  # Exclude soft-deleted tasks (FR-020)
        )

        # Apply status filter
        if params.status == "pending":
            query = query.where(Task.completed == False)
        elif params.status == "completed":
            query = query.where(Task.completed == True)
        # If status=="all", no additional filter needed

        # Execute query
        async with get_db_session() as session:
            result = await session.execute(query)
            tasks = result.scalars().all()

        # Format success response
        response = format_task_list(tasks)

        # Log successful invocation
        duration_ms = (datetime.now(timezone.utc) - start_time).total_seconds() * 1000
        log_tool_invocation(
            tool_name=tool_name,
            user_id=user_id_str,
            parameters=params.model_dump(mode='json'),
            result=f"Retrieved {len(tasks)} tasks",
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
register_tool("todo_list_tasks", list_tasks_handler)
