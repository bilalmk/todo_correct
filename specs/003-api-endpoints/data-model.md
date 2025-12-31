# Data Model: RESTful API Endpoints

**Feature**: 003-api-endpoints
**Date**: 2025-12-30
**Purpose**: Define Pydantic DTOs (Data Transfer Objects) for API requests and responses

---

## Overview

This feature does **NOT** modify the database schema. All database models (Task, Tag, TaskTag, User, Notification) already exist from specs 001 and 002. This document defines **API-layer DTOs** (Pydantic models) that control request validation and response serialization.

---

## Pydantic Models (API Layer)

### 1. Common Enums and Base Models

**File**: `backend/src/schemas/common.py`

```python
from enum import Enum
from pydantic import BaseModel, Field
from typing import Optional


class PriorityEnum(str, Enum):
    """Task priority levels."""
    low = "low"
    medium = "medium"
    high = "high"


class RecurrencePatternEnum(str, Enum):
    """Recurrence patterns for recurring tasks."""
    daily = "daily"
    weekly = "weekly"
    monthly = "monthly"
    custom = "custom"


class ErrorResponse(BaseModel):
    """Standard error response format."""
    error: str = Field(..., description="Human-readable error message")
    code: str = Field(..., description="Machine-readable error code")
    status: int = Field(..., description="HTTP status code")
    request_id: str = Field(..., description="Request ID for tracing")

    model_config = {
        "json_schema_extra": {
            "example": {
                "error": "Task not found",
                "code": "TASK_NOT_FOUND",
                "status": 404,
                "request_id": "req_abc123xyz"
            }
        }
    }
```

---

### 2. Tag Schemas

**File**: `backend/src/schemas/tag.py`

```python
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field, field_validator
from typing import Optional
import re


class TagCreate(BaseModel):
    """Request DTO for creating a new tag."""
    name: str = Field(..., min_length=1, max_length=50, description="Tag name (e.g., 'work', 'personal')")
    color: Optional[str] = Field(None, max_length=7, description="Hex color code (#RRGGBB or #RGB)")

    @field_validator('name')
    @classmethod
    def name_not_empty(cls, v: str) -> str:
        """Ensure name is not whitespace-only."""
        if not v.strip():
            raise ValueError("Tag name cannot be empty or whitespace-only")
        return v.strip()

    @field_validator('color')
    @classmethod
    def validate_hex_color(cls, v: Optional[str]) -> Optional[str]:
        """Validate and normalize hex color format."""
        if v is None:
            return None

        # Remove whitespace
        v = v.strip()

        # Check if it matches hex color format (# + 3 or 6 hex digits)
        if not re.match(r'^#[0-9A-Fa-f]{3}$|^#[0-9A-Fa-f]{6}$', v):
            raise ValueError("Invalid hex color format. Use #RRGGBB or #RGB.")

        # Normalize shorthand (#RGB) to full format (#RRGGBB)
        if len(v) == 4:  # #RGB
            v = '#' + ''.join([c * 2 for c in v[1:]])

        # Normalize to uppercase
        return v.upper()

    model_config = {
        "json_schema_extra": {
            "example": {
                "name": "work",
                "color": "#FF5733"
            }
        }
    }


class TagUpdate(BaseModel):
    """Request DTO for updating a tag (all fields optional for partial updates)."""
    name: Optional[str] = Field(None, min_length=1, max_length=50)
    color: Optional[str] = Field(None, max_length=7)

    @field_validator('name')
    @classmethod
    def name_not_empty(cls, v: Optional[str]) -> Optional[str]:
        """Ensure name is not whitespace-only if provided."""
        if v is not None and not v.strip():
            raise ValueError("Tag name cannot be empty or whitespace-only")
        return v.strip() if v else None

    @field_validator('color')
    @classmethod
    def validate_hex_color(cls, v: Optional[str]) -> Optional[str]:
        """Validate and normalize hex color format."""
        if v is None:
            return None

        v = v.strip()
        if not re.match(r'^#[0-9A-Fa-f]{3}$|^#[0-9A-Fa-f]{6}$', v):
            raise ValueError("Invalid hex color format. Use #RRGGBB or #RGB.")

        # Normalize shorthand to full format
        if len(v) == 4:
            v = '#' + ''.join([c * 2 for c in v[1:]])

        return v.upper()


class TagResponse(BaseModel):
    """Response DTO for tag objects."""
    id: int = Field(..., description="Tag ID")
    user_id: UUID = Field(..., description="Owner user ID")
    name: str = Field(..., description="Tag name")
    color: Optional[str] = Field(None, description="Hex color code (#RRGGBB)")
    created_at: datetime = Field(..., description="Creation timestamp (UTC)")

    model_config = {
        "from_attributes": True,  # Pydantic v2: enable ORM mode
        "json_schema_extra": {
            "example": {
                "id": 1,
                "user_id": "123e4567-e89b-12d3-a456-426614174000",
                "name": "work",
                "color": "#FF5733",
                "created_at": "2025-12-30T10:00:00Z"
            }
        }
    }
```

---

### 3. Task Schemas

**File**: `backend/src/schemas/task.py`

```python
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
from pydantic_core.core_schema import ValidationInfo

from .common import PriorityEnum, RecurrencePatternEnum
from .tag import TagResponse


class TaskCreate(BaseModel):
    """Request DTO for creating a new task."""
    title: str = Field(..., min_length=1, max_length=255, description="Task title (required)")
    description: Optional[str] = Field(None, max_length=10000, description="Detailed description")
    completed: bool = Field(default=False, description="Completion status (defaults to false)")
    priority: Optional[PriorityEnum] = Field(None, description="Priority: low, medium, or high")
    due_date: Optional[datetime] = Field(None, description="Task deadline (ISO 8601 UTC)")
    reminder_at: Optional[datetime] = Field(None, description="Reminder trigger time (ISO 8601 UTC)")
    recurrence_pattern: Optional[RecurrencePatternEnum] = Field(None, description="Recurrence: daily, weekly, monthly, or custom")
    recurrence_config: Optional[dict] = Field(None, description="JSONB config with RRULE format")

    @field_validator('title')
    @classmethod
    def title_not_empty(cls, v: str) -> str:
        """Ensure title is not whitespace-only."""
        if not v.strip():
            raise ValueError("Task title cannot be empty or whitespace-only")
        return v.strip()

    @field_validator('reminder_at')
    @classmethod
    def reminder_before_due(cls, v: Optional[datetime], info: ValidationInfo) -> Optional[datetime]:
        """Ensure reminder_at is before due_date if both are set."""
        if v and info.data.get('due_date') and v >= info.data['due_date']:
            raise ValueError("reminder_at must be before due_date")
        return v

    model_config = {
        "json_schema_extra": {
            "example": {
                "title": "Buy groceries",
                "description": "Milk, eggs, bread",
                "completed": False,
                "priority": "high",
                "due_date": "2025-12-31T10:00:00Z",
                "reminder_at": "2025-12-30T09:45:00Z",
                "recurrence_pattern": "weekly",
                "recurrence_config": {"rrule": "FREQ=WEEKLY;BYDAY=MO,FR"}
            }
        }
    }


class TaskUpdate(BaseModel):
    """Request DTO for partial task updates (PATCH - all fields optional)."""
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=10000)
    completed: Optional[bool] = None
    priority: Optional[PriorityEnum] = None
    due_date: Optional[datetime] = None
    reminder_at: Optional[datetime] = None
    recurrence_pattern: Optional[RecurrencePatternEnum] = None
    recurrence_config: Optional[dict] = None

    @field_validator('title')
    @classmethod
    def title_not_empty(cls, v: Optional[str]) -> Optional[str]:
        """Ensure title is not whitespace-only if provided."""
        if v is not None and not v.strip():
            raise ValueError("Task title cannot be empty or whitespace-only")
        return v.strip() if v else None

    @field_validator('reminder_at')
    @classmethod
    def reminder_before_due(cls, v: Optional[datetime], info: ValidationInfo) -> Optional[datetime]:
        """Ensure reminder_at is before due_date if both are set."""
        if v and info.data.get('due_date') and v >= info.data['due_date']:
            raise ValueError("reminder_at must be before due_date")
        return v


class TaskReplace(BaseModel):
    """Request DTO for full task replacement (PUT - all non-nullable fields required)."""
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=10000)
    completed: bool = Field(...)
    priority: Optional[PriorityEnum] = None
    due_date: Optional[datetime] = None
    reminder_at: Optional[datetime] = None
    recurrence_pattern: Optional[RecurrencePatternEnum] = None
    recurrence_config: Optional[dict] = None

    @field_validator('title')
    @classmethod
    def title_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Task title cannot be empty or whitespace-only")
        return v.strip()

    @field_validator('reminder_at')
    @classmethod
    def reminder_before_due(cls, v: Optional[datetime], info: ValidationInfo) -> Optional[datetime]:
        if v and info.data.get('due_date') and v >= info.data['due_date']:
            raise ValueError("reminder_at must be before due_date")
        return v


class TaskResponse(BaseModel):
    """Response DTO for task objects with nested tags."""
    id: int = Field(..., description="Task ID")
    user_id: UUID = Field(..., description="Owner user ID")
    title: str = Field(..., description="Task title")
    description: Optional[str] = Field(None, description="Task description")
    completed: bool = Field(..., description="Completion status")
    priority: Optional[str] = Field(None, description="Priority level")
    due_date: Optional[datetime] = Field(None, description="Task deadline (UTC)")
    reminder_at: Optional[datetime] = Field(None, description="Reminder time (UTC)")
    recurrence_pattern: Optional[str] = Field(None, description="Recurrence pattern")
    recurrence_config: Optional[dict] = Field(None, description="Recurrence configuration")
    tags: List[TagResponse] = Field(default_factory=list, description="Assigned tags")
    created_at: datetime = Field(..., description="Creation timestamp (UTC)")
    updated_at: datetime = Field(..., description="Last update timestamp (UTC)")

    model_config = {
        "from_attributes": True,  # Pydantic v2: enable ORM mode
        "json_schema_extra": {
            "example": {
                "id": 123,
                "user_id": "123e4567-e89b-12d3-a456-426614174000",
                "title": "Buy groceries",
                "description": "Milk, eggs, bread",
                "completed": False,
                "priority": "high",
                "due_date": "2025-12-31T10:00:00Z",
                "reminder_at": "2025-12-30T09:45:00Z",
                "recurrence_pattern": "weekly",
                "recurrence_config": {"rrule": "FREQ=WEEKLY;BYDAY=MO,FR"},
                "tags": [
                    {"id": 1, "user_id": "123e4567-e89b-12d3-a456-426614174000", "name": "work", "color": "#FF5733", "created_at": "2025-12-30T10:00:00Z"},
                    {"id": 2, "user_id": "123e4567-e89b-12d3-a456-426614174000", "name": "urgent", "color": "#FF0000", "created_at": "2025-12-30T10:00:00Z"}
                ],
                "created_at": "2025-12-30T10:00:00Z",
                "updated_at": "2025-12-30T11:30:00Z"
            }
        }
    }
```

---

### 4. Task-Tag Relationship Schemas

**File**: `backend/src/schemas/task_tag.py`

```python
from pydantic import BaseModel, Field


class TaskTagCreate(BaseModel):
    """Request DTO for assigning a tag to a task."""
    tag_id: int = Field(..., description="ID of the tag to assign", gt=0)

    model_config = {
        "json_schema_extra": {
            "example": {
                "tag_id": 5
            }
        }
    }


class TaskTagResponse(BaseModel):
    """Response DTO for successful tag assignment."""
    task_id: int = Field(..., description="Task ID")
    tag_id: int = Field(..., description="Tag ID")
    message: str = Field(default="Tag assigned successfully", description="Success message")

    model_config = {
        "json_schema_extra": {
            "example": {
                "task_id": 123,
                "tag_id": 5,
                "message": "Tag assigned successfully"
            }
        }
    }
```

---

## Schema Validation Rules

### Cross-Field Validation

1. **reminder_at vs due_date**: If both are set, `reminder_at` must be before `due_date`
2. **Title not whitespace**: `title.strip()` must not be empty
3. **Tag name uniqueness**: Enforced at database level (partial unique index), API returns 409 Conflict

### Field Constraints

| Field | Constraint | Validation |
|-------|-----------|------------|
| `title` | Required, 1-255 chars | Pydantic `min_length=1, max_length=255` |
| `description` | Optional, max 10,000 chars | Pydantic `max_length=10000` |
| `priority` | Enum: low/medium/high | Pydantic `PriorityEnum` |
| `due_date` | ISO 8601 datetime | Pydantic `datetime` type |
| `reminder_at` | ISO 8601 datetime, before due_date | Pydantic validator |
| `recurrence_pattern` | Enum: daily/weekly/monthly/custom | Pydantic `RecurrencePatternEnum` |
| `recurrence_config` | Valid JSON object | Pydantic `dict` type |
| `tag.name` | Required, 1-50 chars, not whitespace-only | Pydantic validator |
| `tag.color` | Optional, #RRGGBB or #RGB format | Pydantic validator with normalization |

---

## Database Models (Existing - No Changes)

The following SQLModel models already exist from spec 002-database-schema:

- **Task**: `backend/src/models/task.py`
- **Tag**: `backend/src/models/tag.py`
- **TaskTag**: `backend/src/models/task_tag.py`
- **User**: `backend/src/models/user.py`
- **Notification**: `backend/src/models/notification.py`

These models are **NOT** modified by this spec. Pydantic DTOs map to/from these models using `model_config = {"from_attributes": True}` (Pydantic v2 ORM mode).

---

## Conversion Between Layers

### Request → Database

```python
# In TaskRepository.create()
async def create(self, user_id: UUID, data: TaskCreate) -> Task:
    task = Task(
        **data.model_dump(exclude_unset=True),  # Only include provided fields
        user_id=user_id,  # Inject from JWT
    )
    self.session.add(task)
    await self.session.flush()
    await self.session.refresh(task, ["tags"])  # Eager load tags
    return task
```

### Database → Response

```python
# In endpoint
@router.get("/api/v1/{user_id}/tasks/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: int,
    user: User = Depends(verify_user_match),
    session: AsyncSession = Depends(get_session),
):
    repo = TaskRepository(session)
    task = await repo.get_by_id(user.id, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    # TaskResponse.model_config["from_attributes"] enables ORM mode
    return TaskResponse.model_validate(task)
```

---

## Summary

- **7 Pydantic Models**: TaskCreate, TaskUpdate, TaskReplace, TaskResponse, TagCreate, TagUpdate, TagResponse, TaskTagCreate, TaskTagResponse, ErrorResponse, PriorityEnum, RecurrencePatternEnum
- **0 Database Changes**: All database models already exist from spec 002
- **Validation**: Cross-field validators (reminder_at < due_date), format validators (hex colors), uniqueness checks (at database level)
- **Normalization**: Hex colors normalized to uppercase #RRGGBB, whitespace trimmed from strings

---

**Next Step**: Phase 1 - Generate API contracts (OpenAPI schema)
