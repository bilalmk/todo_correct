"""Full-text search utilities for PostgreSQL."""
from typing import List, Optional
from uuid import UUID
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from src.models.task import Task


async def search_tasks(
    session: AsyncSession,
    user_id: UUID,
    search_term: str,
    limit: int = 100,
    include_completed: bool = True,
) -> List[Task]:
    """
    Search tasks using PostgreSQL full-text search.

    Uses GIN index on to_tsvector for fast full-text search across
    task titles and descriptions with English language stemming.

    Args:
        session: Async database session
        user_id: User ID to filter tasks
        search_term: Search query (plain text, will be processed by plainto_tsquery)
        limit: Maximum number of results to return (default: 100)
        include_completed: Whether to include completed tasks (default: True)

    Returns:
        List of Task objects matching the search term, ordered by relevance (ts_rank DESC)

    Examples:
        >>> tasks = await search_tasks(session, user_id, "meeting notes")
        >>> tasks = await search_tasks(session, user_id, "urgent project", limit=50)
    """
    # Build WHERE clause conditions
    where_conditions = [
        "user_id = :user_id",
        "to_tsvector('english', coalesce(title, '') || ' ' || coalesce(description, '')) @@ plainto_tsquery('english', :search_term)",
    ]

    if not include_completed:
        where_conditions.append("completed = FALSE")

    where_clause = " AND ".join(where_conditions)

    # Build query with ts_rank for relevance scoring
    query = text(f"""
        SELECT id, user_id, title, description, completed, created_at, updated_at,
               deleted_at, priority, due_date, reminder_at, recurrence_pattern, recurrence_config,
               ts_rank(
                   to_tsvector('english', coalesce(title, '') || ' ' || coalesce(description, '')),
                   plainto_tsquery('english', :search_term)
               ) AS rank
        FROM tasks
        WHERE {where_clause}
        ORDER BY rank DESC, created_at DESC
        LIMIT :limit
    """)

    result = await session.execute(
        query,
        {
            "user_id": str(user_id),
            "search_term": search_term,
            "limit": limit,
        },
    )

    # Fetch all rows and convert to Task objects
    rows = result.fetchall()

    # Manually construct Task objects from row data
    tasks = []
    for row in rows:
        task = Task(
            id=row[0],
            user_id=row[1],
            title=row[2],
            description=row[3],
            completed=row[4],
            created_at=row[5],
            updated_at=row[6],
            deleted_at=row[7],
            priority=row[8],
            due_date=row[9],
            reminder_at=row[10],
            recurrence_pattern=row[11],
            recurrence_config=row[12],
        )
        tasks.append(task)

    return tasks


async def search_tasks_prefix(
    session: AsyncSession,
    user_id: UUID,
    prefix: str,
    limit: int = 100,
) -> List[Task]:
    """
    Search tasks using prefix matching (e.g., "data" matches "database", "data", "datasheet").

    Uses to_tsquery with :* operator for prefix search.

    Args:
        session: Async database session
        user_id: User ID to filter tasks
        prefix: Prefix to search for
        limit: Maximum number of results to return (default: 100)

    Returns:
        List of Task objects matching the prefix, ordered by relevance

    Examples:
        >>> tasks = await search_tasks_prefix(session, user_id, "meet")  # matches "meeting", "meet", etc.
    """
    # Add :* for prefix matching
    search_term = f"{prefix}:*"

    query = text("""
        SELECT id, user_id, title, description, completed, created_at, updated_at,
               deleted_at, priority, due_date, reminder_at, recurrence_pattern, recurrence_config,
               ts_rank(
                   to_tsvector('english', coalesce(title, '') || ' ' || coalesce(description, '')),
                   to_tsquery('english', :search_term)
               ) AS rank
        FROM tasks
        WHERE user_id = :user_id
        AND to_tsvector('english', coalesce(title, '') || ' ' || coalesce(description, ''))
        @@ to_tsquery('english', :search_term)
        ORDER BY rank DESC, created_at DESC
        LIMIT :limit
    """)

    result = await session.execute(
        query,
        {
            "user_id": str(user_id),
            "search_term": search_term,
            "limit": limit,
        },
    )

    rows = result.fetchall()

    tasks = []
    for row in rows:
        task = Task(
            id=row[0],
            user_id=row[1],
            title=row[2],
            description=row[3],
            completed=row[4],
            created_at=row[5],
            updated_at=row[6],
            deleted_at=row[7],
            priority=row[8],
            due_date=row[9],
            reminder_at=row[10],
            recurrence_pattern=row[11],
            recurrence_config=row[12],
        )
        tasks.append(task)

    return tasks


async def search_tasks_count(
    session: AsyncSession,
    user_id: UUID,
    search_term: str,
) -> int:
    """
    Count tasks matching a full-text search query.

    Args:
        session: Async database session
        user_id: User ID to filter tasks
        search_term: Search query

    Returns:
        Count of matching tasks

    Examples:
        >>> count = await search_tasks_count(session, user_id, "urgent project")
    """
    query = text("""
        SELECT COUNT(*)
        FROM tasks
        WHERE user_id = :user_id
        AND to_tsvector('english', coalesce(title, '') || ' ' || coalesce(description, ''))
        @@ plainto_tsquery('english', :search_term)
    """)

    result = await session.execute(
        query,
        {
            "user_id": str(user_id),
            "search_term": search_term,
        },
    )

    return result.scalar_one()
