"""Async database engine and session factory using SQLModel."""
from collections.abc import AsyncGenerator
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine
from sqlalchemy.orm import sessionmaker

from .config import settings


# Create async engine with connection pooling
engine: AsyncEngine = create_async_engine(
    settings.DATABASE_URL,
    echo=not settings.is_production,
    future=True,
    pool_size=5,
    max_overflow=10,
    pool_pre_ping=True,
    pool_recycle=3600,
)

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
