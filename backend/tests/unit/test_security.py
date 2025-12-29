"""Unit tests for security module (password hashing and JWT)."""
import pytest
import jwt
from datetime import datetime, timedelta, timezone
from uuid import uuid4

from src.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    decode_access_token,
    extract_token_from_header,
)
from src.core.config import settings


class TestPasswordHashing:
    """Test password hashing with Argon2 (T097-T098)."""

    def test_hash_password(self):
        """Test password hashing produces valid hash."""
        password = "secure_password123"
        hashed = hash_password(password)

        # Verify hash is not same as password
        assert hashed != password

        # Verify hash is argon2id format
        assert hashed.startswith("$argon2id$")

        # Verify hash is not empty
        assert len(hashed) > 0

    def test_verify_password_correct(self):
        """Test password verification with correct password."""
        password = "secure_password123"
        hashed = hash_password(password)

        # Verify correct password
        assert verify_password(password, hashed) is True

    def test_verify_password_incorrect(self):
        """Test password verification with incorrect password."""
        password = "secure_password123"
        wrong_password = "wrong_password"
        hashed = hash_password(password)

        # Verify incorrect password
        assert verify_password(wrong_password, hashed) is False

    def test_different_passwords_different_hashes(self):
        """Test that different passwords produce different hashes."""
        password1 = "password1"
        password2 = "password2"

        hash1 = hash_password(password1)
        hash2 = hash_password(password2)

        # Verify different hashes
        assert hash1 != hash2

    def test_same_password_different_hashes(self):
        """Test that same password hashed twice produces different hashes (salt)."""
        password = "same_password"

        hash1 = hash_password(password)
        hash2 = hash_password(password)

        # Verify different hashes (due to salt)
        assert hash1 != hash2

        # But both verify correctly
        assert verify_password(password, hash1) is True
        assert verify_password(password, hash2) is True


class TestJWTToken:
    """Test JWT token generation and validation (T099-T100)."""

    def test_create_access_token(self):
        """Test JWT token creation."""
        user_id = uuid4()
        email = "user@example.com"

        token = create_access_token(user_id, email)

        # Verify token is not empty
        assert len(token) > 0

        # Verify token has 3 parts (header.payload.signature)
        assert len(token.split(".")) == 3

    def test_decode_access_token_valid(self):
        """Test JWT token decoding with valid token."""
        user_id = uuid4()
        email = "user@example.com"

        token = create_access_token(user_id, email)
        payload = decode_access_token(token)

        # Verify payload contains correct data
        assert payload["sub"] == str(user_id)
        assert payload["email"] == email
        assert payload["type"] == "access"
        assert "exp" in payload
        assert "iat" in payload

    def test_decode_access_token_expired(self):
        """Test JWT token decoding with expired token."""
        user_id = uuid4()
        email = "user@example.com"

        # Create token that expired 1 day ago
        expire = datetime.now(timezone.utc) - timedelta(days=1)
        payload = {
            "sub": str(user_id),
            "email": email,
            "exp": expire,
            "iat": datetime.now(timezone.utc),
            "type": "access",
        }

        token = jwt.encode(payload, settings.BETTER_AUTH_SECRET, algorithm=settings.JWT_ALGORITHM)

        # Verify token is expired
        with pytest.raises(jwt.ExpiredSignatureError):
            decode_access_token(token)

    def test_decode_access_token_invalid(self):
        """Test JWT token decoding with invalid token."""
        invalid_token = "invalid.token.here"

        # Verify invalid token raises exception
        with pytest.raises(jwt.InvalidTokenError):
            decode_access_token(invalid_token)

    def test_decode_access_token_wrong_secret(self):
        """Test JWT token decoding with wrong secret."""
        user_id = uuid4()
        email = "user@example.com"

        # Create token with different secret
        payload = {
            "sub": str(user_id),
            "email": email,
            "exp": datetime.now(timezone.utc) + timedelta(days=7),
            "iat": datetime.now(timezone.utc),
            "type": "access",
        }

        token = jwt.encode(payload, "wrong_secret", algorithm="HS256")

        # Verify wrong secret raises exception
        with pytest.raises(jwt.InvalidTokenError):
            decode_access_token(token)

    def test_extract_token_from_header_valid(self):
        """Test extracting token from valid Authorization header."""
        token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.test"
        authorization = f"Bearer {token}"

        extracted = extract_token_from_header(authorization)

        assert extracted == token

    def test_extract_token_from_header_invalid(self):
        """Test extracting token from invalid Authorization header."""
        # Missing "Bearer " prefix
        with pytest.raises(ValueError):
            extract_token_from_header("invalid_header")

        # Empty header
        with pytest.raises(ValueError):
            extract_token_from_header("")

        # None header
        with pytest.raises(ValueError):
            extract_token_from_header(None)
