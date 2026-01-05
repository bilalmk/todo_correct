"""create_jwks_table_for_jwt_plugin

Revision ID: 8f0d6466ab3e
Revises: 87756bd28f56
Create Date: 2026-01-02 03:08:28.262419

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = '8f0d6466ab3e'
down_revision: Union[str, None] = '87756bd28f56'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
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


def downgrade() -> None:
    """Drop JWKS table."""
    op.drop_table('jwks')
