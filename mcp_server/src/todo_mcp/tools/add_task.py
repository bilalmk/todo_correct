"""
todo_add_task MCP tool implementation.

Creates a new task for the specified user with title and optional description.
"""

from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from todo_mcp.models.inputs import AddTaskInput
from todo_mcp.utils.logging import log_tool_invocation
from todo_mcp.utils.errors import database_error
from todo_mcp.utils.responses import format_task_result
from todo_mcp.database import get_db_session
from todo_mcp.tools_registry import register_tool

# Import Task model from backend via shared module
from todo_mcp.shared_models import Task


async def add_task_handler(arguments: dict) -> str:
    """Handler function that accepts raw arguments dict."""
    # Validate and parse arguments using Pydantic
    params = AddTaskInput(**arguments)
    return await add_task(params)


async def add_task(params: AddTaskInput) -> str:
    """
    Create a new task for the user with optional advanced fields.

    This tool allows AI chatbot users to create tasks via natural language without requiring
    API syntax knowledge. The task is immediately persisted to the database.

    Supports advanced features (Phase V):
    - Priority levels (low, medium, high)
    - Due dates with natural language parsing
    - Reminder notifications
    - Recurring tasks (daily, weekly, monthly, custom)

    Args:
        params: AddTaskInput containing:
            - user_id (UUID): User identifier
            - title (str, 1-255 chars): Task title (required)
            - description (str, max 10k chars): Task details (optional)
            - priority (str): 'low', 'medium', or 'high' (optional)
            - due_date (datetime): Task deadline in ISO 8601 format (optional)
            - reminder_at (datetime): Reminder time in ISO 8601 format (optional)
            - recurrence_pattern (str): 'daily', 'weekly', 'monthly', 'custom' (optional)
            - recurrence_config (dict): iCalendar RRULE for custom recurrence (optional)

    Returns:
        JSON string with task_id, status="created", title, and all set fields

    Examples:
        User says: "Add a task to buy groceries"
        AI calls: todo_add_task(user_id="550e8400...", title="Buy groceries")
        Returns: {"task_id": 42, "status": "created", "title": "Buy groceries"}

        User says: "Remind me to finish my FastAPI project by January 31st, it's urgent"
        AI calls: todo_add_task(
            user_id="550e8400...",
            title="Finish FastAPI project",
            due_date="2026-01-31T23:59:59Z",
            priority="high"
        )
        Returns: {"task_id": 43, "status": "created", "title": "Finish FastAPI project", "due_date": "2026-01-31T23:59:59Z", "priority": "high"}

        User says: "Weekly team meeting every Monday at 10am"
        AI calls: todo_add_task(
            user_id="550e8400...",
            title="Weekly team meeting",
            recurrence_pattern="weekly"
        )

    Raises:
        ValueError: If validation fails (invalid dates, priority, recurrence pattern, etc.)
        Exception: If database connection fails
    """
    start_time = datetime.now(timezone.utc)
    tool_name = "todo_add_task"
    user_id_str = str(params.user_id)

    try:
        # Create new task instance with advanced fields
        new_task = Task(
            user_id=params.user_id,
            title=params.title,
            description=params.description,
            completed=False,
            created_at=start_time,
            updated_at=start_time,
            deleted_at=None,  # Active task (not soft-deleted)
            # Advanced fields (Phase V - Intermediate/Advanced)
            priority=params.priority,
            due_date=params.due_date,
            reminder_at=params.reminder_at,
            recurrence_pattern=params.recurrence_pattern,
            recurrence_config=params.recurrence_config,
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


# Register the tool handler
register_tool("todo_add_task", add_task_handler)
