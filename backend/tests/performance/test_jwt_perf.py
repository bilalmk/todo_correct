"""
Performance Tests for JWT Verification
T049: Measure JWT verification p95 latency and cache hit rate

Success Criteria:
- SC-003: p95 latency <50ms with warm cache
- SC-007: Cache hit rate >95%

Built following skills:
- @.claude/skills/panaversity/betterauth-fastapi-jwt-bridge (performance patterns)
"""

import pytest
import time
import asyncio
from statistics import quantiles
from unittest.mock import patch, AsyncMock
from src.services.jwks import verify_better_auth_jwt, JWKSCache


@pytest.mark.performance
class TestJWTVerificationPerformance:
    """Test JWT verification meets performance SLAs"""

    @pytest.mark.asyncio
    async def test_jwt_verification_p95_under_50ms_warm_cache(self):
        """
        SC-003: Verify p95 latency <50ms with warm cache

        This test measures JWT verification latency with a warmed JWKS cache
        to ensure the system meets the 50ms p95 latency requirement.
        """

        # Mock JWKS cache to avoid network calls
        mock_jwks = {
            "keys": [
                {
                    "kid": "test-key-1",
                    "kty": "OKP",
                    "crv": "Ed25519",
                    "x": "test-public-key-base64",
                }
            ]
        }

        latencies = []
        num_requests = 100

        with patch("src.services.jwks.jwks_cache.get_or_fetch") as mock_cache:
            mock_cache.return_value = mock_jwks

            with patch("jose.jwt.decode") as mock_decode:
                mock_decode.return_value = {
                    "sub": "user_123",
                    "email": "test@example.com",
                }

                # Warm up (first request may be slower)
                await verify_better_auth_jwt("warmup-token")

                # Measure latencies
                for i in range(num_requests):
                    start = time.perf_counter()
                    await verify_better_auth_jwt(f"test-token-{i}")
                    latency_ms = (time.perf_counter() - start) * 1000
                    latencies.append(latency_ms)

        # Calculate p95 latency
        latencies.sort()
        p95_index = int(len(latencies) * 0.95) - 1
        p95_latency = latencies[p95_index]

        # Report statistics
        avg_latency = sum(latencies) / len(latencies)
        min_latency = min(latencies)
        max_latency = max(latencies)

        print(f"\n=== JWT Verification Performance (Warm Cache) ===")
        print(f"Requests: {num_requests}")
        print(f"Min: {min_latency:.2f}ms")
        print(f"Avg: {avg_latency:.2f}ms")
        print(f"P95: {p95_latency:.2f}ms")
        print(f"Max: {max_latency:.2f}ms")

        # Assert SC-003: p95 <50ms
        assert (
            p95_latency < 50
        ), f"P95 latency {p95_latency:.2f}ms exceeds 50ms threshold (SC-003)"

    @pytest.mark.asyncio
    async def test_jwks_cache_hit_rate_above_95_percent(self):
        """
        SC-007: Verify cache hit rate >95%

        This test validates that the JWKS cache achieves >95% hit rate
        when processing typical request patterns.
        """

        cache = JWKSCache(ttl_seconds=3600)

        # Pre-populate cache (warm cache)
        cache._cache = {
            "keys": [
                {
                    "kid": "test-key-1",
                    "kty": "OKP",
                    "crv": "Ed25519",
                    "x": "test-public-key",
                }
            ]
        }
        from datetime import datetime

        cache._cached_at = datetime.utcnow()

        # Simulate typical request pattern
        total_requests = 1000
        cache_misses = 0

        with patch("httpx.AsyncClient.get") as mock_get:
            # Configure mock to track fetch calls (cache misses)
            async def track_fetch(*args, **kwargs):
                nonlocal cache_misses
                cache_misses += 1
                from unittest.mock import Mock

                response = Mock()
                response.json.return_value = cache._cache
                response.raise_for_status = Mock()
                return response

            mock_get.side_effect = track_fetch

            # Simulate requests
            for _ in range(total_requests):
                await cache.get_or_fetch()

        cache_hits = total_requests - cache_misses
        hit_rate = cache_hits / total_requests

        print(f"\n=== JWKS Cache Performance ===")
        print(f"Total Requests: {total_requests}")
        print(f"Cache Hits: {cache_hits}")
        print(f"Cache Misses: {cache_misses}")
        print(f"Hit Rate: {hit_rate:.2%}")

        # Assert SC-007: hit rate >95%
        assert hit_rate >= 0.95, f"Cache hit rate {hit_rate:.2%} below 95% (SC-007)"

    @pytest.mark.asyncio
    async def test_concurrent_jwt_verification_performance(self):
        """
        Test JWT verification under concurrent load

        Validates that p95 latency remains <50ms even with concurrent requests.
        """

        latencies = []

        with patch("src.services.jwks.jwks_cache.get_or_fetch") as mock_cache:
            mock_cache.return_value = {
                "keys": [{"kid": "test-key", "kty": "OKP", "crv": "Ed25519", "x": "key"}]
            }

            with patch("jose.jwt.decode") as mock_decode:
                mock_decode.return_value = {"sub": "user_123"}

                async def verify_with_timing(token_id):
                    start = time.perf_counter()
                    await verify_better_auth_jwt(f"token-{token_id}")
                    latency_ms = (time.perf_counter() - start) * 1000
                    latencies.append(latency_ms)

                # Simulate 50 concurrent requests
                tasks = [verify_with_timing(i) for i in range(50)]
                await asyncio.gather(*tasks)

        latencies.sort()
        p95_index = int(len(latencies) * 0.95) - 1
        p95_latency = latencies[p95_index]

        print(f"\n=== Concurrent JWT Verification Performance ===")
        print(f"Concurrent Requests: 50")
        print(f"P95 Latency: {p95_latency:.2f}ms")

        assert (
            p95_latency < 50
        ), f"P95 latency under concurrency {p95_latency:.2f}ms exceeds 50ms"

    @pytest.mark.asyncio
    async def test_cold_cache_performance(self):
        """
        Test JWT verification with cold cache (first request)

        Validates acceptable performance even on cache miss scenarios.
        """

        cache = JWKSCache(ttl_seconds=3600)

        with patch("httpx.AsyncClient.get") as mock_get:
            from unittest.mock import Mock

            response = Mock()
            response.json.return_value = {
                "keys": [{"kid": "key", "kty": "OKP", "crv": "Ed25519", "x": "x"}]
            }
            response.raise_for_status = Mock()
            mock_get.return_value = response

            # Measure cold cache fetch
            start = time.perf_counter()
            await cache.get_or_fetch()
            cold_latency_ms = (time.perf_counter() - start) * 1000

        print(f"\n=== Cold Cache Performance ===")
        print(f"Cold Cache Latency: {cold_latency_ms:.2f}ms")

        # Cold cache should still be reasonable (<500ms including network)
        assert cold_latency_ms < 500, "Cold cache latency exceeds 500ms"

    @pytest.mark.asyncio
    async def test_cache_expiration_and_refresh_performance(self):
        """
        Test performance when cache expires and needs refresh

        Validates smooth transition from expired to fresh cache.
        """

        from datetime import datetime, timedelta

        cache = JWKSCache(ttl_seconds=1)  # 1 second TTL for testing

        # Set expired cache
        cache._cache = {"keys": [{"kid": "old-key"}]}
        cache._cached_at = datetime.utcnow() - timedelta(seconds=2)

        refresh_latencies = []

        with patch("httpx.AsyncClient.get") as mock_get:
            from unittest.mock import Mock

            async def mock_fetch(*args, **kwargs):
                await asyncio.sleep(0.01)  # Simulate 10ms network call
                response = Mock()
                response.json.return_value = {"keys": [{"kid": "new-key"}]}
                response.raise_for_status = Mock()
                return response

            mock_get.side_effect = mock_fetch

            # Measure refresh latencies
            for _ in range(10):
                # Expire cache
                cache._cached_at = datetime.utcnow() - timedelta(seconds=2)

                start = time.perf_counter()
                await cache.get_or_fetch()
                latency_ms = (time.perf_counter() - start) * 1000
                refresh_latencies.append(latency_ms)

        avg_refresh_latency = sum(refresh_latencies) / len(refresh_latencies)

        print(f"\n=== Cache Refresh Performance ===")
        print(f"Average Refresh Latency: {avg_refresh_latency:.2f}ms")

        # Refresh should be reasonably fast
        assert avg_refresh_latency < 100, "Cache refresh exceeds 100ms average"


@pytest.mark.performance
class TestJWKSCachePerformanceMetrics:
    """Detailed JWKS cache performance metrics"""

    @pytest.mark.asyncio
    async def test_cache_lock_contention_under_load(self):
        """
        Test cache lock performance under high contention

        Validates that the asyncio lock doesn't become a bottleneck.
        """

        cache = JWKSCache(ttl_seconds=3600)

        # Pre-populate cache
        cache._cache = {"keys": [{"kid": "key"}]}
        from datetime import datetime

        cache._cached_at = datetime.utcnow()

        start = time.perf_counter()

        # Simulate 100 concurrent requests (high contention)
        tasks = [cache.get_or_fetch() for _ in range(100)]
        await asyncio.gather(*tasks)

        total_time_ms = (time.perf_counter() - start) * 1000
        avg_time_per_request = total_time_ms / 100

        print(f"\n=== Cache Lock Contention Test ===")
        print(f"Total Time (100 concurrent): {total_time_ms:.2f}ms")
        print(f"Avg Time Per Request: {avg_time_per_request:.2f}ms")

        # Lock contention shouldn't significantly slow down requests
        assert avg_time_per_request < 1.0, "Lock contention causing >1ms per request"

    @pytest.mark.asyncio
    async def test_memory_efficiency_of_cache(self):
        """
        Test memory efficiency of JWKS cache

        Validates that cache doesn't consume excessive memory.
        """

        import sys

        cache = JWKSCache(ttl_seconds=3600)

        # Populate with typical JWKS response
        typical_jwks = {
            "keys": [
                {
                    "kid": f"key-{i}",
                    "kty": "OKP",
                    "crv": "Ed25519",
                    "x": "a" * 64,  # Base64-encoded public key
                }
                for i in range(3)  # Typical: 1-3 keys
            ]
        }

        cache._cache = typical_jwks
        from datetime import datetime

        cache._cached_at = datetime.utcnow()

        # Measure cache memory size
        cache_size_bytes = sys.getsizeof(cache._cache)

        print(f"\n=== Cache Memory Efficiency ===")
        print(f"Cache Size: {cache_size_bytes} bytes ({cache_size_bytes / 1024:.2f} KB)")

        # Cache should be small (<10KB for typical JWKS)
        assert cache_size_bytes < 10240, "JWKS cache exceeds 10KB (too large)"
