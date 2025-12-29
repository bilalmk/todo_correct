"""Security utilities for password hashing and JWT token handling."""
from datetime import datetime, timedelta, timezone
from uuid import UUID

import jwt
from pwdlib import PasswordHash
from pwdlib.hashers.argon2 import Argon2Hasher

from .config import settings


# Initialize password hasher with argon2
pwd_context = PasswordHash((Argon2Hasher(),))


def hash_password(password: str) -> str:
    """
    Hash password using argon2id algorithm.

    Args:
        password: Plain text password

    Returns:
        Hashed password string

    Example:
        hashed = hash_password("secure_password123")
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify password against hash using constant-time comparison.

    Args:
        plain_password: Plain text password to verify
        hashed_password: Hashed password from database

    Returns:
        True if password matches, False otherwise

    Example:
        if verify_password(input_password, user.password_hash):
            # Password is correct
    """
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(user_id: UUID, email: str) -> str:
    """
    Create JWT access token for authenticated user.

    Args:
        user_id: User's UUID
        email: User's email address

    Returns:
        Encoded JWT token string

    Example:
        token = create_access_token(user.id, user.email)
    """
    expire = datetime.now(timezone.utc) + timedelta(days=settings.JWT_EXPIRATION_DAYS)

    payload = {
        "sub": str(user_id),
        "email": email,
        "exp": expire,
        "iat": datetime.now(timezone.utc),
        "type": "access",
    }

    return jwt.encode(payload, settings.BETTER_AUTH_SECRET, algorithm=settings.JWT_ALGORITHM)


def decode_access_token(token: str) -> dict:
    """
    Decode and validate JWT access token.

    Args:
        token: JWT token string

    Returns:
        Decoded token payload

    Raises:
        jwt.ExpiredSignatureError: If token has expired
        jwt.InvalidTokenError: If token is invalid

    Example:
        try:
            payload = decode_access_token(token)
            user_id = payload["sub"]
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Token expired")
    """
    return jwt.decode(
        token,
        settings.BETTER_AUTH_SECRET,
        algorithms=[settings.JWT_ALGORITHM],
    )


def extract_token_from_header(authorization: str) -> str:
    """
    Extract JWT token from Authorization header.

    Args:
        authorization: Authorization header value (e.g., "Bearer <token>")

    Returns:
        JWT token string

    Raises:
        ValueError: If header format is invalid

    Example:
        token = extract_token_from_header("Bearer eyJ...")
    """
    if not authorization or not authorization.startswith("Bearer "):
        raise ValueError("Invalid authorization header format")

    return authorization.replace("Bearer ", "").strip()
