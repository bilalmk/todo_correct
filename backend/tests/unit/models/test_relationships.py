"""Unit tests for model relationships (TaskTag junction table)."""
import pytest
from datetime import datetime, UTC
from sqlmodel import select

from src.models.task import Task
from src.models.tag import Tag
from src.models.task_tag import TaskTag


@pytest.mark.asyncio
async def test_create_task_tag_relationship(test_session, test_user):
    """Test creating a many-to-many relationship between task and tag."""
    # Create a task
    task = Task(user_id=test_user.id, title="Test task", completed=False)
    test_session.add(task)
    await test_session.commit()
    await test_session.refresh(task)

    # Create a tag
    tag = Tag(user_id=test_user.id, name="work", color="#FF0000")
    test_session.add(tag)
    await test_session.commit()
    await test_session.refresh(tag)

    # Create TaskTag relationship
    task_tag = TaskTag(task_id=task.id, tag_id=tag.id)
    test_session.add(task_tag)
    await test_session.commit()
    await test_session.refresh(task_tag)

    assert task_tag.task_id == task.id
    assert task_tag.tag_id == tag.id
    assert task_tag.created_at is not None


@pytest.mark.asyncio
async def test_task_with_multiple_tags(test_session, test_user):
    """Test assigning multiple tags to a single task."""
    # Create a task
    task = Task(user_id=test_user.id, title="Multi-tag task", completed=False)
    test_session.add(task)
    await test_session.commit()
    await test_session.refresh(task)

    # Create multiple tags
    tag1 = Tag(user_id=test_user.id, name="work", color="#FF0000")
    tag2 = Tag(user_id=test_user.id, name="urgent", color="#FFFF00")
    tag3 = Tag(user_id=test_user.id, name="important", color="#00FF00")
    test_session.add_all([tag1, tag2, tag3])
    await test_session.commit()
    await test_session.refresh(tag1)
    await test_session.refresh(tag2)
    await test_session.refresh(tag3)

    # Assign all tags to the task
    task_tag1 = TaskTag(task_id=task.id, tag_id=tag1.id)
    task_tag2 = TaskTag(task_id=task.id, tag_id=tag2.id)
    task_tag3 = TaskTag(task_id=task.id, tag_id=tag3.id)
    test_session.add_all([task_tag1, task_tag2, task_tag3])
    await test_session.commit()

    # Query all tags for this task
    statement = select(TaskTag).where(TaskTag.task_id == task.id)
    result = await test_session.execute(statement)
    task_tags = result.scalars().all()

    assert len(task_tags) == 3
    tag_ids = {tt.tag_id for tt in task_tags}
    assert tag_ids == {tag1.id, tag2.id, tag3.id}


@pytest.mark.asyncio
async def test_tag_with_multiple_tasks(test_session, test_user):
    """Test assigning a single tag to multiple tasks."""
    # Create multiple tasks
    task1 = Task(user_id=test_user.id, title="Task 1", completed=False)
    task2 = Task(user_id=test_user.id, title="Task 2", completed=False)
    task3 = Task(user_id=test_user.id, title="Task 3", completed=False)
    test_session.add_all([task1, task2, task3])
    await test_session.commit()
    await test_session.refresh(task1)
    await test_session.refresh(task2)
    await test_session.refresh(task3)

    # Create a single tag
    tag = Tag(user_id=test_user.id, name="work", color="#0000FF")
    test_session.add(tag)
    await test_session.commit()
    await test_session.refresh(tag)

    # Assign tag to all tasks
    task_tag1 = TaskTag(task_id=task1.id, tag_id=tag.id)
    task_tag2 = TaskTag(task_id=task2.id, tag_id=tag.id)
    task_tag3 = TaskTag(task_id=task3.id, tag_id=tag.id)
    test_session.add_all([task_tag1, task_tag2, task_tag3])
    await test_session.commit()

    # Query all tasks for this tag
    statement = select(TaskTag).where(TaskTag.tag_id == tag.id)
    result = await test_session.execute(statement)
    task_tags = result.scalars().all()

    assert len(task_tags) == 3
    task_ids = {tt.task_id for tt in task_tags}
    assert task_ids == {task1.id, task2.id, task3.id}


@pytest.mark.asyncio
async def test_task_tag_composite_primary_key_uniqueness(test_session, test_user):
    """Test that (task_id, tag_id) is unique (composite primary key)."""
    # Create task and tag
    task = Task(user_id=test_user.id, title="Test task", completed=False)
    tag = Tag(user_id=test_user.id, name="work", color="#FF0000")
    test_session.add_all([task, tag])
    await test_session.commit()
    await test_session.refresh(task)
    await test_session.refresh(tag)

    # Create first TaskTag relationship
    task_tag1 = TaskTag(task_id=task.id, tag_id=tag.id)
    test_session.add(task_tag1)
    await test_session.commit()

    # Try to create duplicate relationship (should fail)
    task_tag2 = TaskTag(task_id=task.id, tag_id=tag.id)

    with pytest.raises(Exception):  # Should raise primary key constraint error
        test_session.add(task_tag2)
        await test_session.commit()


@pytest.mark.asyncio
async def test_task_tag_cascade_delete_on_task_deletion(test_session, test_user):
    """Test that deleting a task CASCADE deletes TaskTag relationships."""
    # Create task and tags
    task = Task(user_id=test_user.id, title="Task to delete", completed=False)
    tag1 = Tag(user_id=test_user.id, name="tag1")
    tag2 = Tag(user_id=test_user.id, name="tag2")
    test_session.add_all([task, tag1, tag2])
    await test_session.commit()
    await test_session.refresh(task)
    await test_session.refresh(tag1)
    await test_session.refresh(tag2)

    # Create TaskTag relationships
    task_tag1 = TaskTag(task_id=task.id, tag_id=tag1.id)
    task_tag2 = TaskTag(task_id=task.id, tag_id=tag2.id)
    test_session.add_all([task_tag1, task_tag2])
    await test_session.commit()

    # Verify relationships exist
    statement = select(TaskTag).where(TaskTag.task_id == task.id)
    result = await test_session.execute(statement)
    task_tags_before = result.scalars().all()
    assert len(task_tags_before) == 2

    # Delete task (should CASCADE delete TaskTag relationships)
    await test_session.delete(task)
    await test_session.commit()

    # Verify TaskTag relationships are deleted
    statement = select(TaskTag).where(TaskTag.task_id == task.id)
    result = await test_session.execute(statement)
    task_tags_after = result.scalars().all()
    assert len(task_tags_after) == 0

    # Verify tags still exist
    statement = select(Tag).where(Tag.id.in_([tag1.id, tag2.id]))
    result = await test_session.execute(statement)
    tags = result.scalars().all()
    assert len(tags) == 2


@pytest.mark.asyncio
async def test_task_tag_cascade_delete_on_tag_deletion(test_session, test_user):
    """Test that deleting a tag CASCADE deletes TaskTag relationships."""
    # Create tasks and tag
    task1 = Task(user_id=test_user.id, title="Task 1", completed=False)
    task2 = Task(user_id=test_user.id, title="Task 2", completed=False)
    tag = Tag(user_id=test_user.id, name="tag_to_delete")
    test_session.add_all([task1, task2, tag])
    await test_session.commit()
    await test_session.refresh(task1)
    await test_session.refresh(task2)
    await test_session.refresh(tag)

    # Create TaskTag relationships
    task_tag1 = TaskTag(task_id=task1.id, tag_id=tag.id)
    task_tag2 = TaskTag(task_id=task2.id, tag_id=tag.id)
    test_session.add_all([task_tag1, task_tag2])
    await test_session.commit()

    # Verify relationships exist
    statement = select(TaskTag).where(TaskTag.tag_id == tag.id)
    result = await test_session.execute(statement)
    task_tags_before = result.scalars().all()
    assert len(task_tags_before) == 2

    # Delete tag (should CASCADE delete TaskTag relationships)
    await test_session.delete(tag)
    await test_session.commit()

    # Verify TaskTag relationships are deleted
    statement = select(TaskTag).where(TaskTag.tag_id == tag.id)
    result = await test_session.execute(statement)
    task_tags_after = result.scalars().all()
    assert len(task_tags_after) == 0

    # Verify tasks still exist
    statement = select(Task).where(Task.id.in_([task1.id, task2.id]))
    result = await test_session.execute(statement)
    tasks = result.scalars().all()
    assert len(tasks) == 2


@pytest.mark.asyncio
async def test_task_tag_foreign_key_task_required(test_session, test_user):
    """Test that TaskTag requires a valid task_id (foreign key constraint)."""
    # Create a tag
    tag = Tag(user_id=test_user.id, name="work")
    test_session.add(tag)
    await test_session.commit()
    await test_session.refresh(tag)

    # Try to create TaskTag with non-existent task_id
    task_tag = TaskTag(task_id=99999, tag_id=tag.id)  # Invalid task_id

    with pytest.raises(Exception):  # Should raise foreign key constraint error
        test_session.add(task_tag)
        await test_session.commit()


@pytest.mark.asyncio
async def test_task_tag_foreign_key_tag_required(test_session, test_user):
    """Test that TaskTag requires a valid tag_id (foreign key constraint)."""
    # Create a task
    task = Task(user_id=test_user.id, title="Test task", completed=False)
    test_session.add(task)
    await test_session.commit()
    await test_session.refresh(task)

    # Try to create TaskTag with non-existent tag_id
    task_tag = TaskTag(task_id=task.id, tag_id=99999)  # Invalid tag_id

    with pytest.raises(Exception):  # Should raise foreign key constraint error
        test_session.add(task_tag)
        await test_session.commit()
