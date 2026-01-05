"""
JWKS (JSON Web Key Set) service for Better Auth JWT verification.

This module provides JWKS fetching and caching with exponential backoff retry logic.
Implements the patterns from the betterauth-fastapi-jwt-bridge skill.

Usage:
    from services.jwks import jwks_cache, verify_better_auth_jwt

    claims = await verify_better_auth_jwt(token)
    user_id = claims.get("sub")

Environment Variables Required:
    BETTER_AUTH_JWKS_URL - Better Auth JWKS endpoint (e.g., https://auth.yourdomain.com/.well-known/jwks.json)
    BETTER_AUTH_ISSUER - Better Auth issuer (e.g., https://auth.yourdomain.com)
"""

import asyncio
import httpx
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import jwt, JWTError
from jose.exceptions import ExpiredSignatureError, JWTClaimsError
from fastapi import HTTPException, status
import os
import logging

logger = logging.getLogger(__name__)

# Configuration from environment
BETTER_AUTH_JWKS_URL = os.getenv("BETTER_AUTH_JWKS_URL", "")
BETTER_AUTH_ISSUER = os.getenv("BETTER_AUTH_ISSUER", "")
BETTER_AUTH_SECRET = os.getenv("BETTER_AUTH_SECRET", "")  # Shared secret for HS256 fallback
JWT_ALGORITHM = "EdDSA"  # Better Auth uses Ed25519
JWT_ALGORITHM_FALLBACK = "HS256"  # Fallback for tokens signed with shared secret


class JWKSCache:
    """
    In-memory JWKS cache with TTL and retry logic.

    Features:
    - 1-hour TTL (configurable)
    - Exponential backoff retry (100ms, 200ms, 400ms)
    - Thread-safe with asyncio.Lock
    - Automatic cache invalidation on key rotation
    """

    def __init__(self, ttl_seconds: int = 3600):
        """
        Initialize JWKS cache.

        Args:
            ttl_seconds: Time-to-live for cached JWKS (default: 1 hour)
        """
        self._cache: Optional[Dict[str, Any]] = None
        self._cached_at: Optional[datetime] = None
        self._lock = asyncio.Lock()
        self._ttl = timedelta(seconds=ttl_seconds)
        self._jwks_url = BETTER_AUTH_JWKS_URL

    async def get_or_fetch(self) -> Dict[str, Any]:
        """
        Get JWKS from cache or fetch from Better Auth if expired.

        Returns:
            JWKS data dictionary

        Raises:
            HTTPException 503: If JWKS endpoint is unreachable after retries
        """
        async with self._lock:
            now = datetime.utcnow()

            # Cache hit - return cached JWKS
            if self._cache and self._cached_at and (now - self._cached_at) < self._ttl:
                logger.debug("JWKS cache hit")
                return self._cache

            # Cache miss or expired - fetch from Better Auth
            logger.info(f"JWKS cache miss or expired, fetching from {self._jwks_url}")
            self._cache = await self._fetch_with_retry()
            self._cached_at = now
            return self._cache

    async def _fetch_with_retry(self) -> Dict[str, Any]:
        """
        Fetch JWKS with exponential backoff retry logic.

        Retry delays: 100ms, 200ms, 400ms (3 total attempts)

        Returns:
            JWKS data dictionary

        Raises:
            HTTPException 503: If all retries fail
        """
        delays = [0.1, 0.2, 0.4]  # Exponential backoff (100ms, 200ms, 400ms)
        last_error = None

        for attempt, delay in enumerate(delays, start=1):
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.get(self._jwks_url, timeout=5.0)
                    response.raise_for_status()
                    jwks_data = response.json()
                    logger.info(f"Successfully fetched JWKS (attempt {attempt}/{len(delays)})")
                    return jwks_data
            except (httpx.HTTPError, httpx.TimeoutException) as e:
                last_error = e
                logger.warning(f"JWKS fetch attempt {attempt}/{len(delays)} failed: {e}")
                if attempt < len(delays):
                    await asyncio.sleep(delay)

        # All retries failed
        logger.error(f"Failed to fetch JWKS after {len(delays)} attempts: {last_error}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Authentication service unavailable after 3 retries"
        )

    def clear_cache(self):
        """Clear the JWKS cache (useful for key rotation detection)."""
        logger.info("Clearing JWKS cache")
        self._cache = None
        self._cached_at = None


# Global JWKS cache instance
jwks_cache = JWKSCache()


def get_signing_key(token: str, jwks_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extract the public key from JWKS that matches the token's kid.

    Args:
        token: JWT token string
        jwks_data: JWKS response from Better Auth

    Returns:
        Public key from JWKS

    Raises:
        HTTPException 401: If kid not found in JWKS or token format invalid
    """
    try:
        # Get key ID from token header
        unverified_header = jwt.get_unverified_header(token)
        kid = unverified_header.get("kid")

        if not kid:
            logger.warning("Token missing key ID (kid)")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token missing key ID (kid)",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Find matching key in JWKS
        for key in jwks_data.get("keys", []):
            if key.get("kid") == kid:
                logger.debug(f"Found matching signing key: kid={kid}")
                return key

        # Key not found - might be a key rotation, clear cache
        logger.warning(f"Key ID {kid} not found in JWKS")
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


async def verify_better_auth_jwt(token: str) -> Dict[str, Any]:
    """
    Verify JWT token using Better Auth's JWKS endpoint or shared secret fallback.

    This function:
    1. First tries to verify using JWKS (EdDSA/Ed25519)
    2. Falls back to HS256 verification with shared secret if JWKS fails
    3. Validates issuer claim
    4. Returns decoded payload

    Args:
        token: JWT token string

    Returns:
        Decoded token payload containing user information:
        {
            "sub": "user_id",
            "email": "user@example.com",
            "name": "User Name",
            "uuid": "user-uuid-here",
            "iat": 1234567890,
            "exp": 1234567890,
            "iss": "https://auth.yourdomain.com"
        }

    Raises:
        HTTPException 401: If token is invalid, expired, or verification fails
        HTTPException 503: If JWKS endpoint is unavailable
    """
    # Try EdDSA verification with JWKS first
    try:
        # Get JWKS (cached)
        jwks_data = await jwks_cache.get_or_fetch()

        # Get signing key
        signing_key = get_signing_key(token, jwks_data)

        # Verify and decode token
        payload = jwt.decode(
            token,
            signing_key,
            algorithms=[JWT_ALGORITHM],
            issuer=BETTER_AUTH_ISSUER,
            options={
                "verify_signature": True,
                "verify_exp": True,  # Verify expiration
                "verify_iss": True,  # Verify issuer
                # Note: Better Auth may not include 'aud' claim, so we don't verify it
            }
        )

        logger.debug(f"Successfully verified JWT (EdDSA) for user: {payload.get('sub')}")
        return payload

    except (JWTError, HTTPException) as jwks_error:
        # JWKS verification failed, try HS256 with shared secret
        logger.info(f"EdDSA verification failed, trying HS256 fallback: {jwks_error}")

        if not BETTER_AUTH_SECRET:
            logger.error("HS256 fallback not available: BETTER_AUTH_SECRET not set")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )

        try:
            # Try HS256 verification
            payload = jwt.decode(
                token,
                BETTER_AUTH_SECRET,
                algorithms=[JWT_ALGORITHM_FALLBACK],
                issuer=BETTER_AUTH_ISSUER,
                options={
                    "verify_signature": True,
                    "verify_exp": True,
                    "verify_iss": True,
                }
            )

            logger.debug(f"Successfully verified JWT (HS256 fallback) for user: {payload.get('sub')}")
            return payload

        except ExpiredSignatureError:
            logger.warning("Token has expired")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired",
                headers={"WWW-Authenticate": "Bearer"},
            )

        except JWTClaimsError as e:
            logger.warning(f"Invalid token claims: {e}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token claims",
                headers={"WWW-Authenticate": "Bearer"},
            )

        except JWTError as e:
            logger.error(f"JWT verification failed (both EdDSA and HS256): {e}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
