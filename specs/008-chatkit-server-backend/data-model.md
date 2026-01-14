# Data Model: ChatKit Backend Server

**Feature**: 008-chatkit-server-backend
**Date**: 2026-01-08
**Phase**: Phase 1A - Data Model Design

## Overview

This document defines the database schema for the ChatKit backend server, including Conversation and Message entities. Both models follow constitutional requirements: user-scoped data, soft deletes, audit timestamps, and UUID primary keys.

---

## Entity 1: Conversation

**Purpose**: Represents a chat session between a user and the AI assistant.
**Cardinality**: One active conversation per user (enforced via unique constraint).

### Schema

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `conversation_id` | UUID | Primary Key | Auto-generated UUID |
| `user_id` | UUID | Foreign Key (user.id), NOT NULL, Index | Owner of conversation (Better Auth user table) |
| `created_at` | TIMESTAMPTZ | NOT NULL | Creation timestamp (UTC) |
| `updated_at` | TIMESTAMPTZ | NOT NULL | Last modified timestamp (UTC) |
| `deleted_at` | TIMESTAMPTZ | NULL | Soft delete timestamp (NULL = active) |

### Relationships
- **One-to-Many** with Message: One conversation has many messages
- **One-to-One** with User: One user has one active conversation (WHERE deleted_at IS NULL)

### Indexes
- `idx_conversations_user_active` (user_id UNIQUE WHERE deleted_at IS NULL) - Enforce one active conversation per user
- `idx_conversations_user_id` (user_id) - Query conversations by user

### Constraints
- Foreign key `user_id` references `user.id` ON DELETE CASCADE
- Unique constraint on `user_id` for active conversations (partial index with WHERE deleted_at IS NULL)

---

## Entity 2: Message

**Purpose**: Represents a single message in a conversation from user or assistant.
**Cardinality**: Many messages per conversation.

### Schema

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `message_id` | UUID | Primary Key | Auto-generated UUID |
| `conversation_id` | UUID | Foreign Key (conversations.conversation_id), NOT NULL, Index | Parent conversation |
| `user_id` | UUID | Foreign Key (user.id), NOT NULL, Index | Denormalized user_id for query performance |
| `role` | VARCHAR(20) | NOT NULL, CHECK (role IN ('user', 'assistant', 'system')) | Message sender role |
| `content` | TEXT | NOT NULL, CHECK (length(content) <= 10000) | Message content (max 10,000 chars) |
| `is_complete` | BOOLEAN | NOT NULL, DEFAULT true | False if streaming interrupted, true if completed |
| `created_at` | TIMESTAMPTZ | NOT NULL | Message timestamp (UTC) |
| `deleted_at` | TIMESTAMPTZ | NULL | Soft delete timestamp (cascaded from Conversation) |

### Relationships
- **Many-to-One** with Conversation: Many messages belong to one conversation
- **Many-to-One** with User: Many messages belong to one user (denormalized)

### Indexes
- `idx_messages_conversation_created` (conversation_id, created_at) - Load messages chronologically
- `idx_messages_user_id` (user_id) - User isolation queries

### Constraints
- Foreign key `conversation_id` references `conversations.conversation_id` ON DELETE CASCADE
- Foreign key `user_id` references `user.id` ON DELETE CASCADE
- Check constraint: `role` must be 'user', 'assistant', or 'system'
- Check constraint: `content` length <= 10,000 characters

---

## State Transitions

### Conversation States
- **Active** (deleted_at = NULL) → **Soft-Deleted** (deleted_at = timestamp)
  - Trigger: User invokes DELETE /api/chatkit/conversation
  - Effect: All associated messages soft-deleted (cascaded deleted_at)

### Message States
- **In-Progress** (is_complete = false) → **Completed** (is_complete = true)
  - Trigger: Streaming response finishes successfully
  - Effect: Message marked as complete
- **Incomplete** (is_complete = false) → **Interrupted** (remains false)
  - Trigger: Stream exception (network disconnect, browser close)
  - Effect: Partial message content saved, user sees partial response

---

## Query Patterns

### Load Conversation History (Last 20 Messages)
```sql
SELECT * FROM messages
WHERE conversation_id = $1
  AND user_id = $2  -- User isolation
  AND deleted_at IS NULL
ORDER BY created_at DESC
LIMIT 20;
```

### Get or Create Active Conversation
```sql
-- Check if active conversation exists
SELECT conversation_id FROM conversations
WHERE user_id = $1
  AND deleted_at IS NULL;

-- If not found, create new conversation
INSERT INTO conversations (conversation_id, user_id, created_at, updated_at)
VALUES (gen_random_uuid(), $1, NOW(), NOW())
RETURNING conversation_id;
```

### Save User Message
```sql
INSERT INTO messages (
  message_id, conversation_id, user_id, role, content, is_complete, created_at
)
VALUES (
  gen_random_uuid(), $1, $2, 'user', $3, true, NOW()
);
```

### Soft Delete Conversation
```sql
-- Update conversation
UPDATE conversations
SET deleted_at = NOW()
WHERE user_id = $1
  AND deleted_at IS NULL;

-- Cascade soft delete to messages
UPDATE messages
SET deleted_at = NOW()
WHERE conversation_id IN (
  SELECT conversation_id FROM conversations
  WHERE user_id = $1 AND deleted_at IS NOT NULL
);
```

---

## Migration Strategy

### Alembic Migration (backend/alembic/versions/XXX_add_chatkit_models.py)
```python
"""Add Conversation and Message models for ChatKit backend

Revision ID: XXX
Revises: YYY
Create Date: 2026-01-08
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

def upgrade():
    # Create conversations table
    op.create_table(
        'conversations',
        sa.Column('conversation_id', postgresql.UUID(), nullable=False),
        sa.Column('user_id', postgresql.UUID(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('conversation_id'),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], ondelete='CASCADE'),
    )

    # Create indexes for conversations
    op.create_index('idx_conversations_user_id', 'conversations', ['user_id'])
    op.create_index(
        'idx_conversations_user_active',
        'conversations',
        ['user_id'],
        unique=True,
        postgresql_where=sa.text('deleted_at IS NULL'),
    )

    # Create messages table
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
        sa.ForeignKeyConstraint(['conversation_id'], ['conversations.conversation_id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], ondelete='CASCADE'),
        sa.CheckConstraint("role IN ('user', 'assistant', 'system')", name='check_message_role_enum'),
        sa.CheckConstraint('length(content) <= 10000', name='check_message_content_length'),
    )

    # Create indexes for messages
    op.create_index('idx_messages_conversation_created', 'messages', ['conversation_id', 'created_at'])
    op.create_index('idx_messages_user_id', 'messages', ['user_id'])

def downgrade():
    op.drop_table('messages')
    op.drop_table('conversations')
```

---

## Compliance Checklist

✅ **User-Scoped Data**: All entities have `user_id` foreign key
✅ **Soft Deletes**: `deleted_at` timestamp instead of hard delete
✅ **Audit Timestamps**: `created_at`, `updated_at` on Conversation
✅ **UUID Primary Keys**: No sequential integers exposed in URLs
✅ **Indexed Foreign Keys**: All foreign keys have indexes
✅ **UTC Timestamps**: All TIMESTAMPTZ fields store UTC
✅ **ON DELETE CASCADE**: Prevent orphaned records
✅ **Check Constraints**: Enforce data integrity at database level

**Constitutional Alignment**: All database design standards (Section 3) satisfied.
