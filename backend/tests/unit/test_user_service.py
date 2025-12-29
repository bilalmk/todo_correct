"""Unit tests for user service layer (T104-T105)."""
import pytest
from sqlalchemy.exc import IntegrityError

from src.models.user import UserCreate
from src.services.user import create_user, get_user_by_email, get_user_by_id


class TestUserService:
    """Test user service functions (T104-T105)."""

    @pytest.mark.asyncio
    async def test_create_user(self, test_session):
        """Test creating a new user (T104)."""
        user_data = UserCreate(
            email="newuser@example.com",
            password="password123",
            name="New User",
        )

        user = await create_user(test_session, user_data)
        await test_session.commit()

        # Verify user was created
        assert user.id is not None
        assert user.email == "newuser@example.com"
        assert user.name == "New User"
        assert user.password_hash != "password123"  # Should be hashed
        assert user.password_hash.startswith("$argon2id$")
        assert user.created_at is not None
        assert user.updated_at is not None

    @pytest.mark.asyncio
    async def test_create_user_duplicate_email(self, test_session, test_user):
        """Test creating user with duplicate email raises error."""
        user_data = UserCreate(
            email=test_user.email,  # Same email as test_user
            password="password123",
            name="Duplicate User",
        )

        # Should raise IntegrityError
        with pytest.raises(IntegrityError):
            await create_user(test_session, user_data)
            await test_session.commit()

    @pytest.mark.asyncio
    async def test_get_user_by_email(self, test_session, test_user):
        """Test getting user by email (T105)."""
        user = await get_user_by_email(test_session, test_user.email)

        # Verify user was found
        assert user is not None
        assert user.id == test_user.id
        assert user.email == test_user.email
        assert user.name == test_user.name

    @pytest.mark.asyncio
    async def test_get_user_by_email_case_insensitive(self, test_session, test_user):
        """Test getting user by email is case-insensitive."""
        # Test with uppercase email
        user = await get_user_by_email(test_session, test_user.email.upper())

        # Verify user was found
        assert user is not None
        assert user.id == test_user.id

    @pytest.mark.asyncio
    async def test_get_user_by_email_not_found(self, test_session):
        """Test getting non-existent user by email."""
        user = await get_user_by_email(test_session, "nonexistent@example.com")

        # Verify user was not found
        assert user is None

    @pytest.mark.asyncio
    async def test_get_user_by_id(self, test_session, test_user):
        """Test getting user by ID."""
        user = await get_user_by_id(test_session, test_user.id)

        # Verify user was found
        assert user is not None
        assert user.id == test_user.id
        assert user.email == test_user.email
        assert user.name == test_user.name

    @pytest.mark.asyncio
    async def test_get_user_by_id_not_found(self, test_session):
        """Test getting non-existent user by ID."""
        from uuid import uuid4

        user = await get_user_by_id(test_session, uuid4())

        # Verify user was not found
        assert user is None
