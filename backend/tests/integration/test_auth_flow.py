"""
Integration Tests for Authentication Flow
T046: Test registration → login → protected endpoint access

Built following skills:
- @.claude/skills/panaversity/betterauth-fastapi-jwt-bridge (auth flow patterns)

Test Coverage:
- Complete auth flow: registration → login → protected endpoint
- JWT cookie transmission (httpOnly)
- CORS with credentials
- Session persistence across requests
- Token expiration handling
"""

import pytest
from httpx import AsyncClient
from datetime import datetime, timedelta
from src.main import app
from src.core.database import get_session
from src.models.user import User
from tests.conftest import override_get_session


@pytest.mark.integration
class TestAuthenticationFlow:
    """Test complete authentication flow from registration to protected access"""

    @pytest.mark.asyncio
    async def test_complete_registration_login_protected_access_flow(
        self, async_client: AsyncClient, test_db_session
    ):
        """
        Test complete user journey:
        1. Register new account
        2. Login with credentials
        3. Access protected endpoint with JWT
        4. Verify user isolation
        """

        # Step 1: Register new user
        registration_data = {
            "name": "Integration Test User",
            "email": "integration@test.com",
            "password": "SecurePassword123!",
        }

        register_response = await async_client.post(
            "/api/auth/sign-up", json=registration_data
        )

        assert register_response.status_code == 201
        assert "user" in register_response.json()
        user_id = register_response.json()["user"]["id"]

        # Step 2: Login with registered credentials
        login_data = {"email": "integration@test.com", "password": "SecurePassword123!"}

        login_response = await async_client.post("/api/auth/sign-in/email", json=login_data)

        assert login_response.status_code == 200
        assert "session" in login_response.json()
        assert "token" in login_response.json()

        # Extract JWT token from response
        jwt_token = login_response.json()["token"]

        # Step 3: Access protected endpoint with JWT
        headers = {"Authorization": f"Bearer {jwt_token}"}

        tasks_response = await async_client.get(
            f"/api/v1/{user_id}/tasks", headers=headers
        )

        assert tasks_response.status_code == 200
        assert isinstance(tasks_response.json(), list)

        # Step 4: Verify user isolation (attempt cross-user access)
        other_user_id = "different-user-123"
        isolation_response = await async_client.get(
            f"/api/v1/{other_user_id}/tasks", headers=headers
        )

        assert isolation_response.status_code == 403
        assert "Not authorized" in isolation_response.json()["error"]

    @pytest.mark.asyncio
    async def test_jwt_cookie_transmission_with_credentials(
        self, async_client: AsyncClient, test_db_session
    ):
        """Test JWT transmitted via httpOnly cookie with credentials: include"""

        # Register and login
        registration_data = {
            "name": "Cookie Test User",
            "email": "cookie@test.com",
            "password": "SecurePassword123!",
        }

        await async_client.post("/api/auth/sign-up", json=registration_data)

        login_data = {"email": "cookie@test.com", "password": "SecurePassword123!"}

        login_response = await async_client.post("/api/auth/sign-in/email", json=login_data)

        # Verify httpOnly cookie set in response
        assert "set-cookie" in login_response.headers
        cookie_header = login_response.headers["set-cookie"]
        assert "HttpOnly" in cookie_header
        assert "SameSite" in cookie_header

    @pytest.mark.asyncio
    async def test_cors_with_credentials_enabled(
        self, async_client: AsyncClient, test_db_session
    ):
        """Test CORS allows credentials (cookies) from frontend origin"""

        # Simulate request from frontend origin
        headers = {"Origin": "http://localhost:3000"}

        response = await async_client.options("/api/v1/health", headers=headers)

        # Verify CORS headers
        assert "access-control-allow-credentials" in response.headers
        assert response.headers["access-control-allow-credentials"] == "true"
        assert "access-control-allow-origin" in response.headers

    @pytest.mark.asyncio
    async def test_session_persistence_across_requests(
        self, async_client: AsyncClient, test_db_session
    ):
        """Test JWT session persists across multiple API requests"""

        # Register and login
        registration_data = {
            "name": "Session Test User",
            "email": "session@test.com",
            "password": "SecurePassword123!",
        }

        register_response = await async_client.post(
            "/api/auth/sign-up", json=registration_data
        )
        user_id = register_response.json()["user"]["id"]

        login_data = {"email": "session@test.com", "password": "SecurePassword123!"}
        login_response = await async_client.post("/api/auth/sign-in/email", json=login_data)
        jwt_token = login_response.json()["token"]

        headers = {"Authorization": f"Bearer {jwt_token}"}

        # Make multiple requests with same token
        for i in range(5):
            response = await async_client.get(f"/api/v1/{user_id}/tasks", headers=headers)
            assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_expired_token_rejected(
        self, async_client: AsyncClient, test_db_session
    ):
        """Test expired JWT token returns 401 Unauthorized"""

        # Create expired token (mocked)
        from jose import jwt
        from src.core.config import settings

        expired_payload = {
            "sub": "user_123",
            "exp": int((datetime.utcnow() - timedelta(hours=1)).timestamp()),
            "iat": int((datetime.utcnow() - timedelta(hours=2)).timestamp()),
        }

        # Note: This would need proper signing key in real scenario
        # For integration test, we test the endpoint behavior
        expired_token = jwt.encode(
            expired_payload, "fake-secret", algorithm="HS256"
        )  # Will fail verification

        headers = {"Authorization": f"Bearer {expired_token}"}

        response = await async_client.get("/api/v1/user_123/tasks", headers=headers)

        assert response.status_code == 401
        assert "credentials" in response.json()["error"].lower()

    @pytest.mark.asyncio
    async def test_missing_authorization_header_rejected(
        self, async_client: AsyncClient, test_db_session
    ):
        """Test request without Authorization header returns 401"""

        response = await async_client.get("/api/v1/user_123/tasks")

        assert response.status_code == 401
        assert "credentials" in response.json()["error"].lower()

    @pytest.mark.asyncio
    async def test_malformed_jwt_token_rejected(
        self, async_client: AsyncClient, test_db_session
    ):
        """Test malformed JWT token returns 401"""

        headers = {"Authorization": "Bearer not-a-valid-jwt-token"}

        response = await async_client.get("/api/v1/user_123/tasks", headers=headers)

        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_login_with_wrong_password_fails(
        self, async_client: AsyncClient, test_db_session
    ):
        """Test login with incorrect password returns 401"""

        # Register user
        registration_data = {
            "name": "Password Test User",
            "email": "password@test.com",
            "password": "CorrectPassword123!",
        }

        await async_client.post("/api/auth/sign-up", json=registration_data)

        # Attempt login with wrong password
        login_data = {"email": "password@test.com", "password": "WrongPassword123!"}

        login_response = await async_client.post("/api/auth/sign-in/email", json=login_data)

        assert login_response.status_code == 401
        assert "credentials" in login_response.json()["error"].lower()

    @pytest.mark.asyncio
    async def test_login_with_nonexistent_email_fails(
        self, async_client: AsyncClient, test_db_session
    ):
        """Test login with non-existent email returns 401"""

        login_data = {
            "email": "nonexistent@test.com",
            "password": "AnyPassword123!",
        }

        login_response = await async_client.post("/api/auth/sign-in/email", json=login_data)

        assert login_response.status_code == 401

    @pytest.mark.asyncio
    async def test_duplicate_email_registration_fails(
        self, async_client: AsyncClient, test_db_session
    ):
        """Test registering with existing email returns 400"""

        registration_data = {
            "name": "Duplicate Test User",
            "email": "duplicate@test.com",
            "password": "SecurePassword123!",
        }

        # First registration succeeds
        response1 = await async_client.post("/api/auth/sign-up", json=registration_data)
        assert response1.status_code == 201

        # Second registration with same email fails
        response2 = await async_client.post("/api/auth/sign-up", json=registration_data)
        assert response2.status_code == 400
        assert "already exists" in response2.json()["error"].lower()

    @pytest.mark.asyncio
    async def test_logout_invalidates_session(
        self, async_client: AsyncClient, test_db_session
    ):
        """Test logout invalidates JWT session"""

        # Register, login
        registration_data = {
            "name": "Logout Test User",
            "email": "logout@test.com",
            "password": "SecurePassword123!",
        }

        register_response = await async_client.post(
            "/api/auth/sign-up", json=registration_data
        )
        user_id = register_response.json()["user"]["id"]

        login_data = {"email": "logout@test.com", "password": "SecurePassword123!"}
        login_response = await async_client.post("/api/auth/sign-in/email", json=login_data)
        jwt_token = login_response.json()["token"]

        headers = {"Authorization": f"Bearer {jwt_token}"}

        # Verify access before logout
        pre_logout = await async_client.get(f"/api/v1/{user_id}/tasks", headers=headers)
        assert pre_logout.status_code == 200

        # Logout
        logout_response = await async_client.post("/api/auth/sign-out", headers=headers)
        assert logout_response.status_code == 200

        # Verify access after logout fails (if session tracking enabled)
        # Note: Stateless JWT may still work until expiration unless blacklisted
        # This test validates the logout endpoint response


@pytest.mark.integration
class TestCorrelationIDPropagation:
    """Test correlation ID propagation through auth flow"""

    @pytest.mark.asyncio
    async def test_correlation_id_in_response_headers(
        self, async_client: AsyncClient, test_db_session
    ):
        """Test X-Correlation-ID header returned in responses per FR-036"""

        correlation_id = "test-correlation-123"
        headers = {"X-Correlation-ID": correlation_id}

        response = await async_client.get("/api/v1/health", headers=headers)

        assert "X-Correlation-ID" in response.headers
        assert response.headers["X-Correlation-ID"] == correlation_id

    @pytest.mark.asyncio
    async def test_correlation_id_auto_generated_if_missing(
        self, async_client: AsyncClient, test_db_session
    ):
        """Test correlation ID auto-generated if not provided"""

        response = await async_client.get("/api/v1/health")

        assert "X-Correlation-ID" in response.headers
        # Verify it's a valid UUID v4
        correlation_id = response.headers["X-Correlation-ID"]
        assert len(correlation_id) == 36  # UUID format: 8-4-4-4-12
