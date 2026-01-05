"""Unit tests for QueryService dynamic query building (User Story 3)."""

import pytest
from datetime import datetime, timezone, timedelta
from uuid import uuid4

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from src.models.task_tag import TaskTag
from src.models.task import Task
from src.models.tag import Tag
from src.services.query import QueryService


class TestQueryServiceFiltering:
    """Unit tests for QueryService.build_task_query() filtering logic (T065-T073)."""

    @pytest.mark.asyncio
    async def test_filter_by_status_incomplete(self, test_session: AsyncSession, test_user):
        """Test QueryService with status='incomplete' filter (T065)."""
        # Create 2 incomplete and 1 complete task
        task1 = Task(user_id=test_user.id, title="Task 1", completed=False)
        task2 = Task(user_id=test_user.id, title="Task 2", completed=False)
        task3 = Task(user_id=test_user.id, title="Task 3", completed=True)
        test_session.add_all([task1, task2, task3])
        await test_session.commit()

        # Build query with status filter
        stmt = QueryService.build_task_query(
            user_id=test_user.id,
            status="incomplete"
        )

        # Execute query
        result = await test_session.execute(stmt)
        tasks = result.scalars().all()

        # Verify only incomplete tasks returned
        assert len(tasks) == 2
        assert all(not task.completed for task in tasks)

    @pytest.mark.asyncio
    async def test_filter_by_status_complete(self, test_session: AsyncSession, test_user):
        """Test QueryService with status='complete' filter (T065)."""
        # Create 1 incomplete and 2 complete tasks
        task1 = Task(user_id=test_user.id, title="Task 1", completed=False)
        task2 = Task(user_id=test_user.id, title="Task 2", completed=True)
        task3 = Task(user_id=test_user.id, title="Task 3", completed=True)
        test_session.add_all([task1, task2, task3])
        await test_session.commit()

        # Build query with status filter
        stmt = QueryService.build_task_query(
            user_id=test_user.id,
            status="complete"
        )

        # Execute query
        result = await test_session.execute(stmt)
        tasks = result.scalars().all()

        # Verify only complete tasks returned
        assert len(tasks) == 2
        assert all(task.completed for task in tasks)

    @pytest.mark.asyncio
    async def test_filter_by_priority(self, test_session: AsyncSession, test_user):
        """Test QueryService with priority filter (T066)."""
        # Create tasks with different priorities
        task1 = Task(user_id=test_user.id, title="Low", completed=False, priority="low")
        task2 = Task(user_id=test_user.id, title="Medium", completed=False, priority="medium")
        task3 = Task(user_id=test_user.id, title="High", completed=False, priority="high")
        test_session.add_all([task1, task2, task3])
        await test_session.commit()

        # Filter by high priority
        stmt = QueryService.build_task_query(
            user_id=test_user.id,
            priority="high"
        )

        result = await test_session.execute(stmt)
        tasks = result.scalars().all()

        # Verify only high priority task returned
        assert len(tasks) == 1
        assert tasks[0].priority == "high"
        assert tasks[0].title == "High"

    @pytest.mark.asyncio
    async def test_filter_by_single_tag(self, test_session: AsyncSession, test_user):
        """Test QueryService with single tag filter (T067)."""
        # Create tasks and tags
        task1 = Task(user_id=test_user.id, title="Work Task", completed=False)
        task2 = Task(user_id=test_user.id, title="Personal Task", completed=False)
        task3 = Task(user_id=test_user.id, title="No Tags", completed=False)

        tag_work = Tag(user_id=test_user.id, name="work", color="#FF0000")
        tag_personal = Tag(user_id=test_user.id, name="personal", color="#00FF00")

        test_session.add_all([task1, task2, task3, tag_work, tag_personal])
        await test_session.flush()

        # Assign tags
        test_session.add(TaskTag(task_id=task1.id, tag_id=tag_work.id))
        test_session.add(TaskTag(task_id=task2.id, tag_id=tag_personal.id))
        await test_session.commit()

        # Filter by "work" tag
        stmt = QueryService.build_task_query(
            user_id=test_user.id,
            tags=["work"]
        )

        result = await test_session.execute(stmt)
        tasks = result.scalars().all()

        # Verify only task with "work" tag returned
        assert len(tasks) == 1
        assert tasks[0].title == "Work Task"

    @pytest.mark.asyncio
    async def test_filter_by_multiple_tags_or_logic(self, test_session: AsyncSession, test_user):
        """Test QueryService with multiple tags using OR logic (T068)."""
        # Create tasks and tags
        task1 = Task(user_id=test_user.id, title="Work Task", completed=False)
        task2 = Task(user_id=test_user.id, title="Personal Task", completed=False)
        task3 = Task(user_id=test_user.id, title="Urgent Task", completed=False)

        tag_work = Tag(user_id=test_user.id, name="work", color="#FF0000")
        tag_personal = Tag(user_id=test_user.id, name="personal", color="#00FF00")
        tag_urgent = Tag(user_id=test_user.id, name="urgent", color="#0000FF")

        test_session.add_all([task1, task2, task3, tag_work, tag_personal, tag_urgent])
        await test_session.flush()

        # Assign tags
        test_session.add(TaskTag(task_id=task1.id, tag_id=tag_work.id))
        test_session.add(TaskTag(task_id=task2.id, tag_id=tag_personal.id))
        test_session.add(TaskTag(task_id=task3.id, tag_id=tag_urgent.id))
        await test_session.commit()

        # Filter by "work" OR "personal" (should return 2 tasks)
        stmt = QueryService.build_task_query(
            user_id=test_user.id,
            tags=["work", "personal"]
        )

        result = await test_session.execute(stmt)
        tasks = result.scalars().all()

        # Verify both "work" and "personal" tasks returned
        assert len(tasks) == 2
        titles = {task.title for task in tasks}
        assert titles == {"Work Task", "Personal Task"}

    @pytest.mark.asyncio
    async def test_filter_by_tag_none_untagged_tasks(self, test_session: AsyncSession, test_user):
        """Test QueryService with tag='none' for untagged tasks (T069)."""
        # Create tasks with and without tags
        task1 = Task(user_id=test_user.id, title="Tagged", completed=False)
        task2 = Task(user_id=test_user.id, title="Untagged 1", completed=False)
        task3 = Task(user_id=test_user.id, title="Untagged 2", completed=False)

        tag_work = Tag(user_id=test_user.id, name="work", color="#FF0000")

        test_session.add_all([task1, task2, task3, tag_work])
        await test_session.flush()

        # Assign tag to task1 only
        test_session.add(TaskTag(task_id=task1.id, tag_id=tag_work.id))
        await test_session.commit()

        # Filter by "none" (untagged tasks)
        stmt = QueryService.build_task_query(
            user_id=test_user.id,
            tags=["none"]
        )

        result = await test_session.execute(stmt)
        tasks = result.scalars().all()

        # Verify only untagged tasks returned
        assert len(tasks) == 2
        titles = {task.title for task in tasks}
        assert titles == {"Untagged 1", "Untagged 2"}

    @pytest.mark.asyncio
    async def test_filter_by_tag_none_and_tag_name_or_logic(
        self, test_session: AsyncSession, test_user
    ):
        """Test QueryService with tag='none' + tag name (OR logic) (T069)."""
        # Create tasks
        task1 = Task(user_id=test_user.id, title="Work Task", completed=False)
        task2 = Task(user_id=test_user.id, title="Untagged", completed=False)
        task3 = Task(user_id=test_user.id, title="Personal Task", completed=False)

        tag_work = Tag(user_id=test_user.id, name="work", color="#FF0000")
        tag_personal = Tag(user_id=test_user.id, name="personal", color="#00FF00")

        test_session.add_all([task1, task2, task3, tag_work, tag_personal])
        await test_session.flush()

        # Assign tags
        test_session.add(TaskTag(task_id=task1.id, tag_id=tag_work.id))
        test_session.add(TaskTag(task_id=task3.id, tag_id=tag_personal.id))
        await test_session.commit()

        # Filter by "none" OR "work" (should return untagged + work tasks)
        stmt = QueryService.build_task_query(
            user_id=test_user.id,
            tags=["none", "work"]
        )

        result = await test_session.execute(stmt)
        tasks = result.scalars().all()

        # Verify untagged + work tasks returned (not personal)
        assert len(tasks) == 2
        titles = {task.title for task in tasks}
        assert titles == {"Work Task", "Untagged"}

    @pytest.mark.asyncio
    async def test_filter_by_due_date_range(self, test_session: AsyncSession, test_user):
        """Test QueryService with due_before and due_after filters (T070)."""
        now = datetime.now(timezone.utc)
        yesterday = now - timedelta(days=1)
        tomorrow = now + timedelta(days=1)
        next_week = now + timedelta(days=7)

        # Create tasks with different due dates
        task1 = Task(user_id=test_user.id, title="Past Due", completed=False, due_date=yesterday)
        task2 = Task(user_id=test_user.id, title="Due Soon", completed=False, due_date=tomorrow)
        task3 = Task(user_id=test_user.id, title="Future", completed=False, due_date=next_week)

        test_session.add_all([task1, task2, task3])
        await test_session.commit()

        # Filter by due_after=now and due_before=next_week (should return tomorrow task)
        stmt = QueryService.build_task_query(
            user_id=test_user.id,
            due_after=now,
            due_before=next_week
        )

        result = await test_session.execute(stmt)
        tasks = result.scalars().all()

        # Verify only task due tomorrow is returned
        assert len(tasks) == 1
        assert tasks[0].title == "Due Soon"

    @pytest.mark.asyncio
    async def test_full_text_search(self, test_session: AsyncSession, test_user):
        """Test QueryService with full-text search (T071)."""
        # Create tasks with different content
        task1 = Task(
            user_id=test_user.id,
            title="Meeting with client",
            description="Discuss project requirements",
            completed=False
        )
        task2 = Task(
            user_id=test_user.id,
            title="Write report",
            description="Quarterly financial report",
            completed=False
        )
        task3 = Task(
            user_id=test_user.id,
            title="Review code",
            description="Code review for new feature",
            completed=False
        )

        test_session.add_all([task1, task2, task3])
        await test_session.commit()

        # Search for "meeting"
        stmt = QueryService.build_task_query(
            user_id=test_user.id,
            search="meeting"
        )

        result = await test_session.execute(stmt)
        tasks = result.scalars().all()

        # Verify task with "meeting" in title is found
        assert len(tasks) == 1
        assert tasks[0].title == "Meeting with client"

    @pytest.mark.asyncio
    async def test_sorting_by_created_at_desc(self, test_session: AsyncSession, test_user):
        """Test QueryService with sort_by='created_at' order='desc' (T072)."""
        # Create tasks with different timestamps (sleep to ensure different timestamps)
        import asyncio

        task1 = Task(user_id=test_user.id, title="First", completed=False)
        test_session.add(task1)
        await test_session.commit()

        await asyncio.sleep(0.01)  # Ensure different timestamp

        task2 = Task(user_id=test_user.id, title="Second", completed=False)
        test_session.add(task2)
        await test_session.commit()

        await asyncio.sleep(0.01)

        task3 = Task(user_id=test_user.id, title="Third", completed=False)
        test_session.add(task3)
        await test_session.commit()

        # Sort by created_at descending (default)
        stmt = QueryService.build_task_query(
            user_id=test_user.id,
            sort_by="created_at",
            order="desc"
        )

        result = await test_session.execute(stmt)
        tasks = result.scalars().all()

        # Verify tasks in descending order (newest first)
        assert len(tasks) == 3
        assert tasks[0].title == "Third"
        assert tasks[1].title == "Second"
        assert tasks[2].title == "First"

    @pytest.mark.asyncio
    async def test_sorting_by_due_date_asc(self, test_session: AsyncSession, test_user):
        """Test QueryService with sort_by='due_date' order='asc' (T072)."""
        now = datetime.now(timezone.utc)

        # Create tasks with different due dates
        task1 = Task(
            user_id=test_user.id,
            title="Later",
            completed=False,
            due_date=now + timedelta(days=7)
        )
        task2 = Task(
            user_id=test_user.id,
            title="Sooner",
            completed=False,
            due_date=now + timedelta(days=1)
        )
        task3 = Task(
            user_id=test_user.id,
            title="Middle",
            completed=False,
            due_date=now + timedelta(days=3)
        )

        test_session.add_all([task1, task2, task3])
        await test_session.commit()

        # Sort by due_date ascending (earliest first)
        stmt = QueryService.build_task_query(
            user_id=test_user.id,
            sort_by="due_date",
            order="asc"
        )

        result = await test_session.execute(stmt)
        tasks = result.scalars().all()

        # Verify tasks in ascending due date order
        assert len(tasks) == 3
        assert tasks[0].title == "Sooner"
        assert tasks[1].title == "Middle"
        assert tasks[2].title == "Later"

    @pytest.mark.asyncio
    async def test_combined_filters_and_sort(self, test_session: AsyncSession, test_user):
        """Test QueryService with ALL filters combined (T073)."""
        now = datetime.now(timezone.utc)
        tomorrow = now + timedelta(days=1)

        # Create diverse tasks
        task1 = Task(
            user_id=test_user.id,
            title="High priority work task",
            description="Important meeting",
            completed=False,
            priority="high",
            due_date=tomorrow
        )
        task2 = Task(
            user_id=test_user.id,
            title="Low priority personal task",
            completed=False,
            priority="low",
            due_date=tomorrow
        )
        task3 = Task(
            user_id=test_user.id,
            title="High priority personal task",
            completed=True,  # Completed, so should be filtered out
            priority="high",
            due_date=tomorrow
        )

        tag_work = Tag(user_id=test_user.id, name="work", color="#FF0000")

        test_session.add_all([task1, task2, task3, tag_work])
        await test_session.flush()

        # Tag task1 as "work"
        test_session.add(TaskTag(task_id=task1.id, tag_id=tag_work.id))
        await test_session.commit()

        # Apply ALL filters: status + priority + tag + due_before + search + sort
        stmt = QueryService.build_task_query(
            user_id=test_user.id,
            status="incomplete",  # Exclude task3 (completed)
            priority="high",  # Exclude task2 (low priority)
            tags=["work"],  # Only task1 has "work" tag
            due_before=now + timedelta(days=2),  # Include tomorrow
            due_after=now,  # After now
            search="meeting",  # Only task1 has "meeting" in description
            sort_by="priority",
            order="desc"
        )

        result = await test_session.execute(stmt)
        tasks = result.scalars().all()

        # Verify only task1 matches ALL criteria
        assert len(tasks) == 1
        assert tasks[0].title == "High priority work task"
