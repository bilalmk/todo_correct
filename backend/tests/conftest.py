"""Pytest fixtures for testing."""
import asyncio
from typing import AsyncGenerator, Generator

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel

from src.core.config import settings
from src.core.database import get_session
from main import app
from src.models.user import User


# Test database URL (use in-memory SQLite for tests)
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """Create event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="function")
async def test_engine() -> AsyncGenerator[AsyncEngine, None]:
    """Create test database engine."""
    engine = create_async_engine(
        TEST_DATABASE_URL,
        echo=False,
        future=True,
    )

    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

    yield engine

    # Drop tables
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)

    await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def test_session(test_engine: AsyncEngine) -> AsyncGenerator[AsyncSession, None]:
    """Create test database session."""
    async_session_maker = sessionmaker(
        test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autocommit=False,
        autoflush=False,
    )

    async with async_session_maker() as session:
        yield session


@pytest.fixture(scope="function")
def override_get_session(test_session: AsyncSession):
    """Override database session dependency."""
    async def _override_get_session():
        yield test_session

    app.dependency_overrides[get_session] = _override_get_session
    yield
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def client(override_get_session) -> Generator:
    """Create test client."""
    with TestClient(app) as test_client:
        yield test_client


@pytest_asyncio.fixture(scope="function")
async def async_client(override_get_session) -> AsyncGenerator:
    """Create async test client."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest_asyncio.fixture
async def test_user(test_session: AsyncSession) -> User:
    """Create a test user."""
    from src.services.user import create_user
    from src.models.user import UserCreate

    user_data = UserCreate(
        email="test@example.com",
        password="testpassword123",
        name="Test User",
    )

    user = await create_user(test_session, user_data)
    await test_session.commit()
    await test_session.refresh(user)

    return user


@pytest_asyncio.fixture
async def auth_headers(test_user: User) -> dict:
    """Create authentication headers with JWT token."""
    from src.core.security import create_access_token

    token = create_access_token(test_user.id, test_user.email)

    return {
        "Authorization": f"Bearer {token}",
    }
