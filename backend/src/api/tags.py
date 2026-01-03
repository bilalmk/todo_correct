"""Tag API endpoints for tag management."""

from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Path, status
from sqlalchemy.exc import IntegrityError
from sqlmodel.ext.asyncio.session import AsyncSession

from ..api.deps import verify_user_match
from ..core.database import get_session
from ..models.user import User
from ..repositories.tag import TagRepository
from ..schemas.tag import TagCreate, TagUpdate, TagResponse

router = APIRouter()


@router.post(
    "/api/v1/{user_id}/tags",
    response_model=TagResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new tag",
    tags=["Tags"],
)
async def create_tag(
    tag_data: TagCreate,
    user: User = Depends(verify_user_match),
    session: AsyncSession = Depends(get_session),
):
    """
    Create a new tag for the authenticated user.

    - **name**: Tag name (required, max 50 chars, unique per user)
    - **color**: Hex color code (optional, #RRGGBB or #RGB, normalized to #RRGGBB)

    Returns 409 Conflict if tag name already exists for this user.
    """
    repo = TagRepository(session)

    # Check if tag name already exists
    if await repo.exists_by_name(user.uuid, tag_data.name):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "error": "Tag name already exists",
                "code": "TAG_NAME_CONFLICT",
                "status": status.HTTP_409_CONFLICT,
            },
        )

    try:
        tag = await repo.create(user.uuid, tag_data)
        await session.commit()
        return TagResponse.model_validate(tag)
    except IntegrityError:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "error": "Tag name already exists",
                "code": "TAG_NAME_CONFLICT",
                "status": status.HTTP_409_CONFLICT,
            },
        )


@router.get(
    "/api/v1/{user_id}/tags",
    response_model=List[TagResponse],
    summary="List all tags",
    tags=["Tags"],
)
async def list_tags(
    user: User = Depends(verify_user_match),
    session: AsyncSession = Depends(get_session),
):
    """
    List all active tags for the authenticated user.

    Tags are returned sorted by creation date (newest first).
    Soft-deleted tags are excluded.
    """
    repo = TagRepository(session)
    tags = await repo.list_tags(user.uuid)
    return [TagResponse.model_validate(tag) for tag in tags]


@router.get(
    "/api/v1/{user_id}/tags/{tag_id}",
    response_model=TagResponse,
    summary="Get a single tag",
    tags=["Tags"],
)
async def get_tag(
    tag_id: int = Path(..., description="Tag ID", gt=0),
    user: User = Depends(verify_user_match),
    session: AsyncSession = Depends(get_session),
):
    """
    Get a single tag by ID.

    Returns 404 if:
    - Tag does not exist
    - Tag belongs to a different user (user isolation)
    - Tag is soft-deleted
    """
    repo = TagRepository(session)
    tag = await repo.get_by_id(user.uuid, tag_id)

    if not tag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tag not found",
        )

    return TagResponse.model_validate(tag)


@router.put(
    "/api/v1/{user_id}/tags/{tag_id}",
    response_model=TagResponse,
    summary="Update a tag",
    tags=["Tags"],
)
async def update_tag(
    tag_data: TagUpdate,
    tag_id: int = Path(..., description="Tag ID", gt=0),
    user: User = Depends(verify_user_match),
    session: AsyncSession = Depends(get_session),
):
    """
    Update a tag (partial update).

    Only provided fields are updated.
    Omitted fields remain unchanged.

    Returns 404 if tag not found or doesn't belong to user.
    Returns 409 if updated name conflicts with existing tag.
    """
    repo = TagRepository(session)

    # Check if new name conflicts with existing tag
    if tag_data.name:
        existing = await repo.exists_by_name(user.uuid, tag_data.name)
        if existing:
            # Check if it's not the same tag
            current_tag = await repo.get_by_id(user.uuid, tag_id)
            if not current_tag or current_tag.name != tag_data.name:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail={
                        "error": "Tag name already exists",
                        "code": "TAG_NAME_CONFLICT",
                        "status": status.HTTP_409_CONFLICT,
                    },
                )

    tag = await repo.update(user.uuid, tag_id, tag_data)

    if not tag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tag not found",
        )

    await session.commit()
    return TagResponse.model_validate(tag)


@router.delete(
    "/api/v1/{user_id}/tags/{tag_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a tag (soft delete)",
    tags=["Tags"],
)
async def delete_tag(
    tag_id: int = Path(..., description="Tag ID", gt=0),
    user: User = Depends(verify_user_match),
    session: AsyncSession = Depends(get_session),
):
    """
    Soft delete a tag by setting deleted_at timestamp.

    The tag remains in the database but is excluded from all queries.
    TaskTag relationships are preserved.

    Returns 404 if tag not found or doesn't belong to user.
    """
    repo = TagRepository(session)
    success = await repo.soft_delete(user.uuid, tag_id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tag not found",
        )

    await session.commit()
    # 204 No Content - no response body
