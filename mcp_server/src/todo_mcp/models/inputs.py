"""
Pydantic input validation models for MCP tools.

All tools inherit from BaseToolInput to enforce user_id parameter and validation.
"""

from pydantic import BaseModel, Field, field_validator, ConfigDict, model_validator
from uuid import UUID
from typing import Optional, Literal, Dict, Any
from datetime import datetime
import re


class BaseToolInput(BaseModel):
    """
    Base model with user_id validation for all MCP tools.

    All tools inherit from this to enforce user_id parameter and validation.
    """

    model_config = ConfigDict(
        str_strip_whitespace=True,  # Automatically strip whitespace
        validate_assignment=True,  # Validate on field assignment
        extra="forbid",  # Reject unknown fields
    )

    user_id: UUID = Field(
        ...,
        description="User ID performing the action (UUID format: 8-4-4-4-12 hexadecimal)",
        json_schema_extra={"example": "550e8400-e29b-41d4-a716-446655440000"},
    )

    @field_validator("user_id")
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
            if not re.match(
                r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$",
                str_uuid.lower(),
            ):
                raise ValueError("Invalid UUID format")
        except Exception:
            raise ValueError(
                f"Invalid user_id format: {v}. Expected UUID format (8-4-4-4-12 hexadecimal pattern)."
            )
        return v


class AddTaskInput(BaseToolInput):
    """
    Input model for todo_add_task tool.

    Validates task creation parameters:
    - title: required, 1-255 characters
    - description: optional, max 10,000 characters
    - priority: optional, one of 'low', 'medium', 'high'
    - due_date: optional, ISO 8601 datetime string (e.g., "2026-01-31T23:59:59Z")
    - reminder_at: optional, ISO 8601 datetime string for reminder notification
    - recurrence_pattern: optional, one of 'daily', 'weekly', 'monthly', 'custom'
    - recurrence_config: optional, JSON object for custom recurrence (iCalendar RRULE format)
    """

    title: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Task title (required, 1-255 characters)",
        json_schema_extra={"example": "Buy groceries"},
    )

    description: Optional[str] = Field(
        None,
        max_length=10000,
        description="Task description (optional, max 10,000 characters)",
        json_schema_extra={"example": "Milk, eggs, bread, and vegetables"},
    )

    priority: Optional[Literal["low", "medium", "high"]] = Field(
        None,
        description="Task priority: 'low', 'medium', or 'high'. Extract from keywords like 'urgent', 'important', 'asap'.",
        json_schema_extra={"example": "high"},
    )

    due_date: Optional[datetime] = Field(
        None,
        description="Task deadline as ISO 8601 datetime. Parse from natural language like 'tomorrow', 'next week', 'December 31st', 'in 3 days'. Always use UTC timezone.",
        json_schema_extra={"example": "2026-01-31T23:59:59Z"},
    )

    reminder_at: Optional[datetime] = Field(
        None,
        description="Reminder trigger time as ISO 8601 datetime. Parse from phrases like 'remind me 1 hour before', 'notify at 9am'. Always use UTC timezone.",
        json_schema_extra={"example": "2026-01-31T15:00:00Z"},
    )

    recurrence_pattern: Optional[Literal["daily", "weekly", "monthly", "custom"]] = Field(
        None,
        description="Recurrence type: 'daily', 'weekly', 'monthly', 'custom'. Extract from keywords like 'every day', 'weekly', 'monthly', 'repeating'.",
        json_schema_extra={"example": "weekly"},
    )

    recurrence_config: Optional[Dict[str, Any]] = Field(
        None,
        description="Advanced recurrence configuration in iCalendar RRULE format. Only use for 'custom' recurrence_pattern with complex rules.",
        json_schema_extra={"example": {"FREQ": "WEEKLY", "BYDAY": ["MO", "WE", "FR"], "INTERVAL": 1}},
    )

    @field_validator("description")
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

    @field_validator("due_date", "reminder_at", mode="before")
    @classmethod
    def validate_datetime_fields(cls, v):
        """
        Convert empty strings to None for datetime fields.

        AI may send empty strings when it doesn't want to set a field.
        Pydantic can't parse empty strings as datetimes, so convert to None.
        """
        if v == "" or v is None:
            return None
        return v

    @field_validator("recurrence_pattern", "priority", mode="before")
    @classmethod
    def validate_optional_literal_fields(cls, v):
        """
        Convert empty strings to None for optional literal fields.

        AI may send empty strings when it doesn't want to set a field.
        Pydantic can't parse empty strings as Literal types, so convert to None.
        """
        if v == "" or v is None:
            return None
        return v

    @field_validator("recurrence_config")
    @classmethod
    def validate_recurrence_config(cls, v: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """
        Validate recurrence_config structure (basic validation for RRULE format).

        Raises:
            ValueError: If recurrence_config has invalid structure
        """
        if v is not None:
            # Basic validation: must be a dict
            if not isinstance(v, dict):
                raise ValueError("recurrence_config must be a JSON object")

            # Optional: validate FREQ field if present
            if "FREQ" in v:
                valid_freq = ["DAILY", "WEEKLY", "MONTHLY", "YEARLY"]
                if v["FREQ"] not in valid_freq:
                    raise ValueError(f"FREQ must be one of {valid_freq}")

        return v

    @model_validator(mode="after")
    def validate_reminder_before_due_date(self):
        """
        Validate that reminder_at is before due_date if both are provided.

        Raises:
            ValueError: If reminder_at is after due_date
        """
        if self.reminder_at and self.due_date:
            if self.reminder_at >= self.due_date:
                raise ValueError("reminder_at must be before due_date")
        return self

    @model_validator(mode="after")
    def validate_recurrence_pattern_config(self):
        """
        Validate that recurrence_config is only provided when recurrence_pattern is 'custom'.

        Raises:
            ValueError: If recurrence_config provided without custom pattern
        """
        if self.recurrence_config and self.recurrence_pattern != "custom":
            raise ValueError("recurrence_config can only be used with recurrence_pattern='custom'")
        return self


class ListTasksInput(BaseToolInput):
    """
    Input model for todo_list_tasks tool.

    Validates task listing parameters:
    - status: optional filter (all, pending, completed)
    """

    status: Literal["all", "pending", "completed"] = Field(
        default="all",
        description="Filter by task status: 'all' (default), 'pending' (not completed), or 'completed'",
        json_schema_extra={"example": "all"},
    )


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
        json_schema_extra={"example": 42},
    )


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
        json_schema_extra={"example": 42},
    )


class UpdateTaskInput(BaseToolInput):
    """
    Input model for todo_update_task tool.

    Validates task update parameters:
    - task_id: required, positive integer
    - title: optional, 1-255 characters
    - description: optional, max 10,000 characters
    - priority: optional, one of 'low', 'medium', 'high'
    - due_date: optional, ISO 8601 datetime string
    - reminder_at: optional, ISO 8601 datetime string
    - recurrence_pattern: optional, one of 'daily', 'weekly', 'monthly', 'custom'
    - recurrence_config: optional, JSON object for custom recurrence

    At least one field (besides task_id) must be provided for update.
    """

    task_id: int = Field(
        ...,
        ge=1,
        description="Task ID to update (positive integer)",
        json_schema_extra={"example": 42},
    )

    title: Optional[str] = Field(
        None,
        min_length=1,
        max_length=255,
        description="New task title (optional, 1-255 characters)",
        json_schema_extra={"example": "Buy groceries at 5pm"},
    )

    description: Optional[str] = Field(
        None,
        max_length=10000,
        description="New task description (optional, max 10,000 characters)",
        json_schema_extra={"example": "Updated description with more details"},
    )

    priority: Optional[Literal["low", "medium", "high"]] = Field(
        None,
        description="Update task priority: 'low', 'medium', or 'high'. Can be set or cleared.",
        json_schema_extra={"example": "high"},
    )

    due_date: Optional[datetime] = Field(
        None,
        description="Update task deadline as ISO 8601 datetime. Can be set or cleared. Always use UTC timezone.",
        json_schema_extra={"example": "2026-01-31T23:59:59Z"},
    )

    reminder_at: Optional[datetime] = Field(
        None,
        description="Update reminder time as ISO 8601 datetime. Can be set or cleared. Always use UTC timezone.",
        json_schema_extra={"example": "2026-01-31T15:00:00Z"},
    )

    recurrence_pattern: Optional[Literal["daily", "weekly", "monthly", "custom"]] = Field(
        None,
        description="Update recurrence type: 'daily', 'weekly', 'monthly', 'custom'. Can be set or cleared.",
        json_schema_extra={"example": "weekly"},
    )

    recurrence_config: Optional[Dict[str, Any]] = Field(
        None,
        description="Update recurrence configuration in iCalendar RRULE format. Can be set or cleared.",
        json_schema_extra={"example": {"FREQ": "WEEKLY", "BYDAY": ["MO", "WE", "FR"], "INTERVAL": 1}},
    )

    @field_validator("due_date", "reminder_at", mode="before")
    @classmethod
    def validate_datetime_fields(cls, v):
        """
        Convert empty strings to None for datetime fields.

        AI may send empty strings when it doesn't want to set a field.
        Pydantic can't parse empty strings as datetimes, so convert to None.
        """
        if v == "" or v is None:
            return None
        return v

    @field_validator("recurrence_pattern", "priority", mode="before")
    @classmethod
    def validate_optional_literal_fields(cls, v):
        """
        Convert empty strings to None for optional literal fields.

        AI may send empty strings when it doesn't want to set a field.
        Pydantic can't parse empty strings as Literal types, so convert to None.
        """
        if v == "" or v is None:
            return None
        return v

    @model_validator(mode="after")
    def validate_at_least_one_field(self):
        """
        Validate that at least one field (besides task_id) is provided for update.

        Raises:
            ValueError: If no update fields are provided
        """
        update_fields = [
            self.title,
            self.description,
            self.priority,
            self.due_date,
            self.reminder_at,
            self.recurrence_pattern,
            self.recurrence_config,
        ]
        if all(field is None for field in update_fields):
            raise ValueError(
                "At least one field must be provided for update: title, description, priority, due_date, reminder_at, recurrence_pattern, or recurrence_config"
            )
        return self

    @model_validator(mode="after")
    def validate_reminder_before_due_date(self):
        """
        Validate that reminder_at is before due_date if both are provided.

        Raises:
            ValueError: If reminder_at is after due_date
        """
        if self.reminder_at and self.due_date:
            if self.reminder_at >= self.due_date:
                raise ValueError("reminder_at must be before due_date")
        return self

    @model_validator(mode="after")
    def validate_recurrence_pattern_config(self):
        """
        Validate that recurrence_config is only provided when recurrence_pattern is 'custom'.

        Raises:
            ValueError: If recurrence_config provided without custom pattern
        """
        if self.recurrence_config and self.recurrence_pattern != "custom":
            raise ValueError("recurrence_config can only be used with recurrence_pattern='custom'")
        return self
