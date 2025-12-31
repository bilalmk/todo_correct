"""Pydantic schemas for Tag API endpoints."""

from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field, field_validator
from typing import Optional

from ..core.validators import validate_hex_color


class TagCreate(BaseModel):
    """Request DTO for creating a new tag."""

    name: str = Field(
        ...,
        min_length=1,
        max_length=50,
        description="Tag name (e.g., 'work', 'personal')",
    )
    color: Optional[str] = Field(
        None, max_length=7, description="Hex color code (#RRGGBB or #RGB)"
    )

    @field_validator("name")
    @classmethod
    def name_not_empty(cls, v: str) -> str:
        """Ensure name is not whitespace-only."""
        if not v.strip():
            raise ValueError("Tag name cannot be empty or whitespace-only")
        return v.strip()

    @field_validator("color")
    @classmethod
    def validate_and_normalize_hex_color(cls, v: Optional[str]) -> Optional[str]:
        """Validate and normalize hex color format."""
        return validate_hex_color(v)

    model_config = {
        "json_schema_extra": {"example": {"name": "work", "color": "#FF5733"}}
    }


class TagUpdate(BaseModel):
    """Request DTO for updating a tag (all fields optional for partial updates)."""

    name: Optional[str] = Field(None, min_length=1, max_length=50)
    color: Optional[str] = Field(None, max_length=7)

    @field_validator("name")
    @classmethod
    def name_not_empty(cls, v: Optional[str]) -> Optional[str]:
        """Ensure name is not whitespace-only if provided."""
        if v is not None and not v.strip():
            raise ValueError("Tag name cannot be empty or whitespace-only")
        return v.strip() if v else None

    @field_validator("color")
    @classmethod
    def validate_and_normalize_hex_color(cls, v: Optional[str]) -> Optional[str]:
        """Validate and normalize hex color format."""
        return validate_hex_color(v)


class TagResponse(BaseModel):
    """Response DTO for tag objects."""

    id: int = Field(..., description="Tag ID")
    user_id: UUID = Field(..., description="Owner user ID")
    name: str = Field(..., description="Tag name")
    color: Optional[str] = Field(None, description="Hex color code (#RRGGBB)")
    created_at: datetime = Field(..., description="Creation timestamp (UTC)")

    model_config = {
        "from_attributes": True,  # Pydantic v2: enable ORM mode
        "json_schema_extra": {
            "example": {
                "id": 1,
                "user_id": "123e4567-e89b-12d3-a456-426614174000",
                "name": "work",
                "color": "#FF5733",
                "created_at": "2025-12-30T10:00:00Z",
            }
        },
    }
