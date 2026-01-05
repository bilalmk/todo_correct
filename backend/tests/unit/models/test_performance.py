"""Performance tests for database indexes."""
import pytest
from datetime import datetime, UTC, timedelta
import time
from sqlmodel import select

from src.models.task import Task


@pytest.mark.asyncio
async def test_idx_tasks_due_reminders_performance(test_session, test_user):
    """Test idx_tasks_due_reminders index performance (sub-50ms with 10,000 tasks)."""
    # Create 10,000 tasks with varying due dates and reminders
    tasks = []
    base_date = datetime.now(UTC)

    for i in range(10000):
        # Mix of tasks: some with due dates, some with reminders, some with both, some with neither
        task_data = {
            "user_id": test_user.id,
            "title": f"Task {i}",
            "completed": i % 5 == 0,  # 20% completed
            "deleted_at": None if i % 10 != 0 else base_date,  # 10% soft-deleted
        }

        # 40% have due dates
        if i % 10 < 4:
            task_data["due_date"] = base_date + timedelta(days=i % 30)

        # 30% have reminders (subset of those with due dates)
        if i % 10 < 3:
            task_data["reminder_at"] = base_date + timedelta(days=i % 30, hours=-1)

        tasks.append(Task(**task_data))

    # Bulk insert tasks
    test_session.add_all(tasks)
    await test_session.commit()

    # Query for active tasks with upcoming due dates and reminders
    # This query should use idx_tasks_due_reminders index
    start_time = time.perf_counter()

    statement = select(Task).where(
        Task.completed == False,
        Task.deleted_at.is_(None),
        Task.due_date.is_not(None),
        Task.reminder_at.is_not(None),
        Task.due_date >= base_date,
        Task.due_date <= base_date + timedelta(days=7),
    )
    result = await test_session.execute(statement)
    upcoming_tasks = result.scalars().all()

    end_time = time.perf_counter()
    query_time_ms = (end_time - start_time) * 1000

    # Verify query returned results
    assert len(upcoming_tasks) > 0

    # Verify all returned tasks match criteria
    for task in upcoming_tasks:
        assert task.completed is False
        assert task.deleted_at is None
        assert task.due_date is not None
        assert task.reminder_at is not None

    # Performance assertion: query should complete in under 50ms
    assert query_time_ms < 50, f"Query took {query_time_ms:.2f}ms, expected < 50ms"


@pytest.mark.asyncio
async def test_idx_tasks_user_completed_performance(test_session, test_user):
    """Test idx_tasks_user_completed index performance."""
    # Create 5,000 tasks for this user
    tasks = []
    for i in range(5000):
        tasks.append(Task(
            user_id=test_user.id,
            title=f"Task {i}",
            completed=i % 2 == 0,  # 50% completed
        ))

    test_session.add_all(tasks)
    await test_session.commit()

    # Query for incomplete tasks (should use idx_tasks_user_completed)
    start_time = time.perf_counter()

    statement = select(Task).where(
        Task.user_id == test_user.id,
        Task.completed == False,
    )
    result = await test_session.execute(statement)
    incomplete_tasks = result.scalars().all()

    end_time = time.perf_counter()
    query_time_ms = (end_time - start_time) * 1000

    # Verify results
    assert len(incomplete_tasks) == 2500  # 50% of 5000

    # Performance assertion: should be fast with index
    assert query_time_ms < 50, f"Query took {query_time_ms:.2f}ms, expected < 50ms"


@pytest.mark.asyncio
async def test_idx_tasks_user_priority_performance(test_session, test_user):
    """Test idx_tasks_user_priority partial index performance."""
    # Create 5,000 tasks, 40% with priority
    tasks = []
    for i in range(5000):
        task_data = {
            "user_id": test_user.id,
            "title": f"Task {i}",
            "completed": False,
        }

        # 40% have priority
        if i % 10 < 4:
            priorities = ["low", "medium", "high"]
            task_data["priority"] = priorities[i % 3]

        tasks.append(Task(**task_data))

    test_session.add_all(tasks)
    await test_session.commit()

    # Query for high priority tasks (should use idx_tasks_user_priority partial index)
    start_time = time.perf_counter()

    statement = select(Task).where(
        Task.user_id == test_user.id,
        Task.priority == "high",
    )
    result = await test_session.execute(statement)
    high_priority_tasks = result.scalars().all()

    end_time = time.perf_counter()
    query_time_ms = (end_time - start_time) * 1000

    # Verify results
    assert len(high_priority_tasks) > 0

    # Performance assertion
    assert query_time_ms < 50, f"Query took {query_time_ms:.2f}ms, expected < 50ms"


@pytest.mark.asyncio
async def test_idx_tasks_user_due_date_performance(test_session, test_user):
    """Test idx_tasks_user_due_date partial index performance."""
    # Create 5,000 tasks, 40% with due dates
    tasks = []
    base_date = datetime.now(UTC)

    for i in range(5000):
        task_data = {
            "user_id": test_user.id,
            "title": f"Task {i}",
            "completed": False,
        }

        # 40% have due dates
        if i % 10 < 4:
            task_data["due_date"] = base_date + timedelta(days=i % 60)

        tasks.append(Task(**task_data))

    test_session.add_all(tasks)
    await test_session.commit()

    # Query for tasks due in next 7 days (should use idx_tasks_user_due_date partial index)
    start_time = time.perf_counter()

    statement = select(Task).where(
        Task.user_id == test_user.id,
        Task.due_date.is_not(None),
        Task.due_date >= base_date,
        Task.due_date <= base_date + timedelta(days=7),
    )
    result = await test_session.execute(statement)
    upcoming_tasks = result.scalars().all()

    end_time = time.perf_counter()
    query_time_ms = (end_time - start_time) * 1000

    # Verify results
    assert len(upcoming_tasks) > 0

    # Performance assertion
    assert query_time_ms < 50, f"Query took {query_time_ms:.2f}ms, expected < 50ms"


@pytest.mark.asyncio
async def test_notification_pending_index_performance(test_session, test_user):
    """Test idx_notifications_pending partial index performance."""
    from src.models.notification import Notification

    # Create 5,000 notifications with different statuses
    notifications = []
    for i in range(5000):
        status = "pending" if i % 10 < 3 else ("sent" if i % 2 == 0 else "failed")

        notifications.append(Notification(
            user_id=test_user.id,
            type="task_reminder",
            channel="email",
            recipient=f"user{i}@example.com",
            subject=f"Notification {i}",
            body="Test body",
            status=status,
        ))

    test_session.add_all(notifications)
    await test_session.commit()

    # Query for pending notifications (should use idx_notifications_pending partial index)
    start_time = time.perf_counter()

    statement = select(Notification).where(
        Notification.user_id == test_user.id,
        Notification.status == "pending",
    )
    result = await test_session.execute(statement)
    pending_notifications = result.scalars().all()

    end_time = time.perf_counter()
    query_time_ms = (end_time - start_time) * 1000

    # Verify results (30% should be pending)
    assert len(pending_notifications) == 1500

    # Performance assertion
    assert query_time_ms < 50, f"Query took {query_time_ms:.2f}ms, expected < 50ms"


@pytest.mark.asyncio
async def test_gin_index_fulltext_search_performance(test_session, test_user):
    """Test GIN index performance for full-text search (sub-100ms with 5,000+ tasks)."""
    from sqlalchemy import text

    # Create 5,000 tasks with varying content for full-text search
    tasks = []
    keywords = [
        "meeting project urgent",
        "report analysis data",
        "review code pull request",
        "design mockup wireframe",
        "bug fix production issue",
        "documentation API endpoint",
        "testing automation selenium",
        "deployment docker kubernetes",
        "database optimization query",
        "security authentication authorization",
    ]

    for i in range(5000):
        keyword_set = keywords[i % len(keywords)]
        tasks.append(Task(
            user_id=test_user.id,
            title=f"{keyword_set} - Task {i}",
            description=f"Detailed description for {keyword_set} involving multiple steps and requirements",
            completed=i % 3 == 0,  # 33% completed
        ))

    # Bulk insert tasks
    test_session.add_all(tasks)
    await test_session.commit()

    # Perform full-text search query (should use GIN index)
    # Search for common term that appears in many tasks
    start_time = time.perf_counter()

    query = text("""
        SELECT id, title, description,
               ts_rank(
                   to_tsvector('english', coalesce(title, '') || ' ' || coalesce(description, '')),
                   plainto_tsquery('english', :search_term)
               ) AS rank
        FROM tasks
        WHERE user_id = :user_id
        AND to_tsvector('english', coalesce(title, '') || ' ' || coalesce(description, ''))
        @@ plainto_tsquery('english', :search_term)
        ORDER BY rank DESC
        LIMIT 100
    """)

    result = await test_session.execute(
        query, {"user_id": str(test_user.id), "search_term": "project meeting"}
    )
    rows = result.fetchall()

    end_time = time.perf_counter()
    query_time_ms = (end_time - start_time) * 1000

    # Verify results
    assert len(rows) > 0, "Should find tasks matching 'project meeting'"

    # Performance assertion: GIN index should enable sub-100ms queries even with 5,000+ tasks
    assert query_time_ms < 100, f"Full-text search took {query_time_ms:.2f}ms, expected < 100ms"


@pytest.mark.asyncio
async def test_gin_index_prefix_search_performance(test_session, test_user):
    """Test GIN index performance for prefix search."""
    from sqlalchemy import text

    # Create 3,000 tasks with varied prefixes
    tasks = []
    prefixes = ["data", "develop", "deploy", "design", "debug", "document", "database"]

    for i in range(3000):
        prefix = prefixes[i % len(prefixes)]
        tasks.append(Task(
            user_id=test_user.id,
            title=f"{prefix}ing task {i}",
            description=f"This is about {prefix}ment and related activities",
            completed=False,
        ))

    test_session.add_all(tasks)
    await test_session.commit()

    # Perform prefix search (should use GIN index)
    start_time = time.perf_counter()

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

    end_time = time.perf_counter()
    query_time_ms = (end_time - start_time) * 1000

    # Verify results
    assert len(rows) > 0, "Should find tasks with 'data' prefix"

    # Performance assertion
    assert query_time_ms < 100, f"Prefix search took {query_time_ms:.2f}ms, expected < 100ms"


@pytest.mark.asyncio
async def test_gin_index_complex_search_performance(test_session, test_user):
    """Test GIN index performance with complex multi-term search."""
    from sqlalchemy import text

    # Create 4,000 tasks with realistic content
    tasks = []
    categories = [
        ("Frontend", "React", "component UI rendering"),
        ("Backend", "API", "endpoint database query"),
        ("DevOps", "Docker", "container deployment pipeline"),
        ("Testing", "Pytest", "unit integration coverage"),
        ("Security", "OAuth", "authentication authorization token"),
    ]

    for i in range(4000):
        category, tech, content = categories[i % len(categories)]
        tasks.append(Task(
            user_id=test_user.id,
            title=f"{category} - {tech} implementation {i}",
            description=f"Working on {content} for the project",
            completed=i % 4 == 0,
        ))

    test_session.add_all(tasks)
    await test_session.commit()

    # Complex search with multiple terms
    start_time = time.perf_counter()

    query = text("""
        SELECT id, title, description,
               ts_rank(
                   to_tsvector('english', coalesce(title, '') || ' ' || coalesce(description, '')),
                   plainto_tsquery('english', :search_term)
               ) AS rank
        FROM tasks
        WHERE user_id = :user_id
        AND to_tsvector('english', coalesce(title, '') || ' ' || coalesce(description, ''))
        @@ plainto_tsquery('english', :search_term)
        ORDER BY rank DESC
        LIMIT 50
    """)

    result = await test_session.execute(
        query, {"user_id": str(test_user.id), "search_term": "API endpoint database authentication"}
    )
    rows = result.fetchall()

    end_time = time.perf_counter()
    query_time_ms = (end_time - start_time) * 1000

    # Verify results
    assert len(rows) > 0, "Should find tasks matching complex query"

    # Performance assertion
    assert query_time_ms < 100, f"Complex search took {query_time_ms:.2f}ms, expected < 100ms"
