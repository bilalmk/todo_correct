"""TaskTag junction table for many-to-many task-tag relationships."""
from datetime import datetime, timezone
from typing import Optional
from sqlmodel import Field, SQLModel, Column, Index
from sqlalchemy import BigInteger, DateTime, ForeignKey


class TaskTag(SQLModel, table=True):
    """
    Junction table for many-to-many relationship between tasks and tags.

    Uses composite primary key (task_id, tag_id) to ensure each task-tag
    pair is unique. Both foreign keys CASCADE delete to maintain referential integrity.
    """

    __tablename__ = "task_tags"

    # Composite primary key: (task_id, tag_id)
    task_id: int = Field(
        sa_column=Column(
            BigInteger,
            ForeignKey("tasks.id", ondelete="CASCADE"),
            primary_key=True,
            nullable=False,
        ),
        description="Reference to task",
    )

    tag_id: int = Field(
        sa_column=Column(
            BigInteger,
            ForeignKey("tags.id", ondelete="CASCADE"),
            primary_key=True,
            nullable=False,
        ),
        description="Reference to tag",
    )

    # Timestamp for when the relationship was created
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(DateTime(timezone=True), nullable=False),
        description="Relationship creation timestamp (UTC)",
    )

    # Table-level indexes
    __table_args__ = (
        # Index for reverse lookup: find all tasks for a given tag
        Index("idx_task_tags_tag_id", "tag_id"),
        # Forward lookup (task_id) is already covered by composite PK
        {"extend_existing": True},  # Allow table redefinition in tests
    )

    class Config:
        """Pydantic configuration."""

        json_schema_extra = {
            "example": {
                "task_id": 1,
                "tag_id": 1,
            }
        }
