"""Notification model for scheduling and tracking notifications."""
from datetime import datetime, timezone
from typing import Optional
from uuid import UUID
from sqlmodel import Field, SQLModel, Column, Index, text
from sqlalchemy import BigInteger, DateTime, Text, CheckConstraint, ForeignKey


class Notification(SQLModel, table=True):
    """
    Notification model for tracking reminders and alerts.

    Supports various notification types (task reminders, due date alerts)
    and channels (email, push, sms). Tracks delivery status and errors.
    """

    __tablename__ = "notifications"

    # Primary key - BIGSERIAL for 64-bit auto-incrementing ID
    id: Optional[int] = Field(
        default=None,
        sa_column=Column(BigInteger, primary_key=True, autoincrement=True),
    )

    # Foreign key to user table (uuid column) with ON DELETE CASCADE
    user_id: UUID = Field(
        sa_column=Column(
            ForeignKey("user.uuid", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        description="Owner of the notification",
    )

    # Optional foreign key to tasks table with ON DELETE SET NULL
    task_id: Optional[int] = Field(
        default=None,
        sa_column=Column(
            BigInteger,
            ForeignKey("tasks.id", ondelete="SET NULL"),
            nullable=True,
        ),
        description="Related task (nullable)",
    )

    # Notification type (task_reminder, task_due, task_overdue, etc.)
    type: str = Field(
        max_length=50,
        nullable=False,
        description="Notification type",
    )

    # Delivery channel (email, push, sms, webhook)
    channel: str = Field(
        max_length=20,
        nullable=False,
        description="Delivery channel",
    )

    # Recipient address (email, phone number, device token, etc.)
    recipient: str = Field(
        max_length=255,
        nullable=False,
        description="Recipient address",
    )

    # Notification subject/title
    subject: str = Field(
        max_length=255,
        nullable=False,
        description="Notification subject",
    )

    # Notification body/message
    body: str = Field(
        sa_column=Column(Text, nullable=False),
        description="Notification body (max 10,000 chars)",
    )

    # Delivery status (pending, sent, failed)
    status: str = Field(
        max_length=20,
        nullable=False,
        description="Delivery status",
    )

    # Timestamp when notification was sent (NULL if not sent yet)
    sent_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True)),
        description="Sent timestamp (UTC)",
    )

    # Error message if delivery failed
    error_message: Optional[str] = Field(
        default=None,
        sa_column=Column(Text, nullable=True),
        description="Error message if failed",
    )

    # Creation timestamp
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(DateTime(timezone=True), nullable=False),
        description="Creation timestamp (UTC)",
    )

    # Table-level constraints and indexes
    __table_args__ = (
        # Index for user-scoped queries
        Index("idx_notifications_user_id", "user_id"),
        # Partial index for task-related notifications
        Index(
            "idx_notifications_task_id",
            "task_id",
            postgresql_where=text("task_id IS NOT NULL"),
        ),
        # Partial index for pending notifications (for notification service)
        Index(
            "idx_notifications_pending",
            "user_id",
            "status",
            postgresql_where=text("status = 'pending'"),
        ),
        # Check constraint: type must be one of allowed values
        CheckConstraint(
            "type IN ('task_reminder', 'task_due', 'task_overdue', 'task_completed', 'system')",
            name="check_notification_type_enum",
        ),
        # Check constraint: channel must be one of allowed values
        CheckConstraint(
            "channel IN ('email', 'push', 'sms', 'webhook')",
            name="check_notification_channel_enum",
        ),
        # Check constraint: status must be one of allowed values
        CheckConstraint(
            "status IN ('pending', 'sent', 'failed')",
            name="check_notification_status_enum",
        ),
        # Check constraint: body max length 10,000 characters
        CheckConstraint(
            "length(body) <= 10000",
            name="check_notification_body_length",
        ),
        {"extend_existing": True},  # Allow table redefinition in tests
    )

    class Config:
        """Pydantic configuration."""

        json_schema_extra = {
            "example": {
                "user_id": "123e4567-e89b-12d3-a456-426614174000",
                "task_id": 1,
                "type": "task_reminder",
                "channel": "email",
                "recipient": "user@example.com",
                "subject": "Task reminder: Buy groceries",
                "body": "Don't forget to buy groceries today!",
                "status": "pending",
            }
        }
