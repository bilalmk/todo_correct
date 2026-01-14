"""Message model for ChatKit backend - conversation messages.

Feature: 008-chatkit-server-backend
Phase: II (Foundational)
Task: T006 - Create Message SQLModel
Data Model: specs/008-chatkit-server-backend/data-model.md
"""

from datetime import datetime, timezone
from typing import Optional, TYPE_CHECKING
from uuid import UUID, uuid4

from sqlmodel import Field, SQLModel, Relationship, Index, Column
from sqlalchemy import DateTime, Text, CheckConstraint

if TYPE_CHECKING:
    from .conversation import Conversation


class Message(SQLModel, table=True):
    """
    Message model representing a single message in a conversation.

    Constitutional Requirements:
    - User-scoped data: user_id denormalized for query performance (Section 3: Multi-Tenancy)
    - Soft deletes: deleted_at cascaded from parent Conversation (Section 3: Database Design)
    - Audit timestamps: created_at only (messages are immutable after creation)
    - UUID primary key: No sequential IDs exposed (Section 3: Database Design)

    Cardinality:
    - Many messages belong to ONE conversation (many-to-one relationship)
    - Many messages belong to ONE user (denormalized for performance)

    Content Limits:
    - Max content length: 10,000 characters (FR-024)
    - Enforced at: Database check constraint + API truncation with warning

    State Transitions:
    - In-Progress (is_complete=false) → Completed (is_complete=true)
    - Triggered by: Streaming response finishes successfully
    - Incomplete state: Stream interrupted (network disconnect, browser close)
    """

    __tablename__ = "messages"

    # Primary Key
    message_id: UUID = Field(
        default_factory=uuid4,
        primary_key=True,
        nullable=False,
        description="Auto-generated UUID primary key"
    )

    # Foreign Key to Conversation
    conversation_id: UUID = Field(
        foreign_key="conversations.conversation_id",
        nullable=False,
        index=True,
        description="Parent conversation UUID"
    )

    # Denormalized user_id for query performance (avoids JOIN for user isolation checks)
    user_id: UUID = Field(
        foreign_key="user.uuid",
        nullable=False,
        index=True,
        description="Message owner UUID (denormalized from conversation.user_id)"
    )

    # Message Content and Metadata
    role: str = Field(
        max_length=20,
        nullable=False,
        description="Message sender role: 'user', 'assistant', or 'system'"
    )

    content: str = Field(
        sa_column=Column(Text, nullable=False),
        description="Message content (max 10,000 characters, enforced by check constraint)"
    )

    is_complete: bool = Field(
        default=True,
        nullable=False,
        description="False if streaming interrupted, True if completed successfully"
    )

    # Timestamps (UTC timezone)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(DateTime(timezone=True), nullable=False),
        description="Message timestamp (UTC)"
    )

    # Soft Delete Timestamp (cascaded from Conversation soft delete)
    deleted_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), nullable=True),
        description="Soft delete timestamp (cascaded from conversation)"
    )

    # Relationships
    conversation: "Conversation" = Relationship(back_populates="messages")

    # Table-level constraints and indexes
    __table_args__ = (
        # Composite index: Load messages chronologically per conversation
        Index("idx_messages_conversation_created", "conversation_id", "created_at"),

        # Index: User isolation queries (filter messages by user_id)
        Index("idx_messages_user_id", "user_id"),

        # Check constraint: Role must be valid enum value
        CheckConstraint(
            "role IN ('user', 'assistant', 'system')",
            name="check_message_role_enum"
        ),

        # Check constraint: Content length <= 10,000 characters (FR-024)
        CheckConstraint(
            "length(content) <= 10000",
            name="check_message_content_length"
        ),
    )

    class Config:
        """Pydantic model configuration."""
        json_schema_extra = {
            "example": {
                "message_id": "770e8400-e29b-41d4-a716-446655440002",
                "conversation_id": "550e8400-e29b-41d4-a716-446655440000",
                "user_id": "660e8400-e29b-41d4-a716-446655440001",
                "role": "user",
                "content": "Add a task to buy groceries",
                "is_complete": True,
                "created_at": "2026-01-08T10:30:00Z",
                "deleted_at": None
            }
        }


# Note: CASCADE behavior ensures:
# - When conversation is deleted, all messages are soft-deleted (application-level cascade)
# - When user is deleted, all messages are deleted (ON DELETE CASCADE foreign key)
# - user_id denormalization avoids JOIN overhead for user isolation checks
