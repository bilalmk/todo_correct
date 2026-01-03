"""
Integration Tests for User Isolation
T047: Test cross-user access returns 403, user_id mismatch detection, row-level security

Built following skills:
- @.claude/skills/panaversity/betterauth-fastapi-jwt-bridge (user isolation patterns)

Test Coverage:
- Cross-user access attempts return 403 Forbidden
- User ID mismatch detection in verify_user_match
- Row-level security enforcement (database layer)
- Authorization bypass attempts
"""

import pytest
from httpx import AsyncClient
from datetime import datetime, timedelta
from src.models.user import User
from src.models.task import Task
from src.models.tag import Tag
from src.core.database import get_session


@pytest.mark.integration
class TestUserIsolationEnforcement:
    """Test user isolation prevents unauthorized cross-user access"""

    @pytest.mark.asyncio
    async def test_cross_user_task_access_returns_403(
        self, async_client: AsyncClient, test_db_session
    ):
        """Test User A cannot access User B's tasks - returns 403"""

        # Create two users with tasks
        from src.services.user import create_user
        from src.models.user import UserCreate

        user_a_data = UserCreate(
            email="user_a@test.com", password="Password123!", name="User A"
        )
        user_b_data = UserCreate(
            email="user_b@test.com", password="Password123!", name="User B"
        )

        user_a = await create_user(test_db_session, user_a_data)
        user_b = await create_user(test_db_session, user_b_data)
        await test_db_session.commit()

        # User B creates a task
        task_b = Task(
            user_id=user_b.id,
            title="User B's Secret Task",
            description="Confidential",
            completed=False,
        )
        test_db_session.add(task_b)
        await test_db_session.commit()
        await test_db_session.refresh(task_b)

        # User A authenticates and gets JWT
        login_data = {"email": "user_a@test.com", "password": "Password123!"}
        login_response = await async_client.post("/api/auth/sign-in/email", json=login_data)
        user_a_token = login_response.json()["token"]

        headers = {"Authorization": f"Bearer {user_a_token}"}

        # User A attempts to access User B's tasks (should fail)
        response = await async_client.get(f"/api/v1/{user_b.id}/tasks", headers=headers)

        assert response.status_code == 403
        assert "Not authorized" in response.json()["error"]

    @pytest.mark.asyncio
    async def test_cross_user_task_update_returns_403(
        self, async_client: AsyncClient, test_db_session
    ):
        """Test User A cannot update User B's task"""

        from src.services.user import create_user
        from src.models.user import UserCreate

        # Create users
        user_a_data = UserCreate(
            email="user_a_update@test.com", password="Password123!", name="User A"
        )
        user_b_data = UserCreate(
            email="user_b_update@test.com", password="Password123!", name="User B"
        )

        user_a = await create_user(test_db_session, user_a_data)
        user_b = await create_user(test_db_session, user_b_data)
        await test_db_session.commit()

        # User B creates a task
        task_b = Task(user_id=user_b.id, title="Original Title", completed=False)
        test_db_session.add(task_b)
        await test_db_session.commit()
        await test_db_session.refresh(task_b)

        # User A authenticates
        login_data = {"email": "user_a_update@test.com", "password": "Password123!"}
        login_response = await async_client.post("/api/auth/sign-in/email", json=login_data)
        user_a_token = login_response.json()["token"]

        headers = {"Authorization": f"Bearer {user_a_token}"}

        # User A attempts to update User B's task
        update_data = {"title": "Malicious Update"}
        response = await async_client.patch(
            f"/api/v1/{user_b.id}/tasks/{task_b.id}", json=update_data, headers=headers
        )

        assert response.status_code == 403

        # Verify task was not updated
        await test_db_session.refresh(task_b)
        assert task_b.title == "Original Title"

    @pytest.mark.asyncio
    async def test_cross_user_task_deletion_returns_403(
        self, async_client: AsyncClient, test_db_session
    ):
        """Test User A cannot delete User B's task"""

        from src.services.user import create_user
        from src.models.user import UserCreate

        # Create users
        user_a_data = UserCreate(
            email="user_a_delete@test.com", password="Password123!", name="User A"
        )
        user_b_data = UserCreate(
            email="user_b_delete@test.com", password="Password123!", name="User B"
        )

        user_a = await create_user(test_db_session, user_a_data)
        user_b = await create_user(test_db_session, user_b_data)
        await test_db_session.commit()

        # User B creates a task
        task_b = Task(user_id=user_b.id, title="Important Task", completed=False)
        test_db_session.add(task_b)
        await test_db_session.commit()
        await test_db_session.refresh(task_b)
        task_b_id = task_b.id

        # User A authenticates
        login_data = {"email": "user_a_delete@test.com", "password": "Password123!"}
        login_response = await async_client.post("/api/auth/sign-in/email", json=login_data)
        user_a_token = login_response.json()["token"]

        headers = {"Authorization": f"Bearer {user_a_token}"}

        # User A attempts to delete User B's task
        response = await async_client.delete(
            f"/api/v1/{user_b.id}/tasks/{task_b_id}", headers=headers
        )

        assert response.status_code == 403

        # Verify task still exists
        from sqlmodel import select

        result = await test_db_session.exec(select(Task).where(Task.id == task_b_id))
        task_still_exists = result.first()
        assert task_still_exists is not None

    @pytest.mark.asyncio
    async def test_cross_user_tag_access_returns_403(
        self, async_client: AsyncClient, test_db_session
    ):
        """Test User A cannot access User B's tags"""

        from src.services.user import create_user
        from src.models.user import UserCreate

        # Create users
        user_a_data = UserCreate(
            email="user_a_tags@test.com", password="Password123!", name="User A"
        )
        user_b_data = UserCreate(
            email="user_b_tags@test.com", password="Password123!", name="User B"
        )

        user_a = await create_user(test_db_session, user_a_data)
        user_b = await create_user(test_db_session, user_b_data)
        await test_db_session.commit()

        # User B creates a tag
        tag_b = Tag(user_id=user_b.id, name="Secret Tag", color="#FF0000")
        test_db_session.add(tag_b)
        await test_db_session.commit()

        # User A authenticates
        login_data = {"email": "user_a_tags@test.com", "password": "Password123!"}
        login_response = await async_client.post("/api/auth/sign-in/email", json=login_data)
        user_a_token = login_response.json()["token"]

        headers = {"Authorization": f"Bearer {user_a_token}"}

        # User A attempts to access User B's tags
        response = await async_client.get(f"/api/v1/{user_b.id}/tags", headers=headers)

        assert response.status_code == 403


@pytest.mark.integration
class TestUserIDMismatchDetection:
    """Test user_id mismatch detection in verify_user_match dependency"""

    @pytest.mark.asyncio
    async def test_url_path_user_id_must_match_jwt_user_id(
        self, async_client: AsyncClient, test_db_session
    ):
        """Test URL path user_id must match JWT sub claim"""

        from src.services.user import create_user
        from src.models.user import UserCreate

        # Create user
        user_data = UserCreate(
            email="mismatch@test.com", password="Password123!", name="Mismatch User"
        )
        user = await create_user(test_db_session, user_data)
        await test_db_session.commit()

        # Authenticate and get JWT
        login_data = {"email": "mismatch@test.com", "password": "Password123!"}
        login_response = await async_client.post("/api/auth/sign-in/email", json=login_data)
        jwt_token = login_response.json()["token"]

        headers = {"Authorization": f"Bearer {jwt_token}"}

        # Attempt to access with different user_id in path
        fake_user_id = "different-user-id-12345"
        response = await async_client.get(f"/api/v1/{fake_user_id}/tasks", headers=headers)

        assert response.status_code == 403
        assert "Not authorized" in response.json()["error"]

    @pytest.mark.asyncio
    async def test_valid_user_id_match_allows_access(
        self, async_client: AsyncClient, test_db_session
    ):
        """Test matching user_id in JWT and URL path allows access"""

        from src.services.user import create_user
        from src.models.user import UserCreate

        # Create user
        user_data = UserCreate(
            email="valid@test.com", password="Password123!", name="Valid User"
        )
        user = await create_user(test_db_session, user_data)
        await test_db_session.commit()

        # Authenticate
        login_data = {"email": "valid@test.com", "password": "Password123!"}
        login_response = await async_client.post("/api/auth/sign-in/email", json=login_data)
        jwt_token = login_response.json()["token"]

        headers = {"Authorization": f"Bearer {jwt_token}"}

        # Access with correct user_id
        response = await async_client.get(f"/api/v1/{user.id}/tasks", headers=headers)

        assert response.status_code == 200
        assert isinstance(response.json(), list)


@pytest.mark.integration
class TestRowLevelSecurityEnforcement:
    """Test database row-level security prevents data leakage"""

    @pytest.mark.asyncio
    async def test_database_query_filters_by_user_id(
        self, async_client: AsyncClient, test_db_session
    ):
        """Test database queries automatically filter by authenticated user_id"""

        from src.services.user import create_user
        from src.models.user import UserCreate

        # Create two users with tasks
        user_a_data = UserCreate(
            email="rls_a@test.com", password="Password123!", name="RLS User A"
        )
        user_b_data = UserCreate(
            email="rls_b@test.com", password="Password123!", name="RLS User B"
        )

        user_a = await create_user(test_db_session, user_a_data)
        user_b = await create_user(test_db_session, user_b_data)
        await test_db_session.commit()

        # Each user creates tasks
        task_a = Task(user_id=user_a.id, title="User A Task", completed=False)
        task_b = Task(user_id=user_b.id, title="User B Task", completed=False)
        test_db_session.add_all([task_a, task_b])
        await test_db_session.commit()

        # User A authenticates
        login_data = {"email": "rls_a@test.com", "password": "Password123!"}
        login_response = await async_client.post("/api/auth/sign-in/email", json=login_data)
        user_a_token = login_response.json()["token"]

        headers = {"Authorization": f"Bearer {user_a_token}"}

        # User A fetches their tasks
        response = await async_client.get(f"/api/v1/{user_a.id}/tasks", headers=headers)

        assert response.status_code == 200
        tasks = response.json()

        # Verify only User A's tasks returned (not User B's)
        assert len(tasks) == 1
        assert tasks[0]["title"] == "User A Task"
        assert all(task["user_id"] == str(user_a.id) for task in tasks)

    @pytest.mark.asyncio
    async def test_search_filters_respect_user_isolation(
        self, async_client: AsyncClient, test_db_session
    ):
        """Test search queries don't leak other users' data"""

        from src.services.user import create_user
        from src.models.user import UserCreate

        # Create users
        user_a_data = UserCreate(
            email="search_a@test.com", password="Password123!", name="Search User A"
        )
        user_b_data = UserCreate(
            email="search_b@test.com", password="Password123!", name="Search User B"
        )

        user_a = await create_user(test_db_session, user_a_data)
        user_b = await create_user(test_db_session, user_b_data)
        await test_db_session.commit()

        # Both users create tasks with same keyword
        task_a = Task(
            user_id=user_a.id, title="Secret Project Alpha", completed=False
        )
        task_b = Task(
            user_id=user_b.id, title="Secret Project Beta", completed=False
        )
        test_db_session.add_all([task_a, task_b])
        await test_db_session.commit()

        # User A authenticates
        login_data = {"email": "search_a@test.com", "password": "Password123!"}
        login_response = await async_client.post("/api/auth/sign-in/email", json=login_data)
        user_a_token = login_response.json()["token"]

        headers = {"Authorization": f"Bearer {user_a_token}"}

        # User A searches for "Secret" (common keyword)
        response = await async_client.get(
            f"/api/v1/{user_a.id}/tasks?search=Secret", headers=headers
        )

        assert response.status_code == 200
        tasks = response.json()

        # Verify only User A's matching task returned (not User B's)
        assert len(tasks) == 1
        assert "Alpha" in tasks[0]["title"]
        assert "Beta" not in tasks[0]["title"]

    @pytest.mark.asyncio
    async def test_authorization_bypass_attempts_fail(
        self, async_client: AsyncClient, test_db_session
    ):
        """Test various authorization bypass attempts all return 403"""

        from src.services.user import create_user
        from src.models.user import UserCreate

        # Create attacker and victim users
        attacker_data = UserCreate(
            email="attacker@test.com", password="Password123!", name="Attacker"
        )
        victim_data = UserCreate(
            email="victim@test.com", password="Password123!", name="Victim"
        )

        attacker = await create_user(test_db_session, attacker_data)
        victim = await create_user(test_db_session, victim_data)
        await test_db_session.commit()

        # Attacker authenticates
        login_data = {"email": "attacker@test.com", "password": "Password123!"}
        login_response = await async_client.post("/api/auth/sign-in/email", json=login_data)
        attacker_token = login_response.json()["token"]

        headers = {"Authorization": f"Bearer {attacker_token}"}

        # Bypass attempt 1: Direct user_id manipulation in URL
        response1 = await async_client.get(
            f"/api/v1/{victim.id}/tasks", headers=headers
        )
        assert response1.status_code == 403

        # Bypass attempt 2: SQL injection in user_id
        response2 = await async_client.get(
            f"/api/v1/{victim.id}' OR '1'='1/tasks", headers=headers
        )
        assert response2.status_code in [403, 404, 422]  # Should fail

        # Bypass attempt 3: Path traversal
        response3 = await async_client.get(
            f"/api/v1/../{victim.id}/tasks", headers=headers
        )
        assert response3.status_code in [403, 404]  # Should fail
