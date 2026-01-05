"""Unit tests for user isolation in Task model."""
import pytest
from uuid import uuid4
from sqlmodel import select

from src.models.task import Task
from src.models.user import User, UserCreate
from src.services.user import create_user


@pytest.mark.asyncio
async def test_user_isolation_basic(test_session):
    """Test that users can only see their own tasks."""
    # Create two users
    user1_data = UserCreate(email="user1@example.com", password="password123", name="User 1")
    user2_data = UserCreate(email="user2@example.com", password="password123", name="User 2")

    user1 = await create_user(test_session, user1_data)
    user2 = await create_user(test_session, user2_data)
    await test_session.commit()
    await test_session.refresh(user1)
    await test_session.refresh(user2)

    # Create tasks for user 1
    task1_user1 = Task(user_id=user1.id, title="User 1 Task 1", completed=False)
    task2_user1 = Task(user_id=user1.id, title="User 1 Task 2", completed=False)

    # Create tasks for user 2
    task1_user2 = Task(user_id=user2.id, title="User 2 Task 1", completed=False)
    task2_user2 = Task(user_id=user2.id, title="User 2 Task 2", completed=False)

    test_session.add_all([task1_user1, task2_user1, task1_user2, task2_user2])
    await test_session.commit()

    # Query user 1's tasks
    statement = select(Task).where(Task.user_id == user1.id)
    result = await test_session.execute(statement)
    user1_tasks = result.scalars().all()

    assert len(user1_tasks) == 2
    assert all(task.user_id == user1.id for task in user1_tasks)
    assert set(task.title for task in user1_tasks) == {"User 1 Task 1", "User 1 Task 2"}

    # Query user 2's tasks
    statement = select(Task).where(Task.user_id == user2.id)
    result = await test_session.execute(statement)
    user2_tasks = result.scalars().all()

    assert len(user2_tasks) == 2
    assert all(task.user_id == user2.id for task in user2_tasks)
    assert set(task.title for task in user2_tasks) == {"User 2 Task 1", "User 2 Task 2"}


@pytest.mark.asyncio
async def test_user_isolation_with_completed_filter(test_session):
    """Test user isolation with completion status filter."""
    # Create two users
    user1_data = UserCreate(email="user3@example.com", password="password123", name="User 3")
    user2_data = UserCreate(email="user4@example.com", password="password123", name="User 4")

    user1 = await create_user(test_session, user1_data)
    user2 = await create_user(test_session, user2_data)
    await test_session.commit()
    await test_session.refresh(user1)
    await test_session.refresh(user2)

    # User 1: 2 tasks (1 completed, 1 incomplete)
    task1_user1 = Task(user_id=user1.id, title="User 1 Complete", completed=True)
    task2_user1 = Task(user_id=user1.id, title="User 1 Incomplete", completed=False)

    # User 2: 2 tasks (both completed)
    task1_user2 = Task(user_id=user2.id, title="User 2 Complete 1", completed=True)
    task2_user2 = Task(user_id=user2.id, title="User 2 Complete 2", completed=True)

    test_session.add_all([task1_user1, task2_user1, task1_user2, task2_user2])
    await test_session.commit()

    # Query user 1's incomplete tasks
    statement = select(Task).where(Task.user_id == user1.id, Task.completed == False)
    result = await test_session.execute(statement)
    user1_incomplete = result.scalars().all()

    assert len(user1_incomplete) == 1
    assert user1_incomplete[0].title == "User 1 Incomplete"
    assert user1_incomplete[0].user_id == user1.id

    # Query user 2's completed tasks
    statement = select(Task).where(Task.user_id == user2.id, Task.completed == True)
    result = await test_session.execute(statement)
    user2_completed = result.scalars().all()

    assert len(user2_completed) == 2
    assert all(task.user_id == user2.id for task in user2_completed)
    assert all(task.completed is True for task in user2_completed)


@pytest.mark.asyncio
async def test_user_isolation_prevents_cross_user_access(test_session):
    """Test that querying with wrong user_id returns no results."""
    # Create two users
    user1_data = UserCreate(email="user5@example.com", password="password123", name="User 5")
    user2_data = UserCreate(email="user6@example.com", password="password123", name="User 6")

    user1 = await create_user(test_session, user1_data)
    user2 = await create_user(test_session, user2_data)
    await test_session.commit()
    await test_session.refresh(user1)
    await test_session.refresh(user2)

    # Create task for user 1
    task = Task(user_id=user1.id, title="User 1 Task", completed=False)
    test_session.add(task)
    await test_session.commit()

    # Try to query with user 2's ID (should return empty)
    statement = select(Task).where(Task.user_id == user2.id)
    result = await test_session.execute(statement)
    user2_tasks = result.scalars().all()

    assert len(user2_tasks) == 0


@pytest.mark.asyncio
async def test_user_isolation_with_soft_delete(test_session):
    """Test that soft-deleted tasks are isolated per user."""
    from datetime import datetime, UTC

    # Create two users
    user1_data = UserCreate(email="user7@example.com", password="password123", name="User 7")
    user2_data = UserCreate(email="user8@example.com", password="password123", name="User 8")

    user1 = await create_user(test_session, user1_data)
    user2 = await create_user(test_session, user2_data)
    await test_session.commit()
    await test_session.refresh(user1)
    await test_session.refresh(user2)

    # User 1: 1 active, 1 deleted
    task1_user1 = Task(user_id=user1.id, title="User 1 Active", completed=False)
    task2_user1 = Task(
        user_id=user1.id,
        title="User 1 Deleted",
        completed=False,
        deleted_at=datetime.now(UTC),
    )

    # User 2: 1 active
    task1_user2 = Task(user_id=user2.id, title="User 2 Active", completed=False)

    test_session.add_all([task1_user1, task2_user1, task1_user2])
    await test_session.commit()

    # Query user 1's active tasks (exclude deleted)
    statement = select(Task).where(Task.user_id == user1.id, Task.deleted_at.is_(None))
    result = await test_session.execute(statement)
    user1_active = result.scalars().all()

    assert len(user1_active) == 1
    assert user1_active[0].title == "User 1 Active"

    # Query user 1's deleted tasks
    statement = select(Task).where(Task.user_id == user1.id, Task.deleted_at.is_not(None))
    result = await test_session.execute(statement)
    user1_deleted = result.scalars().all()

    assert len(user1_deleted) == 1
    assert user1_deleted[0].title == "User 1 Deleted"


@pytest.mark.asyncio
async def test_user_isolation_index_performance(test_session):
    """Test that user_id index is used for efficient queries."""
    # Create 5 users
    users = []
    for i in range(5):
        user_data = UserCreate(
            email=f"user_perf_{i}@example.com",
            password="password123",
            name=f"User Performance {i}"
        )
        user = await create_user(test_session, user_data)
        users.append(user)

    await test_session.commit()
    for user in users:
        await test_session.refresh(user)

    # Create many tasks for different users
    tasks = []
    for user in users:
        for i in range(10):  # 10 tasks each
            task = Task(
                user_id=user.id,
                title=f"User {user.id} Task {i}",
                completed=False,
            )
            tasks.append(task)

    test_session.add_all(tasks)
    await test_session.commit()

    # Query specific user's tasks (should use index)
    target_user = users[2]  # User 3
    statement = select(Task).where(Task.user_id == target_user.id)
    result = await test_session.execute(statement)
    user3_tasks = result.scalars().all()

    assert len(user3_tasks) == 10
    assert all(task.user_id == target_user.id for task in user3_tasks)
