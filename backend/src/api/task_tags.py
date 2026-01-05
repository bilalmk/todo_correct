"""Task-Tag relationship endpoints for managing task-tag assignments."""

from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Path, status
from sqlalchemy.exc import IntegrityError
from sqlmodel.ext.asyncio.session import AsyncSession

from ..api.deps import verify_user_match
from ..core.database import get_session
from ..models.user import User
from ..repositories.task_tag import TaskTagRepository
from ..schemas.tag import TagResponse
from ..schemas.task_tag import TaskTagCreate, TaskTagResponse

router = APIRouter()


@router.post(
    "/api/v1/{user_id}/tasks/{task_id}/tags",
    response_model=TaskTagResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Assign a tag to a task",
    tags=["Task-Tags"],
)
async def assign_tag_to_task(
    task_tag_data: TaskTagCreate,
    task_id: int = Path(..., description="Task ID", gt=0),
    user: User = Depends(verify_user_match),
    session: AsyncSession = Depends(get_session),
):
    """
    Assign a tag to a task (create many-to-many relationship).

    Validates that both task and tag exist, belong to the user, and are not soft-deleted.

    Returns 404 if task or tag not found.
    Returns 409 if tag is already assigned to this task.
    """
    repo = TaskTagRepository(session)

    try:
        success = await repo.assign_tag(user.uuid, task_id, task_tag_data.tag_id)
        await session.commit()

        return TaskTagResponse(
            task_id=task_id,
            tag_id=task_tag_data.tag_id,
            message="Tag assigned successfully",
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except IntegrityError:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "error": "Tag already assigned to this task",
                "code": "DUPLICATE_TAG_ASSIGNMENT",
                "status": status.HTTP_409_CONFLICT,
            },
        )


@router.get(
    "/api/v1/{user_id}/tasks/{task_id}/tags",
    response_model=List[TagResponse],
    summary="List tags for a task",
    tags=["Task-Tags"],
)
async def list_task_tags(
    task_id: int = Path(..., description="Task ID", gt=0),
    user: User = Depends(verify_user_match),
    session: AsyncSession = Depends(get_session),
):
    """
    List all tags assigned to a task.

    Excludes soft-deleted tags.
    Returns empty list if task has no tags.
    Returns empty list if task not found (for security - no user enumeration).
    """
    repo = TaskTagRepository(session)
    tags = await repo.get_task_tags(user.uuid, task_id)
    return [TagResponse.model_validate(tag) for tag in tags]


@router.delete(
    "/api/v1/{user_id}/tasks/{task_id}/tags/{tag_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Remove a tag from a task",
    tags=["Task-Tags"],
)
async def remove_tag_from_task(
    task_id: int = Path(..., description="Task ID", gt=0),
    tag_id: int = Path(..., description="Tag ID", gt=0),
    user: User = Depends(verify_user_match),
    session: AsyncSession = Depends(get_session),
):
    """
    Remove a tag from a task (delete many-to-many relationship).

    The tag itself is NOT deleted, only the association with the task.

    Returns 404 if task not found or tag was not assigned to the task.
    """
    repo = TaskTagRepository(session)
    success = await repo.unassign_tag(user.uuid, task_id, tag_id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task or tag assignment not found",
        )

    await session.commit()
    # 204 No Content - no response body
