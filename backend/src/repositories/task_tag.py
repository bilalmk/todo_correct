"""TaskTag repository for managing task-tag relationships."""

from datetime import datetime, timezone
from typing import List, Optional
from uuid import UUID

from sqlalchemy.exc import IntegrityError
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from ..models.task_tag import TaskTag  # Import junction table first
from ..models.task import Task
from ..models.tag import Tag


class TaskTagRepository:
    """Repository for TaskTag many-to-many relationship operations."""

    def __init__(self, session: AsyncSession):
        """
        Initialize the TaskTagRepository.

        Args:
            session: Async database session
        """
        self.session = session

    async def assign_tag(self, user_id: UUID, task_id: int, tag_id: int) -> bool:
        """
        Assign a tag to a task (create TaskTag relationship).

        Validates that both task and tag exist, belong to the user, and are not soft-deleted.

        Args:
            user_id: Owner user ID
            task_id: Task ID
            tag_id: Tag ID to assign

        Returns:
            True if assignment succeeded

        Raises:
            IntegrityError: If relationship already exists (duplicate assignment)
            ValueError: If task or tag not found or doesn't belong to user
        """
        # Verify task exists and belongs to user
        task_stmt = (
            select(Task)
            .where(Task.id == task_id)
            .where(Task.user_id == user_id)
            .where(Task.deleted_at.is_(None))
        )
        task_result = await self.session.execute(task_stmt)
        task = task_result.scalar_one_or_none()
        if not task:
            raise ValueError("Task not found or does not belong to user")

        # Verify tag exists and belongs to user
        tag_stmt = (
            select(Tag)
            .where(Tag.id == tag_id)
            .where(Tag.user_id == user_id)
            .where(Tag.deleted_at.is_(None))
        )
        tag_result = await self.session.execute(tag_stmt)
        tag = tag_result.scalar_one_or_none()
        if not tag:
            raise ValueError("Tag not found or does not belong to user")

        # Create relationship
        task_tag = TaskTag(task_id=task_id, tag_id=tag_id)
        self.session.add(task_tag)
        await self.session.flush()
        return True

    async def unassign_tag(self, user_id: UUID, task_id: int, tag_id: int) -> bool:
        """
        Remove a tag from a task (delete TaskTag relationship).

        Args:
            user_id: Owner user ID
            task_id: Task ID
            tag_id: Tag ID to unassign

        Returns:
            True if unassignment succeeded, False if relationship didn't exist
        """
        # Verify task belongs to user (soft delete filtered)
        task_stmt = (
            select(Task)
            .where(Task.id == task_id)
            .where(Task.user_id == user_id)
            .where(Task.deleted_at.is_(None))
        )
        task_result = await self.session.execute(task_stmt)
        task = task_result.scalar_one_or_none()
        if not task:
            return False

        # Delete TaskTag relationship
        task_tag_stmt = (
            select(TaskTag)
            .where(TaskTag.task_id == task_id)
            .where(TaskTag.tag_id == tag_id)
        )
        result = await self.session.execute(task_tag_stmt)
        task_tag = result.scalar_one_or_none()

        if not task_tag:
            return False

        await self.session.delete(task_tag)
        await self.session.flush()
        return True

    async def get_task_tags(self, user_id: UUID, task_id: int) -> List[Tag]:
        """
        Get all tags assigned to a task (excludes soft-deleted tags).

        Args:
            user_id: Owner user ID
            task_id: Task ID

        Returns:
            List of active tags assigned to the task
        """
        # Verify task belongs to user
        task_stmt = (
            select(Task)
            .where(Task.id == task_id)
            .where(Task.user_id == user_id)
            .where(Task.deleted_at.is_(None))
        )
        task_result = await self.session.execute(task_stmt)
        task = task_result.scalar_one_or_none()
        if not task:
            return []

        # Get tags via TaskTag junction (with soft delete filter)
        stmt = (
            select(Tag)
            .join(TaskTag, Tag.id == TaskTag.tag_id)
            .where(TaskTag.task_id == task_id)
            .where(Tag.deleted_at.is_(None))  # Exclude soft-deleted tags
            .order_by(Tag.name)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
