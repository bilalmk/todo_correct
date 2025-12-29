"""User service layer for business logic."""
from typing import Optional
from uuid import UUID

from sqlalchemy.exc import IntegrityError
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from ..core.security import hash_password
from ..models.user import User, UserCreate


async def create_user(session: AsyncSession, user_data: UserCreate) -> User:
    """
    Create a new user account.

    Args:
        session: Database session
        user_data: User registration data

    Returns:
        Created user

    Raises:
        IntegrityError: If email already exists

    Example:
        try:
            user = await create_user(session, user_data)
        except IntegrityError:
            raise HTTPException(400, "Email already registered")
    """
    # Hash password
    password_hash = hash_password(user_data.password)

    # Create user instance
    db_user = User(
        email=user_data.email,
        name=user_data.name,
        password_hash=password_hash,
    )

    # Save to database
    session.add(db_user)
    await session.commit()
    await session.refresh(db_user)

    return db_user


async def get_user_by_email(session: AsyncSession, email: str) -> Optional[User]:
    """
    Get user by email address.

    Args:
        session: Database session
        email: User's email (case-insensitive)

    Returns:
        User if found, None otherwise

    Example:
        user = await get_user_by_email(session, "user@example.com")
        if user:
            # User exists
    """
    statement = select(User).where(User.email == email.lower())
    result = await session.execute(statement)
    return result.scalar_one_or_none()


async def get_user_by_id(session: AsyncSession, user_id: UUID) -> Optional[User]:
    """
    Get user by ID.

    Args:
        session: Database session
        user_id: User's UUID

    Returns:
        User if found, None otherwise

    Example:
        user = await get_user_by_id(session, user_id)
    """
    statement = select(User).where(User.id == user_id)
    result = await session.execute(statement)
    return result.scalar_one_or_none()
