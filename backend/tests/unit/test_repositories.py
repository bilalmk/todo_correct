"""Unit tests for repository soft delete filtering."""

import pytest
from datetime import datetime, timezone
from uuid import uuid4

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from src.models.task_tag import TaskTag  # Import junction table first
from src.models.task import Task
from src.models.tag import Tag
from src.models.user import User
from src.repositories.task import TaskRepository
from src.repositories.tag import TagRepository
from src.schemas.task import TaskCreate, TaskUpdate, TaskReplace


@pytest.fixture
async def create_test_user(test_session: AsyncSession):
    """Helper to create a user for testing."""
    async def _create_user(user_id=None):
        if user_id is None:
            user_id = uuid4()
        user = User(
            id=user_id,
            email=f"{user_id}@test.com",
            name="Test User",
            password_hash="hashed_password",
        )
        test_session.add(user)
        await test_session.flush()
        return user_id
    return _create_user


class TestSoftDeleteFilters:
    """Test that all repository list methods apply WHERE deleted_at IS NULL filter."""

    @pytest.mark.asyncio
    async def test_task_repository_list_tasks_excludes_soft_deleted(
        self, test_session: AsyncSession, create_test_user
    ):
        """Test TaskRepository.list_tasks applies deleted_at IS NULL filter."""
        user_id = await create_test_user()

        # Create 2 active tasks and 1 soft-deleted task
        active_task1 = Task(
            user_id=user_id, title="Active Task 1", completed=False
        )
        active_task2 = Task(
            user_id=user_id, title="Active Task 2", completed=False
        )
        deleted_task = Task(
            user_id=user_id,
            title="Deleted Task",
            completed=False,
            deleted_at=datetime.now(timezone.utc),
        )

        test_session.add(active_task1)
        test_session.add(active_task2)
        test_session.add(deleted_task)
        await test_session.flush()

        # Query using repository
        repo = TaskRepository(test_session)
        tasks = await repo.list_tasks(user_id)

        # Should only return 2 active tasks
        assert len(tasks) == 2
        task_titles = {task.title for task in tasks}
        assert task_titles == {"Active Task 1", "Active Task 2"}
        assert "Deleted Task" not in task_titles

    @pytest.mark.asyncio
    async def test_tag_repository_list_tags_excludes_soft_deleted(
        self, test_session: AsyncSession, create_test_user
    ):
        """Test TagRepository.list_tags applies deleted_at IS NULL filter."""
        user_id = await create_test_user()

        # Create 2 active tags and 1 soft-deleted tag
        active_tag1 = Tag(user_id=user_id, name="work", color="#FF5733")
        active_tag2 = Tag(user_id=user_id, name="personal", color="#00FF00")
        deleted_tag = Tag(
            user_id=user_id,
            name="deleted",
            color="#0000FF",
            deleted_at=datetime.now(timezone.utc),
        )

        test_session.add(active_tag1)
        test_session.add(active_tag2)
        test_session.add(deleted_tag)
        await test_session.flush()

        # Query using repository
        repo = TagRepository(test_session)
        tags = await repo.list_tags(user_id)

        # Should only return 2 active tags
        assert len(tags) == 2
        tag_names = {tag.name for tag in tags}
        assert tag_names == {"work", "personal"}
        assert "deleted" not in tag_names

    @pytest.mark.asyncio
    async def test_soft_deleted_tasks_not_queryable_by_id(
        self, test_session: AsyncSession, create_test_user
    ):
        """Test that get_by_id returns None for soft-deleted tasks."""
        user_id = await create_test_user()

        # Create a task and soft delete it
        task = Task(
            user_id=user_id,
            title="To be deleted",
            completed=False,
            deleted_at=datetime.now(timezone.utc),
        )
        test_session.add(task)
        await test_session.flush()
        task_id = task.id

        # Try to get it by ID
        repo = TaskRepository(test_session)
        result = await repo.get_by_id(user_id, task_id)

        # Should return None (soft delete filter applied)
        assert result is None

    @pytest.mark.asyncio
    async def test_soft_deleted_tags_not_queryable_by_id(
        self, test_session: AsyncSession, create_test_user
    ):
        """Test that get_by_id returns None for soft-deleted tags."""
        user_id = await create_test_user()

        # Create a tag and soft delete it
        tag = Tag(
            user_id=user_id,
            name="deleted_tag",
            color="#FF0000",
            deleted_at=datetime.now(timezone.utc),
        )
        test_session.add(tag)
        await test_session.flush()
        tag_id = tag.id

        # Try to get it by ID
        repo = TagRepository(test_session)
        result = await repo.get_by_id(user_id, tag_id)

        # Should return None (soft delete filter applied)
        assert result is None


class TestTaskRepositoryCRUD:
    """Unit tests for TaskRepository CRUD operations (User Story 1)."""

    @pytest.mark.asyncio
    async def test_create_task(self, test_session: AsyncSession, create_test_user):
        """Test TaskRepository.create() creates task with user_id and returns with ID."""
        user_id = await create_test_user()
        task_data = TaskCreate(
            title="Buy groceries",
            description="Milk, eggs, bread",
            completed=False,
            priority="high",
        )

        repo = TaskRepository(test_session)
        task = await repo.create(user_id, task_data)

        # Verify task was created with ID
        assert task.id is not None
        assert task.user_id == user_id
        assert task.title == "Buy groceries"
        assert task.description == "Milk, eggs, bread"
        assert task.completed is False
        assert task.priority == "high"
        assert task.created_at is not None
        assert task.updated_at is not None
        assert task.deleted_at is None

    @pytest.mark.asyncio
    async def test_get_by_id_with_user_isolation(self, test_session: AsyncSession, create_test_user):
        """Test TaskRepository.get_by_id() enforces user isolation."""
        user1_id = await create_test_user()
        user2_id = await create_test_user()

        # Create task for user1
        task = Task(user_id=user1_id, title="User 1 Task", completed=False)
        test_session.add(task)
        await test_session.flush()
        task_id = task.id

        repo = TaskRepository(test_session)

        # User 1 can access their task
        result = await repo.get_by_id(user1_id, task_id)
        assert result is not None
        assert result.id == task_id

        # User 2 cannot access user 1's task (returns None)
        result = await repo.get_by_id(user2_id, task_id)
        assert result is None

    @pytest.mark.asyncio
    async def test_update_task_partial(self, test_session: AsyncSession, create_test_user):
        """Test TaskRepository.update() performs partial update (PATCH semantics)."""
        user_id = await create_test_user()

        # Create a task
        task = Task(
            user_id=user_id,
            title="Original Title",
            description="Original Description",
            completed=False,
            priority="low",
        )
        test_session.add(task)
        await test_session.flush()
        task_id = task.id

        # Partial update: only title and priority
        update_data = TaskUpdate(title="Updated Title", priority="high")
        repo = TaskRepository(test_session)
        updated_task = await repo.update(user_id, task_id, update_data)

        # Verify only specified fields were updated
        assert updated_task.title == "Updated Title"
        assert updated_task.priority == "high"
        # Other fields remain unchanged
        assert updated_task.description == "Original Description"
        assert updated_task.completed is False
        # Timestamp should be updated
        assert updated_task.updated_at > task.created_at

    @pytest.mark.asyncio
    async def test_replace_task_full(self, test_session: AsyncSession, create_test_user):
        """Test TaskRepository.replace() performs full replacement (PUT semantics)."""
        user_id = await create_test_user()

        # Create a task with all fields
        task = Task(
            user_id=user_id,
            title="Original Title",
            description="Original Description",
            completed=False,
            priority="high",
        )
        test_session.add(task)
        await test_session.flush()
        task_id = task.id

        # Full replacement with different values
        replace_data = TaskReplace(
            title="Replaced Title",
            description="Replaced Description",
            completed=True,
            priority="low",
        )
        repo = TaskRepository(test_session)
        replaced_task = await repo.replace(user_id, task_id, replace_data)

        # All fields should be replaced
        assert replaced_task.title == "Replaced Title"
        assert replaced_task.description == "Replaced Description"
        assert replaced_task.completed is True
        assert replaced_task.priority == "low"

    @pytest.mark.asyncio
    async def test_soft_delete_task(self, test_session: AsyncSession, create_test_user):
        """Test TaskRepository.soft_delete() sets deleted_at timestamp."""
        user_id = await create_test_user()

        # Create a task
        task = Task(user_id=user_id, title="To be deleted", completed=False)
        test_session.add(task)
        await test_session.flush()
        task_id = task.id

        # Soft delete the task
        repo = TaskRepository(test_session)
        result = await repo.soft_delete(user_id, task_id)
        assert result is True

        # Verify task has deleted_at timestamp
        await test_session.refresh(task)
        assert task.deleted_at is not None

        # Verify task is no longer returned by get_by_id
        deleted_task = await repo.get_by_id(user_id, task_id)
        assert deleted_task is None

    @pytest.mark.asyncio
    async def test_soft_delete_nonexistent_task_returns_false(
        self, test_session: AsyncSession
    ):
        """Test soft_delete returns False for non-existent task."""
        user_id = uuid4()
        nonexistent_id = 99999

        repo = TaskRepository(test_session)
        result = await repo.soft_delete(user_id, nonexistent_id)
        assert result is False


class TestTagRepositoryCRUD:
    """Unit tests for TagRepository CRUD operations (User Story 2)."""

    @pytest.mark.asyncio
    async def test_create_tag_with_color_normalization(self, test_session: AsyncSession, test_user):
        """Test TagRepository.create() normalizes hex color to uppercase #RRGGBB."""
        from src.schemas.tag import TagCreate

        tag_data = TagCreate(name="work", color="#f5a")  # Shorthand lowercase

        repo = TagRepository(test_session)
        tag = await repo.create(test_user.id, tag_data)

        assert tag.id is not None
        assert tag.user_id == test_user.id
        assert tag.name == "work"
        assert tag.color == "#FF55AA"  # Normalized to uppercase #RRGGBB

    @pytest.mark.asyncio
    async def test_exists_by_name_for_unique_constraint(self, test_session: AsyncSession, test_user):
        """Test TagRepository.exists_by_name() for unique constraint validation."""
        # Use test_user.id instead of random UUID

        # Create a tag
        tag = Tag(user_id=test_user.id, name="work", color="#FF5733")
        test_session.add(tag)
        await test_session.flush()

        repo = TagRepository(test_session)

        # Should return True for existing tag name
        exists = await repo.exists_by_name(test_user.id, "work")
        assert exists is True

        # Should return False for non-existing tag name
        exists = await repo.exists_by_name(test_user.id, "nonexistent")
        assert exists is False

    @pytest.mark.asyncio
    async def test_update_tag(self, test_session: AsyncSession, test_user):
        """Test TagRepository.update() updates tag fields."""
        from backend.src.schemas.tag import TagUpdate

        # Create a tag
        tag = Tag(user_id=test_user.id, name="work", color="#FF5733")
        test_session.add(tag)
        await test_session.flush()
        tag_id = tag.id

        # Update tag
        update_data = TagUpdate(name="personal", color="#00FF00")
        repo = TagRepository(test_session)
        updated_tag = await repo.update(test_user.id, tag_id, update_data)

        assert updated_tag.name == "personal"
        assert updated_tag.color == "#00FF00"

    @pytest.mark.asyncio
    async def test_soft_delete_tag_preserves_junction_records(
        self, test_session: AsyncSession, test_user
    ):
        """Test TagRepository.soft_delete() preserves TaskTag junction records."""
        from backend.src.models.task_tag import TaskTag

        # Create a task and tag
        task = Task(user_id=test_user.id, title="Test Task", completed=False)
        tag = Tag(user_id=test_user.id, name="work", color="#FF5733")
        test_session.add(task)
        test_session.add(tag)
        await test_session.flush()

        # Create junction record
        task_tag = TaskTag(task_id=task.id, tag_id=tag.id)
        test_session.add(task_tag)
        await test_session.flush()

        # Soft delete the tag
        repo = TagRepository(test_session)
        success = await repo.soft_delete(test_user.id, tag.id)
        assert success is True

        # Verify junction record still exists
        from sqlmodel import select

        stmt = select(TaskTag).where(
            TaskTag.task_id == task.id, TaskTag.tag_id == tag.id
        )
        result = await test_session.execute(stmt)
        junction = result.scalar_one_or_none()
        assert junction is not None  # Junction preserved


class TestTaskTagRepositoryCRUD:
    """Unit tests for TaskTagRepository many-to-many operations (User Story 2)."""

    @pytest.mark.asyncio
    async def test_assign_tag_to_task(self, test_session: AsyncSession, create_test_user):
        """Test TaskTagRepository.assign_tag() creates junction record."""
        from backend.src.repositories.task_tag import TaskTagRepository

        user_id = await create_test_user()

        # Create task and tag
        task = Task(user_id=user_id, title="Test Task", completed=False)
        tag = Tag(user_id=user_id, name="work", color="#FF5733")
        test_session.add(task)
        test_session.add(tag)
        await test_session.flush()

        # Assign tag to task
        repo = TaskTagRepository(test_session)
        success = await repo.assign_tag(user_id, task.id, tag.id)
        assert success is True

        # Verify junction record exists
        from backend.src.models.task_tag import TaskTag
        from sqlmodel import select

        stmt = select(TaskTag).where(
            TaskTag.task_id == task.id, TaskTag.tag_id == tag.id
        )
        result = await test_session.execute(stmt)
        junction = result.scalar_one_or_none()
        assert junction is not None

    @pytest.mark.asyncio
    async def test_unassign_tag_from_task(self, test_session: AsyncSession, create_test_user):
        """Test TaskTagRepository.unassign_tag() removes junction record."""
        from backend.src.repositories.task_tag import TaskTagRepository
        from backend.src.models.task_tag import TaskTag

        user_id = await create_test_user()

        # Create task, tag, and junction
        task = Task(user_id=user_id, title="Test Task", completed=False)
        tag = Tag(user_id=user_id, name="work", color="#FF5733")
        test_session.add(task)
        test_session.add(tag)
        await test_session.flush()

        task_tag = TaskTag(task_id=task.id, tag_id=tag.id)
        test_session.add(task_tag)
        await test_session.flush()

        # Unassign tag
        repo = TaskTagRepository(test_session)
        success = await repo.unassign_tag(user_id, task.id, tag.id)
        assert success is True

        # Verify junction record removed
        from sqlmodel import select

        stmt = select(TaskTag).where(
            TaskTag.task_id == task.id, TaskTag.tag_id == tag.id
        )
        result = await test_session.execute(stmt)
        junction = result.scalar_one_or_none()
        assert junction is None

    @pytest.mark.asyncio
    async def test_get_task_tags_excludes_soft_deleted(self, test_session: AsyncSession, create_test_user):
        """Test TaskTagRepository.get_task_tags() excludes soft-deleted tags."""
        from backend.src.repositories.task_tag import TaskTagRepository
        from backend.src.models.task_tag import TaskTag

        user_id = await create_test_user()

        # Create task with 2 tags
        task = Task(user_id=user_id, title="Test Task", completed=False)
        tag1 = Tag(user_id=user_id, name="work", color="#FF5733")
        tag2 = Tag(user_id=user_id, name="urgent", color="#FF0000", deleted_at=datetime.now(timezone.utc))
        test_session.add(task)
        test_session.add(tag1)
        test_session.add(tag2)
        await test_session.flush()

        # Create junctions for both tags
        task_tag1 = TaskTag(task_id=task.id, tag_id=tag1.id)
        task_tag2 = TaskTag(task_id=task.id, tag_id=tag2.id)
        test_session.add(task_tag1)
        test_session.add(task_tag2)
        await test_session.flush()

        # Get task tags
        repo = TaskTagRepository(test_session)
        tags = await repo.get_task_tags(user_id, task.id)

        # Should only return active tag (tag2 is soft-deleted)
        assert len(tags) == 1
        assert tags[0].name == "work"
