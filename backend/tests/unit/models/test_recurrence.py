"""Unit tests for task recurrence configuration."""
import pytest
from datetime import datetime, UTC
from sqlmodel import select

from src.models.task import Task


@pytest.mark.asyncio
async def test_task_with_recurrence_config_daily(test_session, test_user):
    """Test storing daily recurrence configuration in JSONB field."""
    recurrence_config = {
        "rrule": "FREQ=DAILY;INTERVAL=1",
        "timezone": "UTC",
    }

    task = Task(
        user_id=test_user.id,
        title="Daily standup",
        description="Team sync",
        completed=False,
        recurrence_pattern="daily",
        recurrence_config=recurrence_config,
    )

    test_session.add(task)
    await test_session.commit()
    await test_session.refresh(task)

    assert task.recurrence_pattern == "daily"
    assert task.recurrence_config == recurrence_config
    assert task.recurrence_config["rrule"] == "FREQ=DAILY;INTERVAL=1"


@pytest.mark.asyncio
async def test_task_with_recurrence_config_weekly(test_session, test_user):
    """Test storing weekly recurrence configuration in JSONB field."""
    recurrence_config = {
        "rrule": "FREQ=WEEKLY;BYDAY=MO,WE,FR",
        "timezone": "America/New_York",
    }

    task = Task(
        user_id=test_user.id,
        title="Weekly meeting",
        completed=False,
        recurrence_pattern="weekly",
        recurrence_config=recurrence_config,
    )

    test_session.add(task)
    await test_session.commit()
    await test_session.refresh(task)

    assert task.recurrence_pattern == "weekly"
    assert task.recurrence_config["rrule"] == "FREQ=WEEKLY;BYDAY=MO,WE,FR"
    assert task.recurrence_config["timezone"] == "America/New_York"


@pytest.mark.asyncio
async def test_task_with_recurrence_config_monthly(test_session, test_user):
    """Test storing monthly recurrence configuration in JSONB field."""
    recurrence_config = {
        "rrule": "FREQ=MONTHLY;BYMONTHDAY=1",
        "timezone": "UTC",
    }

    task = Task(
        user_id=test_user.id,
        title="Monthly report",
        completed=False,
        recurrence_pattern="monthly",
        recurrence_config=recurrence_config,
    )

    test_session.add(task)
    await test_session.commit()
    await test_session.refresh(task)

    assert task.recurrence_pattern == "monthly"
    assert task.recurrence_config["rrule"] == "FREQ=MONTHLY;BYMONTHDAY=1"


@pytest.mark.asyncio
async def test_task_with_custom_recurrence_config(test_session, test_user):
    """Test storing custom recurrence configuration with complex RRULE."""
    recurrence_config = {
        "rrule": "FREQ=DAILY;BYDAY=MO,TU,WE,TH,FR;BYHOUR=9;BYMINUTE=0",
        "timezone": "Europe/London",
        "end_date": "2025-12-31T23:59:59Z",
    }

    task = Task(
        user_id=test_user.id,
        title="Workday reminder",
        completed=False,
        recurrence_pattern="custom",
        recurrence_config=recurrence_config,
    )

    test_session.add(task)
    await test_session.commit()
    await test_session.refresh(task)

    assert task.recurrence_pattern == "custom"
    assert task.recurrence_config["rrule"] == "FREQ=DAILY;BYDAY=MO,TU,WE,TH,FR;BYHOUR=9;BYMINUTE=0"
    assert task.recurrence_config["timezone"] == "Europe/London"
    assert task.recurrence_config["end_date"] == "2025-12-31T23:59:59Z"


@pytest.mark.asyncio
async def test_task_recurrence_config_nullable(test_session, test_user):
    """Test that recurrence_config can be NULL for non-recurring tasks."""
    task = Task(
        user_id=test_user.id,
        title="One-time task",
        completed=False,
        recurrence_pattern=None,
        recurrence_config=None,
    )

    test_session.add(task)
    await test_session.commit()
    await test_session.refresh(task)

    assert task.recurrence_pattern is None
    assert task.recurrence_config is None


@pytest.mark.asyncio
async def test_task_recurrence_config_update(test_session, test_user):
    """Test updating recurrence configuration."""
    # Create task with initial recurrence
    task = Task(
        user_id=test_user.id,
        title="Meeting",
        completed=False,
        recurrence_pattern="daily",
        recurrence_config={"rrule": "FREQ=DAILY;INTERVAL=1"},
    )
    test_session.add(task)
    await test_session.commit()
    await test_session.refresh(task)

    # Update recurrence to weekly
    task.recurrence_pattern = "weekly"
    task.recurrence_config = {"rrule": "FREQ=WEEKLY;BYDAY=MO"}
    test_session.add(task)
    await test_session.commit()
    await test_session.refresh(task)

    assert task.recurrence_pattern == "weekly"
    assert task.recurrence_config["rrule"] == "FREQ=WEEKLY;BYDAY=MO"


@pytest.mark.asyncio
async def test_task_recurrence_config_jsonb_query(test_session, test_user):
    """Test querying tasks by JSONB recurrence_config fields."""
    # Create tasks with different recurrence patterns
    daily_task = Task(
        user_id=test_user.id,
        title="Daily task",
        completed=False,
        recurrence_pattern="daily",
        recurrence_config={"rrule": "FREQ=DAILY"},
    )
    weekly_task = Task(
        user_id=test_user.id,
        title="Weekly task",
        completed=False,
        recurrence_pattern="weekly",
        recurrence_config={"rrule": "FREQ=WEEKLY"},
    )
    test_session.add_all([daily_task, weekly_task])
    await test_session.commit()

    # Query tasks with recurrence_config (not NULL)
    statement = select(Task).where(
        Task.user_id == test_user.id,
        Task.recurrence_config.is_not(None)
    )
    result = await test_session.execute(statement)
    recurring_tasks = result.scalars().all()

    assert len(recurring_tasks) == 2


@pytest.mark.asyncio
async def test_task_recurrence_config_complex_structure(test_session, test_user):
    """Test storing complex nested structure in recurrence_config JSONB."""
    recurrence_config = {
        "rrule": "FREQ=MONTHLY;BYMONTHDAY=1,15",
        "timezone": "America/Los_Angeles",
        "exceptions": [
            "2025-01-01T00:00:00Z",  # New Year's Day
            "2025-12-25T00:00:00Z",  # Christmas
        ],
        "metadata": {
            "created_by": "scheduler",
            "version": "1.0",
        },
    }

    task = Task(
        user_id=test_user.id,
        title="Bi-monthly report",
        completed=False,
        recurrence_pattern="custom",
        recurrence_config=recurrence_config,
    )

    test_session.add(task)
    await test_session.commit()
    await test_session.refresh(task)

    assert task.recurrence_config["exceptions"] == [
        "2025-01-01T00:00:00Z",
        "2025-12-25T00:00:00Z",
    ]
    assert task.recurrence_config["metadata"]["created_by"] == "scheduler"
    assert task.recurrence_config["metadata"]["version"] == "1.0"


@pytest.mark.asyncio
async def test_validate_rrule_format():
    """Test RRULE validation helper function."""
    from src.core.validators import validate_rrule

    # Valid RRULE strings
    assert validate_rrule("FREQ=DAILY") is True
    assert validate_rrule("FREQ=WEEKLY;BYDAY=MO,WE,FR") is True
    assert validate_rrule("FREQ=MONTHLY;BYMONTHDAY=1") is True
    assert validate_rrule("FREQ=YEARLY;BYMONTH=1;BYMONTHDAY=1") is True

    # Invalid RRULE strings
    assert validate_rrule("INVALID") is False
    assert validate_rrule("FREQ=INVALID") is False
    assert validate_rrule("") is False
    assert validate_rrule(None) is False


@pytest.mark.asyncio
async def test_validate_rrule_with_complex_pattern():
    """Test RRULE validation with complex patterns."""
    from src.core.validators import validate_rrule

    # Complex valid RRULE
    complex_rrule = "FREQ=DAILY;BYDAY=MO,TU,WE,TH,FR;BYHOUR=9;BYMINUTE=0;UNTIL=20251231T235959Z"
    assert validate_rrule(complex_rrule) is True

    # RRULE with COUNT
    count_rrule = "FREQ=WEEKLY;COUNT=10;BYDAY=MO"
    assert validate_rrule(count_rrule) is True

    # RRULE with INTERVAL
    interval_rrule = "FREQ=DAILY;INTERVAL=2"
    assert validate_rrule(interval_rrule) is True
