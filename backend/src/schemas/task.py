"""Pydantic schemas for Task API endpoints."""

from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
from pydantic_core.core_schema import ValidationInfo

from .common import PriorityEnum, RecurrencePatternEnum
from .tag import TagResponse


class TaskCreate(BaseModel):
    """Request DTO for creating a new task."""

    title: str = Field(
        ..., min_length=1, max_length=255, description="Task title (required)"
    )
    description: Optional[str] = Field(
        None, max_length=10000, description="Detailed description"
    )
    completed: bool = Field(
        default=False, description="Completion status (defaults to false)"
    )
    priority: Optional[PriorityEnum] = Field(
        None, description="Priority: low, medium, or high"
    )
    due_date: Optional[datetime] = Field(
        None, description="Task deadline (ISO 8601 UTC)"
    )
    reminder_at: Optional[datetime] = Field(
        None, description="Reminder trigger time (ISO 8601 UTC)"
    )
    recurrence_pattern: Optional[RecurrencePatternEnum] = Field(
        None, description="Recurrence: daily, weekly, monthly, or custom"
    )
    recurrence_config: Optional[dict] = Field(
        None, description="JSONB config with RRULE format"
    )

    @field_validator("title")
    @classmethod
    def title_not_empty(cls, v: str) -> str:
        """Ensure title is not whitespace-only."""
        if not v.strip():
            raise ValueError("Task title cannot be empty or whitespace-only")
        return v.strip()

    @field_validator("reminder_at")
    @classmethod
    def reminder_before_due(
        cls, v: Optional[datetime], info: ValidationInfo
    ) -> Optional[datetime]:
        """Ensure reminder_at is before due_date if both are set."""
        if v and info.data.get("due_date"):
            due_date = info.data["due_date"]

            # Ensure both datetimes are timezone-aware for comparison
            from datetime import timezone

            reminder = v if v.tzinfo else v.replace(tzinfo=timezone.utc)
            due = due_date if due_date.tzinfo else due_date.replace(tzinfo=timezone.utc)

            if reminder >= due:
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
                "recurrence_config": {"rrule": "FREQ=WEEKLY;BYDAY=MO,FR"},
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

    @field_validator("title")
    @classmethod
    def title_not_empty(cls, v: Optional[str]) -> Optional[str]:
        """Ensure title is not whitespace-only if provided."""
        if v is not None and not v.strip():
            raise ValueError("Task title cannot be empty or whitespace-only")
        return v.strip() if v else None

    @field_validator("reminder_at")
    @classmethod
    def reminder_before_due(
        cls, v: Optional[datetime], info: ValidationInfo
    ) -> Optional[datetime]:
        """Ensure reminder_at is before due_date if both are set."""
        if v and info.data.get("due_date"):
            due_date = info.data["due_date"]

            # Ensure both datetimes are timezone-aware for comparison
            from datetime import timezone

            reminder = v if v.tzinfo else v.replace(tzinfo=timezone.utc)
            due = due_date if due_date.tzinfo else due_date.replace(tzinfo=timezone.utc)

            if reminder >= due:
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

    @field_validator("title")
    @classmethod
    def title_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Task title cannot be empty or whitespace-only")
        return v.strip()

    @field_validator("reminder_at")
    @classmethod
    def reminder_before_due(
        cls, v: Optional[datetime], info: ValidationInfo
    ) -> Optional[datetime]:
        if v and info.data.get("due_date") and v >= info.data["due_date"]:
            raise ValueError("reminder_at must be before due_date")
        return v


class ReorderRequest(BaseModel):
    """Request DTO for reordering tasks via drag-and-drop (T040 - fastapi-expert pattern)."""

    task_ids: List[int] = Field(
        ...,
        min_length=1,
        description="Ordered array of task IDs (1-indexed positions)",
    )

    @field_validator("task_ids")
    @classmethod
    def validate_task_ids(cls, v: List[int]) -> List[int]:
        """Ensure all task IDs are positive integers and array is non-empty."""
        if not v:
            raise ValueError("task_ids array cannot be empty")

        for task_id in v:
            if task_id <= 0:
                raise ValueError(f"Invalid task_id {task_id}: must be positive integer")

        # Check for duplicates
        if len(v) != len(set(v)):
            raise ValueError("task_ids array contains duplicate IDs")

        return v

    model_config = {
        "json_schema_extra": {
            "example": {
                "task_ids": [5, 2, 8, 1, 3]  # New order after drag-and-drop
            }
        }
    }


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
    recurrence_config: Optional[dict] = Field(
        None, description="Recurrence configuration"
    )
    tags: List[TagResponse] = Field(
        default_factory=list, description="Assigned tags"
    )
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
                    {
                        "id": 1,
                        "user_id": "123e4567-e89b-12d3-a456-426614174000",
                        "name": "work",
                        "color": "#FF5733",
                        "created_at": "2025-12-30T10:00:00Z",
                    },
                    {
                        "id": 2,
                        "user_id": "123e4567-e89b-12d3-a456-426614174000",
                        "name": "urgent",
                        "color": "#FF0000",
                        "created_at": "2025-12-30T10:00:00Z",
                    },
                ],
                "created_at": "2025-12-30T10:00:00Z",
                "updated_at": "2025-12-30T11:30:00Z",
            }
        },
    }
