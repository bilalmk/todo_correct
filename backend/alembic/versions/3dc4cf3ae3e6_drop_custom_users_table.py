"""drop_custom_users_table

Revision ID: 3dc4cf3ae3e6
Revises: 51057b6b3956
Create Date: 2026-01-02 14:03:53.849711

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = '3dc4cf3ae3e6'
down_revision: Union[str, None] = '51057b6b3956'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Drop custom users table (replaced by Better Auth user table).

    All foreign keys have been updated to point to Better Auth user.uuid,
    so it's now safe to drop the custom users table.
    """
    # Drop index first
    op.drop_index('idx_users_email', table_name='users', if_exists=True)

    # Drop the custom users table
    op.drop_table('users', if_exists=True)


def downgrade() -> None:
    """Recreate custom users table for rollback."""
    # Recreate users table with original schema
    op.create_table(
        'users',
        sa.Column('id', UUID(), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('password_hash', sa.String(length=255), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email')
    )

    # Recreate index for email lookups
    op.create_index('idx_users_email', 'users', ['email'])
