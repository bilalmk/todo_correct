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

# Import ALL models to register them with SQLModel.metadata
# This ensures create_all() knows about all tables and their dependencies
from src.models.user import User
from src.models.task import Task
from src.models.tag import Tag
from src.models.task_tag import TaskTag
from src.models.notification import Notification
from src.models.conversation import Conversation
from src.models.message import Message


# Test database URL - use separate test database
# IMPORTANT: Never use production database for tests!
# Set TEST_DATABASE_URL in .env to a separate test database
import os
import warnings

TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL")

if not TEST_DATABASE_URL:
    # Fallback to DATABASE_URL but warn user
    DATABASE_URL = os.getenv("DATABASE_URL", "")
    if DATABASE_URL:
        TEST_DATABASE_URL = DATABASE_URL.replace("postgresql+psycopg://", "postgresql+asyncpg://").replace("sslmode=require", "ssl=require")
        warnings.warn(
            "WARNING: Using production DATABASE_URL for tests! "
            "This is NOT recommended. Create a separate test database and set TEST_DATABASE_URL in .env",
            UserWarning
        )
    else:
        raise ValueError("Neither TEST_DATABASE_URL nor DATABASE_URL is set in environment")


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

    # Configure based on driver type (asyncpg vs psycopg)
    is_asyncpg = "asyncpg" in TEST_DATABASE_URL

    if is_asyncpg:
        # asyncpg driver options
        connect_args = {
            "prepared_statement_cache_size": 0,
            "statement_cache_size": 0,
        }
    else:
        # psycopg driver options
        connect_args = {
            "prepare_threshold": None,  # Disable prepared statements for psycopg
        }

    engine = create_async_engine(
        TEST_DATABASE_URL,
        echo=False,
        future=True,
        poolclass=NullPool,  # Disable connection pooling to avoid cached statement errors
        connect_args=connect_args,
    )

    # Drop any existing tables first to ensure clean state
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)

    # Create tables and indexes
    async with engine.begin() as conn:
        # Create tables from SQLModel metadata
        await conn.run_sync(SQLModel.metadata.create_all)

        # Create GIN index for full-text search (from migration 7153bd9cdab5)
        # Only for PostgreSQL
        if "postgresql" in str(engine.url):
            await conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_tasks_fulltext_search ON tasks
                USING gin(to_tsvector('english', coalesce(title, '') || ' ' || coalesce(description, '')))
            """))

    yield engine

    # Drop tables after test
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
    """
    Create a test user with Better Auth schema.

    T020: Updated to use Better Auth user table schema with UUID.
    """
    from uuid import uuid4
    from datetime import datetime

    # Generate unique IDs for this test user
    unique_user_id = f"test_user_{uuid4().hex[:12]}"  # Better Auth String ID
    user_uuid = uuid4()  # Application UUID
    unique_email = f"test-{uuid4().hex[:8]}@example.com"

    # Create user with Better Auth schema
    user = User(
        id=unique_user_id,  # Better Auth String ID
        uuid=user_uuid,  # Application UUID
        email=unique_email,
        emailVerified=True,  # For tests, assume verified
        name="Test User",
        image=None,
        createdAt=datetime.utcnow(),
        updatedAt=datetime.utcnow(),
    )

    test_session.add(user)
    await test_session.commit()
    await test_session.refresh(user)

    return user


@pytest_asyncio.fixture
async def auth_headers(test_user: User) -> dict:
    """
    Create authentication headers with JWT token.

    T020: Updated to create JWT with UUID in payload (matching Better Auth pattern).
    """
    from src.core.security import create_access_token
    import jwt
    from src.core.config import settings

    # Create JWT token with UUID in custom claim (matching Better Auth integration)
    payload = {
        "sub": test_user.id,  # Better Auth String ID (for compatibility)
        "uuid": str(test_user.uuid),  # Application UUID (custom claim)
        "email": test_user.email,
        "name": test_user.name,
    }

    token = jwt.encode(payload, settings.BETTER_AUTH_SECRET, algorithm="HS256")

    return {
        "Authorization": f"Bearer {token}",
    }


@pytest_asyncio.fixture
async def user_id(test_user: User) -> str:
    """
    Return test user UUID as string (for use in API routes).

    T020: Updated to return UUID instead of Better Auth String ID.
    """
    return str(test_user.uuid)


@pytest.fixture(scope="function", autouse=True)
def mock_better_auth_for_tests():
    """
    Override Better Auth JWT verification for integration tests.

    Tests use internal JWT creation/verification instead of Better Auth JWKS.
    """
    from src.api import deps
    from src.core.security import decode_access_token
    from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
    from fastapi import Depends, HTTPException, status
    from uuid import UUID
    from src.core.database import get_session

    security = HTTPBearer()

    async def test_get_current_user(
        credentials: HTTPAuthorizationCredentials = Depends(security),
        session: AsyncSession = Depends(get_session),
    ) -> User:
        """
        Test version of get_current_user using internal JWT verification.

        T020: Updated to extract UUID from JWT payload instead of String ID.
        """
        try:
            # Use internal JWT verification instead of Better Auth JWKS
            payload = decode_access_token(credentials.credentials)

            # T020: Extract UUID from custom claim (matching production behavior)
            user_uuid_str = payload.get("uuid")

            if not user_uuid_str:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Could not validate credentials - missing UUID"
                )

            user_uuid = UUID(user_uuid_str)

            # T020: Query by UUID instead of id
            from sqlmodel import select
            result = await session.execute(
                select(User).where(User.uuid == user_uuid)
            )
            user = result.scalar_one_or_none()

            if not user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="User not found"
                )

            return user

        except Exception as e:
            if isinstance(e, HTTPException):
                raise
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials"
            )

    # Override the dependency
    app.dependency_overrides[deps.get_current_user] = test_get_current_user
    yield
    # Clean up only this override
    if deps.get_current_user in app.dependency_overrides:
        del app.dependency_overrides[deps.get_current_user]
