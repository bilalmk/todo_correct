"""Unit tests for soft delete functionality in Task model."""
import pytest
from datetime import datetime, UTC
from sqlmodel import select

from src.models.task import Task


@pytest.mark.asyncio
async def test_soft_delete_sets_deleted_at(test_session, test_user):
    """Test that soft delete sets deleted_at timestamp."""
    task = Task(user_id=test_user.id, title="Test task", completed=False)
    test_session.add(task)
    await test_session.commit()
    await test_session.refresh(task)

    # Perform soft delete
    task.deleted_at = datetime.now(UTC)
    test_session.add(task)
    await test_session.commit()
    await test_session.refresh(task)

    assert task.deleted_at is not None
    assert isinstance(task.deleted_at, datetime)


@pytest.mark.asyncio
async def test_soft_deleted_tasks_excluded_from_queries(test_session, test_user):
    """Test that soft-deleted tasks are excluded by default."""
    # Create active task
    active_task = Task(user_id=test_user.id, title="Active task", completed=False)

    # Create soft-deleted task
    deleted_task = Task(
        user_id=test_user.id,
        title="Deleted task",
        completed=False,
        deleted_at=datetime.now(UTC),
    )

    test_session.add_all([active_task, deleted_task])
    await test_session.commit()

    # Query active tasks only
    statement = select(Task).where(Task.user_id == test_user.id, Task.deleted_at.is_(None))
    result = await test_session.execute(statement)
    active_tasks = result.scalars().all()

    assert len(active_tasks) == 1
    assert active_tasks[0].title == "Active task"


@pytest.mark.asyncio
async def test_soft_deleted_tasks_can_be_queried(test_session, test_user):
    """Test that soft-deleted tasks can still be queried explicitly."""
    deleted_task = Task(
        user_id=test_user.id,
        title="Deleted task",
        completed=False,
        deleted_at=datetime.now(UTC),
    )
    test_session.add(deleted_task)
    await test_session.commit()

    # Query deleted tasks explicitly
    statement = select(Task).where(Task.user_id == test_user.id, Task.deleted_at.is_not(None))
    result = await test_session.execute(statement)
    deleted_tasks = result.scalars().all()

    assert len(deleted_tasks) == 1
    assert deleted_tasks[0].title == "Deleted task"


@pytest.mark.asyncio
async def test_soft_delete_preserves_data(test_session, test_user):
    """Test that soft delete preserves all task data."""
    task = Task(
        user_id=test_user.id,
        title="Important task",
        description="Critical data",
        completed=False,
        priority="high",
    )
    test_session.add(task)
    await test_session.commit()
    await test_session.refresh(task)

    original_id = task.id
    original_title = task.title
    original_description = task.description

    # Soft delete
    task.deleted_at = datetime.now(UTC)
    test_session.add(task)
    await test_session.commit()

    # Query including deleted
    statement = select(Task).where(Task.id == original_id)
    result = await test_session.execute(statement)
    deleted_task = result.scalars().first()

    assert deleted_task is not None
    assert deleted_task.id == original_id
    assert deleted_task.title == original_title
    assert deleted_task.description == original_description
    assert deleted_task.deleted_at is not None


@pytest.mark.asyncio
async def test_undelete_task(test_session, test_user):
    """Test that tasks can be undeleted by setting deleted_at to NULL."""
    task = Task(
        user_id=test_user.id,
        title="Deleted then restored",
        completed=False,
        deleted_at=datetime.now(UTC),
    )
    test_session.add(task)
    await test_session.commit()
    await test_session.refresh(task)

    # Undelete by setting deleted_at to None
    task.deleted_at = None
    test_session.add(task)
    await test_session.commit()
    await test_session.refresh(task)

    assert task.deleted_at is None

    # Should appear in active tasks
    statement = select(Task).where(Task.user_id == test_user.id, Task.deleted_at.is_(None))
    result = await test_session.execute(statement)
    active_tasks = result.scalars().all()

    assert len(active_tasks) == 1
    assert active_tasks[0].title == "Deleted then restored"


@pytest.mark.asyncio
async def test_multiple_soft_deletes_per_user(test_session, test_user):
    """Test handling multiple soft-deleted tasks per user."""
    tasks = [
        Task(user_id=test_user.id, title=f"Task {i}", completed=False)
        for i in range(5)
    ]
    test_session.add_all(tasks)
    await test_session.commit()

    # Soft delete 3 tasks
    for i in range(3):
        tasks[i].deleted_at = datetime.now(UTC)
        test_session.add(tasks[i])
    await test_session.commit()

    # Query active tasks
    statement = select(Task).where(Task.user_id == test_user.id, Task.deleted_at.is_(None))
    result = await test_session.execute(statement)
    active_tasks = result.scalars().all()

    assert len(active_tasks) == 2

    # Query deleted tasks
    statement = select(Task).where(Task.user_id == test_user.id, Task.deleted_at.is_not(None))
    result = await test_session.execute(statement)
    deleted_tasks = result.scalars().all()

    assert len(deleted_tasks) == 3
