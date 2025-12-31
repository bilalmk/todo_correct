"""Conftest for unit tests - provides user fixtures."""
import pytest_asyncio
from uuid import UUID
from src.models.user import User
from sqlmodel.ext.asyncio.session import AsyncSession


@pytest_asyncio.fixture
async def test_user_unit(test_session: AsyncSession) -> User:
    """Create a test user for unit tests."""
    from src.services.user import create_user
    from src.models.user import UserCreate
    from uuid import uuid4

    # Generate unique email for each test to avoid constraint violations
    unique_email = f"test-unit-{uuid4().hex[:8]}@example.com"

    user_data = UserCreate(
        email=unique_email,
        password="testpassword123",
        name="Test User",
    )

    user = await create_user(test_session, user_data)
    await test_session.commit()
    await test_session.refresh(user)

    return user


@pytest_asyncio.fixture
async def user_id_unit(test_user_unit: User) -> UUID:
    """Return test user ID as UUID."""
    return test_user_unit.id
