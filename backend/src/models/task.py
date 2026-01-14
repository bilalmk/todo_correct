"""Task model for todo application."""
from datetime import datetime, timezone
from typing import Optional, List, TYPE_CHECKING
from uuid import UUID
from sqlmodel import Field, SQLModel, Column, Index, text, Relationship
from sqlalchemy import BigInteger, DateTime, Text, CheckConstraint, String, JSON

# Import TaskTag junction table (defined before this model)
from .task_tag import TaskTag

if TYPE_CHECKING:
    from .tag import Tag


class Task(SQLModel, table=True):
    """
    Task model representing a todo item.

    Supports Phase II (basic features) and Phase V (advanced features).
    Advanced fields (priority, due_date, reminder_at, recurrence_*) are nullable
    to maintain backward compatibility with Phase II.
    """

    __tablename__ = "tasks"

    # Primary key - BIGSERIAL for 64-bit auto-incrementing ID
    id: Optional[int] = Field(
        default=None,
        sa_column=Column(BigInteger, primary_key=True, autoincrement=True),
    )

    # Foreign key to user table (uuid column) with ON DELETE CASCADE
    user_id: UUID = Field(
        foreign_key="user.uuid",
        nullable=False,
        index=True,
        ondelete="CASCADE",
        description="Owner of the task",
    )

    # Basic fields (Phase II)
    title: str = Field(
        max_length=255,
        nullable=False,
        description="Task title (required)",
    )

    description: Optional[str] = Field(
        default=None,
        sa_column=Column(Text),
        description="Detailed description (max 10,000 chars)",
    )

    completed: bool = Field(
        default=False,
        nullable=False,
        index=True,
        description="Completion status",
    )

    # Timestamp fields (TIMESTAMPTZ for UTC storage)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(DateTime(timezone=True), nullable=False),
        description="Creation timestamp (UTC)",
    )

    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(DateTime(timezone=True), nullable=False),
        description="Last update timestamp (UTC)",
    )

    deleted_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True)),
        description="Soft delete timestamp (NULL = active)",
    )

    # Advanced fields (Phase V - Intermediate)
    priority: Optional[str] = Field(
        default=None,
        max_length=20,
        description="Task priority: low, medium, or high",
    )

    due_date: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True)),
        description="Task deadline (UTC)",
    )

    # Advanced fields (Phase V - Advanced)
    reminder_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True)),
        description="Reminder trigger time (UTC)",
    )

    recurrence_pattern: Optional[str] = Field(
        default=None,
        max_length=20,
        description="Recurrence type: daily, weekly, monthly, or custom",
    )

    recurrence_config: Optional[dict] = Field(
        default=None,
        sa_column=Column(JSON),
        description="JSONB field storing iCalendar RRULE format",
    )

    # Drag-and-drop ordering (Phase III - UI Enhancement)
    sort_order: int = Field(
        default=0,
        sa_column=Column(BigInteger, nullable=False, index=True),
        description="User-defined position for manual task ordering (lower = higher in list)",
    )

    # Relationships
    tags: List["Tag"] = Relationship(
        back_populates="tasks",
        link_model=TaskTag,  # Use actual class, not string (per sqlmodel-expert guide)
        sa_relationship_kwargs={"lazy": "select"},
    )

    # Table-level constraints and indexes
    __table_args__ = (
        # Composite index: user_id + completed (for filtering by completion status)
        Index("idx_tasks_user_completed", "user_id", "completed"),
        # Composite index: user_id + sort_order (for efficient sorted task queries)
        Index("idx_tasks_user_sort_order", "user_id", "sort_order"),
        # Partial index: user_id + priority (only for tasks with priority set)
        Index(
            "idx_tasks_user_priority",
            "user_id",
            "priority",
            postgresql_where=text("priority IS NOT NULL"),
        ),
        # Partial index: user_id + due_date (only for tasks with due dates)
        Index(
            "idx_tasks_user_due_date",
            "user_id",
            "due_date",
            postgresql_where=text("due_date IS NOT NULL"),
        ),
        # Composite index for notification service: due_date + reminder_at
        # Only for active tasks with reminders
        Index(
            "idx_tasks_due_reminders",
            "due_date",
            "reminder_at",
            postgresql_where=text("completed = FALSE AND deleted_at IS NULL"),
        ),
        # Check constraint: priority must be one of the allowed values
        CheckConstraint(
            "priority IN ('low', 'medium', 'high') OR priority IS NULL",
            name="check_priority_enum",
        ),
        # Check constraint: recurrence_pattern must be one of the allowed values
        CheckConstraint(
            "recurrence_pattern IN ('daily', 'weekly', 'monthly', 'custom') OR recurrence_pattern IS NULL",
            name="check_recurrence_pattern_enum",
        ),
        # Check constraint: description max length 10,000 characters
        CheckConstraint(
            "length(description) <= 10000",
            name="check_description_length",
        ),
        {"extend_existing": True},  # Allow table redefinition in tests
    )

    class Config:
        """Pydantic configuration."""

        json_schema_extra = {
            "example": {
                "user_id": 1,
                "title": "Buy groceries",
                "description": "Milk, eggs, bread",
                "completed": False,
                "priority": "high",
                "due_date": "2025-12-30T10:00:00Z",
                "reminder_at": "2025-12-30T09:45:00Z",
            }
        }
