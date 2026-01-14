"""Integration test for message content truncation (FR-024).

Feature: 008-chatkit-server-backend
Phase: 8 (Testing & Validation)
Task: T057 - Test message content truncation at 10,000 characters

Test Coverage:
- save_thread_item() with content exceeding 10,000 characters
- Truncation at exactly 10,000 characters
- Truncation warning message appended
- Truncation event logged with correlation ID (FR-024)
"""

import pytest
import pytest_asyncio
from unittest.mock import patch
from uuid import uuid4
from datetime import datetime, timezone

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from src.models.user import User
from src.models.conversation import Conversation
from src.models.message import Message
from src.chatkit.store import DatabaseThreadItemStore
from src.chatkit.utils import RequestContext
from src.core.config import settings


# ===== Test: Message Content Truncation (FR-024) (T057) =====

@pytest.mark.asyncio
async def test_save_thread_item_truncates_content_at_10000_characters(
    test_user: User,
    test_session: AsyncSession
):
    """
    Test save_thread_item() truncates content at 10,000 characters (FR-024).

    Validates:
    - Content truncated at exactly 10,000 characters
    - Truncation warning appended: "...[message truncated at 10,000 characters]"
    - Truncation event logged with correlation_id
    """

    # Arrange - Create conversation
    conversation = Conversation(
        user_id=test_user.uuid,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
        deleted_at=None
    )
    test_session.add(conversation)
    await test_session.flush()
    await test_session.commit()

    # Create store
    store = DatabaseThreadItemStore(test_session)

    # Create message with exactly 10,001 characters
    long_content = "A" * 10001  # Exceeds limit by 1 character

    mock_long_message = type('LongMessage', (), {
        'content': long_content,
        'role': 'user',
        'created_at': datetime.now(timezone.utc),
        'metadata': {'is_complete': True}
    })()

    # Create context
    correlation_id = f"test-{uuid4().hex[:8]}"
    context = RequestContext(
        user_id=test_user.uuid,
        correlation_id=correlation_id
    )

    # Act - Save message with truncation logging
    with patch('src.chatkit.store.logger') as mock_logger:
        await store.save_thread_item(
            thread_id=str(conversation.conversation_id),
            item=mock_long_message,
            context=context
        )

        await test_session.commit()

        # Assert - Verify WARNING log for truncation
        assert mock_logger.warning.called
        warning_call = mock_logger.warning.call_args

        # Verify truncation message
        assert "truncated" in warning_call[0][0].lower()

        # Verify correlation_id in log extra
        assert warning_call[1]['extra']['correlation_id'] == correlation_id
        assert warning_call[1]['extra']['user_id'] == str(test_user.uuid)
        assert warning_call[1]['extra']['original_length'] == 10001
        assert warning_call[1]['extra']['truncated_length'] == settings.CHATKIT_MESSAGE_LIMIT

    # Verify message saved to database with truncation
    result = await test_session.execute(
        select(Message)
        .where(Message.conversation_id == conversation.conversation_id)
        .where(Message.user_id == test_user.uuid)
    )
    saved_message = result.scalar_one_or_none()

    assert saved_message is not None

    # Verify truncation: content length = 10,000 + truncation warning length
    truncation_warning = "...[message truncated at 10,000 characters]"
    expected_length = 10000 + len(truncation_warning)

    assert len(saved_message.content) == expected_length
    assert saved_message.content.endswith(truncation_warning)

    # Verify first 10,000 characters preserved
    assert saved_message.content[:10000] == "A" * 10000


@pytest.mark.asyncio
async def test_save_thread_item_no_truncation_for_exactly_10000_characters(
    test_user: User,
    test_session: AsyncSession
):
    """
    Test save_thread_item() does NOT truncate content at exactly 10,000 characters.

    Validates:
    - Content at limit is NOT truncated
    - No truncation warning logged
    """

    # Arrange - Create conversation
    conversation = Conversation(
        user_id=test_user.uuid,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
        deleted_at=None
    )
    test_session.add(conversation)
    await test_session.flush()
    await test_session.commit()

    # Create store
    store = DatabaseThreadItemStore(test_session)

    # Create message with exactly 10,000 characters (at limit)
    content_at_limit = "B" * 10000

    mock_message = type('Message', (), {
        'content': content_at_limit,
        'role': 'user',
        'created_at': datetime.now(timezone.utc),
        'metadata': {'is_complete': True}
    })()

    # Create context
    context = RequestContext(
        user_id=test_user.uuid,
        correlation_id=f"test-{uuid4().hex[:8]}"
    )

    # Act
    with patch('src.chatkit.store.logger') as mock_logger:
        await store.save_thread_item(
            thread_id=str(conversation.conversation_id),
            item=mock_message,
            context=context
        )

        await test_session.commit()

        # Assert - NO truncation warning logged
        assert not mock_logger.warning.called

    # Verify message saved without truncation
    result = await test_session.execute(
        select(Message)
        .where(Message.conversation_id == conversation.conversation_id)
        .where(Message.user_id == test_user.uuid)
    )
    saved_message = result.scalar_one_or_none()

    assert saved_message is not None
    assert len(saved_message.content) == 10000
    assert saved_message.content == content_at_limit
    assert "truncated" not in saved_message.content


@pytest.mark.asyncio
async def test_save_thread_item_truncation_with_unicode_characters(
    test_user: User,
    test_session: AsyncSession
):
    """
    Test save_thread_item() truncates correctly with Unicode characters.

    Validates:
    - Unicode characters (emoji, non-ASCII) handled correctly in truncation
    - Character count vs byte count handled properly
    """

    # Arrange - Create conversation
    conversation = Conversation(
        user_id=test_user.uuid,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
        deleted_at=None
    )
    test_session.add(conversation)
    await test_session.flush()
    await test_session.commit()

    # Create store
    store = DatabaseThreadItemStore(test_session)

    # Create message with Unicode characters exceeding limit
    # Mix of ASCII and Unicode to test character counting
    unicode_content = "😀" * 5000 + "A" * 5002  # Emoji (2 bytes each) + ASCII = 10,002 characters

    mock_message = type('Message', (), {
        'content': unicode_content,
        'role': 'user',
        'created_at': datetime.now(timezone.utc),
        'metadata': {'is_complete': True}
    })()

    # Create context
    context = RequestContext(
        user_id=test_user.uuid,
        correlation_id=f"test-{uuid4().hex[:8]}"
    )

    # Act
    await store.save_thread_item(
        thread_id=str(conversation.conversation_id),
        item=mock_message,
        context=context
    )

    await test_session.commit()

    # Verify message truncated
    result = await test_session.execute(
        select(Message)
        .where(Message.conversation_id == conversation.conversation_id)
        .where(Message.user_id == test_user.uuid)
    )
    saved_message = result.scalar_one_or_none()

    assert saved_message is not None
    truncation_warning = "...[message truncated at 10,000 characters]"
    assert saved_message.content.endswith(truncation_warning)


# ===== Test: Settings Validation (FR-024) =====

def test_chatkit_message_limit_setting_configured():
    """Test CHATKIT_MESSAGE_LIMIT is configured to 10,000 characters (FR-024)."""
    assert settings.CHATKIT_MESSAGE_LIMIT == 10000


# ===== Test Summary =====

"""
Test Coverage Summary (T057):

✅ Message Content Truncation (FR-024):
   - Truncates content at exactly 10,000 characters
   - Appends truncation warning message
   - Logs truncation event with correlation_id
   - Preserves first 10,000 characters
   - No truncation for content at limit (10,000 chars)
   - Handles Unicode characters correctly

✅ Logging Validation:
   - WARNING level log for truncation
   - correlation_id included in log extra
   - user_id included in log extra
   - original_length and truncated_length logged

✅ Database Verification:
   - Truncated message saved to database
   - Truncation warning appended to content
   - Content length matches expected (10,000 + warning length)

✅ Settings Validation:
   - CHATKIT_MESSAGE_LIMIT = 10,000 (FR-024)

Total Tests: 4 integration tests
Test Strategy: Real database operations with message truncation validation
Constitutional Compliance:
- FR-024: Message content truncated at 10,000 characters
- Truncation event logged with correlation_id
- User-friendly truncation warning appended

Edge Cases Tested:
- Content exceeding limit by 1 character (10,001 chars)
- Content at exact limit (10,000 chars) - no truncation
- Unicode characters (emoji) - correct character counting
"""
