"""User service for Better Auth integration.

T020: Updated to work with Better Auth user table instead of custom users table.
"""
from uuid import UUID
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from ..models.user import User


async def get_user_by_uuid(session: AsyncSession, user_uuid: UUID) -> User | None:
    """
    Get user by UUID from Better Auth user table.

    Args:
        session: Database session
        user_uuid: User UUID

    Returns:
        User if found, None otherwise
    """
    result = await session.execute(
        select(User).where(User.uuid == user_uuid)
    )
    return result.scalar_one_or_none()


async def get_user_by_email(session: AsyncSession, email: str) -> User | None:
    """
    Get user by email from Better Auth user table.

    Args:
        session: Database session
        email: User email address

    Returns:
        User if found, None otherwise
    """
    result = await session.execute(
        select(User).where(User.email == email.lower())
    )
    return result.scalar_one_or_none()


async def get_user_by_id(session: AsyncSession, user_id: UUID) -> User | None:
    """
    Get user by UUID (alias for get_user_by_uuid for backward compatibility).

    Args:
        session: Database session
        user_id: User UUID

    Returns:
        User if found, None otherwise
    """
    return await get_user_by_uuid(session, user_id)


# Removed functions (Better Auth handles these on frontend):
# - create_user() - Registration is handled by Better Auth
# - authenticate_user() - Authentication handled by Better Auth
# - update_user() - User updates handled by Better Auth
