"""
Pydantic input validation models for MCP tools.

All tools inherit from BaseToolInput to enforce user_id parameter and validation.
"""

from pydantic import BaseModel, Field, field_validator, ConfigDict, model_validator
from uuid import UUID
from typing import Optional, Literal
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

    At least one of title or description must be provided.
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

    @model_validator(mode="after")
    def validate_at_least_one_field(self):
        """
        Validate that at least one of title or description is provided.

        Raises:
            ValueError: If both title and description are None
        """
        if self.title is None and self.description is None:
            raise ValueError("At least one of 'title' or 'description' must be provided for update")
        return self
