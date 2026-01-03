"""
JWT verification using Better Auth JWKS endpoint.

This module provides complete JWT token verification for FastAPI applications
integrating with Better Auth.

Usage:
    Copy this file to: backend/app/auth/jwt_verification.py

Environment Variables Required:
    BETTER_AUTH_URL - Better Auth base URL (e.g., http://localhost:3000)
"""

from fastapi import HTTPException, status
from jose import jwt, JWTError
from functools import lru_cache
from typing import Dict, Any
import httpx
import os
import logging

logger = logging.getLogger(__name__)

# Configuration from environment
BETTER_AUTH_URL = os.getenv("BETTER_AUTH_URL", "http://localhost:3000")
JWKS_URL = f"{BETTER_AUTH_URL}/api/auth/jwks"
JWT_ALGORITHM = "EdDSA"  # Better Auth uses Ed25519
JWT_AUDIENCE = BETTER_AUTH_URL
JWT_ISSUER = BETTER_AUTH_URL


@lru_cache(maxsize=1)
def get_jwks() -> Dict[str, Any]:
    """
    Fetch JWKS from Better Auth endpoint.

    This is cached because:
    1. Public keys don't change frequently
    2. Reduces network calls
    3. Better Auth documentation recommends caching

    Cache is invalidated if we encounter a token with unknown kid.

    Returns:
        JWKS data dictionary

    Raises:
        HTTPException 503: If JWKS endpoint is unreachable
    """
    try:
        response = httpx.get(JWKS_URL, timeout=5.0)
        response.raise_for_status()
        jwks_data = response.json()
        logger.info(f"Fetched JWKS from {JWKS_URL}")
        return jwks_data
    except httpx.HTTPError as e:
        logger.error(f"Failed to fetch JWKS from {JWKS_URL}: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Unable to fetch authentication keys",
        )


def get_signing_key(token: str, jwks_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extract the public key from JWKS that matches the token's kid.

    Args:
        token: JWT token string
        jwks_data: JWKS response from Better Auth

    Returns:
        Public key from JWKS

    Raises:
        HTTPException: If kid not found in JWKS
    """
    try:
        # Get key ID from token header
        unverified_header = jwt.get_unverified_header(token)
        kid = unverified_header.get("kid")

        if not kid:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token missing key ID (kid)",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Find matching key in JWKS
        for key in jwks_data.get("keys", []):
            if key.get("kid") == kid:
                return key

        # Key not found - invalidate cache and retry once
        logger.warning(f"Key ID {kid} not found in cached JWKS, refreshing cache")
        get_jwks.cache_clear()
        jwks_data = get_jwks()

        for key in jwks_data.get("keys", []):
            if key.get("kid") == kid:
                return key

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unable to find matching signing key",
            headers={"WWW-Authenticate": "Bearer"},
        )

    except JWTError as e:
        logger.error(f"Error extracting key from token: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token format",
            headers={"WWW-Authenticate": "Bearer"},
        )


def verify_jwt_token(token: str) -> Dict[str, Any]:
    """
    Verify JWT token using Better Auth's JWKS endpoint.

    This function:
    1. Fetches JWKS (cached)
    2. Extracts kid from token header
    3. Finds matching public key
    4. Verifies token signature
    5. Validates issuer and audience
    6. Returns decoded payload

    Args:
        token: JWT token string

    Returns:
        Decoded token payload containing user information

    Raises:
        HTTPException: If token is invalid, expired, or verification fails
    """
    try:
        # Get JWKS (cached)
        jwks_data = get_jwks()

        # Get signing key
        signing_key = get_signing_key(token, jwks_data)

        # Verify and decode token
        payload = jwt.decode(
            token,
            signing_key,
            algorithms=[JWT_ALGORITHM],
            audience=JWT_AUDIENCE,
            issuer=JWT_ISSUER,
            options={
                "verify_signature": True,
                "verify_exp": True,  # Verify expiration
                "verify_aud": True,  # Verify audience
                "verify_iss": True,  # Verify issuer
            }
        )

        logger.debug(f"Successfully verified token for user: {payload.get('sub')}")
        return payload

    except jwt.ExpiredSignatureError:
        logger.warning("Token has expired")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.JWTClaimsError as e:
        logger.warning(f"Invalid token claims: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token claims",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except JWTError as e:
        logger.error(f"JWT verification failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


def extract_user_from_payload(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extract user information from JWT payload.

    JWT payload structure from Better Auth (with UUID integration):
    {
        "sub": "user_abc123",              # Better Auth String ID
        "uuid": "a1b2c3d4-e5f6-...",      # Application UUID (custom claim) ⭐
        "email": "user@example.com",
        "name": "User Name",
        "iat": 1234567890,
        "exp": 1234567890,
        "iss": "http://localhost:3000",
        "aud": "http://localhost:3000"
    }

    Args:
        payload: Decoded JWT payload

    Returns:
        User information dictionary with both String ID and UUID

    Raises:
        HTTPException: If required claims are missing
    """
    user_id = payload.get("sub")
    user_uuid = payload.get("uuid")

    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token missing user ID (sub claim)",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user_uuid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token missing UUID (uuid claim)",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return {
        "user_id": user_id,     # Better Auth String ID
        "uuid": user_uuid,      # Application UUID ⭐
        "email": payload.get("email"),
        "name": payload.get("name"),
        "payload": payload,     # Include full payload for advanced use cases
    }
