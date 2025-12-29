"""Unit tests for User model validation (T101-T103)."""
import pytest
from pydantic import ValidationError

from src.models.user import User, UserCreate, UserLogin


class TestUserModel:
    """Test User SQLModel validation (T101)."""

    def test_user_create_valid(self):
        """Test UserCreate with valid data."""
        user_data = UserCreate(
            email="test@example.com",
            password="password123",
            name="Test User",
        )

        assert user_data.email == "test@example.com"
        assert user_data.password == "password123"
        assert user_data.name == "Test User"

    def test_user_create_email_normalization(self):
        """Test email normalization to lowercase."""
        user_data = UserCreate(
            email="TEST@EXAMPLE.COM",
            password="password123",
            name="Test User",
        )

        # Email should be normalized to lowercase
        assert user_data.email == "test@example.com"

    def test_user_create_name_trimmed(self):
        """Test name trimming."""
        user_data = UserCreate(
            email="test@example.com",
            password="password123",
            name="  Test User  ",
        )

        # Name should be trimmed
        assert user_data.name == "Test User"

    def test_user_create_invalid_email(self):
        """Test UserCreate with invalid email format."""
        with pytest.raises(ValidationError) as exc_info:
            UserCreate(
                email="invalid-email",
                password="password123",
                name="Test User",
            )

        errors = exc_info.value.errors()
        assert any(error["loc"] == ("email",) for error in errors)

    def test_user_create_password_too_short(self):
        """Test UserCreate with password < 8 characters."""
        with pytest.raises(ValidationError) as exc_info:
            UserCreate(
                email="test@example.com",
                password="short",
                name="Test User",
            )

        errors = exc_info.value.errors()
        assert any(
            error["loc"] == ("password",) and "at least 8 characters" in str(error["msg"])
            for error in errors
        )

    def test_user_create_empty_name(self):
        """Test UserCreate with empty name."""
        with pytest.raises(ValidationError) as exc_info:
            UserCreate(
                email="test@example.com",
                password="password123",
                name="",
            )

        errors = exc_info.value.errors()
        assert any(error["loc"] == ("name",) for error in errors)

    def test_user_create_whitespace_only_name(self):
        """Test UserCreate with whitespace-only name."""
        with pytest.raises(ValidationError) as exc_info:
            UserCreate(
                email="test@example.com",
                password="password123",
                name="   ",
            )

        errors = exc_info.value.errors()
        assert any(error["loc"] == ("name",) for error in errors)

    def test_user_create_missing_fields(self):
        """Test UserCreate with missing required fields."""
        # Missing email
        with pytest.raises(ValidationError):
            UserCreate(password="password123", name="Test User")

        # Missing password
        with pytest.raises(ValidationError):
            UserCreate(email="test@example.com", name="Test User")

        # Missing name
        with pytest.raises(ValidationError):
            UserCreate(email="test@example.com", password="password123")


class TestUserLogin:
    """Test UserLogin schema validation (T103)."""

    def test_user_login_valid(self):
        """Test UserLogin with valid data."""
        login_data = UserLogin(
            email="test@example.com",
            password="password123",
        )

        assert login_data.email == "test@example.com"
        assert login_data.password == "password123"

    def test_user_login_email_normalization(self):
        """Test email normalization in login."""
        login_data = UserLogin(
            email="TEST@EXAMPLE.COM",
            password="password123",
        )

        # Email should be normalized to lowercase
        assert login_data.email == "test@example.com"

    def test_user_login_invalid_email(self):
        """Test UserLogin with invalid email format."""
        with pytest.raises(ValidationError) as exc_info:
            UserLogin(
                email="invalid-email",
                password="password123",
            )

        errors = exc_info.value.errors()
        assert any(error["loc"] == ("email",) for error in errors)

    def test_user_login_password_too_short(self):
        """Test UserLogin with password < 8 characters."""
        with pytest.raises(ValidationError) as exc_info:
            UserLogin(
                email="test@example.com",
                password="short",
            )

        errors = exc_info.value.errors()
        assert any(error["loc"] == ("password",) for error in errors)

    def test_user_login_missing_fields(self):
        """Test UserLogin with missing fields."""
        # Missing email
        with pytest.raises(ValidationError):
            UserLogin(password="password123")

        # Missing password
        with pytest.raises(ValidationError):
            UserLogin(email="test@example.com")
