"""Integration tests for Task-Tag relationship endpoints (User Story 2)."""

import pytest
from httpx import AsyncClient
from fastapi import status


class TestTaskTagRelationshipEndpoints:
    """Integration tests for 3 task-tag relationship endpoints."""

    @pytest.mark.asyncio
    async def test_assign_tag_to_task_201_created(
        self, client: AsyncClient, auth_headers: dict, user_id: str, session
    ):
        """Test POST /api/v1/{user_id}/tasks/{id}/tags returns 201."""
        from backend.src.models.task import Task
        from backend.src.models.tag import Tag
        from uuid import UUID

        # Create task and tag
        task = Task(user_id=UUID(user_id), title="Test Task", completed=False)
        tag = Tag(user_id=UUID(user_id), name="work", color="#FF5733")
        session.add(task)
        session.add(tag)
        await session.commit()

        response = await client.post(
            f"/api/v1/{user_id}/tasks/{task.id}/tags",
            json={"tag_id": tag.id},
            headers=auth_headers,
        )

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["task_id"] == task.id
        assert data["tag_id"] == tag.id
        assert "message" in data

    @pytest.mark.asyncio
    async def test_assign_duplicate_tag_409_conflict(
        self, client: AsyncClient, auth_headers: dict, user_id: str, session
    ):
        """Test POST /api/v1/{user_id}/tasks/{id}/tags duplicate returns 409."""
        from backend.src.models.task import Task
        from backend.src.models.tag import Tag
        from backend.src.models.task_tag import TaskTag
        from uuid import UUID

        # Create task, tag, and junction
        task = Task(user_id=UUID(user_id), title="Test Task", completed=False)
        tag = Tag(user_id=UUID(user_id), name="work", color="#FF5733")
        session.add(task)
        session.add(tag)
        await session.flush()

        task_tag = TaskTag(task_id=task.id, tag_id=tag.id)
        session.add(task_tag)
        await session.commit()

        # Try to assign same tag again
        response = await client.post(
            f"/api/v1/{user_id}/tasks/{task.id}/tags",
            json={"tag_id": tag.id},
            headers=auth_headers,
        )

        assert response.status_code == status.HTTP_409_CONFLICT

    @pytest.mark.asyncio
    async def test_list_task_tags_200_ok(
        self, client: AsyncClient, auth_headers: dict, user_id: str, session
    ):
        """Test GET /api/v1/{user_id}/tasks/{id}/tags returns 200 with tags list."""
        from backend.src.models.task import Task
        from backend.src.models.tag import Tag
        from backend.src.models.task_tag import TaskTag
        from uuid import UUID

        # Create task with 2 tags
        task = Task(user_id=UUID(user_id), title="Test Task", completed=False)
        tag1 = Tag(user_id=UUID(user_id), name="work", color="#FF5733")
        tag2 = Tag(user_id=UUID(user_id), name="urgent", color="#FF0000")
        session.add(task)
        session.add(tag1)
        session.add(tag2)
        await session.flush()

        task_tag1 = TaskTag(task_id=task.id, tag_id=tag1.id)
        task_tag2 = TaskTag(task_id=task.id, tag_id=tag2.id)
        session.add(task_tag1)
        session.add(task_tag2)
        await session.commit()

        response = await client.get(
            f"/api/v1/{user_id}/tasks/{task.id}/tags",
            headers=auth_headers,
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 2
        names = {tag["name"] for tag in data}
        assert names == {"work", "urgent"}

    @pytest.mark.asyncio
    async def test_remove_tag_from_task_204_no_content(
        self, client: AsyncClient, auth_headers: dict, user_id: str, session
    ):
        """Test DELETE /api/v1/{user_id}/tasks/{id}/tags/{tag_id} returns 204."""
        from backend.src.models.task import Task
        from backend.src.models.tag import Tag
        from backend.src.models.task_tag import TaskTag
        from uuid import UUID

        # Create task, tag, and junction
        task = Task(user_id=UUID(user_id), title="Test Task", completed=False)
        tag = Tag(user_id=UUID(user_id), name="work", color="#FF5733")
        session.add(task)
        session.add(tag)
        await session.flush()

        task_tag = TaskTag(task_id=task.id, tag_id=tag.id)
        session.add(task_tag)
        await session.commit()

        response = await client.delete(
            f"/api/v1/{user_id}/tasks/{task.id}/tags/{tag.id}",
            headers=auth_headers,
        )

        assert response.status_code == status.HTTP_204_NO_CONTENT

        # Verify tag removed
        get_response = await client.get(
            f"/api/v1/{user_id}/tasks/{task.id}/tags",
            headers=auth_headers,
        )
        data = get_response.json()
        assert len(data) == 0  # No tags
