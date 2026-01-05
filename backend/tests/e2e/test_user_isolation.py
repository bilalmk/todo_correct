"""E2E tests for multi-user isolation and security (Phase 8)."""

import pytest
from datetime import datetime, timedelta, timezone
from uuid import uuid4
from httpx import AsyncClient
from fastapi import status
import jwt

from src.core.config import settings
from src.core.security import create_access_token
from src.models.user import User
from src.models.task import Task
from src.models.tag import Tag
from src.models.task_tag import TaskTag
from sqlmodel.ext.asyncio.session import AsyncSession


class TestUserIsolation:
    """E2E tests for user isolation and security boundaries."""

    @pytest.mark.asyncio
    async def test_user_a_cannot_access_user_b_tasks_returns_404(
        self, async_client: AsyncClient, test_session: AsyncSession
    ):
        """Test T100: User A cannot access User B's tasks (returns 404, not 403)."""
        from src.services.user import create_user
        from src.models.user import UserCreate

        # Create User A and User B
        user_a_data = UserCreate(
            email="usera@example.com",
            password="password123",
            name="User A",
        )
        user_b_data = UserCreate(
            email="userb@example.com",
            password="password123",
            name="User B",
        )

        user_a = await create_user(test_session, user_a_data)
        user_b = await create_user(test_session, user_b_data)
        await test_session.commit()

        # User B creates a task
        task_b = Task(user_id=user_b.id, title="User B's task", completed=False)
        test_session.add(task_b)
        await test_session.commit()
        await test_session.refresh(task_b)

        # User A tries to access User B's task
        token_a = create_access_token(user_a.id, user_a.email)
        headers_a = {"Authorization": f"Bearer {token_a}"}

        response = await async_client.get(
            f"/api/v1/{user_a.id}/tasks/{task_b.id}",
            headers=headers_a,
        )

        # Should return 404 (not found), not 403 (forbidden)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    @pytest.mark.asyncio
    async def test_user_a_cannot_modify_user_b_tasks_returns_404(
        self, async_client: AsyncClient, test_session: AsyncSession
    ):
        """Test T101: User A cannot modify User B's tasks (returns 404)."""
        from src.services.user import create_user
        from src.models.user import UserCreate

        # Create User A and User B
        user_a_data = UserCreate(
            email="usera2@example.com",
            password="password123",
            name="User A2",
        )
        user_b_data = UserCreate(
            email="userb2@example.com",
            password="password123",
            name="User B2",
        )

        user_a = await create_user(test_session, user_a_data)
        user_b = await create_user(test_session, user_b_data)
        await test_session.commit()

        # User B creates a task
        task_b = Task(user_id=user_b.id, title="User B's task", completed=False)
        test_session.add(task_b)
        await test_session.commit()
        await test_session.refresh(task_b)

        # User A tries to update User B's task
        token_a = create_access_token(user_a.id, user_a.email)
        headers_a = {"Authorization": f"Bearer {token_a}"}

        response = await async_client.patch(
            f"/api/v1/{user_a.id}/tasks/{task_b.id}",
            json={"title": "Hacked!"},
            headers=headers_a,
        )

        # Should return 404 (not found)
        assert response.status_code == status.HTTP_404_NOT_FOUND

        # Verify task was not modified
        await test_session.refresh(task_b)
        assert task_b.title == "User B's task"

    @pytest.mark.asyncio
    async def test_user_a_cannot_assign_tags_to_user_b_tasks_returns_404(
        self, async_client: AsyncClient, test_session: AsyncSession
    ):
        """Test T102: User A cannot assign tags to User B's tasks (returns 404)."""
        from src.services.user import create_user
        from src.models.user import UserCreate

        # Create User A and User B
        user_a_data = UserCreate(
            email="usera3@example.com",
            password="password123",
            name="User A3",
        )
        user_b_data = UserCreate(
            email="userb3@example.com",
            password="password123",
            name="User B3",
        )

        user_a = await create_user(test_session, user_a_data)
        user_b = await create_user(test_session, user_b_data)
        await test_session.commit()

        # User A creates a tag
        tag_a = Tag(user_id=user_a.id, name="tag_a", color="#FF0000")
        test_session.add(tag_a)
        await test_session.commit()
        await test_session.refresh(tag_a)

        # User B creates a task
        task_b = Task(user_id=user_b.id, title="User B's task", completed=False)
        test_session.add(task_b)
        await test_session.commit()
        await test_session.refresh(task_b)

        # User A tries to assign their tag to User B's task
        token_a = create_access_token(user_a.id, user_a.email)
        headers_a = {"Authorization": f"Bearer {token_a}"}

        response = await async_client.post(
            f"/api/v1/{user_a.id}/tasks/{task_b.id}/tags",
            json={"tag_id": tag_a.id},
            headers=headers_a,
        )

        # Should return 404 (task not found for user A)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    @pytest.mark.asyncio
    async def test_jwt_user_id_mismatch_returns_403_forbidden(
        self, async_client: AsyncClient, test_session: AsyncSession
    ):
        """Test T103: JWT user_id mismatch returns 403 Forbidden."""
        from src.services.user import create_user
        from src.models.user import UserCreate

        # Create User A
        user_a_data = UserCreate(
            email="usera4@example.com",
            password="password123",
            name="User A4",
        )
        user_a = await create_user(test_session, user_a_data)
        await test_session.commit()

        # Create token for User A
        token_a = create_access_token(user_a.id, user_a.email)
        headers_a = {"Authorization": f"Bearer {token_a}"}

        # Try to access endpoint with different user_id in URL
        fake_user_id = uuid4()
        response = await async_client.get(
            f"/api/v1/{fake_user_id}/tasks",
            headers=headers_a,
        )

        # Should return 403 Forbidden (user_id mismatch)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    @pytest.mark.asyncio
    async def test_expired_jwt_token_returns_401_unauthorized(
        self, async_client: AsyncClient, test_session: AsyncSession
    ):
        """Test T104: Expired JWT token returns 401 Unauthorized."""
        from src.services.user import create_user
        from src.models.user import UserCreate

        # Create User A
        user_a_data = UserCreate(
            email="usera5@example.com",
            password="password123",
            name="User A5",
        )
        user_a = await create_user(test_session, user_a_data)
        await test_session.commit()

        # Create expired token (expires immediately)
        expired_token_data = {
            "sub": str(user_a.id),
            "email": user_a.email,
            "exp": datetime.now(timezone.utc) - timedelta(minutes=1),  # Expired 1 minute ago
        }
        expired_token = jwt.encode(
            expired_token_data,
            settings.BETTER_AUTH_SECRET,
            algorithm=settings.JWT_ALGORITHM,
        )

        headers_expired = {"Authorization": f"Bearer {expired_token}"}

        # Try to access endpoint with expired token
        response = await async_client.get(
            f"/api/v1/{user_a.id}/tasks",
            headers=headers_expired,
        )

        # Should return 401 Unauthorized
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.asyncio
    async def test_cross_user_tag_filtering_returns_empty_results(
        self, async_client: AsyncClient, test_session: AsyncSession
    ):
        """Test T105: Cross-user tag filtering returns empty results (not 403)."""
        from src.services.user import create_user
        from src.models.user import UserCreate

        # Create User A and User B
        user_a_data = UserCreate(
            email="usera6@example.com",
            password="password123",
            name="User A6",
        )
        user_b_data = UserCreate(
            email="userb6@example.com",
            password="password123",
            name="User B6",
        )

        user_a = await create_user(test_session, user_a_data)
        user_b = await create_user(test_session, user_b_data)
        await test_session.commit()

        # User B creates a tag and task
        tag_b = Tag(user_id=user_b.id, name="work", color="#FF0000")
        task_b = Task(user_id=user_b.id, title="User B's work task", completed=False)
        test_session.add(tag_b)
        test_session.add(task_b)
        await test_session.flush()

        # Assign tag to task
        task_tag = TaskTag(task_id=task_b.id, tag_id=tag_b.id)
        test_session.add(task_tag)
        await test_session.commit()

        # User A tries to filter by User B's tag name
        token_a = create_access_token(user_a.id, user_a.email)
        headers_a = {"Authorization": f"Bearer {token_a}"}

        response = await async_client.get(
            f"/api/v1/{user_a.id}/tasks?tag=work",
            headers=headers_a,
        )

        # Should return 200 OK with empty list (not 403)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 0  # Empty results (tag doesn't exist for user A)

    @pytest.mark.asyncio
    async def test_concurrent_updates_and_idempotency(
        self, async_client: AsyncClient, test_session: AsyncSession
    ):
        """Test T106: Idempotency verified (marking task complete twice)."""
        from src.services.user import create_user
        from src.models.user import UserCreate

        # Create User A
        user_a_data = UserCreate(
            email="usera7@example.com",
            password="password123",
            name="User A7",
        )
        user_a = await create_user(test_session, user_a_data)
        await test_session.commit()

        # User A creates a task
        task_a = Task(user_id=user_a.id, title="Test Task", completed=False)
        test_session.add(task_a)
        await test_session.commit()
        await test_session.refresh(task_a)

        token_a = create_access_token(user_a.id, user_a.email)
        headers_a = {"Authorization": f"Bearer {token_a}"}

        # Test: Idempotency - Toggle completion status
        # Toggle 1: False -> True
        response1 = await async_client.patch(
            f"/api/v1/{user_a.id}/tasks/{task_a.id}/complete",
            headers=headers_a,
        )
        assert response1.status_code == status.HTTP_200_OK
        data1 = response1.json()
        assert data1["completed"] is True

        # Toggle 2: True -> False
        response2 = await async_client.patch(
            f"/api/v1/{user_a.id}/tasks/{task_a.id}/complete",
            headers=headers_a,
        )
        assert response2.status_code == status.HTTP_200_OK
        data2 = response2.json()
        assert data2["completed"] is False

        # Toggle 3: False -> True again
        response3 = await async_client.patch(
            f"/api/v1/{user_a.id}/tasks/{task_a.id}/complete",
            headers=headers_a,
        )
        assert response3.status_code == status.HTTP_200_OK
        data3 = response3.json()
        assert data3["completed"] is True

        # Verify final state persists
        final_response = await async_client.get(
            f"/api/v1/{user_a.id}/tasks/{task_a.id}",
            headers=headers_a,
        )
        assert final_response.status_code == status.HTTP_200_OK
        final_data = final_response.json()
        assert final_data["completed"] is True
