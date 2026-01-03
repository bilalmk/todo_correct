"""
Better Auth Database Migration Templates (Alembic)

These migrations ensure Better Auth tables have the correct schema for both
core authentication (session management) and JWT plugin functionality.
"""

from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


# ==============================================================================
# Migration 1: Create Better Auth Core Tables
# ==============================================================================
# Revision ID: cdb86b478398
# Revises: (your previous migration)
# Create Date: 2026-01-02 02:35:50

def create_better_auth_tables_upgrade() -> None:
    """Create all Better Auth tables with CORRECT schema including token column."""

    # Create BetterAuth user table
    op.create_table(
        'user',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('email', sa.String(), nullable=False),
        sa.Column('emailVerified', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('name', sa.String(), nullable=True),
        sa.Column('image', sa.String(), nullable=True),
        sa.Column('createdAt', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('updatedAt', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email')
    )

    # Create BetterAuth session table
    # ⚠️ IMPORTANT: Must include 'token' column!
    op.create_table(
        'session',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('token', sa.String(), nullable=False),  # ✅ REQUIRED for Better Auth
        sa.Column('userId', sa.String(), nullable=False),
        sa.Column('expiresAt', sa.DateTime(), nullable=False),
        sa.Column('ipAddress', sa.String(), nullable=True),
        sa.Column('userAgent', sa.String(), nullable=True),
        sa.Column('createdAt', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('updatedAt', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['userId'], ['user.id'], ondelete='CASCADE')
    )
    op.create_index('idx_session_userId', 'session', ['userId'])

    # Create BetterAuth account table (for OAuth providers)
    op.create_table(
        'account',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('userId', sa.String(), nullable=False),
        sa.Column('accountId', sa.String(), nullable=False),
        sa.Column('providerId', sa.String(), nullable=False),
        sa.Column('accessToken', sa.Text(), nullable=True),
        sa.Column('refreshToken', sa.Text(), nullable=True),
        sa.Column('idToken', sa.Text(), nullable=True),
        sa.Column('expiresAt', sa.DateTime(), nullable=True),
        sa.Column('password', sa.String(), nullable=True),
        sa.Column('createdAt', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('updatedAt', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['userId'], ['user.id'], ondelete='CASCADE'),
        sa.UniqueConstraint('providerId', 'accountId')
    )
    op.create_index('idx_account_userId', 'account', ['userId'])

    # Create BetterAuth verification table (for email verification)
    op.create_table(
        'verification',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('identifier', sa.String(), nullable=False),
        sa.Column('value', sa.String(), nullable=False),
        sa.Column('expiresAt', sa.DateTime(), nullable=False),
        sa.Column('createdAt', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('updatedAt', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_verification_identifier', 'verification', ['identifier'])


def create_better_auth_tables_downgrade() -> None:
    """Drop Better Auth tables in reverse order (due to foreign key constraints)."""
    op.drop_index('idx_verification_identifier', table_name='verification')
    op.drop_table('verification')

    op.drop_index('idx_account_userId', table_name='account')
    op.drop_table('account')

    op.drop_index('idx_session_userId', table_name='session')
    op.drop_table('session')

    op.drop_table('user')


# ==============================================================================
# Migration 2: Add Missing 'token' Column (if needed)
# ==============================================================================
# Revision ID: 87756bd28f56
# Revises: cdb86b478398
# Create Date: 2026-01-02 02:59:30

def add_token_column_upgrade() -> None:
    """
    Add 'token' column to session table.

    Use this migration if you created the session table WITHOUT the token column
    and are now getting errors like:
    "ERROR [Better Auth]: column 'token' of relation 'session' does not exist"
    """
    # Add token column with temporary default value
    op.add_column(
        'session',
        sa.Column('token', sa.String(), nullable=False, server_default='')
    )

    # Remove server_default (it's only needed during migration)
    op.alter_column('session', 'token', server_default=None)


def add_token_column_downgrade() -> None:
    """Remove token column from session table."""
    op.drop_column('session', 'token')


# ==============================================================================
# Migration 3: Create JWKS Table (JWT Plugin)
# ==============================================================================
# This migration is for the JWT plugin only. Run AFTER enabling jwt() plugin.

def create_jwks_table_upgrade() -> None:
    """
    Create JWKS table for Better Auth JWT plugin.

    Required when using the jwt() plugin in Better Auth config.
    Stores public/private key pairs for JWT signature verification.
    """
    op.create_table(
        'jwks',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('publicKey', sa.String(), nullable=False),
        sa.Column('privateKey', sa.String(), nullable=False),
        sa.Column('createdAt', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('expiresAt', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )


def create_jwks_table_downgrade() -> None:
    """Drop JWKS table."""
    op.drop_table('jwks')


# ==============================================================================
# Usage Instructions
# ==============================================================================

"""
## How to Use These Migrations

### Option 1: Create All Tables at Once (Recommended)

Generate a single migration that creates all Better Auth tables:

```bash
alembic revision -m "create_better_auth_tables"
```

Copy the `create_better_auth_tables_upgrade()` function to the `upgrade()` function,
and the `create_better_auth_tables_downgrade()` function to the `downgrade()` function.

Then run:
```bash
alembic upgrade head
```

### Option 2: Fix Missing Token Column

If you already created the session table but it's missing the token column:

```bash
alembic revision -m "add_token_column_to_session_table"
```

Copy the `add_token_column_upgrade()` and `add_token_column_downgrade()` functions.

Then run:
```bash
alembic upgrade head
```

### Option 3: Add JWT Plugin Support

After enabling the jwt() plugin in Better Auth:

```bash
alembic revision -m "create_jwks_table_for_jwt_plugin"
```

Copy the `create_jwks_table_upgrade()` and `create_jwks_table_downgrade()` functions.

Then run:
```bash
alembic upgrade head
```

## Verification

After running migrations, verify the schema:

```python
# Check session table has token column
python -c "
import asyncio
from sqlalchemy import text
from app.core.database import engine

async def check():
    async with engine.begin() as conn:
        result = await conn.execute(text('''
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns
            WHERE table_name = 'session'
            ORDER BY ordinal_position
        '''))
        print('Session table columns:')
        for row in result:
            print(f'  {row[0]:<20} {row[1]:<20} nullable={row[2]}')

asyncio.run(check())
"
```

Expected output should include:
- token (character varying, NO)
- userId (character varying, NO)
- expiresAt (timestamp without time zone, NO)
- All other session columns

## Common Issues

### "column 'token' does not exist"
- Run the `add_token_column_upgrade()` migration
- Or recreate the session table with the correct schema

### "relation 'jwks' does not exist"
- Run the `create_jwks_table_upgrade()` migration
- Ensure jwt() plugin is enabled in Better Auth config

### "JWKS response missing 'keys' field"
- JWT plugin not enabled in frontend Better Auth config
- Run: npx @better-auth/cli migrate
"""
