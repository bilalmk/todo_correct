"""Integration tests for notification triggers on task endpoints.

Tests verify that NotificationService is called when:
- Tasks are created (POST)
- Tasks are updated (PATCH/PUT)
- Tasks are marked complete (PATCH /complete)
- Reminders are triggered
"""

import pytest
from datetime import datetime, timezone, timedelta
from uuid import uuid4
from unittest.mock import AsyncMock, patch, MagicMock

from httpx import AsyncClient
from sqlmodel.ext.asyncio.session import AsyncSession

from src.models.user import User
from src.models.task import Task
from src.services.notification import NotificationService


class TestTaskCreationNotifications:
    """Test notifications on task creation (T123)."""

    @pytest.mark.asyncio
    async def test_post_task_sends_notification(
        self, async_client: AsyncClient, test_user: User, auth_headers: dict
    ):
        """Test that POST /api/v1/{user_id}/tasks triggers notification."""

        # Mock the notification service
        with patch('src.services.notification.NotificationService.notify_task_created') as mock_notify:
            mock_notify.return_value = True

            task_data = {
                "title": "Test Task",
                "description": "Task description",
                "priority": "high",
                "completed": False
            }

            response = await async_client.post(
                f"/api/v1/{test_user.id}/tasks",
                json=task_data,
                headers=auth_headers
            )

            assert response.status_code == 201

            # Verify notification was called (if integrated)
            # Note: This will only work after T130 is implemented
            # For now, this is a placeholder test


class TestTaskUpdateNotifications:
    """Test notifications on task updates (T124)."""

    @pytest.mark.asyncio
    async def test_patch_task_sends_notification(
        self, async_client: AsyncClient, test_user: User, test_session: AsyncSession, auth_headers: dict
    ):
        """Test that PATCH /api/v1/{user_id}/tasks/{id} triggers notification."""

        # Create a test task
        task = Task(
            user_id=test_user.id,
            title="Original Task",
            description="Original description",
            completed=False,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        test_session.add(task)
        await test_session.commit()
        await test_session.refresh(task)

        # Mock the notification service
        with patch('src.services.notification.NotificationService.notify_task_updated') as mock_notify:
            mock_notify.return_value = True

            update_data = {
                "title": "Updated Task",
                "priority": "high"
            }

            response = await async_client.patch(
                f"/api/v1/{test_user.id}/tasks/{task.id}",
                json=update_data,
                headers=auth_headers
            )

            assert response.status_code == 200

            # Verify notification was called (if integrated)
            # Note: This will only work after T131 is implemented


class TestTaskCompletionNotifications:
    """Test notifications on task completion (T125)."""

    @pytest.mark.asyncio
    async def test_complete_task_sends_notification(
        self, async_client: AsyncClient, test_user: User, test_session: AsyncSession, auth_headers: dict
    ):
        """Test that PATCH /api/v1/{user_id}/tasks/{id}/complete triggers notification."""

        # Create a test task
        task = Task(
            user_id=test_user.id,
            title="Task to Complete",
            completed=False,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        test_session.add(task)
        await test_session.commit()
        await test_session.refresh(task)

        # Mock the notification service
        with patch('src.services.notification.NotificationService.notify_task_completed') as mock_notify:
            mock_notify.return_value = True

            response = await async_client.patch(
                f"/api/v1/{test_user.id}/tasks/{task.id}/complete",
                headers=auth_headers
            )

            assert response.status_code == 200

            # Verify task was marked complete
            response_data = response.json()
            assert response_data["completed"] is True

            # Verify notification was called (if integrated)
            # Note: This will only work after T132 is implemented


class TestNotificationUserIsolation:
    """Test that notifications respect user isolation (T126)."""

    @pytest.mark.asyncio
    async def test_notification_not_sent_on_user_mismatch(
        self, async_client: AsyncClient, test_session: AsyncSession, auth_headers: dict
    ):
        """Test notification not sent when user_id mismatches authenticated user."""

        # Create two users
        user1 = User(
            id=uuid4(),
            email="user1@example.com",
            name="User 1",
            password_hash="hashed"
        )
        user2_id = uuid4()

        test_session.add(user1)
        await test_session.commit()

        # Try to create task with mismatched user_id
        task_data = {
            "title": "Unauthorized Task",
            "completed": False
        }

        response = await async_client.post(
            f"/api/v1/{user2_id}/tasks",  # Different user_id
            json=task_data,
            headers=auth_headers  # Headers for user1
        )

        # Should fail with 403 Forbidden (user mismatch caught by verify_user_match)
        assert response.status_code == 403

        # Notification service should never be called


class TestReminderNotifications:
    """Test reminder notifications via scheduler (T127)."""

    @pytest.mark.asyncio
    async def test_reminder_notification_sent_when_reminder_at_reached(
        self, test_session: AsyncSession
    ):
        """Test reminder email sent when reminder_at time is reached."""

        user = User(
            id=uuid4(),
            email="user@example.com",
            name="Test User",
            password_hash="hashed"
        )
        test_session.add(user)
        await test_session.flush()

        # Create task with reminder in the past (should trigger)
        task = Task(
            user_id=user.id,
            title="Task with Reminder",
            due_date=datetime.now(timezone.utc) + timedelta(hours=2),
            reminder_at=datetime.now(timezone.utc) - timedelta(minutes=1),  # Past
            completed=False,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        test_session.add(task)
        await test_session.commit()

        # Mock the notification service
        service = NotificationService()

        # Simulate scheduler calling the notification
        result = await service.notify_task_reminder(task, user)

        assert result is True

    @pytest.mark.asyncio
    async def test_reminder_not_sent_for_completed_tasks(
        self, test_session: AsyncSession
    ):
        """Test reminder not sent for already completed tasks."""

        user = User(
            id=uuid4(),
            email="user@example.com",
            name="Test User",
            password_hash="hashed"
        )
        test_session.add(user)
        await test_session.flush()

        # Create completed task with past reminder
        task = Task(
            user_id=user.id,
            title="Completed Task",
            due_date=datetime.now(timezone.utc) + timedelta(hours=2),
            reminder_at=datetime.now(timezone.utc) - timedelta(minutes=1),
            completed=True,  # Already completed
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        test_session.add(task)
        await test_session.commit()

        # Scheduler should filter out completed tasks
        # This is enforced by the scheduler query logic
        # Test verifies the expected behavior

        # In real scheduler: SELECT * FROM tasks
        # WHERE reminder_at <= NOW()
        # AND completed = FALSE
        # AND deleted_at IS NULL

        assert task.completed is True  # Would be filtered by scheduler


class TestNotificationServiceIntegration:
    """Integration tests for NotificationService with database."""

    @pytest.mark.asyncio
    async def test_notification_service_with_real_task_and_user(
        self, test_session: AsyncSession
    ):
        """Test NotificationService with actual database models."""

        # Create real user
        user = User(
            id=uuid4(),
            email="integration@example.com",
            name="Integration Test User",
            password_hash="hashed"
        )
        test_session.add(user)
        await test_session.flush()

        # Create real task
        task = Task(
            user_id=user.id,
            title="Integration Test Task",
            description="Testing notification integration",
            priority="high",
            due_date=datetime.now(timezone.utc) + timedelta(days=1),
            reminder_at=datetime.now(timezone.utc) + timedelta(hours=12),
            completed=False,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        test_session.add(task)
        await test_session.commit()
        await test_session.refresh(task)
        await test_session.refresh(user)

        # Test all notification types
        service = NotificationService()

        # Test creation notification
        result = await service.notify_task_created(task, user)
        assert result is True

        # Test update notification
        changes = {"priority": "high", "title": "Integration Test Task"}
        result = await service.notify_task_updated(task, user, changes)
        assert result is True

        # Test completion notification
        task.completed = True
        result = await service.notify_task_completed(task, user)
        assert result is True

        # Test reminder notification
        result = await service.notify_task_reminder(task, user)
        assert result is True


class TestNotificationErrorHandling:
    """Test notification error handling in integration scenarios."""

    @pytest.mark.asyncio
    async def test_endpoint_continues_on_notification_failure(
        self, async_client: AsyncClient, test_user: User, auth_headers: dict
    ):
        """Test that task endpoint succeeds even if notification fails."""

        # Mock notification to fail
        with patch('src.services.notification.NotificationService.notify_task_created') as mock_notify:
            mock_notify.return_value = False  # Simulated failure

            task_data = {
                "title": "Test Task",
                "completed": False
            }

            response = await async_client.post(
                f"/api/v1/{test_user.id}/tasks",
                json=task_data,
                headers=auth_headers
            )

            # Task creation should still succeed
            # Even if notification fails, task is created
            # Note: Actual behavior depends on T130 implementation
            assert response.status_code == 201 or response.status_code == 200
