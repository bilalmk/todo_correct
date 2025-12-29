"""User database models and schemas."""
from datetime import datetime, timezone
from typing import Optional
from uuid import UUID, uuid4

from pydantic import EmailStr, field_validator
from sqlmodel import Field, SQLModel


class UserBase(SQLModel):
    """Base user model with shared fields."""

    email: EmailStr = Field(unique=True, index=True, max_length=255, sa_column_kwargs={"unique": True})
    name: str = Field(min_length=1, max_length=255)

    @field_validator("email", mode="before")
    @classmethod
    def normalize_email(cls, v: str) -> str:
        """Normalize email to lowercase."""
        if isinstance(v, str):
            return v.lower().strip()
        return v

    @field_validator("name", mode="before")
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Validate and trim name."""
        if isinstance(v, str):
            v = v.strip()
            if not v:
                raise ValueError("Name cannot be empty")
        return v


class User(UserBase, table=True):
    """User database model."""

    __tablename__ = "users"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    password_hash: str = Field(max_length=255)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class UserCreate(UserBase):
    """Schema for user registration."""

    password: str = Field(min_length=8, max_length=100)

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        """Validate password strength."""
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        return v


class UserLogin(SQLModel):
    """Schema for user login."""

    email: EmailStr = Field(max_length=255)
    password: str = Field(min_length=8, max_length=100)

    @field_validator("email", mode="before")
    @classmethod
    def normalize_email(cls, v: str) -> str:
        """Normalize email to lowercase."""
        if isinstance(v, str):
            return v.lower().strip()
        return v


class UserResponse(UserBase):
    """Schema for user data in responses (no password)."""

    id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class UserWithToken(SQLModel):
    """Schema for authentication responses."""

    access_token: str
    token_type: str = "bearer"
    user: UserResponse
