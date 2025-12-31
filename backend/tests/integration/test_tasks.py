"""Integration tests for Task API endpoints (User Story 1)."""

import pytest
from datetime import datetime, timedelta, timezone
from uuid import uuid4, UUID
from httpx import AsyncClient
from fastapi import status
from sqlmodel.ext.asyncio.session import AsyncSession

from src.models.task import Task


class TestTaskCRUDEndpoints:
    """Integration tests for 7 task endpoints."""

    @pytest.mark.asyncio
    async def test_create_task_201_created(
        self, async_client: AsyncClient, auth_headers: dict, user_id: str
    ):
        """Test POST /api/v1/{user_id}/tasks returns 201 Created with all fields."""
        due_date = (datetime.now() + timedelta(days=1)).isoformat()
        reminder_at = (datetime.now() + timedelta(hours=12)).isoformat()

        response = await async_client.post(
            f"/api/v1/{user_id}/tasks",
            json={
                "title": "Buy groceries",
                "description": "Milk, eggs, bread",
                "completed": False,
                "priority": "high",
                "due_date": due_date,
                "reminder_at": reminder_at,
                "recurrence_pattern": "weekly",
                "recurrence_config": {"rrule": "FREQ=WEEKLY;BYDAY=MO,FR"},
            },
            headers=auth_headers,
        )

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["title"] == "Buy groceries"
        assert data["description"] == "Milk, eggs, bread"
        assert data["completed"] is False
        assert data["priority"] == "high"
        assert "id" in data
        assert "created_at" in data
        assert "updated_at" in data
        assert data["tags"] == []  # New task has no tags

    @pytest.mark.asyncio
    async def test_list_tasks_200_ok_array(
        self, async_client: AsyncClient, auth_headers: dict, user_id: str, test_session: AsyncSession
    ):
        """Test GET /api/v1/{user_id}/tasks returns 200 OK with array of tasks."""
        # Create 2 tasks
        task1 = Task(user_id=UUID(user_id), title="Task 1", completed=False)
        task2 = Task(user_id=UUID(user_id), title="Task 2", completed=True)
        test_session.add(task1)
        test_session.add(task2)
        await test_session.commit()

        response = await async_client.get(
            f"/api/v1/{user_id}/tasks",
            headers=auth_headers,
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 2
        titles = {task["title"] for task in data}
        assert "Task 1" in titles
        assert "Task 2" in titles

    @pytest.mark.asyncio
    async def test_get_single_task_200_ok_with_nested_tags(
        self, async_client: AsyncClient, auth_headers: dict, user_id: str, test_session: AsyncSession
    ):
        """Test GET /api/v1/{user_id}/tasks/{id} returns 200 OK with nested tags."""
        task = Task(user_id=UUID(user_id), title="Test Task", completed=False)
        test_session.add(task)
        await test_session.commit()
        task_id = task.id

        response = await async_client.get(
            f"/api/v1/{user_id}/tasks/{task_id}",
            headers=auth_headers,
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == task_id
        assert data["title"] == "Test Task"
        assert "tags" in data  # Nested tags included

    @pytest.mark.asyncio
    async def test_replace_task_200_ok_full_replacement(
        self, async_client: AsyncClient, auth_headers: dict, user_id: str, test_session: AsyncSession
    ):
        """Test PUT /api/v1/{user_id}/tasks/{id} returns 200 OK (full replacement)."""
        task = Task(
            user_id=UUID(user_id),
            title="Original Title",
            description="Original Description",
            completed=False,
            priority="low",
        )
        test_session.add(task)
        await test_session.commit()
        task_id = task.id

        response = await async_client.put(
            f"/api/v1/{user_id}/tasks/{task_id}",
            json={
                "title": "Replaced Title",
                "description": "Replaced Description",
                "completed": True,
                "priority": "high",
            },
            headers=auth_headers,
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["title"] == "Replaced Title"
        assert data["description"] == "Replaced Description"
        assert data["completed"] is True
        assert data["priority"] == "high"

    @pytest.mark.asyncio
    async def test_update_task_200_ok_partial(
        self, async_client: AsyncClient, auth_headers: dict, user_id: str, test_session: AsyncSession
    ):
        """Test PATCH /api/v1/{user_id}/tasks/{id} returns 200 OK (partial update)."""
        task = Task(
            user_id=UUID(user_id),
            title="Original Title",
            description="Original Description",
            completed=False,
        )
        test_session.add(task)
        await test_session.commit()
        task_id = task.id

        # Only update title
        response = await async_client.patch(
            f"/api/v1/{user_id}/tasks/{task_id}",
            json={"title": "Updated Title"},
            headers=auth_headers,
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["title"] == "Updated Title"
        # Other fields remain unchanged
        assert data["description"] == "Original Description"
        assert data["completed"] is False

    @pytest.mark.asyncio
    async def test_toggle_complete_200_ok(
        self, async_client: AsyncClient, auth_headers: dict, user_id: str, test_session: AsyncSession
    ):
        """Test PATCH /api/v1/{user_id}/tasks/{id}/complete toggles completion."""
        task = Task(user_id=UUID(user_id), title="Test Task", completed=False)
        test_session.add(task)
        await test_session.commit()
        task_id = task.id

        # Toggle to completed
        response = await async_client.patch(
            f"/api/v1/{user_id}/tasks/{task_id}/complete",
            headers=auth_headers,
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["completed"] is True

        # Toggle back to incomplete
        response = await async_client.patch(
            f"/api/v1/{user_id}/tasks/{task_id}/complete",
            headers=auth_headers,
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["completed"] is False

    @pytest.mark.asyncio
    async def test_delete_task_204_no_content(
        self, async_client: AsyncClient, auth_headers: dict, user_id: str, test_session: AsyncSession
    ):
        """Test DELETE /api/v1/{user_id}/tasks/{id} returns 204 (soft delete)."""
        task = Task(user_id=UUID(user_id), title="To be deleted", completed=False)
        test_session.add(task)
        await test_session.commit()
        task_id = task.id

        response = await async_client.delete(
            f"/api/v1/{user_id}/tasks/{task_id}",
            headers=auth_headers,
        )

        assert response.status_code == status.HTTP_204_NO_CONTENT

        # Verify task is soft-deleted (not returned by GET)
        get_response = await async_client.get(
            f"/api/v1/{user_id}/tasks/{task_id}",
            headers=auth_headers,
        )
        assert get_response.status_code == status.HTTP_404_NOT_FOUND


class TestAdvancedFieldsSupport:
    """Integration tests for advanced fields: due_date, reminder_at, recurrence (User Story 4)."""

    @pytest.mark.asyncio
    async def test_create_task_with_due_date_and_reminder(
        self, async_client: AsyncClient, auth_headers: dict, user_id: str
    ):
        """Test POST /api/v1/{user_id}/tasks with due_date and reminder_at fields (T093)."""
        due_date = (datetime.now() + timedelta(days=3)).isoformat()
        reminder_at = (datetime.now() + timedelta(days=2)).isoformat()

        response = await async_client.post(
            f"/api/v1/{user_id}/tasks",
            json={
                "title": "Submit project proposal",
                "description": "Final draft due next week",
                "completed": False,
                "priority": "high",
                "due_date": due_date,
                "reminder_at": reminder_at,
            },
            headers=auth_headers,
        )

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()

        # Verify all fields are returned correctly
        assert data["title"] == "Submit project proposal"
        assert data["priority"] == "high"
        assert "due_date" in data
        assert "reminder_at" in data
        assert data["due_date"] is not None
        assert data["reminder_at"] is not None

    @pytest.mark.asyncio
    async def test_create_task_with_recurrence_pattern_and_config(
        self, async_client: AsyncClient, auth_headers: dict, user_id: str
    ):
        """Test POST /api/v1/{user_id}/tasks with recurrence_pattern and JSONB recurrence_config (T094)."""
        due_date = (datetime.now() + timedelta(days=7)).isoformat()

        response = await async_client.post(
            f"/api/v1/{user_id}/tasks",
            json={
                "title": "Weekly team standup",
                "description": "Every Monday at 10 AM",
                "completed": False,
                "priority": "medium",
                "due_date": due_date,
                "recurrence_pattern": "weekly",
                "recurrence_config": {
                    "rrule": "FREQ=WEEKLY;BYDAY=MO",
                    "interval": 1,
                    "count": 52,  # Repeat for 52 weeks
                },
            },
            headers=auth_headers,
        )

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()

        # Verify recurrence fields are stored and returned correctly
        assert data["title"] == "Weekly team standup"
        assert data["recurrence_pattern"] == "weekly"
        assert data["recurrence_config"] is not None
        assert isinstance(data["recurrence_config"], dict)
        assert data["recurrence_config"]["rrule"] == "FREQ=WEEKLY;BYDAY=MO"
        assert data["recurrence_config"]["interval"] == 1
        assert data["recurrence_config"]["count"] == 52

    @pytest.mark.asyncio
    async def test_update_task_recurrence_fields(
        self, async_client: AsyncClient, auth_headers: dict, user_id: str, test_session: AsyncSession
    ):
        """Test PATCH /api/v1/{user_id}/tasks/{id} to update recurrence_pattern and config (T095)."""
        # Create a task without recurrence
        task = Task(
            user_id=UUID(user_id),
            title="Daily exercise",
            completed=False
        )
        test_session.add(task)
        await test_session.commit()
        task_id = task.id

        # Update to add recurrence
        response = await async_client.patch(
            f"/api/v1/{user_id}/tasks/{task_id}",
            json={
                "recurrence_pattern": "daily",
                "recurrence_config": {
                    "rrule": "FREQ=DAILY",
                    "interval": 1,
                    "until": "2026-12-31T23:59:59Z",
                },
            },
            headers=auth_headers,
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        # Verify recurrence fields were updated
        assert data["title"] == "Daily exercise"  # Title unchanged
        assert data["recurrence_pattern"] == "daily"
        assert data["recurrence_config"]["rrule"] == "FREQ=DAILY"
        assert data["recurrence_config"]["interval"] == 1

    @pytest.mark.asyncio
    async def test_validation_reminder_at_must_be_before_due_date(
        self, async_client: AsyncClient, auth_headers: dict, user_id: str
    ):
        """Test TaskCreate validation: reminder_at must be before due_date (T096)."""
        due_date = (datetime.now() + timedelta(days=1)).isoformat()
        reminder_at = (datetime.now() + timedelta(days=2)).isoformat()  # AFTER due_date (invalid)

        response = await async_client.post(
            f"/api/v1/{user_id}/tasks",
            json={
                "title": "Invalid reminder task",
                "due_date": due_date,
                "reminder_at": reminder_at,  # This should cause validation error
            },
            headers=auth_headers,
        )

        # Should return 422 Unprocessable Entity (validation error)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        data = response.json()

        # Verify error message mentions reminder_at validation (FastAPI format)
        assert "detail" in data
        # FastAPI returns list of validation errors
        error_messages = str(data["detail"]).lower()
        assert "reminder_at" in error_messages

    @pytest.mark.asyncio
    async def test_create_task_with_all_advanced_fields(
        self, async_client: AsyncClient, auth_headers: dict, user_id: str
    ):
        """Test creating a task with ALL advanced fields populated (comprehensive test)."""
        due_date = (datetime.now() + timedelta(days=14)).isoformat()
        reminder_at = (datetime.now() + timedelta(days=13)).isoformat()

        response = await async_client.post(
            f"/api/v1/{user_id}/tasks",
            json={
                "title": "Quarterly business review",
                "description": "Prepare slides and financial reports",
                "completed": False,
                "priority": "high",
                "due_date": due_date,
                "reminder_at": reminder_at,
                "recurrence_pattern": "monthly",
                "recurrence_config": {
                    "rrule": "FREQ=MONTHLY;BYMONTHDAY=1",
                    "interval": 3,  # Every 3 months
                    "count": 4,  # Four quarters
                },
            },
            headers=auth_headers,
        )

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()

        # Verify all fields
        assert data["title"] == "Quarterly business review"
        assert data["priority"] == "high"
        assert data["due_date"] is not None
        assert data["reminder_at"] is not None
        assert data["recurrence_pattern"] == "monthly"
        assert data["recurrence_config"]["rrule"] == "FREQ=MONTHLY;BYMONTHDAY=1"
        assert data["recurrence_config"]["interval"] == 3
        assert data["recurrence_config"]["count"] == 4

    @pytest.mark.asyncio
    async def test_get_task_returns_advanced_fields(
        self, async_client: AsyncClient, auth_headers: dict, user_id: str, test_session: AsyncSession
    ):
        """Test GET /api/v1/{user_id}/tasks/{id} returns advanced fields correctly."""
        due_date = datetime.now(timezone.utc) + timedelta(days=5)
        reminder_at = datetime.now(timezone.utc) + timedelta(days=4)

        task = Task(
            user_id=UUID(user_id),
            title="Team meeting",
            completed=False,
            priority="medium",
            due_date=due_date,
            reminder_at=reminder_at,
            recurrence_pattern="weekly",
            recurrence_config={"rrule": "FREQ=WEEKLY;BYDAY=FR"}
        )
        test_session.add(task)
        await test_session.commit()
        task_id = task.id

        response = await async_client.get(
            f"/api/v1/{user_id}/tasks/{task_id}",
            headers=auth_headers,
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        # Verify all advanced fields are returned
        assert data["priority"] == "medium"
        assert "due_date" in data
        assert "reminder_at" in data
        assert data["recurrence_pattern"] == "weekly"
        assert data["recurrence_config"]["rrule"] == "FREQ=WEEKLY;BYDAY=FR"
