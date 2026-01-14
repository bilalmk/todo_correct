"""Database models for the application."""
from src.models.user import User
from src.models.task_tag import TaskTag  # Import junction table FIRST
from src.models.task import Task
from src.models.tag import Tag
from src.models.notification import Notification
from src.models.conversation import Conversation  # ChatKit Phase III (T005)
from src.models.message import Message  # ChatKit Phase III (T006)

__all__ = ["User", "TaskTag", "Task", "Tag", "Notification", "Conversation", "Message"]
