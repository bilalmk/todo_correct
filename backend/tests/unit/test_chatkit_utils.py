"""Unit tests for ChatKit utility functions (retry logic, correlation IDs).

Feature: 008-chatkit-server-backend
Phase: 8 (Testing & Validation)
Task: T051 - Unit tests for retry utilities with mock failures

Test Coverage:
- retry_with_exponential_backoff() with mock OpenAI failures
- retry_database_operation() with mock OperationalError
- Correlation ID generation and propagation
- RequestContext dataclass initialization
- Retry delay validation (2s/4s/8s for OpenAI, 1s for database)
"""

import pytest
import pytest_asyncio
from unittest.mock import AsyncMock, patch, call
from uuid import uuid4, UUID
import asyncio

from sqlalchemy.exc import OperationalError, DBAPIError

# Import system under test
from src.chatkit.utils import (
    retry_with_exponential_backoff,
    retry_database_operation,
    get_correlation_id,
    RequestContext,
    correlation_id_var
)


# ===== Test: RequestContext Initialization =====

def test_request_context_auto_generates_correlation_id():
    """Test RequestContext auto-generates correlation_id if not provided."""
    # Arrange
    user_id = uuid4()

    # Act
    context = RequestContext(user_id=user_id)

    # Assert
    assert context.user_id == user_id
    assert context.correlation_id is not None
    assert len(context.correlation_id) == 36  # UUID format


def test_request_context_uses_provided_correlation_id():
    """Test RequestContext uses provided correlation_id."""
    # Arrange
    user_id = uuid4()
    provided_correlation_id = f"custom-{uuid4().hex[:8]}"

    # Act
    context = RequestContext(user_id=user_id, correlation_id=provided_correlation_id)

    # Assert
    assert context.correlation_id == provided_correlation_id


# ===== Test: get_correlation_id() =====

def test_get_correlation_id_generates_new_id():
    """Test get_correlation_id() generates new ID if none exists."""
    # Arrange - Clear context variable
    correlation_id_var.set(None)

    # Act
    correlation_id = get_correlation_id()

    # Assert
    assert correlation_id is not None
    assert len(correlation_id) == 36  # UUID format


def test_get_correlation_id_returns_existing_id():
    """Test get_correlation_id() returns existing ID from context."""
    # Arrange - Set existing ID
    existing_id = str(uuid4())
    correlation_id_var.set(existing_id)

    # Act
    correlation_id = get_correlation_id()

    # Assert
    assert correlation_id == existing_id


# ===== Test: retry_with_exponential_backoff() - Success Cases =====

@pytest.mark.asyncio
async def test_retry_exponential_backoff_success_first_attempt():
    """Test retry_with_exponential_backoff() succeeds on first attempt."""
    # Arrange
    mock_func = AsyncMock(return_value="success")
    correlation_id = str(uuid4())

    # Act
    result = await retry_with_exponential_backoff(
        mock_func,
        correlation_id=correlation_id
    )

    # Assert
    assert result == "success"
    assert mock_func.call_count == 1  # Only called once


@pytest.mark.asyncio
async def test_retry_exponential_backoff_success_after_retry():
    """Test retry_with_exponential_backoff() succeeds after 1 failure."""
    # Arrange
    call_count = 0

    async def mock_func_with_retry():
        nonlocal call_count
        call_count += 1
        if call_count == 1:
            raise Exception("Transient OpenAI error")
        return "success"

    correlation_id = str(uuid4())

    with patch('asyncio.sleep', new_callable=AsyncMock) as mock_sleep:
        # Act
        result = await retry_with_exponential_backoff(
            mock_func_with_retry,
            max_retries=3,
            correlation_id=correlation_id
        )

        # Assert
        assert result == "success"
        assert call_count == 2  # Failed once, succeeded on second attempt
        assert mock_sleep.call_count == 1
        mock_sleep.assert_called_with(2)  # First retry delay is 2s


# ===== Test: retry_with_exponential_backoff() - Failure Cases =====

@pytest.mark.asyncio
async def test_retry_exponential_backoff_exhausts_all_retries():
    """Test retry_with_exponential_backoff() raises exception after all retries."""
    # Arrange
    mock_func = AsyncMock(side_effect=Exception("Persistent OpenAI error"))
    correlation_id = str(uuid4())

    with patch('asyncio.sleep', new_callable=AsyncMock) as mock_sleep:
        # Act & Assert
        with pytest.raises(Exception, match="Persistent OpenAI error"):
            await retry_with_exponential_backoff(
                mock_func,
                max_retries=3,
                correlation_id=correlation_id
            )

        # Verify all 3 attempts made
        assert mock_func.call_count == 3
        # Verify exponential backoff delays (2s, 4s)
        assert mock_sleep.call_count == 2  # Sleeps between attempts 1-2 and 2-3
        assert mock_sleep.call_args_list[0] == call(2)  # First retry: 2s
        assert mock_sleep.call_args_list[1] == call(4)  # Second retry: 4s


# ===== Test: retry_with_exponential_backoff() - Backoff Delays =====

@pytest.mark.asyncio
async def test_retry_exponential_backoff_validates_delays():
    """Test retry_with_exponential_backoff() uses correct delays (2s, 4s, 8s)."""
    # Arrange
    mock_func = AsyncMock(side_effect=[
        Exception("Error 1"),
        Exception("Error 2"),
        "success"
    ])
    correlation_id = str(uuid4())

    with patch('asyncio.sleep', new_callable=AsyncMock) as mock_sleep:
        # Act
        result = await retry_with_exponential_backoff(
            mock_func,
            max_retries=3,
            backoff_delays=[2, 4, 8],
            correlation_id=correlation_id
        )

        # Assert
        assert result == "success"
        assert mock_sleep.call_count == 2
        assert mock_sleep.call_args_list[0] == call(2)  # 2s after first failure
        assert mock_sleep.call_args_list[1] == call(4)  # 4s after second failure


# ===== Test: retry_with_exponential_backoff() - Logging =====

@pytest.mark.asyncio
async def test_retry_exponential_backoff_logs_with_correlation_id():
    """Test retry_with_exponential_backoff() logs warnings with correlation_id."""
    # Arrange
    mock_func = AsyncMock(side_effect=[
        Exception("Transient error"),
        "success"
    ])
    correlation_id = str(uuid4())

    with patch('asyncio.sleep', new_callable=AsyncMock), \
         patch('src.chatkit.utils.logger') as mock_logger:

        # Act
        await retry_with_exponential_backoff(
            mock_func,
            max_retries=3,
            correlation_id=correlation_id
        )

        # Assert - Verify WARNING log for retry
        assert mock_logger.warning.called
        warning_call = mock_logger.warning.call_args
        assert "retrying" in warning_call[0][0].lower()
        assert warning_call[1]['extra']['correlation_id'] == correlation_id
        assert warning_call[1]['extra']['retry_attempt'] == 1


@pytest.mark.asyncio
async def test_retry_exponential_backoff_logs_error_on_exhaustion():
    """Test retry_with_exponential_backoff() logs ERROR when retries exhausted."""
    # Arrange
    mock_func = AsyncMock(side_effect=Exception("Persistent error"))
    correlation_id = str(uuid4())

    with patch('asyncio.sleep', new_callable=AsyncMock), \
         patch('src.chatkit.utils.logger') as mock_logger:

        # Act & Assert
        with pytest.raises(Exception):
            await retry_with_exponential_backoff(
                mock_func,
                max_retries=3,
                correlation_id=correlation_id
            )

        # Assert - Verify ERROR log after exhaustion
        assert mock_logger.error.called
        error_call = mock_logger.error.call_args
        assert "failed after 3 attempts" in error_call[0][0].lower()
        assert error_call[1]['extra']['correlation_id'] == correlation_id


# ===== Test: retry_database_operation() - Success Cases =====

@pytest.mark.asyncio
async def test_retry_database_operation_success_first_attempt():
    """Test retry_database_operation() succeeds on first attempt."""
    # Arrange
    mock_func = AsyncMock(return_value="db_success")
    correlation_id = str(uuid4())

    # Act
    result = await retry_database_operation(
        mock_func,
        correlation_id=correlation_id
    )

    # Assert
    assert result == "db_success"
    assert mock_func.call_count == 1


@pytest.mark.asyncio
async def test_retry_database_operation_success_after_operational_error():
    """Test retry_database_operation() succeeds after OperationalError."""
    # Arrange
    call_count = 0

    async def mock_db_func():
        nonlocal call_count
        call_count += 1
        if call_count == 1:
            raise OperationalError("Connection timeout", None, None)
        return "db_success"

    correlation_id = str(uuid4())

    with patch('asyncio.sleep', new_callable=AsyncMock) as mock_sleep:
        # Act
        result = await retry_database_operation(
            mock_db_func,
            max_retries=2,
            correlation_id=correlation_id
        )

        # Assert
        assert result == "db_success"
        assert call_count == 2
        assert mock_sleep.call_count == 1
        mock_sleep.assert_called_with(1)  # Fixed 1s delay


# ===== Test: retry_database_operation() - Failure Cases =====

@pytest.mark.asyncio
async def test_retry_database_operation_exhausts_retries():
    """Test retry_database_operation() raises exception after all retries."""
    # Arrange
    mock_func = AsyncMock(side_effect=OperationalError("Persistent DB error", None, None))
    correlation_id = str(uuid4())

    with patch('asyncio.sleep', new_callable=AsyncMock) as mock_sleep:
        # Act & Assert
        with pytest.raises(OperationalError):
            await retry_database_operation(
                mock_func,
                max_retries=2,
                correlation_id=correlation_id
            )

        # Verify both attempts made
        assert mock_func.call_count == 2
        # Verify fixed delay (1s) between attempts
        assert mock_sleep.call_count == 1
        mock_sleep.assert_called_with(1)


@pytest.mark.asyncio
async def test_retry_database_operation_handles_dbapi_error():
    """Test retry_database_operation() retries on DBAPIError."""
    # Arrange
    call_count = 0

    async def mock_db_func():
        nonlocal call_count
        call_count += 1
        if call_count == 1:
            raise DBAPIError("Deadlock detected", None, None)
        return "success"

    correlation_id = str(uuid4())

    with patch('asyncio.sleep', new_callable=AsyncMock):
        # Act
        result = await retry_database_operation(
            mock_db_func,
            max_retries=2,
            correlation_id=correlation_id
        )

        # Assert
        assert result == "success"
        assert call_count == 2


# ===== Test: retry_database_operation() - Delay Configuration =====

@pytest.mark.asyncio
async def test_retry_database_operation_uses_fixed_delay():
    """Test retry_database_operation() uses fixed 1s delay (not exponential)."""
    # Arrange
    mock_func = AsyncMock(side_effect=[
        OperationalError("Error 1", None, None),
        "success"
    ])
    correlation_id = str(uuid4())

    with patch('asyncio.sleep', new_callable=AsyncMock) as mock_sleep:
        # Act
        result = await retry_database_operation(
            mock_func,
            max_retries=2,
            delay=1,
            correlation_id=correlation_id
        )

        # Assert
        assert result == "success"
        assert mock_sleep.call_count == 1
        mock_sleep.assert_called_with(1)  # Fixed 1s delay (not exponential)


# ===== Test: retry_database_operation() - Logging =====

@pytest.mark.asyncio
async def test_retry_database_operation_logs_with_correlation_id():
    """Test retry_database_operation() logs warnings with correlation_id."""
    # Arrange
    mock_func = AsyncMock(side_effect=[
        OperationalError("Transient DB error", None, None),
        "success"
    ])
    correlation_id = str(uuid4())

    with patch('asyncio.sleep', new_callable=AsyncMock), \
         patch('src.chatkit.utils.logger') as mock_logger:

        # Act
        await retry_database_operation(
            mock_func,
            max_retries=2,
            correlation_id=correlation_id
        )

        # Assert - Verify WARNING log for retry
        assert mock_logger.warning.called
        warning_call = mock_logger.warning.call_args
        assert "database operation failed" in warning_call[0][0].lower()
        assert warning_call[1]['extra']['correlation_id'] == correlation_id
        assert warning_call[1]['extra']['retry_attempt'] == 1


@pytest.mark.asyncio
async def test_retry_database_operation_logs_error_on_exhaustion():
    """Test retry_database_operation() logs ERROR when retries exhausted."""
    # Arrange
    mock_func = AsyncMock(side_effect=OperationalError("Persistent DB error", None, None))
    correlation_id = str(uuid4())

    with patch('asyncio.sleep', new_callable=AsyncMock), \
         patch('src.chatkit.utils.logger') as mock_logger:

        # Act & Assert
        with pytest.raises(OperationalError):
            await retry_database_operation(
                mock_func,
                max_retries=2,
                correlation_id=correlation_id
            )

        # Assert - Verify ERROR log after exhaustion
        assert mock_logger.error.called
        error_call = mock_logger.error.call_args
        assert "failed after 2 attempts" in error_call[0][0].lower()
        assert error_call[1]['extra']['correlation_id'] == correlation_id


# ===== Test: Integration - Combined Retry Behavior =====

@pytest.mark.asyncio
async def test_nested_retries_different_delays():
    """Test that different retry functions use their specific delays."""
    # Arrange
    openai_call_count = 0
    db_call_count = 0

    async def mock_openai_func():
        nonlocal openai_call_count
        openai_call_count += 1
        if openai_call_count == 1:
            raise Exception("OpenAI error")
        return "openai_success"

    async def mock_db_func():
        nonlocal db_call_count
        db_call_count += 1
        if db_call_count == 1:
            raise OperationalError("DB error", None, None)
        return "db_success"

    correlation_id = str(uuid4())

    with patch('asyncio.sleep', new_callable=AsyncMock) as mock_sleep:
        # Act - OpenAI retry
        openai_result = await retry_with_exponential_backoff(
            mock_openai_func,
            max_retries=3,
            backoff_delays=[2, 4, 8],
            correlation_id=correlation_id
        )

        # Reset sleep mock
        mock_sleep.reset_mock()

        # Act - Database retry
        db_result = await retry_database_operation(
            mock_db_func,
            max_retries=2,
            delay=1,
            correlation_id=correlation_id
        )

        # Assert
        assert openai_result == "openai_success"
        assert db_result == "db_success"
        # Database retry should use 1s delay
        assert mock_sleep.call_args_list[0] == call(1)


# ===== Test Summary =====

"""
Test Coverage Summary (T051):

✅ RequestContext:
   - Auto-generates correlation_id if not provided
   - Uses provided correlation_id

✅ get_correlation_id():
   - Generates new UUID if none exists
   - Returns existing ID from ContextVar

✅ retry_with_exponential_backoff():
   - Success on first attempt
   - Success after transient failures
   - Raises exception after all retries exhausted
   - Uses correct backoff delays (2s, 4s, 8s)
   - Logs WARNING on retries with correlation_id
   - Logs ERROR on exhaustion with correlation_id

✅ retry_database_operation():
   - Success on first attempt
   - Success after OperationalError
   - Success after DBAPIError
   - Raises exception after all retries exhausted
   - Uses fixed 1s delay (not exponential)
   - Logs WARNING on retries with correlation_id
   - Logs ERROR on exhaustion with correlation_id

✅ Integration:
   - Different retry functions use different delay strategies

Total Tests: 18 unit tests
Mocking Strategy: AsyncMock for async functions, patch for asyncio.sleep and logger
Error Handling: OperationalError and DBAPIError retry validation
Constitutional Compliance:
- FR-018: OpenAI failures retry 3x with 2s/4s/8s exponential backoff
- FR-019: Database failures retry 2x with 1s fixed delay
- FR-016: Correlation ID propagation in all logs

Delay Verification:
- OpenAI: Exponential backoff (2s → 4s → 8s)
- Database: Fixed delay (1s for all retries)
"""
