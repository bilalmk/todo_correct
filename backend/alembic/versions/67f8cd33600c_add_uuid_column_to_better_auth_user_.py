"""add_uuid_column_to_better_auth_user_table

Revision ID: 67f8cd33600c
Revises: 8f0d6466ab3e
Create Date: 2026-01-02 14:01:59.262776

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = '67f8cd33600c'
down_revision: Union[str, None] = '8f0d6466ab3e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add UUID column to Better Auth user table for application use.

    Better Auth uses String IDs internally, but we add a UUID column
    for type consistency across our application's API routes and foreign keys.
    """
    # 1. Add uuid column (NOT NULL with default)
    # No existing users to migrate, so can create as NOT NULL directly
    op.add_column(
        'user',
        sa.Column(
            'uuid',
            sa.UUID(),
            nullable=False,
            server_default=sa.text('gen_random_uuid()')
        )
    )

    # 2. Create unique constraint and index
    op.create_unique_constraint('uq_user_uuid', 'user', ['uuid'])
    op.create_index('idx_user_uuid', 'user', ['uuid'])


def downgrade() -> None:
    """Remove UUID column from Better Auth user table."""
    op.drop_index('idx_user_uuid', table_name='user')
    op.drop_constraint('uq_user_uuid', 'user', type_='unique')
    op.drop_column('user', 'uuid')
