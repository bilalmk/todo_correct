"""
Database connection management for Todo MCP Server.

Uses SQLModel async engine with lifespan management for stateless operations.
"""

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import NullPool
from contextlib import asynccontextmanager
from typing import AsyncGenerator
from todo_mcp.config import get_settings


# Global engine instance (initialized on startup via lifespan)
_engine = None
_async_session_maker = None


def get_engine():
    """
    Get or create SQLModel async engine.

    Uses NullPool for stateless architecture - no persistent connections stored in memory.
    Each request gets a fresh connection from the pool.

    Returns:
        AsyncEngine: SQLModel async engine for PostgreSQL
    """
    global _engine
    if _engine is None:
        settings = get_settings()
        _engine = create_async_engine(
            settings.database_url,
            echo=False,  # Set to True for SQL query logging
            pool_pre_ping=True,  # Verify connections before using them
            poolclass=NullPool,  # No connection pooling (stateless requirement)
        )
    return _engine


def get_session_maker():
    """
    Get or create async session maker.

    Returns:
        async_sessionmaker: Factory for creating async database sessions
    """
    global _async_session_maker
    if _async_session_maker is None:
        engine = get_engine()
        _async_session_maker = async_sessionmaker(
            engine,
            class_=AsyncSession,
            expire_on_commit=False,  # Don't expire objects after commit
        )
    return _async_session_maker


@asynccontextmanager
async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Get async database session context manager.

    This is a context manager that automatically handles:
    - Session creation
    - Transaction commit on success
    - Rollback on error
    - Session cleanup

    Usage:
        async with get_db_session() as session:
            result = await session.execute(select(Task))
            tasks = result.scalars().all()

    Yields:
        AsyncSession: SQLModel async session for database operations
    """
    session_maker = get_session_maker()
    async with session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def dispose_engine():
    """
    Dispose of the database engine and close all connections.

    This should be called on application shutdown via lifespan context.
    """
    global _engine, _async_session_maker
    if _engine is not None:
        await _engine.dispose()
        _engine = None
        _async_session_maker = None


# Lifespan context manager for FastMCP
@asynccontextmanager
async def database_lifespan():
    """
    Lifespan context manager for database engine.

    Initializes engine on startup and disposes on shutdown.

    Usage in app.py:
        @asynccontextmanager
        async def app_lifespan():
            async with database_lifespan():
                yield
    """
    # Startup: Initialize engine
    get_engine()
    get_session_maker()
    yield
    # Shutdown: Dispose engine
    await dispose_engine()
