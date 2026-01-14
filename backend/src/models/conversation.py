"""Conversation model for ChatKit backend - user chat sessions.

Feature: 008-chatkit-server-backend
Phase: II (Foundational)
Task: T005 - Create Conversation SQLModel
Data Model: specs/008-chatkit-server-backend/data-model.md
"""

from datetime import datetime, timezone
from typing import Optional, List, TYPE_CHECKING
from uuid import UUID, uuid4

from sqlmodel import Field, SQLModel, Relationship, Index, Column
from sqlalchemy import DateTime, text

if TYPE_CHECKING:
    from .message import Message


class Conversation(SQLModel, table=True):
    """
    Conversation model representing a chat session between user and AI assistant.

    Constitutional Requirements:
    - User-scoped data: user_id foreign key (Section 3: Multi-Tenancy)
    - Soft deletes: deleted_at timestamp (Section 3: Database Design)
    - Audit timestamps: created_at, updated_at (Section 3: Database Design)
    - UUID primary key: No sequential IDs exposed (Section 3: Database Design)

    Cardinality:
    - One user has ONE active conversation (unique constraint with WHERE deleted_at IS NULL)
    - One conversation has MANY messages (one-to-many relationship)

    State Transitions:
    - Active (deleted_at = NULL) → Soft-Deleted (deleted_at = timestamp)
    - Triggered by: DELETE /api/chatkit/conversation endpoint (FR-020)
    """

    __tablename__ = "conversations"

    # Primary Key
    conversation_id: UUID = Field(
        default_factory=uuid4,
        primary_key=True,
        nullable=False,
        description="Auto-generated UUID primary key"
    )

    # Foreign Key to Better Auth user table (references user.uuid, not user.id)
    user_id: UUID = Field(
        foreign_key="user.uuid",
        nullable=False,
        index=True,
        description="Owner of conversation (Better Auth user UUID)"
    )

    # Timestamps (UTC timezone)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(DateTime(timezone=True), nullable=False),
        description="Creation timestamp (UTC)"
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(DateTime(timezone=True), nullable=False),
        description="Last modified timestamp (UTC)"
    )

    # Soft Delete Timestamp (NULL = active, NOT NULL = deleted)
    deleted_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), nullable=True),
        description="Soft delete timestamp (NULL = active)"
    )

    # Relationships
    messages: List["Message"] = Relationship(
        back_populates="conversation",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )

    # Table-level constraints and indexes
    __table_args__ = (
        # Unique constraint: Only one active conversation per user
        # Uses partial index with WHERE clause (PostgreSQL-specific)
        Index(
            "idx_conversations_user_active",
            "user_id",
            unique=True,
            postgresql_where=text("deleted_at IS NULL")
        ),
        # Index for querying conversations by user (general queries)
        Index("idx_conversations_user_id", "user_id"),
    )

    class Config:
        """Pydantic model configuration."""
        json_schema_extra = {
            "example": {
                "conversation_id": "550e8400-e29b-41d4-a716-446655440000",
                "user_id": "660e8400-e29b-41d4-a716-446655440001",
                "created_at": "2026-01-08T10:30:00Z",
                "updated_at": "2026-01-08T10:35:00Z",
                "deleted_at": None
            }
        }


# Note: CASCADE behavior ensures when user is deleted, all conversations are deleted
# Note: ON DELETE CASCADE for user_id ensures referential integrity
