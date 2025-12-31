"""Tag repository for data access operations."""

from datetime import datetime, timezone
from typing import List, Optional
from uuid import UUID

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from ..models.tag import Tag
from ..schemas.tag import TagCreate, TagUpdate


class TagRepository:
    """Repository for Tag database operations."""

    def __init__(self, session: AsyncSession):
        """
        Initialize the TagRepository.

        Args:
            session: Async database session
        """
        self.session = session

    async def create(self, user_id: UUID, data: TagCreate) -> Tag:
        """
        Create a new tag.

        Args:
            user_id: Owner user ID (from JWT)
            data: Tag creation data

        Returns:
            Created tag with generated ID

        Raises:
            IntegrityError: If tag name already exists for this user
        """
        tag = Tag(
            **data.model_dump(),
            user_id=user_id,
        )
        self.session.add(tag)
        await self.session.flush()
        await self.session.refresh(tag)
        return tag

    async def get_by_id(self, user_id: UUID, tag_id: int) -> Optional[Tag]:
        """
        Get tag by ID with user isolation and soft delete filter.

        Args:
            user_id: Owner user ID
            tag_id: Tag ID

        Returns:
            Tag if found and active, None otherwise
        """
        stmt = (
            select(Tag)
            .where(Tag.id == tag_id)
            .where(Tag.user_id == user_id)
            .where(Tag.deleted_at.is_(None))
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_tags(self, user_id: UUID) -> List[Tag]:
        """
        List all active tags for a user.

        Args:
            user_id: Owner user ID

        Returns:
            List of active tags sorted by creation date (newest first)
        """
        stmt = (
            select(Tag)
            .where(Tag.user_id == user_id)
            .where(Tag.deleted_at.is_(None))  # Soft delete filter
            .order_by(Tag.created_at.desc())
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def update(
        self, user_id: UUID, tag_id: int, data: TagUpdate
    ) -> Optional[Tag]:
        """
        Update tag fields (partial update).

        Args:
            user_id: Owner user ID
            tag_id: Tag ID to update
            data: Fields to update

        Returns:
            Updated tag if found, None otherwise
        """
        tag = await self.get_by_id(user_id, tag_id)
        if not tag:
            return None

        # Update only provided fields
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(tag, field, value)

        await self.session.flush()
        await self.session.refresh(tag)
        return tag

    async def soft_delete(self, user_id: UUID, tag_id: int) -> bool:
        """
        Soft delete tag by setting deleted_at timestamp.

        Note: TaskTag junction records are preserved (cascade=False).

        Args:
            user_id: Owner user ID
            tag_id: Tag ID to delete

        Returns:
            True if tag was deleted, False if not found
        """
        tag = await self.get_by_id(user_id, tag_id)
        if not tag:
            return False

        tag.deleted_at = datetime.now(timezone.utc)
        await self.session.flush()
        return True

    async def exists_by_name(self, user_id: UUID, name: str) -> bool:
        """
        Check if tag name already exists for user (excluding soft-deleted tags).

        Used for enforcing unique constraint before create/update operations.

        Args:
            user_id: Owner user ID
            name: Tag name to check

        Returns:
            True if tag name exists, False otherwise
        """
        stmt = (
            select(Tag)
            .where(Tag.user_id == user_id)
            .where(Tag.name == name)
            .where(Tag.deleted_at.is_(None))
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none() is not None
