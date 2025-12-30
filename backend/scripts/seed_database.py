"""Database seeding script with Factory pattern.

Creates sample data for development and testing:
- 3 users
- 10 tasks per user (variety of statuses, priorities, due dates)
- 5 tags per user
- Sample notifications for each user

Usage:
    python scripts/seed_database.py
"""
import asyncio
import random
from datetime import datetime, timedelta, timezone
from typing import List
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from src.core.database import get_session
from src.models.user import User, UserCreate
from src.models.task import Task
from src.models.tag import Tag
from src.models.task_tag import TaskTag
from src.models.notification import Notification
from src.services.user import create_user


class DataFactory:
    """Factory for generating realistic test data."""

    FIRST_NAMES = ["Alice", "Bob", "Carol", "David", "Eve", "Frank", "Grace", "Henry"]
    LAST_NAMES = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller"]

    TASK_TITLES = [
        "Review quarterly report",
        "Prepare presentation slides",
        "Update project documentation",
        "Fix critical bug in production",
        "Implement new feature",
        "Conduct team meeting",
        "Write unit tests",
        "Deploy to staging environment",
        "Review pull requests",
        "Refactor legacy code",
        "Optimize database queries",
        "Create API documentation",
        "Setup CI/CD pipeline",
        "Analyze user feedback",
        "Design new UI mockups",
        "Research competitor products",
        "Plan sprint backlog",
        "Conduct code review",
        "Update dependencies",
        "Security audit",
    ]

    TASK_DESCRIPTIONS = [
        "This task requires immediate attention and careful planning.",
        "Follow the standard procedure outlined in the documentation.",
        "Coordinate with the team before proceeding.",
        "Ensure all tests pass before deployment.",
        "Document any changes made during implementation.",
        "Consider edge cases and error handling.",
        "Review previous implementations for reference.",
        "Get stakeholder approval before finalizing.",
        "Monitor performance metrics after completion.",
        "Schedule a follow-up meeting to discuss results.",
    ]

    TAG_NAMES = [
        ("Work", "#3B82F6"),
        ("Personal", "#10B981"),
        ("Urgent", "#EF4444"),
        ("Important", "#F59E0B"),
        ("Health", "#8B5CF6"),
        ("Finance", "#EC4899"),
        ("Learning", "#6366F1"),
        ("Shopping", "#14B8A6"),
        ("Family", "#F97316"),
        ("Travel", "#06B6D4"),
        ("Home", "#84CC16"),
        ("Project", "#A855F7"),
    ]

    @staticmethod
    def generate_email(first_name: str, last_name: str, index: int = 0) -> str:
        """Generate a unique email address."""
        suffix = f"{index}" if index > 0 else ""
        return f"{first_name.lower()}.{last_name.lower()}{suffix}@example.com"

    @staticmethod
    def generate_user(index: int) -> UserCreate:
        """Generate a user with realistic data."""
        first = random.choice(DataFactory.FIRST_NAMES)
        last = random.choice(DataFactory.LAST_NAMES)

        return UserCreate(
            email=DataFactory.generate_email(first, last, index),
            password="Password123!",  # Same password for all test users
            name=f"{first} {last}",
        )

    @staticmethod
    def generate_task(user_id: UUID, index: int) -> Task:
        """Generate a task with realistic data."""
        now = datetime.now(timezone.utc)

        # Vary completion status (60% incomplete, 40% complete)
        completed = random.random() < 0.4

        # Vary priority (30% high, 40% medium, 30% low or None)
        priority_choice = random.random()
        if priority_choice < 0.3:
            priority = "high"
        elif priority_choice < 0.7:
            priority = "medium"
        elif priority_choice < 0.9:
            priority = "low"
        else:
            priority = None

        # Vary due dates (60% have due dates)
        due_date = None
        reminder_at = None
        if random.random() < 0.6:
            # Due date between -7 days (overdue) and +30 days (future)
            days_offset = random.randint(-7, 30)
            due_date = now + timedelta(days=days_offset)

            # 50% of tasks with due dates have reminders
            if random.random() < 0.5:
                reminder_at = due_date - timedelta(hours=random.randint(1, 24))

        # Vary recurrence (20% of tasks)
        recurrence_pattern = None
        recurrence_config = None
        if random.random() < 0.2:
            recurrence_pattern = random.choice(["daily", "weekly", "monthly"])
            if recurrence_pattern == "weekly":
                recurrence_config = {"days": [random.choice([1, 2, 3, 4, 5])]}
            elif recurrence_pattern == "monthly":
                recurrence_config = {"day_of_month": random.randint(1, 28)}

        return Task(
            user_id=user_id,
            title=random.choice(DataFactory.TASK_TITLES),
            description=random.choice(DataFactory.TASK_DESCRIPTIONS) if random.random() < 0.8 else None,
            completed=completed,
            priority=priority,
            due_date=due_date,
            reminder_at=reminder_at,
            recurrence_pattern=recurrence_pattern,
            recurrence_config=recurrence_config,
        )

    @staticmethod
    def generate_tag(user_id: UUID, index: int) -> Tag:
        """Generate a tag with realistic data."""
        tag_data = DataFactory.TAG_NAMES[index % len(DataFactory.TAG_NAMES)]
        name, color = tag_data

        return Tag(
            user_id=user_id,
            name=f"{name}",
            color=color,
        )

    @staticmethod
    def generate_notification(user_id: UUID, task_id: int | None, index: int) -> Notification:
        """Generate a notification with realistic data."""
        notification_types = ["task_reminder", "task_due", "task_overdue", "task_completed"]
        channels = ["email", "push"]
        statuses = ["pending", "sent", "failed"]

        # Most notifications are pending (70%)
        status_weights = [0.7, 0.25, 0.05]
        status = random.choices(statuses, weights=status_weights)[0]

        notif_type = random.choice(notification_types)
        channel = random.choice(channels)

        # Generate appropriate content based on type
        subjects = {
            "task_reminder": "Reminder: Task due soon",
            "task_due": "Task is due today",
            "task_overdue": "Task is overdue",
            "task_completed": "Task completed successfully",
        }

        bodies = {
            "task_reminder": "Don't forget about your upcoming task!",
            "task_due": "Your task is due today. Please complete it soon.",
            "task_overdue": "This task is now overdue. Please address it ASAP.",
            "task_completed": "Great job! You've completed this task.",
        }

        return Notification(
            user_id=user_id,
            task_id=task_id,
            type=notif_type,
            channel=channel,
            recipient=f"user{index}@example.com",
            subject=subjects[notif_type],
            body=bodies[notif_type],
            status=status,
            sent_at=datetime.now(timezone.utc) if status == "sent" else None,
            error_message="SMTP connection timeout" if status == "failed" else None,
        )


async def seed_database() -> None:
    """Seed the database with sample data."""
    print("🌱 Starting database seeding...")

    async for session in get_session():
        try:
            # Check if data already exists
            result = await session.exec(select(User))
            # session.exec may return a Result or a ScalarResult depending on SQLModel/SQLAlchemy versions.
            # Handle both cases robustly.
            scalars_func = getattr(result, "scalars", None)
            if callable(scalars_func):
                existing_users = scalars_func().all()
            else:
                rows = result.all()
                # rows may be a list of Row objects (tuples) or of User objects
                if rows and not isinstance(rows[0], User):
                    existing_users = [r[0] for r in rows]
                else:
                    existing_users = rows

            if len(existing_users) > 0:
                print(f"⚠️  Database already contains {len(existing_users)} users.")
                response = input("Do you want to continue and add more data? (y/n): ")
                if response.lower() != 'y':
                    print("❌ Seeding cancelled.")
                    return

            # Create 3 users
            print("\n👥 Creating users...")
            users: List[User] = []
            for i in range(3):
                user_data = DataFactory.generate_user(i)
                user = await create_user(session, user_data)
                users.append(user)
                print(f"   ✓ Created user: {user.name} ({user.email})")

            await session.commit()

            # Refresh users to get their IDs
            for user in users:
                await session.refresh(user)

            print(f"\n✅ Created {len(users)} users")

            # For each user, create tasks, tags, and notifications
            for user_index, user in enumerate(users):
                print(f"\n📊 Creating data for {user.name}...")

                # Create 10 tasks
                tasks: List[Task] = []
                for i in range(10):
                    task = DataFactory.generate_task(user.id, i)
                    session.add(task)
                    tasks.append(task)

                await session.commit()

                # Refresh tasks to get their IDs
                for task in tasks:
                    await session.refresh(task)

                print(f"   ✓ Created {len(tasks)} tasks")

                # Create 5 tags
                tags: List[Tag] = []
                for i in range(5):
                    tag = DataFactory.generate_tag(user.id, user_index * 5 + i)
                    session.add(tag)
                    tags.append(tag)

                await session.commit()

                # Refresh tags to get their IDs
                for tag in tags:
                    await session.refresh(tag)

                print(f"   ✓ Created {len(tags)} tags")

                # Assign random tags to tasks (each task gets 1-3 tags)
                task_tag_count = 0
                for task in tasks:
                    num_tags = random.randint(1, 3)
                    selected_tags = random.sample(tags, min(num_tags, len(tags)))

                    for tag in selected_tags:
                        task_tag = TaskTag(task_id=task.id, tag_id=tag.id)
                        session.add(task_tag)
                        task_tag_count += 1

                await session.commit()
                print(f"   ✓ Created {task_tag_count} task-tag associations")

                # Create notifications (3 per user, some linked to tasks)
                notifications: List[Notification] = []
                for i in range(3):
                    # 70% of notifications are linked to a task
                    task_id = random.choice(tasks).id if random.random() < 0.7 else None

                    notification = DataFactory.generate_notification(user.id, task_id, i)
                    session.add(notification)
                    notifications.append(notification)

                await session.commit()
                print(f"   ✓ Created {len(notifications)} notifications")

            # Print summary
            print("\n" + "="*50)
            print("✅ Database seeding completed successfully!")
            print("="*50)
            print(f"   Users: {len(users)}")
            print(f"   Tasks: {len(users) * 10}")
            print(f"   Tags: {len(users) * 5}")
            print(f"   Notifications: {len(users) * 3}")
            print("="*50)

        except Exception as e:
            print(f"\n❌ Error during seeding: {e}")
            await session.rollback()
            raise
        finally:
            await session.close()
            break


if __name__ == "__main__":
    asyncio.run(seed_database())
