"""add ChatKit conversation and message tables

Revision ID: b7c8d9e0f1a2
Revises: a1b2c3d4e5f6
Create Date: 2026-01-13 13:30:00.000000

Feature: 008-chatkit-server-backend (Phase III: ChatKit Backend)
Tasks: T007 (Create migration), T008 (Run migration)
Data Model: specs/008-chatkit-server-backend/data-model.md
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'b7c8d9e0f1a2'
down_revision: Union[str, None] = 'a1b2c3d4e5f6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Create conversations and messages tables for ChatKit backend.

    Tables:
    1. conversations - User chat sessions with AI assistant
    2. messages - Individual messages in conversations

    Features:
    - UUID primary keys (constitutional requirement)
    - Soft deletes (deleted_at timestamps)
    - User isolation (user_id foreign keys)
    - Indexes for performance
    - Check constraints for data integrity
    """

    # ===== Create conversations table =====
    op.create_table(
        'conversations',
        sa.Column('conversation_id', postgresql.UUID(), nullable=False),
        sa.Column('user_id', postgresql.UUID(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('conversation_id'),
        sa.ForeignKeyConstraint(
            ['user_id'],
            ['user.uuid'],  # References user.uuid (UUID), not user.id (String)
            ondelete='CASCADE'
        ),
    )

    # Create indexes for conversations table
    op.create_index(
        'idx_conversations_user_id',
        'conversations',
        ['user_id'],
        unique=False
    )

    # Create unique partial index: only one active conversation per user
    # PostgreSQL-specific partial index with WHERE clause
    op.create_index(
        'idx_conversations_user_active',
        'conversations',
        ['user_id'],
        unique=True,
        postgresql_where=sa.text('deleted_at IS NULL')
    )

    # ===== Create messages table =====
    op.create_table(
        'messages',
        sa.Column('message_id', postgresql.UUID(), nullable=False),
        sa.Column('conversation_id', postgresql.UUID(), nullable=False),
        sa.Column('user_id', postgresql.UUID(), nullable=False),
        sa.Column('role', sa.String(length=20), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('is_complete', sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('message_id'),
        sa.ForeignKeyConstraint(
            ['conversation_id'],
            ['conversations.conversation_id'],
            ondelete='CASCADE'
        ),
        sa.ForeignKeyConstraint(
            ['user_id'],
            ['user.uuid'],  # References user.uuid (UUID), not user.id (String)
            ondelete='CASCADE'
        ),
        # Check constraint: role must be valid enum value
        sa.CheckConstraint(
            "role IN ('user', 'assistant', 'system')",
            name='check_message_role_enum'
        ),
        # Check constraint: content length <= 10,000 characters (FR-024)
        sa.CheckConstraint(
            'length(content) <= 10000',
            name='check_message_content_length'
        ),
    )

    # Create composite index for chronological message loading
    op.create_index(
        'idx_messages_conversation_created',
        'messages',
        ['conversation_id', 'created_at'],
        unique=False
    )

    # Create index for user isolation queries
    op.create_index(
        'idx_messages_user_id',
        'messages',
        ['user_id'],
        unique=False
    )


def downgrade() -> None:
    """
    Drop conversations and messages tables.

    Note: This will CASCADE delete all conversation history.
    Use with caution in production.
    """

    # Drop messages table first (has foreign key to conversations)
    op.drop_index('idx_messages_user_id', table_name='messages')
    op.drop_index('idx_messages_conversation_created', table_name='messages')
    op.drop_table('messages')

    # Drop conversations table
    op.drop_index('idx_conversations_user_active', table_name='conversations')
    op.drop_index('idx_conversations_user_id', table_name='conversations')
    op.drop_table('conversations')
