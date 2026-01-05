"""Unit tests for Task model."""
import pytest
from datetime import datetime, UTC
from uuid import uuid4
from sqlmodel import select

from src.models.task import Task


@pytest.mark.asyncio
async def test_create_task(test_session, test_user):
    """Test creating a basic task with required fields."""
    task = Task(
        user_id=test_user.id,
        title="Buy groceries",
        description="Milk, eggs, bread",
        completed=False,
    )

    test_session.add(task)
    await test_session.commit()
    await test_session.refresh(task)

    assert task.id is not None
    assert task.user_id == test_user.id
    assert task.title == "Buy groceries"
    assert task.description == "Milk, eggs, bread"
    assert task.completed is False
    assert task.created_at is not None
    assert task.updated_at is not None
    assert task.deleted_at is None
    assert task.priority is None
    assert task.due_date is None
    assert task.reminder_at is None
    assert task.recurrence_pattern is None
    assert task.recurrence_config is None


@pytest.mark.asyncio
async def test_create_task_with_advanced_fields(test_session, test_user):
    """Test creating a task with advanced Phase V fields."""
    due_date = datetime.now(UTC)
    reminder_at = datetime.now(UTC)
    recurrence_config = {"rrule": "FREQ=DAILY;BYDAY=MO,TU,WE,TH,FR"}

    task = Task(
        user_id=test_user.id,
        title="Team standup",
        description="Daily sync meeting",
        completed=False,
        priority="high",
        due_date=due_date,
        reminder_at=reminder_at,
        recurrence_pattern="custom",
        recurrence_config=recurrence_config,
    )

    test_session.add(task)
    await test_session.commit()
    await test_session.refresh(task)

    assert task.priority == "high"
    assert task.due_date == due_date
    assert task.reminder_at == reminder_at
    assert task.recurrence_pattern == "custom"
    assert task.recurrence_config == recurrence_config


@pytest.mark.asyncio
async def test_task_title_required(test_session, test_user):
    """Test that task title is required (NOT NULL constraint)."""
    task = Task(
        user_id=test_user.id,
        title=None,  # This should fail
        completed=False,
    )

    with pytest.raises(Exception):  # Should raise validation or database error
        test_session.add(task)
        await test_session.commit()


@pytest.mark.asyncio
async def test_task_user_id_required(test_session, test_user):
    """Test that user_id is required (NOT NULL constraint)."""
    task = Task(
        user_id=None,  # This should fail
        title="Test task",
        completed=False,
    )

    with pytest.raises(Exception):  # Should raise validation or database error
        test_session.add(task)
        await test_session.commit()


@pytest.mark.asyncio
async def test_task_default_completed_false(test_session, test_user):
    """Test that completed defaults to False."""
    task = Task(
        user_id=test_user.id,
        title="Test task",
        # completed not specified
    )

    test_session.add(task)
    await test_session.commit()
    await test_session.refresh(task)

    assert task.completed is False


@pytest.mark.asyncio
async def test_task_priority_enum_constraint(test_session, test_user):
    """Test that priority must be one of: low, medium, high or NULL."""
    task = Task(
        user_id=test_user.id,
        title="Test task",
        completed=False,
        priority="invalid",  # Should fail CHECK constraint
    )

    with pytest.raises(Exception):  # Should raise database constraint error
        test_session.add(task)
        await test_session.commit()


@pytest.mark.asyncio
async def test_task_recurrence_pattern_enum_constraint(test_session, test_user):
    """Test that recurrence_pattern must be one of: daily, weekly, monthly, custom or NULL."""
    task = Task(
        user_id=test_user.id,
        title="Test task",
        completed=False,
        recurrence_pattern="invalid",  # Should fail CHECK constraint
    )

    with pytest.raises(Exception):  # Should raise database constraint error
        test_session.add(task)
        await test_session.commit()


@pytest.mark.asyncio
async def test_task_description_max_length(test_session, test_user):
    """Test that description has max length of 10,000 characters."""
    long_description = "A" * 10001  # 10,001 characters

    task = Task(
        user_id=test_user.id,
        title="Test task",
        description=long_description,  # Should fail CHECK constraint
        completed=False,
    )

    with pytest.raises(Exception):  # Should raise database constraint error
        test_session.add(task)
        await test_session.commit()
