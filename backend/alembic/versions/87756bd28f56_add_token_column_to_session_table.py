"""add_token_column_to_session_table

Revision ID: 87756bd28f56
Revises: cdb86b478398
Create Date: 2026-01-02 02:59:30.255555

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = '87756bd28f56'
down_revision: Union[str, None] = 'cdb86b478398'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add token column to session table
    # This is a required field for Better Auth session management
    op.add_column('session', sa.Column('token', sa.String(), nullable=False, server_default=''))

    # Remove server_default after adding column (it's just for the migration)
    op.alter_column('session', 'token', server_default=None)


def downgrade() -> None:
    # Remove token column from session table
    op.drop_column('session', 'token')
