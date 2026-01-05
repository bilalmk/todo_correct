"""Unit tests for tag filtering queries."""
import pytest
from datetime import datetime, UTC
from sqlmodel import select

from src.models.task import Task
from src.models.tag import Tag
from src.models.task_tag import TaskTag


@pytest.mark.asyncio
async def test_find_all_tasks_with_specific_tag(test_session, test_user):
    """Test finding all tasks that have a specific tag."""
    # Create tasks
    task1 = Task(user_id=test_user.id, title="Work meeting", completed=False)
    task2 = Task(user_id=test_user.id, title="Work report", completed=False)
    task3 = Task(user_id=test_user.id, title="Personal shopping", completed=False)
    test_session.add_all([task1, task2, task3])
    await test_session.commit()
    await test_session.refresh(task1)
    await test_session.refresh(task2)
    await test_session.refresh(task3)

    # Create tags
    work_tag = Tag(user_id=test_user.id, name="work", color="#FF0000")
    personal_tag = Tag(user_id=test_user.id, name="personal", color="#00FF00")
    test_session.add_all([work_tag, personal_tag])
    await test_session.commit()
    await test_session.refresh(work_tag)
    await test_session.refresh(personal_tag)

    # Assign tags to tasks
    test_session.add_all([
        TaskTag(task_id=task1.id, tag_id=work_tag.id),
        TaskTag(task_id=task2.id, tag_id=work_tag.id),
        TaskTag(task_id=task3.id, tag_id=personal_tag.id),
    ])
    await test_session.commit()

    # Find all tasks with "work" tag
    statement = (
        select(Task)
        .join(TaskTag, Task.id == TaskTag.task_id)
        .where(TaskTag.tag_id == work_tag.id)
    )
    result = await test_session.execute(statement)
    work_tasks = result.scalars().all()

    assert len(work_tasks) == 2
    assert set(task.title for task in work_tasks) == {"Work meeting", "Work report"}


@pytest.mark.asyncio
async def test_find_tasks_with_multiple_tags(test_session, test_user):
    """Test finding tasks that have multiple specific tags (AND logic)."""
    # Create tasks
    task1 = Task(user_id=test_user.id, title="Urgent work meeting", completed=False)
    task2 = Task(user_id=test_user.id, title="Regular work task", completed=False)
    task3 = Task(user_id=test_user.id, title="Urgent personal task", completed=False)
    test_session.add_all([task1, task2, task3])
    await test_session.commit()
    await test_session.refresh(task1)
    await test_session.refresh(task2)
    await test_session.refresh(task3)

    # Create tags
    work_tag = Tag(user_id=test_user.id, name="work")
    urgent_tag = Tag(user_id=test_user.id, name="urgent")
    personal_tag = Tag(user_id=test_user.id, name="personal")
    test_session.add_all([work_tag, urgent_tag, personal_tag])
    await test_session.commit()
    await test_session.refresh(work_tag)
    await test_session.refresh(urgent_tag)
    await test_session.refresh(personal_tag)

    # Assign tags
    test_session.add_all([
        TaskTag(task_id=task1.id, tag_id=work_tag.id),
        TaskTag(task_id=task1.id, tag_id=urgent_tag.id),
        TaskTag(task_id=task2.id, tag_id=work_tag.id),
        TaskTag(task_id=task3.id, tag_id=urgent_tag.id),
        TaskTag(task_id=task3.id, tag_id=personal_tag.id),
    ])
    await test_session.commit()

    # Find tasks that have BOTH "work" AND "urgent" tags
    statement = (
        select(Task)
        .join(TaskTag, Task.id == TaskTag.task_id)
        .where(TaskTag.tag_id == work_tag.id)
        .where(
            Task.id.in_(
                select(TaskTag.task_id)
                .where(TaskTag.tag_id == urgent_tag.id)
            )
        )
    )
    result = await test_session.execute(statement)
    urgent_work_tasks = result.scalars().all()

    assert len(urgent_work_tasks) == 1
    assert urgent_work_tasks[0].title == "Urgent work meeting"


@pytest.mark.asyncio
async def test_find_tags_for_specific_task(test_session, test_user):
    """Test finding all tags assigned to a specific task."""
    # Create task
    task = Task(user_id=test_user.id, title="Multi-tagged task", completed=False)
    test_session.add(task)
    await test_session.commit()
    await test_session.refresh(task)

    # Create tags
    tag1 = Tag(user_id=test_user.id, name="work")
    tag2 = Tag(user_id=test_user.id, name="urgent")
    tag3 = Tag(user_id=test_user.id, name="important")
    test_session.add_all([tag1, tag2, tag3])
    await test_session.commit()
    await test_session.refresh(tag1)
    await test_session.refresh(tag2)
    await test_session.refresh(tag3)

    # Assign tags to task
    test_session.add_all([
        TaskTag(task_id=task.id, tag_id=tag1.id),
        TaskTag(task_id=task.id, tag_id=tag2.id),
        TaskTag(task_id=task.id, tag_id=tag3.id),
    ])
    await test_session.commit()

    # Find all tags for this task
    statement = (
        select(Tag)
        .join(TaskTag, Tag.id == TaskTag.tag_id)
        .where(TaskTag.task_id == task.id)
    )
    result = await test_session.execute(statement)
    task_tags = result.scalars().all()

    assert len(task_tags) == 3
    assert set(tag.name for tag in task_tags) == {"work", "urgent", "important"}


@pytest.mark.asyncio
async def test_filter_tasks_by_tag_and_user_isolation(test_session):
    """Test that tag filtering respects user isolation."""
    from src.services.user import create_user
    from src.models.user import UserCreate

    # Create two users
    user1_data = UserCreate(email="tagquery1@example.com", password="password123", name="User 1")
    user2_data = UserCreate(email="tagquery2@example.com", password="password123", name="User 2")

    user1 = await create_user(test_session, user1_data)
    user2 = await create_user(test_session, user2_data)
    await test_session.commit()
    await test_session.refresh(user1)
    await test_session.refresh(user2)

    # Create tasks for both users
    task1_user1 = Task(user_id=user1.id, title="User 1 work task", completed=False)
    task2_user1 = Task(user_id=user1.id, title="User 1 personal task", completed=False)
    task1_user2 = Task(user_id=user2.id, title="User 2 work task", completed=False)
    test_session.add_all([task1_user1, task2_user1, task1_user2])
    await test_session.commit()
    await test_session.refresh(task1_user1)
    await test_session.refresh(task2_user1)
    await test_session.refresh(task1_user2)

    # Create "work" tag for both users
    work_tag_user1 = Tag(user_id=user1.id, name="work")
    work_tag_user2 = Tag(user_id=user2.id, name="work")
    test_session.add_all([work_tag_user1, work_tag_user2])
    await test_session.commit()
    await test_session.refresh(work_tag_user1)
    await test_session.refresh(work_tag_user2)

    # Assign tags
    test_session.add_all([
        TaskTag(task_id=task1_user1.id, tag_id=work_tag_user1.id),
        TaskTag(task_id=task1_user2.id, tag_id=work_tag_user2.id),
    ])
    await test_session.commit()

    # Find user1's tasks with "work" tag (should only see user1's tasks)
    statement = (
        select(Task)
        .join(TaskTag, Task.id == TaskTag.task_id)
        .where(TaskTag.tag_id == work_tag_user1.id)
        .where(Task.user_id == user1.id)
    )
    result = await test_session.execute(statement)
    user1_work_tasks = result.scalars().all()

    assert len(user1_work_tasks) == 1
    assert user1_work_tasks[0].title == "User 1 work task"
    assert user1_work_tasks[0].user_id == user1.id


@pytest.mark.asyncio
async def test_filter_tasks_excluding_soft_deleted_tags(test_session, test_user):
    """Test that soft-deleted tags are excluded from queries."""
    # Create tasks
    task1 = Task(user_id=test_user.id, title="Task 1", completed=False)
    task2 = Task(user_id=test_user.id, title="Task 2", completed=False)
    test_session.add_all([task1, task2])
    await test_session.commit()
    await test_session.refresh(task1)
    await test_session.refresh(task2)

    # Create tag
    tag = Tag(user_id=test_user.id, name="work")
    test_session.add(tag)
    await test_session.commit()
    await test_session.refresh(tag)

    # Assign tag to both tasks
    test_session.add_all([
        TaskTag(task_id=task1.id, tag_id=tag.id),
        TaskTag(task_id=task2.id, tag_id=tag.id),
    ])
    await test_session.commit()

    # Soft delete the tag
    tag.deleted_at = datetime.now(UTC)
    test_session.add(tag)
    await test_session.commit()

    # Query tasks with non-deleted tags only
    statement = (
        select(Task)
        .join(TaskTag, Task.id == TaskTag.task_id)
        .join(Tag, Tag.id == TaskTag.tag_id)
        .where(Tag.deleted_at.is_(None))
        .where(Task.user_id == test_user.id)
    )
    result = await test_session.execute(statement)
    active_tagged_tasks = result.scalars().all()

    # Should return no tasks because the tag is soft-deleted
    assert len(active_tagged_tasks) == 0


@pytest.mark.asyncio
async def test_count_tasks_per_tag(test_session, test_user):
    """Test counting how many tasks are assigned to each tag."""
    from sqlalchemy import func

    # Create tasks
    tasks = [
        Task(user_id=test_user.id, title=f"Task {i}", completed=False)
        for i in range(5)
    ]
    test_session.add_all(tasks)
    await test_session.commit()
    for task in tasks:
        await test_session.refresh(task)

    # Create tags
    work_tag = Tag(user_id=test_user.id, name="work")
    urgent_tag = Tag(user_id=test_user.id, name="urgent")
    test_session.add_all([work_tag, urgent_tag])
    await test_session.commit()
    await test_session.refresh(work_tag)
    await test_session.refresh(urgent_tag)

    # Assign tags: 3 tasks with "work", 2 tasks with "urgent"
    test_session.add_all([
        TaskTag(task_id=tasks[0].id, tag_id=work_tag.id),
        TaskTag(task_id=tasks[1].id, tag_id=work_tag.id),
        TaskTag(task_id=tasks[2].id, tag_id=work_tag.id),
        TaskTag(task_id=tasks[3].id, tag_id=urgent_tag.id),
        TaskTag(task_id=tasks[4].id, tag_id=urgent_tag.id),
    ])
    await test_session.commit()

    # Count tasks per tag
    statement = (
        select(Tag.name, func.count(TaskTag.task_id).label("task_count"))
        .join(TaskTag, Tag.id == TaskTag.tag_id)
        .where(Tag.user_id == test_user.id)
        .group_by(Tag.id, Tag.name)
    )
    result = await test_session.execute(statement)
    tag_counts = result.all()

    # Convert to dict for easier assertion
    counts_dict = {name: count for name, count in tag_counts}

    assert counts_dict["work"] == 3
    assert counts_dict["urgent"] == 2


@pytest.mark.asyncio
async def test_find_untagged_tasks(test_session, test_user):
    """Test finding tasks that have no tags assigned."""
    # Create tasks
    tagged_task = Task(user_id=test_user.id, title="Tagged task", completed=False)
    untagged_task1 = Task(user_id=test_user.id, title="Untagged task 1", completed=False)
    untagged_task2 = Task(user_id=test_user.id, title="Untagged task 2", completed=False)
    test_session.add_all([tagged_task, untagged_task1, untagged_task2])
    await test_session.commit()
    await test_session.refresh(tagged_task)
    await test_session.refresh(untagged_task1)
    await test_session.refresh(untagged_task2)

    # Create tag and assign to one task
    tag = Tag(user_id=test_user.id, name="work")
    test_session.add(tag)
    await test_session.commit()
    await test_session.refresh(tag)

    task_tag = TaskTag(task_id=tagged_task.id, tag_id=tag.id)
    test_session.add(task_tag)
    await test_session.commit()

    # Find tasks with no tags (LEFT JOIN WHERE task_tags.task_id IS NULL)
    from sqlalchemy.orm import outerjoin

    statement = (
        select(Task)
        .outerjoin(TaskTag, Task.id == TaskTag.task_id)
        .where(TaskTag.task_id.is_(None))
        .where(Task.user_id == test_user.id)
    )
    result = await test_session.execute(statement)
    untagged_tasks = result.scalars().all()

    assert len(untagged_tasks) == 2
    assert set(task.title for task in untagged_tasks) == {"Untagged task 1", "Untagged task 2"}
