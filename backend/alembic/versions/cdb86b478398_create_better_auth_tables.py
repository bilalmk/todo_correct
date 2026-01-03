"""create_better_auth_tables

Revision ID: cdb86b478398
Revises: 999_convert_user_id_to_uuid
Create Date: 2026-01-02 02:35:50.331526

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = 'cdb86b478398'
down_revision: Union[str, None] = '999_convert_user_id_to_uuid'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
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
    op.create_table(
        'session',
        sa.Column('id', sa.String(), nullable=False),
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

    # Create BetterAuth account table
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

    # Create BetterAuth verification table
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


def downgrade() -> None:
    # Drop tables in reverse order (due to foreign key constraints)
    op.drop_index('idx_verification_identifier', table_name='verification')
    op.drop_table('verification')

    op.drop_index('idx_account_userId', table_name='account')
    op.drop_table('account')

    op.drop_index('idx_session_userId', table_name='session')
    op.drop_table('session')

    op.drop_table('user')
