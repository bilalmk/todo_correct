"""Async database engine and session factory using SQLModel."""
from collections.abc import AsyncGenerator
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool
import os

from .config import settings


# Use NullPool in test environment to avoid cached statement issues
is_test = os.getenv("PYTEST_CURRENT_TEST") is not None

# Create async engine with connection pooling
engine_kwargs = {
    "echo": not settings.is_production,
    "future": True,
}

if is_test:
    # Use NullPool for tests to avoid cached statement errors
    engine_kwargs["poolclass"] = NullPool
else:
    # Use connection pooling for production
    # T009 (FR-023): Configure pool to support 50 concurrent requests (SC-003)
    engine_kwargs.update({
        "pool_size": 10,          # Minimum persistent connections
        "max_overflow": 40,       # Additional connections on demand (total max=50)
        "pool_timeout": 30,       # Wait up to 30s for connection before TimeoutError
        "pool_pre_ping": True,    # Health check connections before use
        "pool_recycle": 3600,     # Recycle connections every hour
    })

engine: AsyncEngine = create_async_engine(
    settings.DATABASE_URL,
    **engine_kwargs,
)

print("===========================")
print(settings.DATABASE_URL)
print("===========================")

# Create async session factory
async_session_maker = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI dependency to get async database session.

    Yields:
        AsyncSession: Database session for the request

    Example:
        @app.get("/users")
        async def get_users(session: AsyncSession = Depends(get_session)):
            ...
    """
    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


async def create_db_and_tables() -> None:
    """
    Create all database tables.

    Note: In production, use Alembic migrations instead.
    This is useful for testing and development.
    """
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)


async def close_db_connection() -> None:
    """Close database connection pool."""
    await engine.dispose()


async def check_database_health() -> bool:
    """
    Check database connectivity and schema health.

    Returns:
        bool: True if database is healthy, False otherwise
    """
    try:
        async with async_session_maker() as session:
            # Verify connection with simple query
            result = await session.execute("SELECT 1")
            result.scalar()

            # Verify critical tables exist (will be populated after migrations)
            # T020: Updated to use Better Auth user table instead of custom users table
            from sqlalchemy import inspect
            async with engine.connect() as conn:
                def check_tables(connection):
                    inspector = inspect(connection)
                    tables = inspector.get_table_names()
                    required_tables = {
                        'user',          # Better Auth user table (singular)
                        'session',       # Better Auth session table
                        'account',       # Better Auth account table
                        'verification',  # Better Auth verification table
                        'jwks',          # Better Auth JWKS table (JWT plugin)
                        'tasks',
                        'tags',
                        'task_tags',
                        'notifications',
                        'conversations', # ChatKit Phase III (T005)
                        'messages',      # ChatKit Phase III (T006)
                    }
                    return required_tables.issubset(set(tables))

                tables_exist = await conn.run_sync(check_tables)
                return tables_exist
    except Exception as e:
        print(f"Database health check failed: {e}")
        return False
