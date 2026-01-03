"""update_foreign_keys_to_better_auth_user_uuid

Revision ID: 51057b6b3956
Revises: 67f8cd33600c
Create Date: 2026-01-02 14:03:23.452123

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = '51057b6b3956'
down_revision: Union[str, None] = '67f8cd33600c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Update foreign keys to point to Better Auth user.uuid instead of users.id.

    This migrates all foreign key relationships from the custom users table
    to the Better Auth user table, using the uuid column as the reference.
    """
    # Tasks table: user_id FK
    op.drop_constraint('tasks_user_id_fkey', 'tasks', type_='foreignkey')
    op.create_foreign_key(
        'tasks_user_uuid_fkey',
        'tasks',
        'user',
        ['user_id'],  # Column name stays the same
        ['uuid'],      # Now references user.uuid instead of users.id
        ondelete='CASCADE'
    )

    # Tags table: user_id FK
    op.drop_constraint('tags_user_id_fkey', 'tags', type_='foreignkey')
    op.create_foreign_key(
        'tags_user_uuid_fkey',
        'tags',
        'user',
        ['user_id'],
        ['uuid'],
        ondelete='CASCADE'
    )

    # Notifications table: user_id FK
    op.drop_constraint('notifications_user_id_fkey', 'notifications', type_='foreignkey')
    op.create_foreign_key(
        'notifications_user_uuid_fkey',
        'notifications',
        'user',
        ['user_id'],
        ['uuid'],
        ondelete='CASCADE'
    )


def downgrade() -> None:
    """Rollback: Point foreign keys back to custom users table."""
    # Notifications table
    op.drop_constraint('notifications_user_uuid_fkey', 'notifications', type_='foreignkey')
    op.create_foreign_key(
        'notifications_user_id_fkey',
        'notifications',
        'users',
        ['user_id'],
        ['id'],
        ondelete='CASCADE'
    )

    # Tags table
    op.drop_constraint('tags_user_uuid_fkey', 'tags', type_='foreignkey')
    op.create_foreign_key(
        'tags_user_id_fkey',
        'tags',
        'users',
        ['user_id'],
        ['id'],
        ondelete='CASCADE'
    )

    # Tasks table
    op.drop_constraint('tasks_user_uuid_fkey', 'tasks', type_='foreignkey')
    op.create_foreign_key(
        'tasks_user_id_fkey',
        'tasks',
        'users',
        ['user_id'],
        ['id'],
        ondelete='CASCADE'
    )
