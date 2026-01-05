"""Reminder notification scheduler for task reminders.

This module provides a background worker that periodically checks for tasks
with upcoming reminders and sends notifications to users.
"""

import asyncio
import logging
from datetime import datetime, timezone
from typing import Optional

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from ..core.database import get_session
from ..models.task import Task
from ..models.user import User
from ..services.notification import NotificationService

logger = logging.getLogger(__name__)


class ReminderScheduler:
    """Background scheduler for task reminder notifications.

    Periodically checks for tasks with reminder_at <= NOW() and sends
    email notifications to users. Only processes incomplete, non-deleted tasks.
    """

    def __init__(
        self,
        check_interval: int = 60,
        email_enabled: bool = False,
        smtp_config: Optional[dict] = None,
    ):
        """Initialize the reminder scheduler.

        Args:
            check_interval: Seconds between reminder checks (default: 60)
            email_enabled: Enable actual email sending (default: False for dev)
            smtp_config: SMTP configuration for email delivery
        """
        self.check_interval = check_interval
        self.notification_service = NotificationService(
            email_enabled=email_enabled,
            smtp_config=smtp_config or {}
        )
        self.running = False
        logger.info(
            f"ReminderScheduler initialized: check_interval={check_interval}s, "
            f"email_enabled={email_enabled}"
        )

    async def start(self):
        """Start the reminder scheduler background loop."""
        if self.running:
            logger.warning("Scheduler already running")
            return

        self.running = True
        logger.info("ReminderScheduler started")

        try:
            while self.running:
                await self._check_reminders()
                await asyncio.sleep(self.check_interval)
        except asyncio.CancelledError:
            logger.info("ReminderScheduler cancelled")
        except Exception as e:
            logger.error(f"ReminderScheduler error: {e}", exc_info=True)
        finally:
            self.running = False
            logger.info("ReminderScheduler stopped")

    async def stop(self):
        """Stop the reminder scheduler."""
        logger.info("Stopping ReminderScheduler...")
        self.running = False

    async def _check_reminders(self):
        """Check for tasks with reminders due and send notifications.

        Query logic:
        - reminder_at <= NOW()
        - completed = FALSE
        - deleted_at IS NULL
        - reminder_sent = FALSE (if implemented)

        For each matching task, fetch the user and send notification.
        """
        try:
            async for session in get_session():
                now = datetime.now(timezone.utc)

                # Query for tasks with reminders due
                stmt = (
                    select(Task)
                    .where(Task.reminder_at <= now)
                    .where(Task.completed == False)
                    .where(Task.deleted_at == None)
                )

                result = await session.execute(stmt)
                tasks = result.scalars().all()

                if not tasks:
                    logger.debug(f"No reminders due at {now.isoformat()}")
                    return

                logger.info(f"Found {len(tasks)} tasks with reminders due")

                # Process each task
                for task in tasks:
                    await self._send_reminder(session, task)

                await session.commit()

        except Exception as e:
            logger.error(f"Error checking reminders: {e}", exc_info=True)

    async def _send_reminder(self, session: AsyncSession, task: Task):
        """Send reminder notification for a single task.

        Args:
            session: Database session
            task: Task with reminder due
        """
        try:
            # Fetch user
            user_stmt = select(User).where(User.id == task.user_id)
            user_result = await session.execute(user_stmt)
            user = user_result.scalar_one_or_none()

            if not user:
                logger.warning(f"User {task.user_id} not found for task {task.id}")
                return

            # Send notification
            success = await self.notification_service.notify_task_reminder(task, user)

            if success:
                logger.info(
                    f"Reminder sent for task {task.id} "
                    f"(user: {user.email}, title: '{task.title}')"
                )

                # Optional: Mark reminder as sent to avoid duplicates
                # This requires adding a 'reminder_sent' field to Task model
                # For now, we rely on clearing reminder_at after sending
                # or implementing idempotency in the notification service

            else:
                logger.warning(f"Failed to send reminder for task {task.id}")

        except Exception as e:
            logger.error(f"Error sending reminder for task {task.id}: {e}", exc_info=True)


async def run_scheduler(
    check_interval: int = 60,
    email_enabled: bool = False,
    smtp_config: Optional[dict] = None,
):
    """Run the reminder scheduler as a standalone background task.

    Usage:
        # In main.py or separate worker process
        import asyncio
        from src.notifications.scheduler import run_scheduler

        asyncio.run(run_scheduler(
            check_interval=60,
            email_enabled=True,
            smtp_config={
                "host": "smtp.gmail.com",
                "port": 587,
                "username": "app@example.com",
                "password": "secret"
            }
        ))

    Args:
        check_interval: Seconds between checks (default: 60)
        email_enabled: Enable email sending (default: False)
        smtp_config: SMTP configuration dict
    """
    scheduler = ReminderScheduler(
        check_interval=check_interval,
        email_enabled=email_enabled,
        smtp_config=smtp_config,
    )

    try:
        await scheduler.start()
    except KeyboardInterrupt:
        logger.info("Received interrupt signal")
    finally:
        await scheduler.stop()


# Example: Run scheduler as main module for testing
if __name__ == "__main__":
    import sys

    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        stream=sys.stdout,
    )

    # Run scheduler
    asyncio.run(run_scheduler(check_interval=30))  # Check every 30 seconds for testing
