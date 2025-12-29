"""Unit tests for Notification model."""
import pytest
from datetime import datetime, UTC
from sqlmodel import select

from src.models.notification import Notification
from src.models.task import Task


@pytest.mark.asyncio
async def test_create_notification(test_session, test_user):
    """Test creating a basic notification with required fields."""
    notification = Notification(
        user_id=test_user.id,
        type="task_reminder",
        channel="email",
        recipient="test@example.com",
        subject="Task reminder",
        body="Don't forget your task!",
        status="pending",
    )

    test_session.add(notification)
    await test_session.commit()
    await test_session.refresh(notification)

    assert notification.id is not None
    assert notification.user_id == test_user.id
    assert notification.type == "task_reminder"
    assert notification.channel == "email"
    assert notification.recipient == "test@example.com"
    assert notification.subject == "Task reminder"
    assert notification.body == "Don't forget your task!"
    assert notification.status == "pending"
    assert notification.task_id is None
    assert notification.sent_at is None
    assert notification.error_message is None
    assert notification.created_at is not None


@pytest.mark.asyncio
async def test_create_notification_with_task(test_session, test_user):
    """Test creating a notification linked to a task."""
    # Create a task
    task = Task(user_id=test_user.id, title="Important task", completed=False)
    test_session.add(task)
    await test_session.commit()
    await test_session.refresh(task)

    # Create notification linked to task
    notification = Notification(
        user_id=test_user.id,
        task_id=task.id,
        type="task_reminder",
        channel="email",
        recipient="test@example.com",
        subject="Task reminder",
        body="Complete your task!",
        status="pending",
    )

    test_session.add(notification)
    await test_session.commit()
    await test_session.refresh(notification)

    assert notification.task_id == task.id


@pytest.mark.asyncio
async def test_notification_status_transition_pending_to_sent(test_session, test_user):
    """Test transitioning notification status from pending to sent."""
    notification = Notification(
        user_id=test_user.id,
        type="task_reminder",
        channel="email",
        recipient="test@example.com",
        subject="Test",
        body="Test body",
        status="pending",
    )
    test_session.add(notification)
    await test_session.commit()
    await test_session.refresh(notification)

    # Transition to sent
    notification.status = "sent"
    notification.sent_at = datetime.now(UTC)
    test_session.add(notification)
    await test_session.commit()
    await test_session.refresh(notification)

    assert notification.status == "sent"
    assert notification.sent_at is not None


@pytest.mark.asyncio
async def test_notification_status_transition_pending_to_failed(test_session, test_user):
    """Test transitioning notification status from pending to failed."""
    notification = Notification(
        user_id=test_user.id,
        type="task_reminder",
        channel="email",
        recipient="test@example.com",
        subject="Test",
        body="Test body",
        status="pending",
    )
    test_session.add(notification)
    await test_session.commit()
    await test_session.refresh(notification)

    # Transition to failed
    notification.status = "failed"
    notification.error_message = "SMTP connection timeout"
    test_session.add(notification)
    await test_session.commit()
    await test_session.refresh(notification)

    assert notification.status == "failed"
    assert notification.error_message == "SMTP connection timeout"


@pytest.mark.asyncio
async def test_notification_type_enum_constraint(test_session, test_user):
    """Test that type must be one of the allowed values."""
    notification = Notification(
        user_id=test_user.id,
        type="invalid_type",  # Should fail CHECK constraint
        channel="email",
        recipient="test@example.com",
        subject="Test",
        body="Test body",
        status="pending",
    )

    with pytest.raises(Exception):  # Should raise database constraint error
        test_session.add(notification)
        await test_session.commit()


@pytest.mark.asyncio
async def test_notification_channel_enum_constraint(test_session, test_user):
    """Test that channel must be one of the allowed values."""
    notification = Notification(
        user_id=test_user.id,
        type="task_reminder",
        channel="invalid_channel",  # Should fail CHECK constraint
        recipient="test@example.com",
        subject="Test",
        body="Test body",
        status="pending",
    )

    with pytest.raises(Exception):  # Should raise database constraint error
        test_session.add(notification)
        await test_session.commit()


@pytest.mark.asyncio
async def test_notification_status_enum_constraint(test_session, test_user):
    """Test that status must be one of the allowed values."""
    notification = Notification(
        user_id=test_user.id,
        type="task_reminder",
        channel="email",
        recipient="test@example.com",
        subject="Test",
        body="Test body",
        status="invalid_status",  # Should fail CHECK constraint
    )

    with pytest.raises(Exception):  # Should raise database constraint error
        test_session.add(notification)
        await test_session.commit()


@pytest.mark.asyncio
async def test_notification_recipient_max_length(test_session, test_user):
    """Test that recipient has max length of 255 characters."""
    long_recipient = "a" * 256  # 256 characters

    notification = Notification(
        user_id=test_user.id,
        type="task_reminder",
        channel="email",
        recipient=long_recipient,  # Should fail max length constraint
        subject="Test",
        body="Test body",
        status="pending",
    )

    with pytest.raises(Exception):  # Should raise validation or database error
        test_session.add(notification)
        await test_session.commit()


@pytest.mark.asyncio
async def test_notification_subject_max_length(test_session, test_user):
    """Test that subject has max length of 255 characters."""
    long_subject = "a" * 256  # 256 characters

    notification = Notification(
        user_id=test_user.id,
        type="task_reminder",
        channel="email",
        recipient="test@example.com",
        subject=long_subject,  # Should fail max length constraint
        body="Test body",
        status="pending",
    )

    with pytest.raises(Exception):  # Should raise validation or database error
        test_session.add(notification)
        await test_session.commit()


@pytest.mark.asyncio
async def test_notification_body_max_length(test_session, test_user):
    """Test that body has max length of 10,000 characters."""
    long_body = "a" * 10001  # 10,001 characters

    notification = Notification(
        user_id=test_user.id,
        type="task_reminder",
        channel="email",
        recipient="test@example.com",
        subject="Test",
        body=long_body,  # Should fail CHECK constraint
        status="pending",
    )

    with pytest.raises(Exception):  # Should raise database constraint error
        test_session.add(notification)
        await test_session.commit()


@pytest.mark.asyncio
async def test_notification_cascade_delete_on_user(test_session):
    """Test that deleting a user CASCADE deletes their notifications."""
    from src.services.user import create_user
    from src.models.user import UserCreate

    # Create user
    user_data = UserCreate(email="notifuser@example.com", password="password123", name="Notif User")
    user = await create_user(test_session, user_data)
    await test_session.commit()
    await test_session.refresh(user)

    # Create notifications
    notif1 = Notification(
        user_id=user.id,
        type="task_reminder",
        channel="email",
        recipient="test@example.com",
        subject="Reminder 1",
        body="Body 1",
        status="pending",
    )
    notif2 = Notification(
        user_id=user.id,
        type="task_due",
        channel="email",
        recipient="test@example.com",
        subject="Reminder 2",
        body="Body 2",
        status="pending",
    )
    test_session.add_all([notif1, notif2])
    await test_session.commit()

    # Verify notifications exist
    statement = select(Notification).where(Notification.user_id == user.id)
    result = await test_session.execute(statement)
    notifs_before = result.scalars().all()
    assert len(notifs_before) == 2

    # Delete user (should CASCADE delete notifications)
    await test_session.delete(user)
    await test_session.commit()

    # Verify notifications are deleted
    statement = select(Notification).where(Notification.user_id == user.id)
    result = await test_session.execute(statement)
    notifs_after = result.scalars().all()
    assert len(notifs_after) == 0


@pytest.mark.asyncio
async def test_notification_set_null_on_task_deletion(test_session, test_user):
    """Test that deleting a task sets task_id to NULL (not CASCADE delete)."""
    # Create task
    task = Task(user_id=test_user.id, title="Task to delete", completed=False)
    test_session.add(task)
    await test_session.commit()
    await test_session.refresh(task)

    # Create notification linked to task
    notification = Notification(
        user_id=test_user.id,
        task_id=task.id,
        type="task_reminder",
        channel="email",
        recipient="test@example.com",
        subject="Reminder",
        body="Task reminder",
        status="pending",
    )
    test_session.add(notification)
    await test_session.commit()
    await test_session.refresh(notification)

    notification_id = notification.id
    assert notification.task_id == task.id

    # Delete task (should SET NULL on notification.task_id)
    await test_session.delete(task)
    await test_session.commit()

    # Expire all objects to force fresh queries
    test_session.expire_all()

    # Verify notification still exists but task_id is NULL
    statement = select(Notification).where(Notification.id == notification_id)
    result = await test_session.execute(statement)
    updated_notification = result.scalars().first()

    assert updated_notification is not None
    assert updated_notification.task_id is None


@pytest.mark.asyncio
async def test_query_pending_notifications(test_session, test_user):
    """Test querying notifications by pending status."""
    # Create notifications with different statuses
    pending1 = Notification(
        user_id=test_user.id,
        type="task_reminder",
        channel="email",
        recipient="test@example.com",
        subject="Pending 1",
        body="Body",
        status="pending",
    )
    pending2 = Notification(
        user_id=test_user.id,
        type="task_due",
        channel="email",
        recipient="test@example.com",
        subject="Pending 2",
        body="Body",
        status="pending",
    )
    sent = Notification(
        user_id=test_user.id,
        type="task_reminder",
        channel="email",
        recipient="test@example.com",
        subject="Sent",
        body="Body",
        status="sent",
        sent_at=datetime.now(UTC),
    )
    failed = Notification(
        user_id=test_user.id,
        type="task_reminder",
        channel="email",
        recipient="test@example.com",
        subject="Failed",
        body="Body",
        status="failed",
        error_message="Error",
    )

    test_session.add_all([pending1, pending2, sent, failed])
    await test_session.commit()

    # Query only pending notifications
    statement = select(Notification).where(
        Notification.user_id == test_user.id,
        Notification.status == "pending"
    )
    result = await test_session.execute(statement)
    pending_notifs = result.scalars().all()

    assert len(pending_notifs) == 2
    assert all(n.status == "pending" for n in pending_notifs)
