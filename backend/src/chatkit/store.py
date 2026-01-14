"""Database-backed ThreadItemStore implementation using SQLModel.

This module implements the ThreadItemStore protocol for persisting conversation
history to PostgreSQL, enforcing constitutional 20-message limit and user isolation.

Feature: 008-chatkit-server-backend
Phase: II (Foundational) - ThreadItemStore Implementation
Task Reference: T014-T016 (load/save/delete thread items)
Research: research.md R003 (lines 175-343)
"""

import logging
from typing import Optional, Any, List
from uuid import UUID
from datetime import datetime, timezone

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy import update

from ..models.message import Message
from ..core.config import settings
from .utils import RequestContext, get_correlation_id

logger = logging.getLogger(__name__)

# TODO: Import ChatKit ThreadItemStore protocol when SDK installed
# from chatkit.server import ThreadItemStore, ThreadItem, ThreadItemsPage


class DatabaseThreadItemStore:
    """
    Database-backed implementation of ThreadItemStore protocol.

    Constitutional Compliance:
    - 20-message history limit (FR-007, constitutional requirement)
    - User isolation (all queries filtered by user_id)
    - Content truncation at 10,000 characters (FR-024)
    - Soft deletes (deleted_at timestamp)
    - Structured logging with correlation IDs (FR-016)

    Task References:
    - T014: load_thread_items() implementation
    - T015: save_thread_item() implementation
    - T016: delete_thread_items() implementation
    """

    def __init__(self, session: AsyncSession):
        """
        Initialize store with database session.

        Args:
            session: Async SQLModel session for database operations
        """
        self.session = session

    # ===== T014: Load Thread Items =====

    async def load_thread_items(
        self,
        thread_id: str,
        after: Optional[str],
        limit: int,
        order: str,
        context: RequestContext,
    ) -> Any:  # Returns ThreadItemsPage
        """
        Load conversation messages from database with user isolation.

        Implementation based on research.md R003 (lines 226-280).

        Constitutional Requirement (FR-007):
        - Enforces 20-message history limit (min(limit, 20))
        - Token budget management for OpenAI Agents SDK

        Args:
            thread_id: Conversation UUID (as string)
            after: Cursor for pagination (message_id, optional)
            limit: Requested message limit (capped at 20)
            order: Sort order ("asc" or "desc")
            context: RequestContext with user_id and correlation_id

        Returns:
            ThreadItemsPage with messages converted to ThreadItem format

        User Isolation:
            - Filters by conversation_id AND user_id
            - Prevents cross-user conversation access (FR-017)
        """
        conversation_id = UUID(thread_id)
        user_id = context.user_id
        correlation_id = context.correlation_id

        # Enforce constitutional 20-message limit (FR-007)
        effective_limit = min(limit, settings.CHATKIT_HISTORY_LIMIT)

        # Log message load attempt
        logger.info(
            f"Loading thread items for conversation {conversation_id}",
            extra={
                "correlation_id": correlation_id,
                "user_id": str(user_id),
                "conversation_id": str(conversation_id),
                "requested_limit": limit,
                "effective_limit": effective_limit,
                "order": order
            }
        )

        # Build query with user isolation
        query = (
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .where(Message.user_id == user_id)  # User isolation (FR-017)
            .where(Message.deleted_at.is_(None))  # Exclude soft-deleted
            .order_by(
                Message.created_at.desc() if order == "desc" else Message.created_at.asc()
            )
            .limit(effective_limit)
        )

        # Cursor pagination (if 'after' provided)
        if after:
            after_message_id = UUID(after)
            after_msg = await self.session.get(Message, after_message_id)
            if after_msg:
                query = query.where(Message.created_at > after_msg.created_at)

        # Execute query
        result = await self.session.execute(query)
        messages = result.scalars().all()

        # Log loaded message count
        logger.info(
            f"Loaded {len(messages)} thread items",
            extra={
                "correlation_id": correlation_id,
                "message_count": len(messages),
                "conversation_id": str(conversation_id)
            }
        )

        # TODO: Convert SQLModel Message to ChatKit ThreadItem (when SDK installed)
        # thread_items = [
        #     ThreadItem(
        #         id=str(msg.message_id),
        #         role=msg.role,
        #         content=msg.content,
        #         created_at=msg.created_at,
        #         metadata={"is_complete": msg.is_complete},
        #     )
        #     for msg in messages
        # ]
        #
        # return ThreadItemsPage(
        #     data=thread_items,
        #     has_more=len(thread_items) == effective_limit,
        # )

        # Placeholder return (for now, return raw messages)
        return {
            "data": messages,
            "has_more": len(messages) == effective_limit,
        }

    # ===== T015: Save Thread Item =====

    async def save_thread_item(
        self,
        thread_id: str,
        item: Any,  # ThreadItem type
        context: RequestContext,
    ) -> None:
        """
        Persist message to database with content validation.

        Implementation based on research.md R003 (lines 281-316).

        Content Limits (FR-024):
        - Max content length: 10,000 characters
        - Truncation: Append "...[message truncated at 10,000 characters]"
        - Log truncation event with correlation ID

        Args:
            thread_id: Conversation UUID (as string)
            item: ThreadItem containing role, content, created_at
            context: RequestContext with user_id and correlation_id

        Side Effects:
            - Creates new Message record in database
            - Flushes immediately (don't wait for request end)
        """
        conversation_id = UUID(thread_id)
        user_id = context.user_id
        correlation_id = context.correlation_id

        # Extract content from ThreadItem (placeholder until SDK installed)
        # In real implementation: content = item.content, role = item.role, etc.
        content = getattr(item, 'content', '')
        role = getattr(item, 'role', 'user')
        is_complete = getattr(item, 'metadata', {}).get('is_complete', True)
        created_at = getattr(item, 'created_at', None) or datetime.now(timezone.utc)

        # Truncate content if exceeds limit (FR-024)
        if len(content) > settings.CHATKIT_MESSAGE_LIMIT:
            original_length = len(content)
            content = content[:settings.CHATKIT_MESSAGE_LIMIT] + "...[message truncated at 10,000 characters]"

            # Log truncation event
            logger.warning(
                f"Message content truncated from {original_length} to {settings.CHATKIT_MESSAGE_LIMIT} characters",
                extra={
                    "correlation_id": correlation_id,
                    "user_id": str(user_id),
                    "conversation_id": str(conversation_id),
                    "original_length": original_length,
                    "truncated_length": settings.CHATKIT_MESSAGE_LIMIT
                }
            )

        # Create Message record
        message = Message(
            conversation_id=conversation_id,
            user_id=user_id,
            role=role,
            content=content,
            is_complete=is_complete,
            created_at=created_at,
        )

        self.session.add(message)
        await self.session.flush()  # Persist immediately

        # Log successful save
        logger.info(
            f"Saved thread item: {message.message_id}",
            extra={
                "correlation_id": correlation_id,
                "message_id": str(message.message_id),
                "conversation_id": str(conversation_id),
                "role": role,
                "content_length": len(content),
                "is_complete": is_complete
            }
        )

    # ===== T016: Delete Thread Items =====

    async def delete_thread_items(
        self,
        thread_id: str,
        context: RequestContext,
    ) -> None:
        """
        Soft-delete all messages in conversation.

        Implementation based on research.md R003 (lines 317-336).

        Soft Delete Strategy:
        - Sets deleted_at timestamp (not hard delete)
        - Cascaded from Conversation soft delete
        - User isolation enforced (user_id filter)

        Args:
            thread_id: Conversation UUID (as string)
            context: RequestContext with user_id and correlation_id

        Side Effects:
            - Updates all messages in conversation with deleted_at timestamp
            - Flushes immediately
        """
        conversation_id = UUID(thread_id)
        user_id = context.user_id
        correlation_id = context.correlation_id

        # Log deletion attempt
        logger.info(
            f"Soft-deleting all messages in conversation {conversation_id}",
            extra={
                "correlation_id": correlation_id,
                "user_id": str(user_id),
                "conversation_id": str(conversation_id)
            }
        )

        # Soft delete all messages with user isolation
        await self.session.execute(
            update(Message)
            .where(Message.conversation_id == conversation_id)
            .where(Message.user_id == user_id)  # User isolation (FR-017)
            .values(deleted_at=datetime.now(timezone.utc))
        )

        await self.session.flush()

        # Log successful deletion
        logger.info(
            f"Soft-deleted all messages in conversation {conversation_id}",
            extra={
                "correlation_id": correlation_id,
                "conversation_id": str(conversation_id)
            }
        )
