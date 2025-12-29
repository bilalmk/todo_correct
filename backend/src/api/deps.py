"""FastAPI dependencies for request handling."""
from typing import Optional
from uuid import UUID

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlmodel.ext.asyncio.session import AsyncSession

from ..core.database import get_session
from ..core.security import decode_access_token
from ..models.user import User
from ..services.user import get_user_by_id


# HTTP Bearer token security scheme
security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    session: AsyncSession = Depends(get_session),
) -> User:
    """
    Get current authenticated user from JWT token.

    Args:
        credentials: HTTP Bearer token from Authorization header
        session: Database session

    Returns:
        Authenticated user

    Raises:
        HTTPException: 401 if token is invalid or user not found

    Example:
        @app.get("/protected")
        async def protected_route(user: User = Depends(get_current_user)):
            return {"user_id": user.id}
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        # Decode JWT token
        payload = decode_access_token(credentials.credentials)
        user_id_str: Optional[str] = payload.get("sub")

        if user_id_str is None:
            raise credentials_exception

        user_id = UUID(user_id_str)

    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError, ValueError):
        raise credentials_exception

    # Fetch user from database
    user = await get_user_by_id(session, user_id)

    if user is None:
        raise credentials_exception

    return user


async def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False)),
    session: AsyncSession = Depends(get_session),
) -> Optional[User]:
    """
    Get current user if authenticated, None otherwise.

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
        payload = decode_access_token(credentials.credentials)
        user_id_str: Optional[str] = payload.get("sub")

        if user_id_str is None:
            return None

        user_id = UUID(user_id_str)
        user = await get_user_by_id(session, user_id)
        return user

    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError, ValueError):
        return None
