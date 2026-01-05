"""Integration tests for Task reorder endpoint (User Story 3 - Drag-and-Drop)."""

import pytest
from datetime import datetime, timezone
from uuid import uuid4, UUID
from httpx import AsyncClient
from fastapi import status
from sqlmodel.ext.asyncio.session import AsyncSession

from src.models.task import Task


class TestTaskReorderEndpoint:
    """Integration tests for PATCH /api/v1/{user_id}/tasks/reorder endpoint."""

    @pytest.mark.asyncio
    async def test_reorder_tasks_200_ok_sequential_sort_order(
        self, async_client: AsyncClient, auth_headers: dict, user_id: str, test_session: AsyncSession
    ):
        """Test PATCH /api/v1/{user_id}/tasks/reorder returns 200 OK with sequential sort_order values."""
        # Create 5 tasks with initial sort_order (chronological)
        tasks = []
        for i in range(1, 6):
            task = Task(
                user_id=UUID(user_id),
                title=f"Task {i}",
                completed=False,
                sort_order=i * 1000,  # Initial: 1000, 2000, 3000, 4000, 5000
            )
            test_session.add(task)
            tasks.append(task)
        await test_session.commit()
        await test_session.refresh(tasks[0])
        await test_session.refresh(tasks[1])
        await test_session.refresh(tasks[2])
        await test_session.refresh(tasks[3])
        await test_session.refresh(tasks[4])

        # Reorder: Move task 3 to position 1, task 5 to position 2, rest unchanged
        # New order: [task3, task5, task1, task2, task4]
        task_ids = [tasks[2].id, tasks[4].id, tasks[0].id, tasks[1].id, tasks[3].id]

        response = await async_client.patch(
            f"/api/v1/{user_id}/tasks/reorder",
            json={"task_ids": task_ids},
            headers=auth_headers,
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["updated"] == 5
        assert data["message"] == "Tasks reordered successfully"

        # Verify sort_order values are sequential (1000, 2000, 3000, 4000, 5000)
        updated_tasks = []
        for task_id in task_ids:
            task = await test_session.get(Task, task_id)
            updated_tasks.append(task)

        assert updated_tasks[0].sort_order == 1000  # task3 now first
        assert updated_tasks[1].sort_order == 2000  # task5 now second
        assert updated_tasks[2].sort_order == 3000  # task1 now third
        assert updated_tasks[3].sort_order == 4000  # task2 now fourth
        assert updated_tasks[4].sort_order == 5000  # task4 now fifth

    @pytest.mark.asyncio
    async def test_reorder_tasks_400_empty_array(
        self, async_client: AsyncClient, auth_headers: dict, user_id: str
    ):
        """Test PATCH /api/v1/{user_id}/tasks/reorder returns 400 for empty array."""
        response = await async_client.patch(
            f"/api/v1/{user_id}/tasks/reorder",
            json={"task_ids": []},
            headers=auth_headers,
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        data = response.json()
        assert "error" in data
        assert data["code"] == "VALIDATION_ERROR"

    @pytest.mark.asyncio
    async def test_reorder_tasks_400_duplicate_ids(
        self, async_client: AsyncClient, auth_headers: dict, user_id: str, test_session: AsyncSession
    ):
        """Test PATCH /api/v1/{user_id}/tasks/reorder returns 400 for duplicate task IDs."""
        # Create 2 tasks
        task1 = Task(user_id=UUID(user_id), title="Task 1", completed=False, sort_order=1000)
        task2 = Task(user_id=UUID(user_id), title="Task 2", completed=False, sort_order=2000)
        test_session.add(task1)
        test_session.add(task2)
        await test_session.commit()
        await test_session.refresh(task1)
        await test_session.refresh(task2)

        # Try to reorder with duplicate IDs
        response = await async_client.patch(
            f"/api/v1/{user_id}/tasks/reorder",
            json={"task_ids": [task1.id, task2.id, task1.id]},  # task1 appears twice
            headers=auth_headers,
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        data = response.json()
        assert "error" in data
        assert data["code"] == "VALIDATION_ERROR"

    @pytest.mark.asyncio
    async def test_reorder_tasks_400_invalid_task_ids(
        self, async_client: AsyncClient, auth_headers: dict, user_id: str, test_session: AsyncSession
    ):
        """Test PATCH /api/v1/{user_id}/tasks/reorder returns 400 for non-existent task IDs."""
        # Create 1 task
        task = Task(user_id=UUID(user_id), title="Task 1", completed=False, sort_order=1000)
        test_session.add(task)
        await test_session.commit()
        await test_session.refresh(task)

        # Try to reorder with invalid IDs (non-existent task ID)
        response = await async_client.patch(
            f"/api/v1/{user_id}/tasks/reorder",
            json={"task_ids": [task.id, 999999]},  # 999999 doesn't exist
            headers=auth_headers,
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        data = response.json()
        assert "error" in data
        assert data["code"] == "INVALID_TASK_IDS"
        assert "invalid_ids" in data
        assert 999999 in data["invalid_ids"]

    @pytest.mark.asyncio
    async def test_reorder_tasks_403_forbidden_other_user_tasks(
        self, async_client: AsyncClient, auth_headers: dict, user_id: str, test_session: AsyncSession
    ):
        """Test PATCH /api/v1/{user_id}/tasks/reorder returns 403 when trying to reorder another user's tasks."""
        # Create task for authenticated user
        user_task = Task(user_id=UUID(user_id), title="My Task", completed=False, sort_order=1000)
        test_session.add(user_task)
        await test_session.commit()
        await test_session.refresh(user_task)

        # Create task for different user
        other_user_id = uuid4()
        other_task = Task(user_id=other_user_id, title="Other User Task", completed=False, sort_order=2000)
        test_session.add(other_task)
        await test_session.commit()
        await test_session.refresh(other_task)

        # Try to reorder with another user's task ID
        response = await async_client.patch(
            f"/api/v1/{user_id}/tasks/reorder",
            json={"task_ids": [user_task.id, other_task.id]},  # other_task belongs to different user
            headers=auth_headers,
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        data = response.json()
        assert "error" in data
        assert data["code"] == "INVALID_TASK_IDS"
        assert "invalid_ids" in data
        assert other_task.id in data["invalid_ids"]

    @pytest.mark.asyncio
    async def test_reorder_tasks_401_unauthorized_no_token(
        self, async_client: AsyncClient, user_id: str
    ):
        """Test PATCH /api/v1/{user_id}/tasks/reorder returns 401 without JWT token."""
        response = await async_client.patch(
            f"/api/v1/{user_id}/tasks/reorder",
            json={"task_ids": [1, 2, 3]},
            # No auth headers
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.asyncio
    async def test_reorder_tasks_partial_update_only_provided_ids(
        self, async_client: AsyncClient, auth_headers: dict, user_id: str, test_session: AsyncSession
    ):
        """Test reordering updates ONLY the tasks in the payload (partial reorder)."""
        # Create 5 tasks with initial sort_order
        tasks = []
        for i in range(1, 6):
            task = Task(
                user_id=UUID(user_id),
                title=f"Task {i}",
                completed=False,
                sort_order=i * 1000,  # Initial: 1000, 2000, 3000, 4000, 5000
            )
            test_session.add(task)
            tasks.append(task)
        await test_session.commit()
        for task in tasks:
            await test_session.refresh(task)

        # Reorder ONLY tasks 1, 2, 3 (leave tasks 4, 5 unchanged)
        task_ids = [tasks[0].id, tasks[1].id, tasks[2].id]

        response = await async_client.patch(
            f"/api/v1/{user_id}/tasks/reorder",
            json={"task_ids": task_ids},
            headers=auth_headers,
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["updated"] == 3  # Only 3 tasks updated

        # Verify tasks 1, 2, 3 have new sort_order (1000, 2000, 3000)
        await test_session.refresh(tasks[0])
        await test_session.refresh(tasks[1])
        await test_session.refresh(tasks[2])
        assert tasks[0].sort_order == 1000
        assert tasks[1].sort_order == 2000
        assert tasks[2].sort_order == 3000

        # Verify tasks 4, 5 are UNCHANGED (still 4000, 5000)
        await test_session.refresh(tasks[3])
        await test_session.refresh(tasks[4])
        assert tasks[3].sort_order == 4000  # UNCHANGED
        assert tasks[4].sort_order == 5000  # UNCHANGED

    @pytest.mark.asyncio
    async def test_reorder_tasks_updates_updated_at_timestamp(
        self, async_client: AsyncClient, auth_headers: dict, user_id: str, test_session: AsyncSession
    ):
        """Test reordering updates the updated_at timestamp for affected tasks."""
        # Create task with known created_at/updated_at
        task = Task(
            user_id=UUID(user_id),
            title="Task 1",
            completed=False,
            sort_order=1000,
        )
        test_session.add(task)
        await test_session.commit()
        await test_session.refresh(task)
        original_updated_at = task.updated_at

        # Wait a moment to ensure timestamp changes
        import asyncio
        await asyncio.sleep(0.1)

        # Reorder the task
        response = await async_client.patch(
            f"/api/v1/{user_id}/tasks/reorder",
            json={"task_ids": [task.id]},
            headers=auth_headers,
        )

        assert response.status_code == status.HTTP_200_OK

        # Verify updated_at changed
        await test_session.refresh(task)
        assert task.updated_at > original_updated_at
