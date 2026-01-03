"""
FastAPI dependencies for authentication with Better Auth UUID integration.

This module provides FastAPI dependencies for JWT authentication and user authorization.
Updated to support Better Auth hybrid ID approach (String ID + UUID).

Usage:
    Copy this file to: backend/app/auth/dependencies.py

Example:
    from app.auth.dependencies import get_current_user, verify_user_access
    from uuid import UUID

    @router.get("/protected")
    async def protected_route(user: dict = Depends(get_current_user)):
        return {"user_uuid": user["uuid"]}  # Use UUID

    @router.get("/{user_id}/tasks")
    async def get_tasks(
        user_id: UUID,  # UUID in path
        user: dict = Depends(verify_user_access)
    ):
        # user_id is guaranteed to match authenticated user's UUID
        return get_user_tasks(user_id)
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from typing import Dict, Any
from uuid import UUID
from .jwt_verification import verify_jwt_token, extract_user_from_payload

# OAuth2 scheme for Swagger UI
# This tells FastAPI to look for the token in the Authorization header
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="token",
    description="JWT token from Better Auth"
)


async def get_current_user(token: str = Depends(oauth2_scheme)) -> Dict[str, Any]:
    """
    FastAPI dependency to get the current authenticated user.

    This dependency:
    1. Extracts JWT token from Authorization header
    2. Verifies token signature using JWKS
    3. Validates token claims (exp, iss, aud)
    4. Returns user information from token payload

    Usage:
        @app.get("/protected")
        async def protected_route(user: dict = Depends(get_current_user)):
            return {"user_id": user["user_id"]}

    Args:
        token: JWT token from Authorization header (injected by FastAPI)

    Returns:
        User information dictionary:
        {
            "user_id": "user_abc123",          # Better Auth String ID (from 'sub')
            "uuid": "a1b2c3d4-e5f6-...",      # Application UUID (from 'uuid' claim) ⭐
            "email": "user@example.com",
            "name": "User Name",
            "payload": {...}  # Full JWT payload
        }

    Raises:
        HTTPException 401: If token is invalid, expired, or missing
    """
    # Verify token using JWKS
    payload = verify_jwt_token(token)

    # Extract user information
    user = extract_user_from_payload(payload)

    return user


async def verify_user_access(
    user_id: UUID,
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Verify that the authenticated user's UUID matches the requested user_id.

    This prevents users from accessing other users' data by checking that
    the UUID in the URL path matches the UUID from the JWT token.

    Updated for Better Auth UUID integration: Compares UUID (not String ID).

    Usage:
        @app.get("/api/v1/{user_id}/tasks")
        async def get_tasks(
            user_id: UUID,  # UUID from URL path
            user: dict = Depends(verify_user_access)
        ):
            # If we reach here, user_id is guaranteed to match authenticated user's UUID
            return db.query(Task).filter(Task.user_id == user_id).all()

    Args:
        user_id: User UUID from URL path parameter
        current_user: Current authenticated user from JWT (injected by get_current_user)

    Returns:
        User information if access is granted

    Raises:
        HTTPException 403: If user tries to access another user's resources
    """
    # Compare UUIDs (not String IDs)
    current_user_uuid = UUID(current_user["uuid"])
    if current_user_uuid != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this user's resources",
        )

    return current_user


async def get_current_active_user(
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Get the current active user (with additional active/disabled check).

    Extend this function if you have a user status in your database.

    Usage:
        @app.get("/users/me")
        async def read_users_me(user: dict = Depends(get_current_active_user)):
            return user

    Args:
        current_user: Current authenticated user from JWT

    Returns:
        User information if user is active

    Raises:
        HTTPException 400: If user is disabled (if you implement this check)
    """
    # Example: Check if user is disabled in your database
    # from app.database import get_db
    # user_in_db = db.query(User).filter(User.id == current_user["user_id"]).first()
    # if user_in_db and user_in_db.disabled:
    #     raise HTTPException(status_code=400, detail="Inactive user")

    return current_user


async def require_admin(
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Require admin role for the current user.

    Extend this function if you have role-based access control (RBAC).

    Usage:
        @app.delete("/admin/users/{user_id}")
        async def delete_user(
            user_id: str,
            admin: dict = Depends(require_admin)
        ):
            # Only admins can reach this endpoint
            delete_user_from_db(user_id)

    Args:
        current_user: Current authenticated user from JWT

    Returns:
        User information if user is admin

    Raises:
        HTTPException 403: If user is not an admin
    """
    # Example: Check if user has admin role
    # This depends on how you implement roles in your system
    # Option 1: Role in JWT payload
    # user_role = current_user["payload"].get("role")
    # if user_role != "admin":
    #     raise HTTPException(status_code=403, detail="Admin access required")

    # Option 2: Role in database
    # from app.database import get_db
    # user_in_db = db.query(User).filter(User.id == current_user["user_id"]).first()
    # if not user_in_db or not user_in_db.is_admin:
    #     raise HTTPException(status_code=403, detail="Admin access required")

    # For now, return user (customize based on your role implementation)
    return current_user
