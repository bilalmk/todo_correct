"""
Response formatting utilities for Todo MCP Server.

Provides consistent JSON response schemas for single task operations and task lists.
"""

import json
from typing import Literal, List
from datetime import datetime


def format_task_result(task, status: Literal["created", "completed", "deleted", "updated"]) -> str:
    """
    Format single task operation result with all task fields.

    Args:
        task: Task model instance from database (with id, title, and all advanced fields)
        status: Operation status (created, completed, deleted, updated)

    Returns:
        JSON string with task_id, status, title, and all advanced fields (priority, due_date, etc.)

    Example:
        task = Task(id=42, title="Buy groceries", priority="high", due_date=datetime(...))
        format_task_result(task, "created")
        # Returns:
        # {
        #   "task_id": 42,
        #   "status": "created",
        #   "title": "Buy groceries",
        #   "description": null,
        #   "completed": false,
        #   "priority": "high",
        #   "due_date": "2026-01-20T14:00:00+00:00",
        #   "reminder_at": null,
        #   "recurrence_pattern": null,
        #   "created_at": "2026-01-14T19:40:00+00:00",
        #   "updated_at": "2026-01-14T19:40:00+00:00"
        # }
    """
    result = {
        "task_id": task.id,
        "status": status,
        "title": task.title,
        "description": task.description,
        "completed": task.completed,
        "created_at": task.created_at.isoformat() if isinstance(task.created_at, datetime) else task.created_at,
        "updated_at": task.updated_at.isoformat() if isinstance(task.updated_at, datetime) else task.updated_at,
    }

    # Add advanced fields (Phase V - only include if they have values or always include for consistency)
    # Always include for API consistency (null if not set)
    result["priority"] = task.priority
    result["due_date"] = task.due_date.isoformat() if isinstance(task.due_date, datetime) and task.due_date else task.due_date
    result["reminder_at"] = task.reminder_at.isoformat() if isinstance(task.reminder_at, datetime) and task.reminder_at else task.reminder_at
    result["recurrence_pattern"] = task.recurrence_pattern
    result["recurrence_config"] = task.recurrence_config

    return json.dumps(result, indent=2)


def format_task_list(tasks: List) -> str:
    """
    Format task list operation result.

    Args:
        tasks: List of Task model instances from database

    Returns:
        JSON string with total count and array of task objects

    Example:
        tasks = [
            Task(id=42, title="Buy groceries", description="Milk, eggs", completed=False,
                 created_at=datetime.now(), updated_at=datetime.now()),
            Task(id=43, title="Call dentist", description=None, completed=True,
                 created_at=datetime.now(), updated_at=datetime.now())
        ]
        format_task_list(tasks)
        # Returns:
        # {
        #   "total": 2,
        #   "tasks": [
        #     {
        #       "task_id": 42,
        #       "title": "Buy groceries",
        #       "description": "Milk, eggs",
        #       "completed": false,
        #       "created_at": "2026-01-07T10:30:00Z",
        #       "updated_at": "2026-01-07T10:30:00Z"
        #     },
        #     {
        #       "task_id": 43,
        #       "title": "Call dentist",
        #       "description": null,
        #       "completed": true,
        #       "created_at": "2026-01-06T14:20:00Z",
        #       "updated_at": "2026-01-07T09:15:00Z"
        #     }
        #   ]
        # }
    """
    task_list = []
    for task in tasks:
        task_dict = {
            "task_id": task.id,
            "title": task.title,
            "description": task.description,
            "completed": task.completed,
            "created_at": task.created_at.isoformat() if isinstance(task.created_at, datetime) else task.created_at,
            "updated_at": task.updated_at.isoformat() if isinstance(task.updated_at, datetime) else task.updated_at,
        }

        # Add advanced fields (Phase V)
        task_dict["priority"] = task.priority
        task_dict["due_date"] = task.due_date.isoformat() if isinstance(task.due_date, datetime) and task.due_date else task.due_date
        task_dict["reminder_at"] = task.reminder_at.isoformat() if isinstance(task.reminder_at, datetime) and task.reminder_at else task.reminder_at
        task_dict["recurrence_pattern"] = task.recurrence_pattern
        task_dict["recurrence_config"] = task.recurrence_config

        task_list.append(task_dict)

    return json.dumps(
        {
            "total": len(tasks),
            "tasks": task_list,
        },
        indent=2,
    )
