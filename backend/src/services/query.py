"""Query service for building dynamic task queries with filters, search, and sorting."""

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from sqlalchemy import exists, or_, text
from sqlalchemy.orm import selectinload
from sqlalchemy.sql import Select
from sqlmodel import select

from ..models.task_tag import TaskTag  # Import junction table first
from ..models.task import Task
from ..models.tag import Tag


class QueryService:
    """Service for building dynamic SQLAlchemy queries with filters and search."""

    @staticmethod
    def build_task_query(
        user_id: UUID,
        status: Optional[str] = None,
        priority: Optional[str] = None,
        tags: Optional[List[str]] = None,
        due_before: Optional[datetime] = None,
        due_after: Optional[datetime] = None,
        search: Optional[str] = None,
        sort_by: str = "sort_order",
        order: str = "asc",
    ) -> Select:
        """
        Build dynamic task query with filters, full-text search, and sorting.

        All filters use AND logic (all conditions must match).
        Multiple tags use OR logic (match any of the specified tags).

        Args:
            user_id: Owner user ID (required for user isolation)
            status: Filter by completion status ("complete" or "incomplete")
            priority: Filter by priority level ("low", "medium", "high")
            tags: List of tag names to filter by (OR logic), or ["none"] for untagged tasks
            due_before: Filter tasks due before this datetime
            due_after: Filter tasks due after this datetime
            search: Full-text search query (searches title and description)
            sort_by: Column to sort by ("created_at", "due_date", "priority", "title", "sort_order")
            order: Sort order ("asc" or "desc")

        Returns:
            SQLAlchemy Select statement with filters, eager loading, and sorting applied

        Example:
            >>> stmt = QueryService.build_task_query(
            ...     user_id=user_id,
            ...     status="incomplete",
            ...     priority="high",
            ...     tags=["work", "urgent"],
            ...     sort_by="due_date",
            ...     order="asc"
            ... )
            >>> result = await session.execute(stmt)
            >>> tasks = result.scalars().all()
        """
        # Base query with user isolation and soft delete filter
        stmt = (
            select(Task)
            .where(Task.user_id == user_id)
            .where(Task.deleted_at.is_(None))
            # Eager load tags (prevents N+1 queries)
            .options(selectinload(Task.tags))
        )

        # Filter by completion status
        if status == "complete":
            stmt = stmt.where(Task.completed == True)
        elif status == "incomplete":
            stmt = stmt.where(Task.completed == False)

        # Filter by priority
        if priority:
            stmt = stmt.where(Task.priority == priority)

        # Filter by due date range
        if due_before:
            stmt = stmt.where(Task.due_date < due_before)
        if due_after:
            stmt = stmt.where(Task.due_date > due_after)

        # Filter by tags (with OR logic and special "none" case)
        if tags:
            if "none" in tags:
                # Special case: tasks with no tags
                has_no_tags = ~exists(
                    select(1).where(TaskTag.task_id == Task.id).select_from(TaskTag)
                )

                if len(tags) == 1:
                    # Only "none" - return untagged tasks
                    stmt = stmt.where(has_no_tags)
                else:
                    # "none" + other tag names - return untagged OR tagged with specified tags
                    tag_names = [t for t in tags if t != "none"]
                    has_tags = exists(
                        select(1)
                        .select_from(TaskTag)
                        .join(Tag, TaskTag.tag_id == Tag.id)
                        .where(TaskTag.task_id == Task.id)
                        .where(Tag.user_id == user_id)
                        .where(Tag.name.in_(tag_names))
                        .where(Tag.deleted_at.is_(None))
                    )
                    stmt = stmt.where(or_(has_no_tags, has_tags))
            else:
                # Tasks with any of the specified tags (OR logic)
                stmt = stmt.where(
                    exists(
                        select(1)
                        .select_from(TaskTag)
                        .join(Tag, TaskTag.tag_id == Tag.id)
                        .where(TaskTag.task_id == Task.id)
                        .where(Tag.user_id == user_id)
                        .where(Tag.name.in_(tags))
                        .where(Tag.deleted_at.is_(None))
                    )
                )

        # Full-text search using PostgreSQL to_tsvector and GIN index
        if search:
            stmt = stmt.where(
                text(
                    """
                    to_tsvector('english', coalesce(title, '') || ' ' || coalesce(description, ''))
                    @@ plainto_tsquery('english', :search)
                    """
                ).bindparams(search=search)
            )

        # Sorting (T043 - sqlmodel-expert: defaults to sort_order for drag-and-drop)
        sort_column = getattr(Task, sort_by, Task.sort_order)
        if order == "asc":
            stmt = stmt.order_by(sort_column.asc())
        else:
            stmt = stmt.order_by(sort_column.desc())

        return stmt
