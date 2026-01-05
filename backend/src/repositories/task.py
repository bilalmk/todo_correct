"""Task repository for data access operations."""

from datetime import datetime, timezone
from typing import List, Optional
from uuid import UUID

from sqlalchemy.orm import selectinload
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from ..models.task_tag import TaskTag  # Import junction table first
from ..models.task import Task
from ..models.tag import Tag
from ..schemas.task import TaskCreate, TaskUpdate, TaskReplace


class TaskRepository:
    """Repository for Task database operations with eager loading support."""

    def __init__(self, session: AsyncSession):
        """
        Initialize the TaskRepository.

        Args:
            session: Async database session
        """
        self.session = session

    def _get_eager_load_options(self):
        """
        Get SQLAlchemy options for eager loading tags relationship.

        This prevents N+1 query problem by loading tags in a separate query
        using selectinload (executes 1 query for tasks + 1 query for all tags).

        Returns:
            SelectInLoad option for eager loading tags
        """
        return selectinload(Task.tags)

    async def create(self, user_id: UUID, data: TaskCreate) -> Task:
        """
        Create a new task.

        Args:
            user_id: Owner user ID (from JWT)
            data: Task creation data

        Returns:
            Created task with generated ID and empty tags list
        """
        task = Task(
            **data.model_dump(),
            user_id=user_id,
        )
        self.session.add(task)
        await self.session.flush()
        # Refresh with tags relationship (will be empty for new task)
        await self.session.refresh(task, ["tags"])
        return task

    async def get_by_id(self, user_id: UUID, task_id: int) -> Optional[Task]:
        """
        Get task by ID with user isolation, soft delete filter, and eager-loaded tags.

        Args:
            user_id: Owner user ID
            task_id: Task ID

        Returns:
            Task with nested tags if found and active, None otherwise
        """
        stmt = (
            select(Task)
            .where(Task.id == task_id)
            .where(Task.user_id == user_id)
            .where(Task.deleted_at.is_(None))
            .options(self._get_eager_load_options())
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_tasks(self, user_id: UUID) -> List[Task]:
        """
        List all active tasks for a user.

        Args:
            user_id: Owner user ID

        Returns:
            List of tasks with nested tags, sorted by creation date (newest first)
        """
        stmt = (
            select(Task)
            .where(Task.user_id == user_id)
            .where(Task.deleted_at.is_(None))  # Soft delete filter
            .options(self._get_eager_load_options())
            .order_by(Task.created_at.desc())
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def update(
        self, user_id: UUID, task_id: int, data: TaskUpdate
    ) -> Optional[Task]:
        """
        Partial update task fields (PATCH semantics).

        Only updates provided fields, leaves others unchanged.

        Args:
            user_id: Owner user ID
            task_id: Task ID to update
            data: Fields to update (only non-None values are applied)

        Returns:
            Updated task with nested tags if found, None otherwise
        """
        task = await self.get_by_id(user_id, task_id)
        if not task:
            return None

        # Update only provided fields
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(task, field, value)

        # Update timestamp
        task.updated_at = datetime.now(timezone.utc)

        await self.session.flush()
        await self.session.refresh(task, ["tags"])
        return task

    async def replace(
        self, user_id: UUID, task_id: int, data: TaskReplace
    ) -> Optional[Task]:
        """
        Full replacement of task fields (PUT semantics).

        All fields are replaced with provided values.

        Args:
            user_id: Owner user ID
            task_id: Task ID to replace
            data: All task fields (required fields must be provided)

        Returns:
            Replaced task with nested tags if found, None otherwise
        """
        task = await self.get_by_id(user_id, task_id)
        if not task:
            return None

        # Replace all fields (model_dump includes all fields, even None values)
        replace_data = data.model_dump()
        for field, value in replace_data.items():
            setattr(task, field, value)

        # Update timestamp
        task.updated_at = datetime.now(timezone.utc)

        await self.session.flush()
        await self.session.refresh(task, ["tags"])
        return task

    async def soft_delete(self, user_id: UUID, task_id: int) -> bool:
        """
        Soft delete task by setting deleted_at timestamp.

        Note: TaskTag junction records are preserved (cascade=False).
        Soft-deleted tasks are excluded from queries via deleted_at IS NULL filter.

        Args:
            user_id: Owner user ID
            task_id: Task ID to delete

        Returns:
            True if task was deleted, False if not found
        """
        task = await self.get_by_id(user_id, task_id)
        if not task:
            return False

        task.deleted_at = datetime.now(timezone.utc)
        task.updated_at = datetime.now(timezone.utc)
        await self.session.flush()
        return True

    async def reorder_tasks(self, user_id: UUID, task_ids: List[int]) -> bool:
        """
        Reorder tasks by updating sort_order based on drag-and-drop array position.

        T041 - Uses sqlmodel-expert bulk update pattern for efficient transaction handling.

        Algorithm:
        1. Fetch all tasks by IDs with user isolation
        2. Validate all tasks belong to the user
        3. Update sort_order for each task (position in array = sort_order)
        4. Commit transaction (caller responsibility)

        Args:
            user_id: Owner user ID (ensures user isolation)
            task_ids: Ordered array of task IDs (position = new sort_order)

        Returns:
            True if reorder succeeded, False if any task not found or access denied

        Raises:
            None - Returns False on validation errors

        Example:
            task_ids = [5, 2, 8, 1, 3]
            # Task 5 → sort_order=1, Task 2 → sort_order=2, etc.
        """
        # Validate all tasks exist and belong to user (sqlmodel-expert: user isolation pattern)
        stmt = (
            select(Task)
            .where(Task.id.in_(task_ids))
            .where(Task.user_id == user_id)
            .where(Task.deleted_at.is_(None))
        )
        result = await self.session.execute(stmt)
        tasks = list(result.scalars().all())

        # Validation: ensure all requested tasks were found
        if len(tasks) != len(task_ids):
            return False  # Some tasks not found or access denied

        # Build task ID → Task object mapping for efficient lookup
        task_map = {task.id: task for task in tasks}

        # Update sort_order for each task (sqlmodel-expert: bulk update pattern)
        # Use sequential increments of 1000 per data-model.md spec (1000, 2000, 3000, ...)
        now = datetime.now(timezone.utc)
        for position, task_id in enumerate(task_ids, start=1):
            task = task_map.get(task_id)
            if task:  # Extra safety check
                task.sort_order = position * 1000  # Sequential: 1000, 2000, 3000, ...
                task.updated_at = now

        # Flush changes to database (sqlmodel-expert: transaction pattern)
        # Note: Caller must commit() the session to finalize transaction
        await self.session.flush()
        return True
