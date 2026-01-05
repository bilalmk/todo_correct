"""Unit tests for CASCADE delete behavior in Task model."""
import pytest
from uuid import uuid4
from sqlmodel import select

from src.models.task import Task
from src.models.user import User


@pytest.mark.asyncio
async def test_cascade_delete_removes_tasks(test_session, test_user):
    """Test that deleting a user CASCADE deletes their tasks."""
    # Create tasks for the test user
    task1 = Task(user_id=test_user.id, title="Task 1", completed=False)
    task2 = Task(user_id=test_user.id, title="Task 2", completed=False)

    test_session.add_all([task1, task2])
    await test_session.commit()

    # Verify tasks exist
    statement = select(Task).where(Task.user_id == test_user.id)
    result = await test_session.execute(statement)
    tasks_before = result.scalars().all()
    assert len(tasks_before) == 2

    # Delete user (should CASCADE delete tasks)
    await test_session.delete(test_user)
    await test_session.commit()

    # Verify tasks are deleted
    statement = select(Task).where(Task.user_id == test_user.id)
    result = await test_session.execute(statement)
    tasks_after = result.scalars().all()
    assert len(tasks_after) == 0


@pytest.mark.asyncio
async def test_cascade_delete_only_affects_user_tasks(test_session):
    """Test that CASCADE delete only removes tasks for the deleted user."""
    from src.services.user import create_user
    from src.models.user import UserCreate

    # Create two users
    user1_data = UserCreate(email="user1@example.com", password="password123", name="User 1")
    user2_data = UserCreate(email="user2@example.com", password="password123", name="User 2")

    user1 = await create_user(test_session, user1_data)
    user2 = await create_user(test_session, user2_data)
    await test_session.commit()
    await test_session.refresh(user1)
    await test_session.refresh(user2)

    # Create tasks for both users
    task1_user1 = Task(user_id=user1.id, title="User 1 Task", completed=False)
    task1_user2 = Task(user_id=user2.id, title="User 2 Task", completed=False)

    test_session.add_all([task1_user1, task1_user2])
    await test_session.commit()

    # Delete user 1
    await test_session.delete(user1)
    await test_session.commit()

    # Verify user 1's tasks are deleted
    statement = select(Task).where(Task.user_id == user1.id)
    result = await test_session.execute(statement)
    user1_tasks = result.scalars().all()
    assert len(user1_tasks) == 0

    # Verify user 2's tasks still exist
    statement = select(Task).where(Task.user_id == user2.id)
    result = await test_session.execute(statement)
    user2_tasks = result.scalars().all()
    assert len(user2_tasks) == 1
    assert user2_tasks[0].title == "User 2 Task"


@pytest.mark.asyncio
async def test_orphaned_task_prevented_by_foreign_key(test_session):
    """Test that tasks cannot exist without a valid user_id (foreign key constraint)."""
    # Attempt to create task with non-existent user_id
    fake_uuid = uuid4()
    task = Task(user_id=fake_uuid, title="Orphaned task", completed=False)
    test_session.add(task)

    with pytest.raises(Exception):  # Should raise foreign key constraint error
        await test_session.commit()
