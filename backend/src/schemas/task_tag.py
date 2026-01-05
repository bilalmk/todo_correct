"""Pydantic schemas for Task-Tag relationship API endpoints."""

from pydantic import BaseModel, Field


class TaskTagCreate(BaseModel):
    """Request DTO for assigning a tag to a task."""

    tag_id: int = Field(..., description="ID of the tag to assign", gt=0)

    model_config = {"json_schema_extra": {"example": {"tag_id": 5}}}


class TaskTagResponse(BaseModel):
    """Response DTO for successful tag assignment."""

    task_id: int = Field(..., description="Task ID")
    tag_id: int = Field(..., description="Tag ID")
    message: str = Field(
        default="Tag assigned successfully", description="Success message"
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "task_id": 123,
                "tag_id": 5,
                "message": "Tag assigned successfully",
            }
        }
    }
