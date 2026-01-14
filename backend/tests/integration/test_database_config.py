"""Integration test for database connection pool configuration (FR-023, SC-003).

Feature: 008-chatkit-server-backend
Phase: 8 (Testing & Validation)
Task: T059 - Database connection pool configuration test

Test Coverage:
- Connection pool size = 10 (pool_size)
- Max overflow = 40 (max_overflow)
- Total capacity = 50 concurrent connections
- Pool timeout = 30 seconds
- Pre-ping enabled for health checks
- Validates FR-023 requirements to support 50 concurrent requests per SC-003
"""

import pytest
from sqlalchemy.ext.asyncio import AsyncEngine

from src.core.database import async_engine


# ===== Test: Database Connection Pool Configuration (FR-023, SC-003) (T059) =====

def test_database_pool_size_configured():
    """
    Test database connection pool size is configured to 10 (FR-023).

    Validates:
    - pool_size = 10 (base pool size)
    - Supports up to 10 concurrent connections without overflow
    """
    assert isinstance(async_engine, AsyncEngine)

    # Get pool from engine
    pool = async_engine.pool

    # Verify pool size
    # Note: AsyncEngine uses QueuePool, size is configured via pool_size parameter
    assert hasattr(pool, '_pool')  # QueuePool has _pool attribute
    assert pool.size() == 10  # Base pool size


def test_database_pool_max_overflow_configured():
    """
    Test database max_overflow is configured to 40 (FR-023).

    Validates:
    - max_overflow = 40 (additional connections beyond pool_size)
    - Total capacity = pool_size (10) + max_overflow (40) = 50 connections
    """
    pool = async_engine.pool

    # Verify max_overflow
    assert hasattr(pool, '_max_overflow')
    assert pool._max_overflow == 40


def test_database_pool_total_capacity():
    """
    Test database pool total capacity is 50 concurrent connections (SC-003).

    Validates:
    - pool_size (10) + max_overflow (40) = 50 total connections
    - Meets SC-003 requirement: 50 concurrent requests supported
    """
    pool = async_engine.pool

    pool_size = pool.size()
    max_overflow = pool._max_overflow
    total_capacity = pool_size + max_overflow

    assert total_capacity == 50  # SC-003 requirement


def test_database_pool_timeout_configured():
    """
    Test database pool timeout is configured to 30 seconds (FR-023).

    Validates:
    - pool_timeout = 30 seconds
    - Prevents indefinite blocking when pool exhausted
    """
    pool = async_engine.pool

    # Verify timeout
    assert hasattr(pool, '_timeout')
    assert pool._timeout == 30  # 30 seconds


def test_database_pool_pre_ping_enabled():
    """
    Test database pre-ping is enabled for connection health checks (FR-023).

    Validates:
    - pool_pre_ping = True
    - SQLAlchemy tests connections before use
    - Handles stale connections gracefully
    """
    pool = async_engine.pool

    # Verify pre-ping enabled
    assert hasattr(pool, '_pre_ping')
    assert pool._pre_ping is True


def test_database_engine_configuration():
    """
    Test database engine configuration is correct.

    Validates:
    - Engine is AsyncEngine instance
    - Pool is configured (not NullPool)
    - Async driver configured (asyncpg)
    """
    # Verify async engine
    assert isinstance(async_engine, AsyncEngine)

    # Verify driver
    assert "asyncpg" in str(async_engine.url) or "psycopg" in str(async_engine.url)

    # Verify pool exists (not NullPool)
    pool = async_engine.pool
    assert pool is not None
    assert pool.__class__.__name__ != "NullPool"  # Real pool, not null pool


def test_database_pool_supports_concurrent_requests():
    """
    Test database pool configuration supports 50 concurrent requests (SC-003).

    Validates:
    - Configuration meets scalability requirement
    - Pool size + overflow = 50 connections
    - Constitutional compliance (SC-003)
    """
    pool = async_engine.pool

    # Calculate total capacity
    total_capacity = pool.size() + pool._max_overflow

    # Verify meets SC-003 requirement
    assert total_capacity >= 50  # At least 50 concurrent connections

    # Verify configuration details
    assert pool.size() == 10
    assert pool._max_overflow == 40
    assert pool._timeout == 30
    assert pool._pre_ping is True


# ===== Test Summary =====

"""
Test Coverage Summary (T059):

✅ Database Connection Pool Configuration (FR-023):
   - pool_size = 10 (base connections)
   - max_overflow = 40 (additional connections)
   - Total capacity = 50 concurrent connections
   - pool_timeout = 30 seconds
   - pool_pre_ping = True (health checks)

✅ Scalability Requirements (SC-003):
   - Supports 50 concurrent requests
   - Meets constitutional scalability requirement
   - Prevents connection exhaustion

✅ Engine Configuration:
   - AsyncEngine configured
   - Async driver (asyncpg or psycopg) used
   - Real connection pool (not NullPool)

Total Tests: 7 integration tests
Test Strategy: Inspect engine.pool configuration attributes
Constitutional Compliance:
- FR-023: Database connection pool configured for concurrent requests
- SC-003: System supports 50 concurrent requests

Configuration Breakdown:
- Base Pool Size: 10 connections (always available)
- Overflow: 40 connections (created on demand)
- Total Capacity: 50 connections (10 base + 40 overflow)
- Timeout: 30 seconds (prevents indefinite blocking)
- Pre-ping: Enabled (tests connections before use)

Why This Configuration:
- 10 base connections: Reduces connection overhead for normal load
- 40 overflow connections: Handles traffic spikes up to 50 concurrent requests
- 30s timeout: Balances responsiveness with grace period
- Pre-ping: Ensures connection validity, handles database restarts
"""
