"""
Unit Tests for Authentication Dependencies
T045: Test JWT verification, user_id extraction, correlation ID logging

Built following skills:
- @.claude/skills/panaversity/betterauth-fastapi-jwt-bridge (security test patterns)

Test Coverage:
- Valid/expired/tampered token handling
- User ID extraction from JWT payload
- JWKS verification integration
- Correlation ID logging per FR-032
- User isolation enforcement
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from fastapi import HTTPException, status
from jose import JWTError
from datetime import datetime, timedelta
from src.api.deps import (
    get_current_user,
    verify_user_match,
    get_correlation_id,
)
from src.models.user import User


class TestGetCurrentUser:
    """Test JWT verification and user extraction in get_current_user dependency"""

    @pytest.mark.asyncio
    async def test_valid_token_returns_user(self):
        """Test valid JWT token returns authenticated user"""
        # Mock JWT verification
        with patch("src.api.deps.verify_better_auth_jwt") as mock_verify:
            mock_verify.return_value = {
                "sub": "user_123",
                "email": "test@example.com",
                "name": "Test User",
            }

            # Mock database user fetch
            with patch("src.api.deps.get_user_by_id") as mock_get_user:
                mock_user = User(
                    id="user_123",
                    email="test@example.com",
                    name="Test User",
                    password_hash="hashed",
                )
                mock_get_user.return_value = mock_user

                # Mock request with Authorization header
                mock_credentials = Mock()
                mock_credentials.credentials = "valid-jwt-token"

                user = await get_current_user(mock_credentials)

                assert user.id == "user_123"
                assert user.email == "test@example.com"
                mock_verify.assert_called_once_with("valid-jwt-token")

    @pytest.mark.asyncio
    async def test_expired_token_raises_401(self):
        """Test expired JWT token raises 401 Unauthorized"""
        with patch(
            "src.api.deps.verify_better_auth_jwt",
            side_effect=JWTError("Token has expired"),
        ):
            mock_credentials = Mock()
            mock_credentials.credentials = "expired-token"

            with pytest.raises(HTTPException) as exc_info:
                await get_current_user(mock_credentials)

            assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
            assert "Invalid authentication credentials" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_tampered_token_raises_401(self):
        """Test tampered JWT token (invalid signature) raises 401"""
        with patch(
            "src.api.deps.verify_better_auth_jwt",
            side_effect=JWTError("Invalid signature"),
        ):
            mock_credentials = Mock()
            mock_credentials.credentials = "tampered-token"

            with pytest.raises(HTTPException) as exc_info:
                await get_current_user(mock_credentials)

            assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.asyncio
    async def test_missing_sub_claim_raises_401(self):
        """Test JWT without 'sub' claim raises 401"""
        with patch("src.api.deps.verify_better_auth_jwt") as mock_verify:
            # Return payload without 'sub' claim
            mock_verify.return_value = {"email": "test@example.com"}

            mock_credentials = Mock()
            mock_credentials.credentials = "token-without-sub"

            with pytest.raises(HTTPException) as exc_info:
                await get_current_user(mock_credentials)

            assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
            assert "user identifier" in exc_info.value.detail.lower()

    @pytest.mark.asyncio
    async def test_user_not_found_raises_401(self):
        """Test user_id from JWT not found in database raises 401"""
        with patch("src.api.deps.verify_better_auth_jwt") as mock_verify:
            mock_verify.return_value = {"sub": "nonexistent_user"}

            with patch("src.api.deps.get_user_by_id", return_value=None):
                mock_credentials = Mock()
                mock_credentials.credentials = "valid-token-unknown-user"

                with pytest.raises(HTTPException) as exc_info:
                    await get_current_user(mock_credentials)

                assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
                assert "User not found" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_correlation_id_logging_on_success(self):
        """Test correlation ID logged on successful JWT validation per FR-032"""
        with patch("src.api.deps.verify_better_auth_jwt") as mock_verify:
            mock_verify.return_value = {"sub": "user_123"}

            with patch("src.api.deps.get_user_by_id") as mock_get_user:
                mock_user = User(
                    id="user_123", email="test@example.com", password_hash="hashed"
                )
                mock_get_user.return_value = mock_user

                with patch("src.api.deps.logger.info") as mock_log:
                    with patch("src.api.deps.get_correlation_id", return_value="abc123"):
                        mock_credentials = Mock()
                        mock_credentials.credentials = "valid-token"

                        await get_current_user(mock_credentials)

                        # Verify logging occurred with correlation ID
                        mock_log.assert_called()
                        log_call_args = str(mock_log.call_args)
                        assert "correlation_id" in log_call_args
                        assert "abc123" in log_call_args

    @pytest.mark.asyncio
    async def test_correlation_id_logging_on_failure(self):
        """Test correlation ID logged on JWT validation failure per FR-032"""
        with patch(
            "src.api.deps.verify_better_auth_jwt", side_effect=JWTError("Invalid token")
        ):
            with patch("src.api.deps.logger.warning") as mock_log:
                with patch("src.api.deps.get_correlation_id", return_value="xyz789"):
                    mock_credentials = Mock()
                    mock_credentials.credentials = "invalid-token"

                    with pytest.raises(HTTPException):
                        await get_current_user(mock_credentials)

                    # Verify warning logged with correlation ID
                    mock_log.assert_called()
                    log_call_args = str(mock_log.call_args)
                    assert "correlation_id" in log_call_args or "xyz789" in log_call_args


class TestVerifyUserMatch:
    """Test user isolation enforcement in verify_user_match dependency"""

    @pytest.mark.asyncio
    async def test_matching_user_id_returns_user(self):
        """Test matching user_id in JWT and URL returns user"""
        current_user = User(
            id="user_123", email="test@example.com", password_hash="hashed"
        )

        # Should not raise exception
        result = await verify_user_match(user_id="user_123", current_user=current_user)
        assert result == current_user

    @pytest.mark.asyncio
    async def test_mismatched_user_id_raises_403(self):
        """Test user_id mismatch raises 403 Forbidden per user isolation"""
        current_user = User(
            id="user_123", email="test@example.com", password_hash="hashed"
        )

        with pytest.raises(HTTPException) as exc_info:
            await verify_user_match(user_id="user_456", current_user=current_user)

        assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN
        assert "Not authorized" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_user_isolation_logging(self):
        """Test user isolation violation logged with correlation ID"""
        current_user = User(
            id="user_123", email="attacker@example.com", password_hash="hashed"
        )

        with patch("src.api.deps.logger.warning") as mock_log:
            with patch("src.api.deps.get_correlation_id", return_value="iso_123"):
                with pytest.raises(HTTPException):
                    await verify_user_match(user_id="victim_456", current_user=current_user)

                # Verify security warning logged
                mock_log.assert_called()
                log_call = str(mock_log.call_args)
                assert "isolation" in log_call.lower()
                assert "user_123" in log_call  # Attacker ID
                assert "victim_456" in log_call or "user_456" in log_call  # Target ID

    @pytest.mark.asyncio
    async def test_uuid_and_string_id_comparison(self):
        """Test user_id comparison handles both UUID and string types"""
        from uuid import UUID

        current_user = User(
            id="550e8400-e29b-41d4-a716-446655440000",
            email="test@example.com",
            password_hash="hashed",
        )

        # Should match when comparing string to UUID string
        result = await verify_user_match(
            user_id="550e8400-e29b-41d4-a716-446655440000", current_user=current_user
        )
        assert result == current_user

    @pytest.mark.asyncio
    async def test_case_sensitive_id_comparison(self):
        """Test user_id comparison is case-sensitive"""
        current_user = User(id="User_123", email="test@example.com", password_hash="hashed")

        with pytest.raises(HTTPException) as exc_info:
            await verify_user_match(user_id="user_123", current_user=current_user)

        assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN


class TestCorrelationIDExtraction:
    """Test correlation ID extraction from request context"""

    def test_get_correlation_id_from_context(self):
        """Test correlation ID extracted from context variable"""
        with patch("src.api.deps.correlation_id_var.get", return_value="cor_abc123"):
            correlation_id = get_correlation_id()
            assert correlation_id == "cor_abc123"

    def test_get_correlation_id_default_empty(self):
        """Test correlation ID returns empty string when not set"""
        with patch("src.api.deps.correlation_id_var.get", return_value=""):
            correlation_id = get_correlation_id()
            assert correlation_id == ""


class TestJWKSIntegration:
    """Test JWKS verification integration with auth dependencies"""

    @pytest.mark.asyncio
    async def test_jwks_cache_used_for_verification(self):
        """Test JWKS cache is consulted for JWT verification"""
        with patch("src.services.jwks.jwks_cache.get_or_fetch") as mock_cache:
            mock_cache.return_value = {
                "keys": [
                    {
                        "kid": "key-1",
                        "kty": "OKP",
                        "crv": "Ed25519",
                        "x": "test-key",
                    }
                ]
            }

            with patch("jose.jwt.decode") as mock_decode:
                mock_decode.return_value = {"sub": "user_123"}

                with patch("src.api.deps.get_user_by_id") as mock_get_user:
                    mock_user = User(
                        id="user_123", email="test@example.com", password_hash="hashed"
                    )
                    mock_get_user.return_value = mock_user

                    mock_credentials = Mock()
                    mock_credentials.credentials = "jwt-token"

                    await get_current_user(mock_credentials)

                    # Verify JWKS cache was consulted
                    mock_cache.assert_called()

    @pytest.mark.asyncio
    async def test_eddsa_algorithm_enforced_in_deps(self):
        """Test only EdDSA algorithm accepted per betterauth-fastapi-jwt-bridge"""
        with patch("src.api.deps.verify_better_auth_jwt") as mock_verify:
            # Simulate RS256 token (should be rejected)
            mock_verify.side_effect = JWTError("Algorithm not allowed")

            mock_credentials = Mock()
            mock_credentials.credentials = "rs256-token"

            with pytest.raises(HTTPException) as exc_info:
                await get_current_user(mock_credentials)

            assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
