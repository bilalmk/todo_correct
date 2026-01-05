"""Tag model for task categorization."""
from datetime import datetime, timezone
from typing import Optional, List, TYPE_CHECKING
from uuid import UUID
from sqlmodel import Field, SQLModel, Column, Index, text, Relationship
from sqlalchemy import BigInteger, DateTime, CheckConstraint

# Import TaskTag junction table (defined before this model)
from .task_tag import TaskTag

if TYPE_CHECKING:
    from .task import Task


class Tag(SQLModel, table=True):
    """
    Tag model for categorizing tasks with labels (work, personal, urgent).

    Supports many-to-many relationship with tasks through TaskTag junction table.
    Includes soft delete functionality with partial unique constraint.
    """

    __tablename__ = "tags"

    # Primary key - BIGSERIAL for 64-bit auto-incrementing ID
    id: Optional[int] = Field(
        default=None,
        sa_column=Column(BigInteger, primary_key=True, autoincrement=True),
    )

    # Foreign key to users table with ON DELETE CASCADE
    user_id: UUID = Field(
        foreign_key="user.uuid",
        nullable=False,
        index=True,
        ondelete="CASCADE",
        description="Owner of the tag",
    )

    # Tag name (required, max 50 chars)
    name: str = Field(
        max_length=50,
        nullable=False,
        description="Tag name (e.g., 'work', 'personal', 'urgent')",
    )

    # Optional color in hex format (#RRGGBB)
    color: Optional[str] = Field(
        default=None,
        max_length=7,
        description="Hex color code (e.g., '#FF5733')",
    )

    # Timestamp fields (TIMESTAMPTZ for UTC storage)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(DateTime(timezone=True), nullable=False),
        description="Creation timestamp (UTC)",
    )

    deleted_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True)),
        description="Soft delete timestamp (NULL = active)",
    )

    # Relationships
    tasks: List["Task"] = Relationship(
        back_populates="tags",
        link_model=TaskTag,  # Use actual class, not string (per sqlmodel-expert guide)
        sa_relationship_kwargs={"lazy": "select"},
    )

    # Table-level constraints and indexes
    __table_args__ = (
        # Composite index: user_id (for efficient user-scoped queries)
        Index("idx_tags_user_id", "user_id"),
        # Partial unique constraint: (user_id, name) WHERE deleted_at IS NULL
        # Allows tag name reuse after soft delete
        Index(
            "idx_tags_user_name_unique",
            "user_id",
            "name",
            unique=True,
            postgresql_where=text("deleted_at IS NULL"),
        ),
        # Check constraint: color must be hex format (#RRGGBB) or NULL
        CheckConstraint(
            "color IS NULL OR color ~ '^#[0-9A-Fa-f]{6}$'",
            name="check_color_hex_format",
        ),
        {"extend_existing": True},  # Allow table redefinition in tests
    )

    class Config:
        """Pydantic configuration."""

        json_schema_extra = {
            "example": {
                "user_id": "123e4567-e89b-12d3-a456-426614174000",
                "name": "work",
                "color": "#FF5733",
            }
        }
