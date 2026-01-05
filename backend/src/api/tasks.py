"""Task API endpoints for CRUD operations."""

from typing import List, Optional
from uuid import UUID
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from sqlmodel.ext.asyncio.session import AsyncSession

from ..api.deps import verify_user_match
from ..core.database import get_session
from ..models.user import User
from ..repositories.task import TaskRepository
from ..schemas.task import TaskCreate, TaskUpdate, TaskReplace, TaskResponse, ReorderRequest
from ..services.query import QueryService
from ..services.notification import NotificationService

router = APIRouter()


@router.post(
    "/api/v1/{user_id}/tasks",
    response_model=TaskResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new task",
    tags=["Tasks"],
)
async def create_task(
    task_data: TaskCreate,
    user: User = Depends(verify_user_match),
    session: AsyncSession = Depends(get_session),
):
    """
    Create a new task for the authenticated user.

    - **title**: Task title (required, max 255 chars)
    - **description**: Optional description (max 10,000 chars)
    - **completed**: Completion status (defaults to false)
    - **priority**: Priority level (low, medium, high)
    - **due_date**: Task deadline (ISO 8601 UTC)
    - **reminder_at**: Reminder time (must be before due_date)
    - **recurrence_pattern**: Recurrence type (daily, weekly, monthly, custom)
    - **recurrence_config**: JSONB config with RRULE format

    Returns the created task with ID and timestamps.
    """
    repo = TaskRepository(session)
    task = await repo.create(user.uuid, task_data)
    await session.commit()
    await session.refresh(task, ["tags"])

    # T130: Send task creation notification
    notification_service = NotificationService()
    await notification_service.notify_task_created(task, user)

    return TaskResponse.model_validate(task)


@router.get(
    "/api/v1/{user_id}/tasks",
    response_model=List[TaskResponse],
    summary="List all tasks with optional filters",
    tags=["Tasks"],
)
async def list_tasks(
    user: User = Depends(verify_user_match),
    session: AsyncSession = Depends(get_session),
    status: Optional[str] = Query(
        None,
        description="Filter by completion status: 'complete' or 'incomplete'",
        pattern="^(complete|incomplete)$"
    ),
    priority: Optional[str] = Query(
        None,
        description="Filter by priority: 'low', 'medium', or 'high'",
        pattern="^(low|medium|high)$"
    ),
    tag: Optional[List[str]] = Query(
        None,
        description="Filter by tag names (OR logic). Use 'none' for untagged tasks.",
        alias="tag"
    ),
    due_before: Optional[datetime] = Query(
        None,
        description="Filter tasks due before this datetime (ISO 8601 format)"
    ),
    due_after: Optional[datetime] = Query(
        None,
        description="Filter tasks due after this datetime (ISO 8601 format)"
    ),
    search: Optional[str] = Query(
        None,
        description="Full-text search in title and description",
        max_length=255
    ),
    sort_by: str = Query(
        "sort_order",
        description="Column to sort by (T043: defaults to sort_order for drag-and-drop)",
        pattern="^(created_at|due_date|priority|title|sort_order)$"
    ),
    order: str = Query(
        "asc",
        description="Sort order: 'asc' or 'desc' (T043: defaults to asc for sort_order)",
        pattern="^(asc|desc)$"
    ),
):
    """
    List all active tasks for the authenticated user with optional filters and sorting.

    **Filtering** (all filters use AND logic):
    - **status**: Filter by completion status ('complete' or 'incomplete')
    - **priority**: Filter by priority level ('low', 'medium', 'high')
    - **tag**: Filter by tag names (multiple tags use OR logic). Use 'none' for untagged tasks.
    - **due_before**: Filter tasks due before specified datetime
    - **due_after**: Filter tasks due after specified datetime
    - **search**: Full-text search in title and description

    **Sorting** (T043 - sqlmodel-expert sorting pattern):
    - **sort_by**: Column to sort by (created_at, due_date, priority, title, sort_order)
    - **order**: Sort order (asc or desc)

    **Default behavior** (T043): Returns all tasks sorted by sort_order ascending (drag-and-drop order).

    Soft-deleted tasks are excluded. Each task includes nested tags.
    """
    # Build dynamic query with filters
    stmt = QueryService.build_task_query(
        user_id=user.uuid,
        status=status,
        priority=priority,
        tags=tag,
        due_before=due_before,
        due_after=due_after,
        search=search,
        sort_by=sort_by,
        order=order,
    )

    # Execute query
    result = await session.execute(stmt)
    tasks = result.scalars().all()

    return [TaskResponse.model_validate(task) for task in tasks]


@router.get(
    "/api/v1/{user_id}/tasks/{task_id}",
    response_model=TaskResponse,
    summary="Get a single task",
    tags=["Tasks"],
)
async def get_task(
    task_id: int = Path(..., description="Task ID", gt=0),
    user: User = Depends(verify_user_match),
    session: AsyncSession = Depends(get_session),
):
    """
    Get a single task by ID with nested tags.

    Returns 404 if:
    - Task does not exist
    - Task belongs to a different user (user isolation)
    - Task is soft-deleted
    """
    repo = TaskRepository(session)
    task = await repo.get_by_id(user.uuid, task_id)

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )

    return TaskResponse.model_validate(task)


@router.put(
    "/api/v1/{user_id}/tasks/{task_id}",
    response_model=TaskResponse,
    summary="Replace a task (full update)",
    tags=["Tasks"],
)
async def replace_task(
    task_data: TaskReplace,
    task_id: int = Path(..., description="Task ID", gt=0),
    user: User = Depends(verify_user_match),
    session: AsyncSession = Depends(get_session),
):
    """
    Fully replace a task (PUT semantics).

    All non-nullable fields must be provided.
    Omitted optional fields are set to None.

    Returns 404 if task not found or doesn't belong to user.
    """
    repo = TaskRepository(session)
    task = await repo.replace(user.uuid, task_id, task_data)

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )

    await session.commit()
    await session.refresh(task, ["tags"])

    # T131: Send task update notification
    changes = task_data.model_dump(exclude_unset=True)
    notification_service = NotificationService()
    await notification_service.notify_task_updated(task, user, changes)

    return TaskResponse.model_validate(task)


@router.patch(
    "/api/v1/{user_id}/tasks/{task_id}",
    response_model=TaskResponse,
    summary="Update a task (partial update)",
    tags=["Tasks"],
)
async def update_task(
    task_data: TaskUpdate,
    task_id: int = Path(..., description="Task ID", gt=0),
    user: User = Depends(verify_user_match),
    session: AsyncSession = Depends(get_session),
):
    """
    Partially update a task (PATCH semantics).

    Only provided fields are updated.
    Omitted fields remain unchanged.

    Returns 404 if task not found or doesn't belong to user.
    """
    repo = TaskRepository(session)
    task = await repo.update(user.uuid, task_id, task_data)

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )

    await session.commit()
    await session.refresh(task, ["tags"])

    # T131: Send task update notification
    changes = task_data.model_dump(exclude_unset=True)
    notification_service = NotificationService()
    await notification_service.notify_task_updated(task, user, changes)

    return TaskResponse.model_validate(task)


@router.patch(
    "/api/v1/{user_id}/tasks/{task_id}/complete",
    response_model=TaskResponse,
    summary="Toggle task completion",
    tags=["Tasks"],
)
async def toggle_task_completion(
    task_id: int = Path(..., description="Task ID", gt=0),
    user: User = Depends(verify_user_match),
    session: AsyncSession = Depends(get_session),
):
    """
    Toggle the completion status of a task.

    If completed is True, sets it to False.
    If completed is False, sets it to True.

    Returns 404 if task not found or doesn't belong to user.
    """
    repo = TaskRepository(session)
    task = await repo.get_by_id(user.uuid, task_id)

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )

    # Toggle completion
    task_update = TaskUpdate(completed=not task.completed)
    updated_task = await repo.update(user.uuid, task_id, task_update)

    await session.commit()
    await session.refresh(updated_task, ["tags"])

    # T132: Send completion notification (only when marking as complete)
    if updated_task.completed:
        notification_service = NotificationService()
        await notification_service.notify_task_completed(updated_task, user)

    return TaskResponse.model_validate(updated_task)


@router.delete(
    "/api/v1/{user_id}/tasks/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a task (soft delete)",
    tags=["Tasks"],
)
async def delete_task(
    task_id: int = Path(..., description="Task ID", gt=0),
    user: User = Depends(verify_user_match),
    session: AsyncSession = Depends(get_session),
):
    """
    Soft delete a task by setting deleted_at timestamp.

    The task remains in the database but is excluded from all queries.
    TaskTag relationships are preserved.

    Returns 404 if task not found or doesn't belong to user.
    """
    repo = TaskRepository(session)
    success = await repo.soft_delete(user.uuid, task_id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )

    await session.commit()
    # 204 No Content - no response body


@router.patch(
    "/api/v1/{user_id}/tasks/reorder",
    status_code=status.HTTP_200_OK,
    summary="Reorder tasks via drag-and-drop",
    tags=["Tasks"],
)
async def reorder_tasks(
    reorder_data: ReorderRequest,
    user: User = Depends(verify_user_match),
    session: AsyncSession = Depends(get_session),
):
    """
    Reorder tasks by updating sort_order based on drag-and-drop array position.

    T042 - Uses betterauth-fastapi-jwt-bridge for JWT validation via verify_user_match.

    **Request Body:**
    - **task_ids**: Ordered array of task IDs (position = new sort_order)

    **Security:**
    - JWT authentication required (Authorization: Bearer token)
    - User isolation enforced (verify_user_match dependency)
    - All tasks must belong to authenticated user

    **Returns:**
    - 200 OK: Reorder successful, returns confirmation message
    - 400 Bad Request: Invalid task IDs or validation error
    - 401 Unauthorized: Missing or invalid JWT token
    - 403 Forbidden: Task belongs to different user
    - 404 Not Found: One or more tasks not found

    **Example Request:**
    ```json
    {
        "task_ids": [5, 2, 8, 1, 3]
    }
    ```

    **Result:** Task 5 → sort_order=1, Task 2 → sort_order=2, etc.
    """
    repo = TaskRepository(session)

    # Validate all task IDs exist and belong to user (T044 - error handling)
    # Fetch tasks first to identify invalid IDs
    from sqlmodel import select
    from ..models.task import Task

    stmt = (
        select(Task.id)
        .where(Task.id.in_(reorder_data.task_ids))
        .where(Task.user_id == user.uuid)
        .where(Task.deleted_at.is_(None))
    )
    result = await session.execute(stmt)
    valid_task_ids = set(result.scalars().all())

    # Check for invalid IDs (FR-019b structured error response)
    invalid_ids = [task_id for task_id in reorder_data.task_ids if task_id not in valid_task_ids]
    if invalid_ids:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": "Invalid task IDs provided",
                "code": "INVALID_TASK_IDS",
                "invalid_ids": invalid_ids
            }
        )

    # Call repository reorder method (validates ownership + updates sort_order)
    # betterauth-fastapi-jwt-bridge: user.uuid extracted from verified JWT token
    success = await repo.reorder_tasks(user.uuid, reorder_data.task_ids)

    if not success:
        # This should not happen if validation above passed, but keep for safety
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to reorder tasks"
        )

    # Commit transaction (sqlmodel-expert pattern)
    await session.commit()

    return {
        "message": "Tasks reordered successfully",
        "updated": len(reorder_data.task_ids)  # Match test expectations
    }
