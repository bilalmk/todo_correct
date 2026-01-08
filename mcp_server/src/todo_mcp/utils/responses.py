"""
Response formatting utilities for Todo MCP Server.

Provides consistent JSON response schemas for single task operations and task lists.
"""

import json
from typing import Literal, List
from datetime import datetime


def format_task_result(task, status: Literal["created", "completed", "deleted", "updated"]) -> str:
    """
    Format single task operation result.

    Args:
        task: Task model instance from database (must have id, title attributes)
        status: Operation status (created, completed, deleted, updated)

    Returns:
        JSON string with task_id, status, and title

    Example:
        task = Task(id=42, title="Buy groceries")
        format_task_result(task, "created")
        # Returns:
        # {
        #   "task_id": 42,
        #   "status": "created",
        #   "title": "Buy groceries"
        # }
    """
    return json.dumps(
        {
            "task_id": task.id,
            "status": status,
            "title": task.title,
        },
        indent=2,
    )


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
    return json.dumps(
        {
            "total": len(tasks),
            "tasks": [
                {
                    "task_id": task.id,
                    "title": task.title,
                    "description": task.description,
                    "completed": task.completed,
                    "created_at": task.created_at.isoformat() if isinstance(task.created_at, datetime) else task.created_at,
                    "updated_at": task.updated_at.isoformat() if isinstance(task.updated_at, datetime) else task.updated_at,
                }
                for task in tasks
            ],
        },
        indent=2,
    )
