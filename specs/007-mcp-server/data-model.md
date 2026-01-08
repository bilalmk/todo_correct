# Data Model: MCP Server Input/Output Schemas

**Feature**: 007-mcp-server
**Date**: 2026-01-07
**Purpose**: Define Pydantic input models and response schemas for MCP tools

---

## Overview

The MCP server defines input validation models using Pydantic v2 BaseModel and returns structured JSON responses. All tools share a common `BaseToolInput` for user_id validation, and tool-specific models extend this base.

**Note**: The MCP server **reuses existing database models** from `backend/src/models/` (Task, User). This document focuses on **input validation models** and **response schemas**, not database entities.

---

## Input Models (Pydantic)

### BaseToolInput

**Purpose**: Base class with user_id validation for all MCP tools

**Location**: `mcp_server/src/todo_mcp/models/inputs.py`

```python
from pydantic import BaseModel, Field, field_validator, ConfigDict
from uuid import UUID
import re

class BaseToolInput(BaseModel):
    """
    Base model with user_id validation for all MCP tools.

    All tools inherit from this to enforce user_id parameter and validation.
    """
    model_config = ConfigDict(
        str_strip_whitespace=True,  # Automatically strip whitespace
        validate_assignment=True,    # Validate on field assignment
        extra='forbid'               # Reject unknown fields
    )

    user_id: UUID = Field(
        ...,
        description="User ID performing the action (UUID format: 8-4-4-4-12 hexadecimal)",
        json_schema_extra={
            "example": "550e8400-e29b-41d4-a716-446655440000"
        }
    )

    @field_validator('user_id')
    @classmethod
    def validate_user_id_format(cls, v: UUID) -> UUID:
        """
        Validate user_id conforms to UUID format.

        Raises:
            ValueError: If user_id is not a valid UUID format
        """
        try:
            str_uuid = str(v)
            # Validate UUID format (8-4-4-4-12 hexadecimal pattern)
            if not re.match(r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$', str_uuid.lower()):
                raise ValueError("Invalid UUID format")
        except Exception:
            raise ValueError(
                f"Invalid user_id format: {v}. Expected UUID format (8-4-4-4-12 hexadecimal pattern)."
            )
        return v
```

**Validation Rules**:
- **Type**: UUID (Pydantic built-in type)
- **Required**: Yes (no default value)
- **Format**: 8-4-4-4-12 hexadecimal pattern (e.g., `550e8400-e29b-41d4-a716-446655440000`)
- **Error Message**: "Invalid user_id format: {value}. Expected UUID format (8-4-4-4-12 hexadecimal pattern)."

**References**:
- Spec FR-002: "System MUST require user_id parameter (UUID format) for all 5 tools"
- Spec FR-021: "System MUST validate user_id parameter conforms to UUID format"

---

### AddTaskInput

**Purpose**: Input validation for `todo_add_task` tool

**Location**: `mcp_server/src/todo_mcp/models/inputs.py`

```python
from typing import Optional

class AddTaskInput(BaseToolInput):
    """
    Input model for todo_add_task tool.

    Validates task creation parameters:
    - title: required, 1-255 characters
    - description: optional, max 10,000 characters
    """

    title: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Task title (required, 1-255 characters)",
        json_schema_extra={
            "example": "Buy groceries"
        }
    )

    description: Optional[str] = Field(
        None,
        max_length=10000,
        description="Task description (optional, max 10,000 characters)",
        json_schema_extra={
            "example": "Milk, eggs, bread, and vegetables"
        }
    )

    @field_validator('description')
    @classmethod
    def validate_description_length(cls, v: Optional[str]) -> Optional[str]:
        """
        Validate description length does not exceed 10,000 characters.

        Raises:
            ValueError: If description exceeds 10,000 characters
        """
        if v is not None and len(v) > 10000:
            raise ValueError("Task description exceeds maximum length of 10,000 characters")
        return v
```

**Validation Rules**:
| Field | Type | Required | Constraints | Error Message |
|-------|------|----------|-------------|---------------|
| `user_id` | UUID | Yes | Valid UUID format | "Invalid user_id format: {value}. Expected UUID format." |
| `title` | str | Yes | 1-255 characters | "Task title exceeds maximum length of 255 characters" |
| `description` | str | No | Max 10,000 characters | "Task description exceeds maximum length of 10,000 characters" |

**References**:
- Spec FR-006: "System MUST implement add_task tool with required parameters (user_id, title) and optional description parameter"
- Spec FR-022: "System MUST validate task title length (max 255 characters) and description length (max 10,000 characters)"

---

### ListTasksInput

**Purpose**: Input validation for `todo_list_tasks` tool

**Location**: `mcp_server/src/todo_mcp/models/inputs.py`

```python
from typing import Literal

class ListTasksInput(BaseToolInput):
    """
    Input model for todo_list_tasks tool.

    Validates task listing parameters:
    - status: optional filter (all, pending, completed)
    """

    status: Literal["all", "pending", "completed"] = Field(
        default="all",
        description="Filter by task status: 'all' (default), 'pending' (not completed), or 'completed'",
        json_schema_extra={
            "example": "all"
        }
    )
```

**Validation Rules**:
| Field | Type | Required | Constraints | Default | Error Message |
|-------|------|----------|-------------|---------|---------------|
| `user_id` | UUID | Yes | Valid UUID format | N/A | "Invalid user_id format..." |
| `status` | str | No | Enum: "all", "pending", "completed" | "all" | "status must be one of: all, pending, completed" |

**References**:
- Spec FR-007: "System MUST implement list_tasks tool with required user_id parameter and optional status filter (all/pending/completed)"

---

### CompleteTaskInput

**Purpose**: Input validation for `todo_complete_task` tool

**Location**: `mcp_server/src/todo_mcp/models/inputs.py`

```python
class CompleteTaskInput(BaseToolInput):
    """
    Input model for todo_complete_task tool.

    Validates task completion parameters:
    - task_id: required, positive integer
    """

    task_id: int = Field(
        ...,
        ge=1,
        description="Task ID to mark as completed (positive integer)",
        json_schema_extra={
            "example": 42
        }
    )
```

**Validation Rules**:
| Field | Type | Required | Constraints | Error Message |
|-------|------|----------|-------------|---------------|
| `user_id` | UUID | Yes | Valid UUID format | "Invalid user_id format..." |
| `task_id` | int | Yes | >= 1 | "task_id must be a positive integer" |

**References**:
- Spec FR-008: "System MUST implement complete_task tool with required parameters (user_id, task_id)"

---

### DeleteTaskInput

**Purpose**: Input validation for `todo_delete_task` tool

**Location**: `mcp_server/src/todo_mcp/models/inputs.py`

```python
class DeleteTaskInput(BaseToolInput):
    """
    Input model for todo_delete_task tool.

    Validates task deletion parameters:
    - task_id: required, positive integer
    """

    task_id: int = Field(
        ...,
        ge=1,
        description="Task ID to soft delete (positive integer)",
        json_schema_extra={
            "example": 42
        }
    )
```

**Validation Rules**:
| Field | Type | Required | Constraints | Error Message |
|-------|------|----------|-------------|---------------|
| `user_id` | UUID | Yes | Valid UUID format | "Invalid user_id format..." |
| `task_id` | int | Yes | >= 1 | "task_id must be a positive integer" |

**References**:
- Spec FR-009: "System MUST implement delete_task tool with required parameters (user_id, task_id) that performs soft delete"

---

### UpdateTaskInput

**Purpose**: Input validation for `todo_update_task` tool

**Location**: `mcp_server/src/todo_mcp/models/inputs.py`

```python
class UpdateTaskInput(BaseToolInput):
    """
    Input model for todo_update_task tool.

    Validates task update parameters:
    - task_id: required, positive integer
    - title: optional, 1-255 characters
    - description: optional, max 10,000 characters

    At least one of title or description must be provided.
    """

    task_id: int = Field(
        ...,
        ge=1,
        description="Task ID to update (positive integer)",
        json_schema_extra={
            "example": 42
        }
    )

    title: Optional[str] = Field(
        None,
        min_length=1,
        max_length=255,
        description="New task title (optional, 1-255 characters)",
        json_schema_extra={
            "example": "Buy groceries at 5pm"
        }
    )

    description: Optional[str] = Field(
        None,
        max_length=10000,
        description="New task description (optional, max 10,000 characters)",
        json_schema_extra={
            "example": "Updated description with more details"
        }
    )

    @field_validator('title', 'description')
    @classmethod
    def validate_at_least_one_field(cls, v, info):
        """
        Validate that at least one of title or description is provided.

        Raises:
            ValueError: If both title and description are None
        """
        # Access field data from validation context
        data = info.data
        if data.get('title') is None and data.get('description') is None:
            raise ValueError("At least one of 'title' or 'description' must be provided for update")
        return v
```

**Validation Rules**:
| Field | Type | Required | Constraints | Error Message |
|-------|------|----------|-------------|---------------|
| `user_id` | UUID | Yes | Valid UUID format | "Invalid user_id format..." |
| `task_id` | int | Yes | >= 1 | "task_id must be a positive integer" |
| `title` | str | No* | 1-255 characters | "Task title exceeds maximum length of 255 characters" |
| `description` | str | No* | Max 10,000 characters | "Task description exceeds maximum length of 10,000 characters" |

*At least one of `title` or `description` must be provided

**References**:
- Spec FR-010: "System MUST implement update_task tool with required user_id and task_id, and optional title and description parameters"
- Spec FR-022: "System MUST validate task title length (max 255 characters) and description length (max 10,000 characters)"

---

## Response Schemas (JSON)

### Success Response Schema

All successful tool operations return a consistent JSON structure as defined in FR-005.

#### Single Task Operation Response

**Used by**: `todo_add_task`, `todo_complete_task`, `todo_delete_task`, `todo_update_task`

```json
{
  "task_id": 42,
  "status": "created" | "completed" | "deleted" | "updated",
  "title": "Buy groceries"
}
```

**Schema**:
```python
# utils/responses.py
from typing import Literal

def format_task_result(task: Task, status: Literal["created", "completed", "deleted", "updated"]) -> str:
    """
    Format single task operation result.

    Args:
        task: Task model instance from database
        status: Operation status (created, completed, deleted, updated)

    Returns:
        JSON string with task_id, status, and title
    """
    import json
    return json.dumps({
        "task_id": task.id,
        "status": status,
        "title": task.title
    }, indent=2)
```

**Fields**:
| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `task_id` | int | Unique task identifier | 42 |
| `status` | str | Operation result | "created", "completed", "deleted", "updated" |
| `title` | str | Task title | "Buy groceries" |

**References**:
- Spec FR-005: "System MUST return consistent response schema: {task_id, status, title} for single task operations"

---

#### List Tasks Response

**Used by**: `todo_list_tasks`

```json
{
  "total": 15,
  "tasks": [
    {
      "task_id": 42,
      "title": "Buy groceries",
      "description": "Milk, eggs, bread",
      "completed": false,
      "created_at": "2026-01-07T10:30:00Z",
      "updated_at": "2026-01-07T10:30:00Z"
    },
    {
      "task_id": 43,
      "title": "Call dentist",
      "description": null,
      "completed": true,
      "created_at": "2026-01-06T14:20:00Z",
      "updated_at": "2026-01-07T09:15:00Z"
    }
  ]
}
```

**Schema**:
```python
def format_task_list(tasks: list[Task]) -> str:
    """
    Format task list operation result.

    Args:
        tasks: List of Task model instances from database

    Returns:
        JSON string with total count and array of task objects
    """
    import json
    return json.dumps({
        "total": len(tasks),
        "tasks": [
            {
                "task_id": task.id,
                "title": task.title,
                "description": task.description,
                "completed": task.completed,
                "created_at": task.created_at.isoformat(),
                "updated_at": task.updated_at.isoformat()
            }
            for task in tasks
        ]
    }, indent=2)
```

**Fields**:
| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `total` | int | Number of tasks returned | 15 |
| `tasks` | array | Array of task objects | [...] |
| `tasks[].task_id` | int | Unique task identifier | 42 |
| `tasks[].title` | str | Task title | "Buy groceries" |
| `tasks[].description` | str\|null | Task description (nullable) | "Milk, eggs, bread" |
| `tasks[].completed` | bool | Completion status | false |
| `tasks[].created_at` | str | ISO 8601 timestamp (UTC) | "2026-01-07T10:30:00Z" |
| `tasks[].updated_at` | str | ISO 8601 timestamp (UTC) | "2026-01-07T10:30:00Z" |

**References**:
- Spec FR-005: "System MUST return consistent response schema: array of task objects for list operations"
- Spec FR-007: "System MUST implement list_tasks tool"

---

### Error Response Schema

All errors return a consistent JSON structure with human-readable messages (FR-012).

```json
{
  "error": true,
  "message": "Task 42 not found for user 550e8400-e29b-41d4-a716-446655440000. Please verify the task ID and try again.",
  "code": "TASK_NOT_FOUND",
  "task_id": 42,
  "user_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

**Schema**:
```python
# utils/errors.py
from typing import Optional

def format_error(
    message: str,
    code: str,
    task_id: Optional[int] = None,
    user_id: Optional[str] = None
) -> str:
    """
    Format error response for AI consumption.

    Args:
        message: Human-readable error message
        code: Error code (TASK_NOT_FOUND, VALIDATION_ERROR, DATABASE_ERROR, INVALID_USER_ID)
        task_id: Optional task ID context
        user_id: Optional user ID context

    Returns:
        JSON string with error details
    """
    import json
    result = {
        "error": True,
        "message": message,
        "code": code
    }
    if task_id is not None:
        result["task_id"] = task_id
    if user_id is not None:
        result["user_id"] = user_id
    return json.dumps(result, indent=2)
```

**Error Codes**:
| Code | HTTP Equivalent | Example Message | Context Fields |
|------|----------------|-----------------|----------------|
| `TASK_NOT_FOUND` | 404 | "Task 42 not found for user {user_id}. Please verify the task ID and try again." | task_id, user_id |
| `VALIDATION_ERROR` | 400 | "Task title exceeds maximum length of 255 characters" | field_name |
| `DATABASE_ERROR` | 500 | "Database connection error: unable to execute operation. Please try again." | None |
| `INVALID_USER_ID` | 400 | "Invalid user_id format: {value}. Expected UUID format (8-4-4-4-12 hexadecimal pattern)." | user_id |

**References**:
- Spec FR-012: "System MUST return human-readable error messages optimized for AI reformulation into natural language"

---

## Database Models (Reused from Backend)

The MCP server **imports existing models** from `backend/src/models/` rather than defining new ones.

### Task Model (Existing)

**Location**: `backend/src/models/task.py`

**Key Fields for MCP Server**:
```python
class Task(SQLModel, table=True):
    id: Optional[int]                    # Primary key (BIGSERIAL)
    user_id: UUID                        # Foreign key to user table
    title: str                           # Max 255 characters
    description: Optional[str]           # Max 10,000 characters (TEXT)
    completed: bool                      # Completion status (default: False)
    created_at: datetime                 # UTC timestamp
    updated_at: datetime                 # UTC timestamp
    deleted_at: Optional[datetime]       # Soft delete timestamp (NULL = active)
```

**Indexes**:
- `idx_tasks_user_completed` (user_id, completed)
- `idx_tasks_user_sort_order` (user_id, sort_order)
- `idx_tasks_user_priority` (user_id, priority) - partial index where priority IS NOT NULL
- `idx_tasks_user_due_date` (user_id, due_date) - partial index where due_date IS NOT NULL

**Constraints**:
- `check_description_length`: description length <= 10,000 characters
- Foreign key: user_id → user.id (ON DELETE CASCADE)

**Usage in MCP Server**:
```python
# tools/add_task.py
from backend.src.models.task import Task
from datetime import datetime, timezone

async def add_task_tool(params: AddTaskInput, session: AsyncSession) -> str:
    new_task = Task(
        user_id=params.user_id,
        title=params.title,
        description=params.description,
        completed=False,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )
    session.add(new_task)
    await session.commit()
    await session.refresh(new_task)
    return format_task_result(new_task, "created")
```

---

### User Model (Existing)

**Location**: `backend/src/models/user.py`

**Key Fields**:
```python
class User(SQLModel, table=True):
    id: str                              # Better Auth String ID (primary key)
    uuid: UUID                           # Application UUID (unique, indexed)
    email: str                           # Unique, indexed
    name: Optional[str]
    createdAt: datetime
    updatedAt: datetime
```

**Usage in MCP Server**:
- MCP server receives `user_id` as UUID (matches `User.uuid` column)
- No need to query User table for tool operations (user_id validated by UUID format, user existence validated by foreign key constraint on Task.user_id)

---

## Summary

### Input Models
| Model | Purpose | Required Fields | Optional Fields |
|-------|---------|----------------|-----------------|
| `BaseToolInput` | Base class for all tools | user_id (UUID) | None |
| `AddTaskInput` | Create new task | title (1-255 chars) | description (max 10k chars) |
| `ListTasksInput` | List tasks with filter | None | status (all/pending/completed) |
| `CompleteTaskInput` | Mark task completed | task_id (int >= 1) | None |
| `DeleteTaskInput` | Soft delete task | task_id (int >= 1) | None |
| `UpdateTaskInput` | Update task details | task_id (int >= 1), title OR description* | title, description |

*At least one of title or description required

### Response Schemas
| Operation | Schema | Fields |
|-----------|--------|--------|
| Single task | `{task_id, status, title}` | task_id (int), status (str), title (str) |
| List tasks | `{total, tasks: [...]}` | total (int), tasks (array of task objects) |
| Error | `{error, message, code, ...}` | error (bool), message (str), code (str), optional context |

### Database Models (Reused)
| Model | Location | Purpose |
|-------|----------|---------|
| Task | `backend/src/models/task.py` | Todo item with soft delete support |
| User | `backend/src/models/user.py` | User account (Better Auth integration) |

---

**Data model design completed**: 2026-01-07
**Next**: Generate contracts/mcp_tools.yaml (OpenAPI-compatible tool schemas)
