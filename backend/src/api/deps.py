"""FastAPI dependencies for request handling."""
from typing import Optional, Dict, Any
from uuid import UUID
import logging

import jwt
from fastapi import Depends, HTTPException, Path, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlmodel.ext.asyncio.session import AsyncSession

from ..core.database import get_session
from ..core.logging import get_correlation_id
from ..services.jwks import verify_better_auth_jwt
from ..models.user import User
from ..services.user import get_user_by_id

logger = logging.getLogger(__name__)


# HTTP Bearer token security scheme
security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    session: AsyncSession = Depends(get_session),
) -> User:
    """
    Get current authenticated user from Better Auth JWT token.

    T008: Updated to use Better Auth JWKS verification.
    T020: Updated to extract UUID from JWT payload (custom claim).

    This function:
    1. Verifies JWT signature using Better Auth JWKS endpoint
    2. Validates token claims (exp, iss)
    3. Extracts uuid from JWT custom claim (not 'sub')
    4. Fetches user from Better Auth user table by UUID
    5. Logs validation events with correlation IDs (FR-032-033)

    Args:
        credentials: HTTP Bearer token from Authorization header
        session: Database session

    Returns:
        Authenticated user from Better Auth user table

    Raises:
        HTTPException: 401 if token is invalid or user not found

    Example:
        @app.get("/protected")
        async def protected_route(user: User = Depends(get_current_user)):
            return {"user_uuid": user.uuid}
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        # Verify JWT token using Better Auth JWKS (T008)
        payload = await verify_better_auth_jwt(credentials.credentials)

        # T020: Extract UUID from custom claim (not 'sub')
        user_uuid_str: Optional[str] = payload.get("uuid")

        if user_uuid_str is None:
            logger.warning(
                "JWT token missing 'uuid' claim",
                extra={
                    "correlation_id": get_correlation_id(),
                    "error_message": "Token missing UUID claim (custom claim)"
                }
            )
            raise credentials_exception

        user_uuid = UUID(user_uuid_str)

        # Log successful JWT validation (FR-032)
        logger.info(
            f"JWT validated successfully for user UUID {user_uuid}",
            extra={
                "user_uuid": str(user_uuid),
                "correlation_id": get_correlation_id(),
            }
        )

    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError, ValueError) as e:
        # Log JWT validation failure (FR-033)
        logger.warning(
            f"JWT validation failed: {str(e)}",
            extra={
                "correlation_id": get_correlation_id(),
                "error_message": str(e)
            }
        )
        raise credentials_exception

    # T020: Fetch user from Better Auth user table by UUID
    from sqlmodel import select
    result = await session.execute(
        select(User).where(User.uuid == user_uuid)
    )
    user = result.scalar_one_or_none()

    if user is None:
        logger.warning(
            f"User with UUID {user_uuid} not found in database",
            extra={
                "user_uuid": str(user_uuid),
                "correlation_id": get_correlation_id(),
            }
        )
        raise credentials_exception

    return user


async def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False)),
    session: AsyncSession = Depends(get_session),
) -> Optional[User]:
    """
    Get current user if authenticated, None otherwise.

    T008: Updated to use Better Auth JWKS verification.
    T020: Updated to extract UUID from JWT payload.

    Useful for endpoints that have optional authentication.

    Args:
        credentials: Optional HTTP Bearer token
        session: Database session

    Returns:
        User if authenticated, None otherwise
    """
    if credentials is None:
        return None

    try:
        # Verify JWT token using Better Auth JWKS (T008)
        payload = await verify_better_auth_jwt(credentials.credentials)

        # T020: Extract UUID from custom claim
        user_uuid_str: Optional[str] = payload.get("uuid")

        if user_uuid_str is None:
            return None

        user_uuid = UUID(user_uuid_str)

        # T020: Fetch user from Better Auth user table by UUID
        from sqlmodel import select
        result = await session.execute(
            select(User).where(User.uuid == user_uuid)
        )
        return result.scalar_one_or_none()

    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError, ValueError):
        return None


async def verify_user_match(
    current_user: User = Depends(get_current_user),
    user_id: UUID = Path(..., description="User UUID from URL path"),
) -> User:
    """
    Verify that the authenticated user's UUID matches the URL path user_id.

    T014: Updated with user isolation enforcement and security logging.
    T020: Updated to compare UUID instead of Better Auth String ID.

    This dependency ensures authorization by preventing users from accessing
    other users' resources via URL manipulation (per security-checklist.md).

    Args:
        current_user: Authenticated user from JWT token
        user_id: User UUID from URL path parameter

    Returns:
        The authenticated user if match is successful

    Raises:
        HTTPException: 403 Forbidden if user_id mismatch

    Example:
        @app.get("/api/v1/{user_id}/tasks")
        async def list_tasks(user: User = Depends(verify_user_match)):
            # user.uuid is guaranteed to match URL user_id
            pass
    """
    # T020: Verify JWT user UUID matches URL {user_id} parameter
    if current_user.uuid != user_id:
        # Log security violation (attempted cross-user access)
        logger.warning(
            f"User isolation violation: User {current_user.uuid} attempted to access resources for user {user_id}",
            extra={
                "authenticated_user_uuid": str(current_user.uuid),
                "requested_user_uuid": str(user_id),
                "correlation_id": get_correlation_id(),
                "error_message": "Cross-user access attempt blocked"
            }
        )

        # Return 403 Forbidden per security-checklist.md (section 3: User Isolation)
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this user's resources",
        )

    # Log successful user isolation check (optional, for audit trail)
    logger.debug(
        f"User isolation check passed for user {current_user.uuid}",
        extra={
            "user_uuid": str(current_user.uuid),
            "correlation_id": get_correlation_id(),
        }
    )

    return current_user
