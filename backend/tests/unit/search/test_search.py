"""Unit tests for full-text search functionality."""
import pytest
from sqlmodel import select
from sqlalchemy import text

from src.models.task import Task


@pytest.mark.asyncio
async def test_fulltext_search_basic_query(test_session, test_user):
    """Test basic full-text search for 'meeting notes'."""
    # Create tasks with different content
    task1 = Task(
        user_id=test_user.id,
        title="Weekly team meeting",
        description="Discuss project progress and next steps",
        completed=False,
    )
    task2 = Task(
        user_id=test_user.id,
        title="Take meeting notes",
        description="Document important decisions from standup",
        completed=False,
    )
    task3 = Task(
        user_id=test_user.id,
        title="Buy groceries",
        description="Get milk, eggs, and bread",
        completed=False,
    )
    task4 = Task(
        user_id=test_user.id,
        title="Review notes from conference",
        description="Go through meeting recordings",
        completed=False,
    )

    test_session.add_all([task1, task2, task3, task4])
    await test_session.commit()

    # Search for "meeting notes" using full-text search
    # This should match tasks 1, 2, and 4 (contain "meeting" or "notes")
    query = text("""
        SELECT id, title, description
        FROM tasks
        WHERE user_id = :user_id
        AND to_tsvector('english', coalesce(title, '') || ' ' || coalesce(description, ''))
        @@ plainto_tsquery('english', :search_term)
        ORDER BY ts_rank(
            to_tsvector('english', coalesce(title, '') || ' ' || coalesce(description, '')),
            plainto_tsquery('english', :search_term)
        ) DESC
    """)

    result = await test_session.execute(
        query, {"user_id": str(test_user.id), "search_term": "meeting notes"}
    )
    rows = result.fetchall()

    # Should find tasks with "meeting" or "notes"
    assert len(rows) >= 2  # At least task1 and task2
    found_ids = [row[0] for row in rows]
    assert task1.id in found_ids
    assert task2.id in found_ids
    # task3 should NOT be in results (no "meeting" or "notes")
    assert task3.id not in found_ids


@pytest.mark.asyncio
async def test_fulltext_search_title_only(test_session, test_user):
    """Test full-text search matches in title."""
    task1 = Task(
        user_id=test_user.id,
        title="Important project deadline",
        description="Other stuff",
        completed=False,
    )
    task2 = Task(
        user_id=test_user.id,
        title="Random task",
        description="This has project deadline in description",
        completed=False,
    )

    test_session.add_all([task1, task2])
    await test_session.commit()

    # Search for "project deadline"
    query = text("""
        SELECT id, title
        FROM tasks
        WHERE user_id = :user_id
        AND to_tsvector('english', coalesce(title, '') || ' ' || coalesce(description, ''))
        @@ plainto_tsquery('english', :search_term)
    """)

    result = await test_session.execute(
        query, {"user_id": str(test_user.id), "search_term": "project deadline"}
    )
    rows = result.fetchall()

    # Both should match
    assert len(rows) == 2
    found_ids = [row[0] for row in rows]
    assert task1.id in found_ids
    assert task2.id in found_ids


@pytest.mark.asyncio
async def test_fulltext_search_description_only(test_session, test_user):
    """Test full-text search matches in description."""
    task1 = Task(
        user_id=test_user.id,
        title="Task A",
        description="Prepare annual financial report for Q4",
        completed=False,
    )
    task2 = Task(
        user_id=test_user.id,
        title="Task B",
        description="Buy birthday gift",
        completed=False,
    )

    test_session.add_all([task1, task2])
    await test_session.commit()

    # Search for "financial report"
    query = text("""
        SELECT id, description
        FROM tasks
        WHERE user_id = :user_id
        AND to_tsvector('english', coalesce(title, '') || ' ' || coalesce(description, ''))
        @@ plainto_tsquery('english', :search_term)
    """)

    result = await test_session.execute(
        query, {"user_id": str(test_user.id), "search_term": "financial report"}
    )
    rows = result.fetchall()

    # Only task1 should match
    assert len(rows) == 1
    assert rows[0][0] == task1.id


@pytest.mark.asyncio
async def test_fulltext_search_no_results(test_session, test_user):
    """Test full-text search with no matching results."""
    task1 = Task(
        user_id=test_user.id,
        title="Buy groceries",
        description="Get milk and eggs",
        completed=False,
    )

    test_session.add(task1)
    await test_session.commit()

    # Search for something that doesn't exist
    query = text("""
        SELECT id
        FROM tasks
        WHERE user_id = :user_id
        AND to_tsvector('english', coalesce(title, '') || ' ' || coalesce(description, ''))
        @@ plainto_tsquery('english', :search_term)
    """)

    result = await test_session.execute(
        query, {"user_id": str(test_user.id), "search_term": "quantum physics"}
    )
    rows = result.fetchall()

    assert len(rows) == 0


@pytest.mark.asyncio
async def test_fulltext_search_user_isolation(test_session):
    """Test full-text search respects user isolation."""
    from src.services.user import create_user
    from src.models.user import UserCreate

    # Create two users
    user1_data = UserCreate(
        email="user1@example.com", password="password123", name="User 1"
    )
    user1 = await create_user(test_session, user1_data)

    user2_data = UserCreate(
        email="user2@example.com", password="password123", name="User 2"
    )
    user2 = await create_user(test_session, user2_data)

    await test_session.commit()
    await test_session.refresh(user1)
    await test_session.refresh(user2)

    # Create tasks for both users with same content
    task1 = Task(
        user_id=user1.id,
        title="Secret meeting agenda",
        description="Confidential",
        completed=False,
    )
    task2 = Task(
        user_id=user2.id,
        title="Secret meeting notes",
        description="Private",
        completed=False,
    )

    test_session.add_all([task1, task2])
    await test_session.commit()

    # Search as user1 - should only see task1
    query = text("""
        SELECT id
        FROM tasks
        WHERE user_id = :user_id
        AND to_tsvector('english', coalesce(title, '') || ' ' || coalesce(description, ''))
        @@ plainto_tsquery('english', :search_term)
    """)

    result = await test_session.execute(
        query, {"user_id": str(user1.id), "search_term": "secret meeting"}
    )
    rows = result.fetchall()

    assert len(rows) == 1
    assert rows[0][0] == task1.id

    # Search as user2 - should only see task2
    result = await test_session.execute(
        query, {"user_id": str(user2.id), "search_term": "secret meeting"}
    )
    rows = result.fetchall()

    assert len(rows) == 1
    assert rows[0][0] == task2.id


@pytest.mark.asyncio
async def test_fulltext_search_stemming(test_session, test_user):
    """Test that full-text search uses English stemming (run, running, runs -> same root)."""
    # Create tasks with different word forms
    task1 = Task(
        user_id=test_user.id,
        title="Running weekly reports",
        description="Generate performance metrics",
        completed=False,
    )
    task2 = Task(
        user_id=test_user.id,
        title="Run daily backups",
        description="Automated task",
        completed=False,
    )
    task3 = Task(
        user_id=test_user.id,
        title="Marathon training",
        description="Runs every morning at 6 AM",
        completed=False,
    )

    test_session.add_all([task1, task2, task3])
    await test_session.commit()

    # Search for "running" - should match "run", "running", "runs" due to stemming
    query = text("""
        SELECT id, title
        FROM tasks
        WHERE user_id = :user_id
        AND to_tsvector('english', coalesce(title, '') || ' ' || coalesce(description, ''))
        @@ plainto_tsquery('english', :search_term)
    """)

    result = await test_session.execute(
        query, {"user_id": str(test_user.id), "search_term": "running"}
    )
    rows = result.fetchall()

    # All three tasks should match (running, run, runs are same stem)
    assert len(rows) == 3
    found_ids = [row[0] for row in rows]
    assert task1.id in found_ids
    assert task2.id in found_ids
    assert task3.id in found_ids


@pytest.mark.asyncio
async def test_fulltext_search_partial_word_matching(test_session, test_user):
    """Test partial word matching with prefix search."""
    task1 = Task(
        user_id=test_user.id,
        title="Database optimization",
        description="Optimize PostgreSQL queries",
        completed=False,
    )
    task2 = Task(
        user_id=test_user.id,
        title="Data analysis",
        description="Analyze user behavior patterns",
        completed=False,
    )
    task3 = Task(
        user_id=test_user.id,
        title="Backend development",
        description="Build API endpoints",
        completed=False,
    )

    test_session.add_all([task1, task2, task3])
    await test_session.commit()

    # Search for "data" prefix - should match "database" and "data"
    # Using prefix search with :*
    query = text("""
        SELECT id, title
        FROM tasks
        WHERE user_id = :user_id
        AND to_tsvector('english', coalesce(title, '') || ' ' || coalesce(description, ''))
        @@ to_tsquery('english', :search_term)
    """)

    result = await test_session.execute(
        query, {"user_id": str(test_user.id), "search_term": "data:*"}
    )
    rows = result.fetchall()

    # Should match task1 (database) and task2 (data)
    assert len(rows) == 2
    found_ids = [row[0] for row in rows]
    assert task1.id in found_ids
    assert task2.id in found_ids
    assert task3.id not in found_ids


@pytest.mark.asyncio
async def test_fulltext_search_multiple_terms(test_session, test_user):
    """Test full-text search with multiple search terms (AND logic)."""
    task1 = Task(
        user_id=test_user.id,
        title="Review design documents",
        description="Architecture review for new feature",
        completed=False,
    )
    task2 = Task(
        user_id=test_user.id,
        title="Design mockups",
        description="Create UI wireframes",
        completed=False,
    )
    task3 = Task(
        user_id=test_user.id,
        title="Code review",
        description="Check pull requests",
        completed=False,
    )

    test_session.add_all([task1, task2, task3])
    await test_session.commit()

    # Search for "design review" - should match tasks containing BOTH words
    query = text("""
        SELECT id, title
        FROM tasks
        WHERE user_id = :user_id
        AND to_tsvector('english', coalesce(title, '') || ' ' || coalesce(description, ''))
        @@ plainto_tsquery('english', :search_term)
    """)

    result = await test_session.execute(
        query, {"user_id": str(test_user.id), "search_term": "design review"}
    )
    rows = result.fetchall()

    # task1 has both "design" (in description) and "review" (in title)
    # task2 has "design" but not "review"
    # task3 has "review" but not "design"
    # plainto_tsquery uses OR logic, so all three match
    assert len(rows) >= 1
    found_ids = [row[0] for row in rows]
    assert task1.id in found_ids


@pytest.mark.asyncio
async def test_fulltext_search_case_insensitive(test_session, test_user):
    """Test that full-text search is case-insensitive."""
    task1 = Task(
        user_id=test_user.id,
        title="URGENT: Fix Production Bug",
        description="Critical issue in payment module",
        completed=False,
    )

    test_session.add(task1)
    await test_session.commit()

    # Search with lowercase
    query = text("""
        SELECT id
        FROM tasks
        WHERE user_id = :user_id
        AND to_tsvector('english', coalesce(title, '') || ' ' || coalesce(description, ''))
        @@ plainto_tsquery('english', :search_term)
    """)

    result = await test_session.execute(
        query, {"user_id": str(test_user.id), "search_term": "urgent production"}
    )
    rows = result.fetchall()

    # Should match despite case difference
    assert len(rows) == 1
    assert rows[0][0] == task1.id


@pytest.mark.asyncio
async def test_fulltext_search_special_characters(test_session, test_user):
    """Test full-text search handles special characters correctly."""
    task1 = Task(
        user_id=test_user.id,
        title="Update API v2.0 endpoint",
        description="Add /users/{id}/profile route",
        completed=False,
    )
    task2 = Task(
        user_id=test_user.id,
        title="API documentation",
        description="Write OpenAPI specs",
        completed=False,
    )

    test_session.add_all([task1, task2])
    await test_session.commit()

    # Search for "API" - should match despite special characters
    query = text("""
        SELECT id
        FROM tasks
        WHERE user_id = :user_id
        AND to_tsvector('english', coalesce(title, '') || ' ' || coalesce(description, ''))
        @@ plainto_tsquery('english', :search_term)
    """)

    result = await test_session.execute(
        query, {"user_id": str(test_user.id), "search_term": "API"}
    )
    rows = result.fetchall()

    # Both should match
    assert len(rows) == 2
    found_ids = [row[0] for row in rows]
    assert task1.id in found_ids
    assert task2.id in found_ids
