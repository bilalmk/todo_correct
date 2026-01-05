"""
Unit Tests for JWKS Service
T044: Test JWKS cache, TTL expiration, retry logic, EdDSA signature validation

Built following skills:
- @.claude/skills/panaversity/betterauth-fastapi-jwt-bridge (security test patterns)

Test Coverage:
- Cache hit/miss behavior
- TTL expiration (1-hour cache)
- Retry logic with exponential backoff (100ms, 200ms, 400ms)
- EdDSA/Ed25519 signature validation
- JWKS endpoint failures
- Invalid JWT token handling
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, AsyncMock
from jose import jwt, JWTError
from src.services.jwks import (
    JWKSCache,
    verify_better_auth_jwt,
    BETTER_AUTH_JWKS_URL,
    BETTER_AUTH_ISSUER,
)


class TestJWKSCache:
    """Test JWKS caching behavior per betterauth-fastapi-jwt-bridge patterns"""

    @pytest.mark.asyncio
    async def test_cache_miss_on_first_fetch(self):
        """Test cache miss triggers JWKS fetch on first call"""
        cache = JWKSCache(ttl_seconds=3600)

        # First call should be cache miss
        assert cache._cache is None
        assert cache._cached_at is None

        with patch("httpx.AsyncClient.get") as mock_get:
            mock_response = Mock()
            mock_response.json.return_value = {"keys": [{"kid": "test-key"}]}
            mock_response.raise_for_status = Mock()
            mock_get.return_value = mock_response

            result = await cache.get_or_fetch()

            # Verify fetch was called
            mock_get.assert_called_once()
            assert result == {"keys": [{"kid": "test-key"}]}
            assert cache._cache is not None
            assert cache._cached_at is not None

    @pytest.mark.asyncio
    async def test_cache_hit_within_ttl(self):
        """Test cache hit returns cached data without fetching"""
        cache = JWKSCache(ttl_seconds=3600)

        # Populate cache
        cache._cache = {"keys": [{"kid": "cached-key"}]}
        cache._cached_at = datetime.utcnow()

        with patch("httpx.AsyncClient.get") as mock_get:
            result = await cache.get_or_fetch()

            # Verify no fetch occurred
            mock_get.assert_not_called()
            assert result == {"keys": [{"kid": "cached-key"}]}

    @pytest.mark.asyncio
    async def test_cache_expires_after_ttl(self):
        """Test cache expires after TTL (1 hour default) and re-fetches"""
        cache = JWKSCache(ttl_seconds=10)  # 10 seconds for testing

        # Set cache as expired (11 seconds old)
        cache._cache = {"keys": [{"kid": "old-key"}]}
        cache._cached_at = datetime.utcnow() - timedelta(seconds=11)

        with patch("httpx.AsyncClient.get") as mock_get:
            mock_response = Mock()
            mock_response.json.return_value = {"keys": [{"kid": "new-key"}]}
            mock_response.raise_for_status = Mock()
            mock_get.return_value = mock_response

            result = await cache.get_or_fetch()

            # Verify re-fetch occurred
            mock_get.assert_called_once()
            assert result == {"keys": [{"kid": "new-key"}]}
            assert cache._cache["keys"][0]["kid"] == "new-key"

    @pytest.mark.asyncio
    async def test_retry_logic_with_exponential_backoff(self):
        """Test exponential backoff: 100ms, 200ms, 400ms on failures"""
        cache = JWKSCache(ttl_seconds=3600)

        call_times = []

        async def mock_failing_get(*args, **kwargs):
            call_times.append(datetime.utcnow())
            raise Exception("Network error")

        with patch("httpx.AsyncClient.get", side_effect=mock_failing_get):
            with pytest.raises(Exception, match="Network error"):
                await cache._fetch_with_retry()

        # Verify 3 retry attempts occurred
        assert len(call_times) == 3

        # Verify exponential backoff delays (with tolerance for timing jitter)
        if len(call_times) >= 2:
            delay1 = (call_times[1] - call_times[0]).total_seconds()
            assert 0.08 <= delay1 <= 0.15  # ~100ms ± tolerance

        if len(call_times) >= 3:
            delay2 = (call_times[2] - call_times[1]).total_seconds()
            assert 0.15 <= delay2 <= 0.25  # ~200ms ± tolerance

    @pytest.mark.asyncio
    async def test_concurrent_fetch_uses_lock(self):
        """Test concurrent requests don't trigger duplicate fetches"""
        cache = JWKSCache(ttl_seconds=3600)

        fetch_count = 0

        async def mock_slow_fetch(*args, **kwargs):
            nonlocal fetch_count
            fetch_count += 1
            await asyncio.sleep(0.1)  # Simulate slow network
            response = Mock()
            response.json.return_value = {"keys": [{"kid": "key"}]}
            response.raise_for_status = Mock()
            return response

        with patch("httpx.AsyncClient.get", side_effect=mock_slow_fetch):
            # Trigger 5 concurrent fetches
            results = await asyncio.gather(*[cache.get_or_fetch() for _ in range(5)])

            # Verify only 1 fetch occurred (lock prevented duplicates)
            assert fetch_count == 1
            assert all(r == results[0] for r in results)


class TestJWTVerification:
    """Test JWT verification with EdDSA algorithm"""

    @pytest.fixture
    def mock_jwks_cache(self):
        """Mock JWKS cache with test keys"""
        with patch("src.services.jwks.jwks_cache") as mock_cache:
            mock_cache.get_or_fetch = AsyncMock(
                return_value={
                    "keys": [
                        {
                            "kid": "test-key-1",
                            "kty": "OKP",
                            "crv": "Ed25519",
                            "x": "test-public-key-base64",
                        }
                    ]
                }
            )
            yield mock_cache

    @pytest.mark.asyncio
    async def test_valid_jwt_token_verification(self, mock_jwks_cache):
        """Test valid JWT token with EdDSA signature verifies successfully"""
        # Mock JWT decode to simulate successful verification
        with patch("jose.jwt.decode") as mock_decode:
            mock_decode.return_value = {
                "sub": "user_123",
                "email": "test@example.com",
                "iat": int(datetime.utcnow().timestamp()),
                "exp": int((datetime.utcnow() + timedelta(hours=1)).timestamp()),
            }

            token = "eyJhbGciOiJFZERTQSIsImtpZCI6InRlc3Qta2V5LTEifQ..."
            result = await verify_better_auth_jwt(token)

            assert result["sub"] == "user_123"
            assert result["email"] == "test@example.com"
            mock_decode.assert_called_once()

    @pytest.mark.asyncio
    async def test_expired_token_raises_error(self, mock_jwks_cache):
        """Test expired JWT token raises JWTError"""
        with patch("jose.jwt.decode", side_effect=JWTError("Token has expired")):
            token = "eyJhbGciOiJFZERTQSIsImtpZCI6InRlc3Qta2V5LTEifQ..."

            with pytest.raises(JWTError, match="Token has expired"):
                await verify_better_auth_jwt(token)

    @pytest.mark.asyncio
    async def test_tampered_token_raises_error(self, mock_jwks_cache):
        """Test tampered JWT token (invalid signature) raises JWTError"""
        with patch("jose.jwt.decode", side_effect=JWTError("Invalid signature")):
            token = "eyJhbGciOiJFZERTQSIsImtpZCI6InRlc3Qta2V5LTEifQ.tampered..."

            with pytest.raises(JWTError, match="Invalid signature"):
                await verify_better_auth_jwt(token)

    @pytest.mark.asyncio
    async def test_missing_kid_raises_error(self):
        """Test JWT without kid (key ID) raises ValueError"""
        token = "eyJhbGciOiJFZERTQSJ9..."  # Missing kid in header

        with pytest.raises(ValueError, match="kid"):
            await verify_better_auth_jwt(token)

    @pytest.mark.asyncio
    async def test_unknown_kid_raises_error(self, mock_jwks_cache):
        """Test JWT with unknown kid raises ValueError"""
        # Mock JWKS with different key ID
        mock_jwks_cache.get_or_fetch.return_value = {
            "keys": [{"kid": "different-key"}]
        }

        token = "eyJhbGciOiJFZERTQSIsImtpZCI6InVua25vd24ta2V5In0..."

        with pytest.raises(ValueError, match="Unable to find matching signing key"):
            await verify_better_auth_jwt(token)

    @pytest.mark.asyncio
    async def test_wrong_issuer_raises_error(self, mock_jwks_cache):
        """Test JWT with wrong issuer claim raises JWTError"""
        with patch("jose.jwt.decode", side_effect=JWTError("Invalid issuer")):
            token = "eyJhbGciOiJFZERTQSIsImtpZCI6InRlc3Qta2V5LTEifQ..."

            with pytest.raises(JWTError, match="Invalid issuer"):
                await verify_better_auth_jwt(token)

    @pytest.mark.asyncio
    async def test_eddsa_algorithm_enforced(self, mock_jwks_cache):
        """Test only EdDSA algorithm is accepted per betterauth-fastapi-jwt-bridge"""
        with patch("jose.jwt.decode") as mock_decode:
            mock_decode.return_value = {"sub": "user_123"}

            token = "eyJhbGciOiJFZERTQSIsImtpZCI6InRlc3Qta2V5LTEifQ..."
            await verify_better_auth_jwt(token)

            # Verify EdDSA algorithm was specified
            call_kwargs = mock_decode.call_args.kwargs
            assert call_kwargs["algorithms"] == ["EdDSA"]


class TestPerformance:
    """Test JWKS cache performance metrics"""

    @pytest.mark.asyncio
    async def test_cache_hit_rate_above_95_percent(self):
        """Test cache hit rate >95% per SC-007 success criteria"""
        cache = JWKSCache(ttl_seconds=3600)

        # Pre-populate cache
        cache._cache = {"keys": [{"kid": "test-key"}]}
        cache._cached_at = datetime.utcnow()

        hits = 0
        total_requests = 100

        with patch("httpx.AsyncClient.get") as mock_get:
            for _ in range(total_requests):
                await cache.get_or_fetch()
                if not mock_get.called:
                    hits += 1

        hit_rate = hits / total_requests
        assert hit_rate >= 0.95, f"Cache hit rate {hit_rate:.2%} below 95%"

    @pytest.mark.asyncio
    async def test_warm_cache_verification_under_50ms(self, mock_jwks_cache):
        """Test JWT verification p95 <50ms with warm cache per SC-003"""
        import time

        latencies = []

        with patch("jose.jwt.decode") as mock_decode:
            mock_decode.return_value = {"sub": "user_123"}

            for _ in range(100):
                start = time.perf_counter()
                await verify_better_auth_jwt("test-token")
                latency_ms = (time.perf_counter() - start) * 1000
                latencies.append(latency_ms)

        latencies.sort()
        p95_latency = latencies[94]  # 95th percentile

        assert (
            p95_latency < 50
        ), f"P95 latency {p95_latency:.2f}ms exceeds 50ms threshold"
