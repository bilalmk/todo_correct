"""Convert users.id from INTEGER to UUID and update all foreign keys

Revision ID: 999_convert_user_id_to_uuid
Revises: 7153bd9cdab5
Create Date: 2025-12-30

CRITICAL BREAKING CHANGE:
This migration converts the users table primary key from INTEGER to UUID,
and updates all foreign key references in tasks, tags, task_tags, and notifications.

DANGER: This migration will LOSE DATA if not handled carefully!
- All existing user IDs will be replaced with UUIDs
- Authentication tokens referencing old integer IDs will become invalid
- Client applications must re-authenticate after this migration

PREREQUISITES:
1. BACKUP YOUR DATABASE before running this migration
2. Notify all users that they will need to log in again
3. Test this migration on a staging environment first
4. Schedule downtime window for production deployment

ROLLBACK STRATEGY:
- Downgrade function is provided but data conversion is ONE-WAY
- Downgrading will LOSE UUID mappings
- Only downgrade in emergency; prefer forward-only deployment
"""
from typing import Sequence, Union
from uuid import uuid4

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID


# revision identifiers, used by Alembic.
revision: str = '999_convert_user_id_to_uuid'
down_revision: Union[str, None] = '7153bd9cdab5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Convert users.id from INTEGER to UUID and update all foreign keys.

    Steps:
    1. Add temporary UUID column to users table
    2. Generate UUIDs for existing users
    3. Add temporary UUID columns to all tables with user_id FK
    4. Copy UUID values from users to referencing tables
    5. Drop old INTEGER foreign keys
    6. Rename UUID columns to replace old columns
    7. Recreate foreign key constraints with CASCADE
    """

    # ============================================================================
    # STEP 1: Add temporary UUID column to users table
    # ============================================================================
    print("Step 1/7: Adding temporary UUID column to users table...")
    op.add_column('users', sa.Column('id_uuid_temp', UUID(), nullable=True))

    # Generate UUIDs for all existing users
    print("Step 1b/7: Generating UUIDs for existing users...")
    op.execute("""
        UPDATE users
        SET id_uuid_temp = gen_random_uuid()
        WHERE id_uuid_temp IS NULL
    """)

    # Make the UUID column NOT NULL now that all rows have values
    op.alter_column('users', 'id_uuid_temp', nullable=False)


    # ============================================================================
    # STEP 2: Add temporary UUID columns to all referencing tables
    # ============================================================================
    print("Step 2/7: Adding temporary UUID columns to referencing tables...")

    # Tasks table
    op.add_column('tasks', sa.Column('user_id_uuid_temp', UUID(), nullable=True))

    # Tags table
    op.add_column('tags', sa.Column('user_id_uuid_temp', UUID(), nullable=True))

    # Notifications table
    op.add_column('notifications', sa.Column('user_id_uuid_temp', UUID(), nullable=True))


    # ============================================================================
    # STEP 3: Copy UUID values from users to referencing tables
    # ============================================================================
    print("Step 3/7: Copying UUID values to referencing tables...")

    # Update tasks.user_id_uuid_temp from users.id_uuid_temp
    op.execute("""
        UPDATE tasks t
        SET user_id_uuid_temp = u.id_uuid_temp
        FROM users u
        WHERE t.user_id = u.id
    """)

    # Update tags.user_id_uuid_temp from users.id_uuid_temp
    op.execute("""
        UPDATE tags t
        SET user_id_uuid_temp = u.id_uuid_temp
        FROM users u
        WHERE t.user_id = u.id
    """)

    # Update notifications.user_id_uuid_temp from users.id_uuid_temp
    op.execute("""
        UPDATE notifications n
        SET user_id_uuid_temp = u.id_uuid_temp
        FROM users u
        WHERE n.user_id = u.id
    """)

    # Make UUID columns NOT NULL
    op.alter_column('tasks', 'user_id_uuid_temp', nullable=False)
    op.alter_column('tags', 'user_id_uuid_temp', nullable=False)
    op.alter_column('notifications', 'user_id_uuid_temp', nullable=False)


    # ============================================================================
    # STEP 4: Drop old foreign key constraints
    # ============================================================================
    print("Step 4/7: Dropping old foreign key constraints...")

    op.drop_constraint('tasks_user_id_fkey', 'tasks', type_='foreignkey')
    op.drop_constraint('tags_user_id_fkey', 'tags', type_='foreignkey')
    op.drop_constraint('notifications_user_id_fkey', 'notifications', type_='foreignkey')


    # ============================================================================
    # STEP 5: Drop old INTEGER columns and indexes
    # ============================================================================
    print("Step 5/7: Dropping old INTEGER columns...")

    # Drop indexes on old user_id columns
    op.drop_index('ix_tasks_user_id', table_name='tasks', if_exists=True)
    op.drop_index('ix_tags_user_id', table_name='tags', if_exists=True)
    op.drop_index('ix_notifications_user_id', table_name='notifications', if_exists=True)

    # Drop old primary key and user_id columns
    op.drop_constraint('users_pkey', 'users', type_='primary')
    op.drop_column('users', 'id')
    op.drop_column('tasks', 'user_id')
    op.drop_column('tags', 'user_id')
    op.drop_column('notifications', 'user_id')


    # ============================================================================
    # STEP 6: Rename UUID columns to final names
    # ============================================================================
    print("Step 6/7: Renaming UUID columns to final names...")

    op.alter_column('users', 'id_uuid_temp', new_column_name='id')
    op.alter_column('tasks', 'user_id_uuid_temp', new_column_name='user_id')
    op.alter_column('tags', 'user_id_uuid_temp', new_column_name='user_id')
    op.alter_column('notifications', 'user_id_uuid_temp', new_column_name='user_id')


    # ============================================================================
    # STEP 7: Recreate primary key and foreign key constraints
    # ============================================================================
    print("Step 7/7: Recreating constraints and indexes...")

    # Add primary key constraint on users.id
    op.create_primary_key('users_pkey', 'users', ['id'])

    # Recreate foreign key constraints with CASCADE
    op.create_foreign_key(
        'tasks_user_id_fkey',
        'tasks', 'users',
        ['user_id'], ['id'],
        ondelete='CASCADE'
    )

    op.create_foreign_key(
        'tags_user_id_fkey',
        'tags', 'users',
        ['user_id'], ['id'],
        ondelete='CASCADE'
    )

    op.create_foreign_key(
        'notifications_user_id_fkey',
        'notifications', 'users',
        ['user_id'], ['id'],
        ondelete='CASCADE'
    )

    # Recreate indexes on user_id columns
    op.create_index('ix_tasks_user_id', 'tasks', ['user_id'])
    op.create_index('ix_tags_user_id', 'tags', ['user_id'])
    op.create_index('ix_notifications_user_id', 'notifications', ['user_id'])

    print("✅ Migration completed successfully!")
    print("⚠️  WARNING: All JWT tokens are now invalid - users must re-authenticate")


def downgrade() -> None:
    """
    DANGER: Downgrade is NOT RECOMMENDED and will LOSE DATA.

    This converts UUIDs back to auto-incrementing integers, but:
    - UUID → INTEGER mapping is arbitrary (uses ROW_NUMBER)
    - All existing JWTs will be invalidated
    - Any external systems referencing UUIDs will break

    Only use this in EMERGENCY situations on non-production data.
    """

    print("⚠️  WARNING: Downgrading from UUID to INTEGER - DATA LOSS IMMINENT")
    print("This operation is IRREVERSIBLE and should only be used in emergencies!")

    # Add temporary INTEGER columns
    op.add_column('users', sa.Column('id_int_temp', sa.Integer(), autoincrement=True, nullable=True))
    op.add_column('tasks', sa.Column('user_id_int_temp', sa.Integer(), nullable=True))
    op.add_column('tags', sa.Column('user_id_int_temp', sa.Integer(), nullable=True))
    op.add_column('notifications', sa.Column('user_id_int_temp', sa.Integer(), nullable=True))

    # Generate sequential integers for users (ARBITRARY MAPPING - DATA LOSS)
    op.execute("""
        UPDATE users
        SET id_int_temp = (
            SELECT ROW_NUMBER() OVER (ORDER BY created_at, id)
            FROM (SELECT id, created_at FROM users) AS u
            WHERE u.id = users.id
        )
    """)

    # Copy integer IDs to referencing tables
    op.execute("""
        UPDATE tasks t
        SET user_id_int_temp = u.id_int_temp
        FROM users u
        WHERE t.user_id = u.id
    """)

    op.execute("""
        UPDATE tags t
        SET user_id_int_temp = u.id_int_temp
        FROM users u
        WHERE t.user_id = u.id
    """)

    op.execute("""
        UPDATE notifications n
        SET user_id_int_temp = u.id_int_temp
        FROM users u
        WHERE n.user_id = u.id
    """)

    # Make columns NOT NULL
    op.alter_column('users', 'id_int_temp', nullable=False)
    op.alter_column('tasks', 'user_id_int_temp', nullable=False)
    op.alter_column('tags', 'user_id_int_temp', nullable=False)
    op.alter_column('notifications', 'user_id_int_temp', nullable=False)

    # Drop foreign keys and UUID columns
    op.drop_constraint('tasks_user_id_fkey', 'tasks', type_='foreignkey')
    op.drop_constraint('tags_user_id_fkey', 'tags', type_='foreignkey')
    op.drop_constraint('notifications_user_id_fkey', 'notifications', type_='foreignkey')

    op.drop_index('ix_tasks_user_id', table_name='tasks')
    op.drop_index('ix_tags_user_id', table_name='tags')
    op.drop_index('ix_notifications_user_id', table_name='notifications')

    op.drop_constraint('users_pkey', 'users', type_='primary')
    op.drop_column('users', 'id')
    op.drop_column('tasks', 'user_id')
    op.drop_column('tags', 'user_id')
    op.drop_column('notifications', 'user_id')

    # Rename integer columns back
    op.alter_column('users', 'id_int_temp', new_column_name='id')
    op.alter_column('tasks', 'user_id_int_temp', new_column_name='user_id')
    op.alter_column('tags', 'user_id_int_temp', new_column_name='user_id')
    op.alter_column('notifications', 'user_id_int_temp', new_column_name='user_id')

    # Recreate constraints
    op.create_primary_key('users_pkey', 'users', ['id'])
    op.create_foreign_key('tasks_user_id_fkey', 'tasks', 'users', ['user_id'], ['id'], ondelete='CASCADE')
    op.create_foreign_key('tags_user_id_fkey', 'tags', 'users', ['user_id'], ['id'], ondelete='CASCADE')
    op.create_foreign_key('notifications_user_id_fkey', 'notifications', 'users', ['user_id'], ['id'], ondelete='CASCADE')

    op.create_index('ix_tasks_user_id', 'tasks', ['user_id'])
    op.create_index('ix_tags_user_id', 'tags', ['user_id'])
    op.create_index('ix_notifications_user_id', 'notifications', ['user_id'])

    print("⚠️  Downgrade completed - UUID → INTEGER conversion done (with data loss)")
