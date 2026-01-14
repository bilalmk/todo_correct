"""
Tool registry for Official MCP SDK.

This module provides a centralized registry for all MCP tools and handlers.
"""

from typing import Dict, Callable, Any
from mcp.types import Tool, TextContent
import json

# Tool registry: maps tool names to their handler functions
_TOOL_HANDLERS: Dict[str, Callable] = {}


def register_tool(name: str, handler: Callable) -> None:
    """Register a tool handler."""
    _TOOL_HANDLERS[name] = handler


def get_tool_handler(name: str) -> Callable:
    """Get a tool handler by name."""
    return _TOOL_HANDLERS.get(name)


def get_all_tool_names() -> list[str]:
    """Get list of all registered tool names."""
    return list(_TOOL_HANDLERS.keys())


# Tool definitions for list_tools response
TOOL_DEFINITIONS = [
    Tool(
        name="todo_add_task",
        description="Create a new task for the user with advanced natural language parsing. Extract priority from keywords (urgent/important=high, low priority=low). Parse due dates from natural language (tomorrow, next week, January 31st, etc.) and convert to ISO 8601 datetime UTC. Detect recurrence patterns (daily, weekly, monthly). Extract clean title without temporal/priority keywords. Supports priorities, due dates, reminders, and recurring tasks.",
        inputSchema={
            "type": "object",
            "properties": {
                "user_id": {
                    "type": "string",
                    "format": "uuid",
                    "description": "User UUID from JWT token (automatically injected, DO NOT provide)"
                },
                "title": {
                    "type": "string",
                    "minLength": 1,
                    "maxLength": 255,
                    "description": "Task title (1-255 characters). Extract clean title without temporal keywords (tomorrow, by Friday) or priority keywords (urgent)."
                },
                "description": {
                    "type": "string",
                    "maxLength": 10000,
                    "description": "Optional task description (max 10k chars). Add extra details mentioned by user beyond the title."
                },
                "priority": {
                    "type": "string",
                    "enum": ["low", "medium", "high"],
                    "description": "Task priority. Extract from keywords: 'urgent'/'important'/'critical'/'asap' → high, 'low priority'/'not urgent' → low, default → medium"
                },
                "due_date": {
                    "type": "string",
                    "format": "date-time",
                    "description": "Task deadline as ISO 8601 datetime UTC (e.g., '2026-01-31T23:59:59Z'). Parse from natural language: 'tomorrow', 'next week', 'January 31st', 'by Friday', 'in 3 days'. Today is 2026-01-14. Use 23:59:59 for end-of-day unless specific time mentioned."
                },
                "reminder_at": {
                    "type": "string",
                    "format": "date-time",
                    "description": "Reminder time as ISO 8601 datetime UTC. Parse from phrases: 'remind me 1 hour before' (due_date - 1h), 'notify at 9am', 'reminder the day before' (due_date - 24h)."
                },
                "recurrence_pattern": {
                    "type": "string",
                    "enum": ["daily", "weekly", "monthly", "custom"],
                    "description": "Recurrence type. Extract from keywords: 'every day'/'daily' → daily, 'every week'/'weekly'/'every Monday' → weekly, 'every month'/'monthly' → monthly"
                },
                "recurrence_config": {
                    "type": "object",
                    "description": "Advanced recurrence config in iCalendar RRULE format. Only for recurrence_pattern='custom' with complex patterns like 'every Monday, Wednesday, Friday'.",
                    "properties": {
                        "FREQ": {
                            "type": "string",
                            "enum": ["DAILY", "WEEKLY", "MONTHLY", "YEARLY"]
                        },
                        "BYDAY": {
                            "type": "array",
                            "items": {"type": "string"}
                        },
                        "INTERVAL": {
                            "type": "integer"
                        }
                    }
                }
            },
            "required": ["user_id", "title"]
        }
    ),
    Tool(
        name="todo_list_tasks",
        description="List tasks filtered by status. Returns all tasks for the authenticated user, optionally filtered by completion status.",
        inputSchema={
            "type": "object",
            "properties": {
                "user_id": {
                    "type": "string",
                    "format": "uuid",
                    "description": "User UUID from JWT token"
                },
                "status": {
                    "type": "string",
                    "enum": ["pending", "completed", "all"],
                    "description": "Filter by task status (pending/completed/all)"
                }
            },
            "required": ["user_id"]
        }
    ),
    Tool(
        name="todo_complete_task",
        description="Mark a task as completed. Sets the completed flag to true and updates the updated_at timestamp.",
        inputSchema={
            "type": "object",
            "properties": {
                "user_id": {
                    "type": "string",
                    "format": "uuid",
                    "description": "User UUID from JWT token"
                },
                "task_id": {
                    "type": "integer",
                    "description": "Task ID to mark as completed"
                }
            },
            "required": ["user_id", "task_id"]
        }
    ),
    Tool(
        name="todo_update_task",
        description="Update any task field including title, description, priority, due dates, reminders, and recurrence. Parse natural language changes like 'change deadline to tomorrow', 'make it urgent', 'set to weekly'. At least one field (besides task_id) must be provided.",
        inputSchema={
            "type": "object",
            "properties": {
                "user_id": {
                    "type": "string",
                    "format": "uuid",
                    "description": "User UUID from JWT token (automatically injected, DO NOT provide)"
                },
                "task_id": {
                    "type": "integer",
                    "description": "Task ID to update (must be positive integer)"
                },
                "title": {
                    "type": "string",
                    "minLength": 1,
                    "maxLength": 255,
                    "description": "New task title (1-255 characters). Extract clean title without temporal/priority keywords."
                },
                "description": {
                    "type": "string",
                    "maxLength": 10000,
                    "description": "New task description (max 10k chars). Set to update or clear description."
                },
                "priority": {
                    "type": "string",
                    "enum": ["low", "medium", "high"],
                    "description": "Update priority. Extract from keywords: 'urgent'/'important'/'make it high priority' → high, 'low priority'/'not urgent' → low, 'normal' → medium"
                },
                "due_date": {
                    "type": "string",
                    "format": "date-time",
                    "description": "Update deadline as ISO 8601 datetime UTC (e.g., '2026-02-15T23:59:59Z'). Parse from natural language: 'change to tomorrow', 'extend to next week', 'February 15th'. Today is 2026-01-14."
                },
                "reminder_at": {
                    "type": "string",
                    "format": "date-time",
                    "description": "Update reminder time as ISO 8601 datetime UTC. Parse from phrases like 'remind me 1 hour before', 'set reminder to 9am'."
                },
                "recurrence_pattern": {
                    "type": "string",
                    "enum": ["daily", "weekly", "monthly", "custom"],
                    "description": "Update recurrence type. Extract from keywords: 'make it daily', 'change to weekly', 'set monthly', 'make it repeat every week'."
                },
                "recurrence_config": {
                    "type": "object",
                    "description": "Update recurrence config in iCalendar RRULE format. Only for recurrence_pattern='custom'.",
                    "properties": {
                        "FREQ": {
                            "type": "string",
                            "enum": ["DAILY", "WEEKLY", "MONTHLY", "YEARLY"]
                        },
                        "BYDAY": {
                            "type": "array",
                            "items": {"type": "string"}
                        },
                        "INTERVAL": {
                            "type": "integer"
                        }
                    }
                }
            },
            "required": ["user_id", "task_id"]
        }
    ),
    Tool(
        name="todo_delete_task",
        description="Delete a task (soft delete). Sets the deleted_at timestamp to mark the task as deleted.",
        inputSchema={
            "type": "object",
            "properties": {
                "user_id": {
                    "type": "string",
                    "format": "uuid",
                    "description": "User UUID from JWT token"
                },
                "task_id": {
                    "type": "integer",
                    "description": "Task ID to delete"
                }
            },
            "required": ["user_id", "task_id"]
        }
    ),
]


async def call_tool_handler(name: str, arguments: dict) -> list[TextContent]:
    """
    Call a registered tool handler with arguments.

    Args:
        name: Tool name
        arguments: Tool arguments as dict

    Returns:
        List of TextContent with tool result
    """
    handler = get_tool_handler(name)
    if not handler:
        raise ValueError(f"Unknown tool: {name}")

    # Call the tool handler
    result = await handler(arguments)

    # Return as TextContent
    return [TextContent(type="text", text=result)]
