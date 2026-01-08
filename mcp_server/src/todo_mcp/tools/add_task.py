"""
todo_add_task MCP tool implementation.

Creates a new task for the specified user with title and optional description.
"""

from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from todo_mcp.app import mcp
from todo_mcp.models.inputs import AddTaskInput
from todo_mcp.utils.logging import log_tool_invocation
from todo_mcp.utils.errors import database_error
from todo_mcp.utils.responses import format_task_result
from todo_mcp.database import get_db_session

# Import Task model from backend via shared module
from todo_mcp.shared_models import Task


@mcp.tool(name="todo_add_task")
async def add_task(params: AddTaskInput) -> str:
    """
    Create a new task for the user.

    This tool allows AI chatbot users to create tasks via natural language without requiring
    API syntax knowledge. The task is immediately persisted to the database.

    Args:
        params: AddTaskInput containing user_id (UUID), title (1-255 chars), and optional description (max 10k chars)

    Returns:
        JSON string with task_id, status="created", and title

    Example:
        User says: "Add a task to buy groceries"
        AI calls: todo_add_task(user_id="550e8400...", title="Buy groceries", description=None)
        Returns: {"task_id": 42, "status": "created", "title": "Buy groceries"}

    Raises:
        ValueError: If validation fails (title too long, description too long, invalid user_id)
        Exception: If database connection fails
    """
    start_time = datetime.now(timezone.utc)
    tool_name = "todo_add_task"
    user_id_str = str(params.user_id)

    try:
        # Create new task instance
        new_task = Task(
            user_id=params.user_id,
            title=params.title,
            description=params.description,
            completed=False,
            created_at=start_time,
            updated_at=start_time,
            deleted_at=None,  # Active task (not soft-deleted)
        )

        # Persist to database
        async with get_db_session() as session:
            session.add(new_task)
            await session.commit()
            await session.refresh(new_task)

        # Format success response
        result = format_task_result(new_task, "created")

        # Log successful invocation
        duration_ms = (datetime.now(timezone.utc) - start_time).total_seconds() * 1000
        log_tool_invocation(
            tool_name=tool_name,
            user_id=user_id_str,
            parameters=params.model_dump(mode='json'),  # Use mode='json' to serialize UUIDs properly
            result=result,
            duration_ms=duration_ms,
        )

        return result

    except ValueError as e:
        # Validation error (should be caught by Pydantic, but handle just in case)
        error_msg = str(e)
        duration_ms = (datetime.now(timezone.utc) - start_time).total_seconds() * 1000
        log_tool_invocation(
            tool_name=tool_name,
            user_id=user_id_str,
            parameters=params.model_dump(mode='json'),  # Use mode='json' to serialize UUIDs properly
            error=error_msg,
            duration_ms=duration_ms,
        )
        raise

    except Exception as e:
        # Database connection error or other unexpected errors
        error_msg = f"Database error: {str(e)}"
        duration_ms = (datetime.now(timezone.utc) - start_time).total_seconds() * 1000
        log_tool_invocation(
            tool_name=tool_name,
            user_id=user_id_str,
            parameters=params.model_dump(mode='json'),  # Use mode='json' to serialize UUIDs properly
            error=error_msg,
            duration_ms=duration_ms,
        )
        return database_error()
