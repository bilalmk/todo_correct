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


# Test database URL (use same PostgreSQL database with asyncpg driver for tests)
# asyncpg uses 'ssl=require' instead of 'sslmode=require'
import os
TEST_DATABASE_URL = os.getenv("DATABASE_URL", "").replace("postgresql+psycopg://", "postgresql+asyncpg://").replace("sslmode=require", "ssl=require") if os.getenv("DATABASE_URL") else "postgresql+asyncpg://neondb_owner:npg_dv3nXfaukYb0@ep-fancy-shadow-a1aw89ne-pooler.ap-southeast-1.aws.neon.tech/todo_web_hackathon_final?ssl=require"


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """Create event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="function")
async def test_engine() -> AsyncGenerator[AsyncEngine, None]:
    """Create test database engine."""
    from sqlalchemy import text
    from sqlalchemy.pool import NullPool

    engine = create_async_engine(
        TEST_DATABASE_URL,
        echo=False,
        future=True,
        poolclass=NullPool,  # Disable connection pooling to avoid cached statement errors
    )

    # Create tables and indexes
    async with engine.begin() as conn:
        # Create tables from SQLModel metadata
        await conn.run_sync(SQLModel.metadata.create_all)

        # Create GIN index for full-text search (from migration 7153bd9cdab5)
        await conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_tasks_fulltext_search ON tasks
            USING gin(to_tsvector('english', coalesce(title, '') || ' ' || coalesce(description, '')))
        """))

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
