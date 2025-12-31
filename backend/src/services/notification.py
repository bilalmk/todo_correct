"""Notification service for task-related events.

This service handles notification delivery for:
- Task creation
- Task updates
- Task completion
- Due date reminders

Note: Email delivery requires SMTP configuration in production.
For development, notifications are logged only.
"""

import logging
from typing import Optional, Dict, Any
from datetime import datetime
from uuid import UUID

from ..models.task import Task
from ..models.user import User


logger = logging.getLogger(__name__)


class NotificationService:
    """Service for managing task-related notifications."""

    def __init__(self, email_enabled: bool = False, smtp_config: Optional[Dict[str, Any]] = None):
        """
        Initialize notification service.

        Args:
            email_enabled: Whether to send actual emails (requires SMTP config)
            smtp_config: SMTP server configuration (host, port, username, password)
        """
        self.email_enabled = email_enabled
        self.smtp_config = smtp_config or {}

    async def notify_task_created(self, task: Task, user: User) -> bool:
        """
        Send notification when a task is created.

        Args:
            task: The created task
            user: The task owner

        Returns:
            True if notification was sent successfully
        """
        subject = f"Task Created: {task.title}"
        message = self._render_task_created_template(task, user)

        return await self._send_notification(
            user_email=user.email,
            subject=subject,
            message=message,
            notification_type="task_created"
        )

    async def notify_task_updated(self, task: Task, user: User, changes: Dict[str, Any]) -> bool:
        """
        Send notification when a task is updated.

        Args:
            task: The updated task
            user: The task owner
            changes: Dictionary of changed fields

        Returns:
            True if notification was sent successfully
        """
        subject = f"Task Updated: {task.title}"
        message = self._render_task_updated_template(task, user, changes)

        return await self._send_notification(
            user_email=user.email,
            subject=subject,
            message=message,
            notification_type="task_updated"
        )

    async def notify_task_completed(self, task: Task, user: User) -> bool:
        """
        Send notification when a task is marked as completed.

        Args:
            task: The completed task
            user: The task owner

        Returns:
            True if notification was sent successfully
        """
        subject = f"Task Completed: {task.title}"
        message = self._render_task_completed_template(task, user)

        return await self._send_notification(
            user_email=user.email,
            subject=subject,
            message=message,
            notification_type="task_completed"
        )

    async def notify_task_reminder(self, task: Task, user: User) -> bool:
        """
        Send reminder notification for an upcoming task.

        Args:
            task: The task with approaching due date
            user: The task owner

        Returns:
            True if notification was sent successfully
        """
        subject = f"Reminder: {task.title}"
        message = self._render_task_reminder_template(task, user)

        return await self._send_notification(
            user_email=user.email,
            subject=subject,
            message=message,
            notification_type="task_reminder"
        )

    async def _send_notification(
        self,
        user_email: str,
        subject: str,
        message: str,
        notification_type: str
    ) -> bool:
        """
        Send notification via configured channel (email/log).

        Args:
            user_email: Recipient email address
            subject: Email subject
            message: Email body
            notification_type: Type of notification (for logging/metrics)

        Returns:
            True if notification was sent successfully
        """
        if self.email_enabled and self.smtp_config:
            # TODO: Implement actual email sending with SMTP
            # For now, log the notification
            logger.info(
                f"[EMAIL] Would send {notification_type} to {user_email}: {subject}"
            )
            return True
        else:
            # Development mode: log notifications
            logger.info(
                f"[NOTIFICATION] Type: {notification_type}\n"
                f"  To: {user_email}\n"
                f"  Subject: {subject}\n"
                f"  Message: {message[:100]}..."
            )
            return True

    def _render_task_created_template(self, task: Task, user: User) -> str:
        """Render email template for task creation."""
        return f"""
Hello {user.name or user.email},

A new task has been created:

Title: {task.title}
Description: {task.description or 'No description'}
Priority: {task.priority or 'Not set'}
Due Date: {task.due_date.strftime('%Y-%m-%d %H:%M') if task.due_date else 'Not set'}

Created at: {task.created_at.strftime('%Y-%m-%d %H:%M')}

Best regards,
Todo Application
"""

    def _render_task_updated_template(self, task: Task, user: User, changes: Dict[str, Any]) -> str:
        """Render email template for task update."""
        changes_text = "\n".join([f"  - {key}: {value}" for key, value in changes.items()])

        return f"""
Hello {user.name or user.email},

Your task "{task.title}" has been updated.

Changes made:
{changes_text}

Current Status:
  Priority: {task.priority or 'Not set'}
  Due Date: {task.due_date.strftime('%Y-%m-%d %H:%M') if task.due_date else 'Not set'}
  Completed: {'Yes' if task.completed else 'No'}

Best regards,
Todo Application
"""

    def _render_task_completed_template(self, task: Task, user: User) -> str:
        """Render email template for task completion."""
        return f"""
Hello {user.name or user.email},

Congratulations! You've completed a task:

Title: {task.title}
Description: {task.description or 'No description'}

Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M')}

Keep up the great work!

Best regards,
Todo Application
"""

    def _render_task_reminder_template(self, task: Task, user: User) -> str:
        """Render email template for task reminder."""
        return f"""
Hello {user.name or user.email},

This is a reminder for your upcoming task:

Title: {task.title}
Description: {task.description or 'No description'}
Priority: {task.priority or 'Not set'}
Due Date: {task.due_date.strftime('%Y-%m-%d %H:%M') if task.due_date else 'Unknown'}

Don't forget to complete it!

Best regards,
Todo Application
"""
