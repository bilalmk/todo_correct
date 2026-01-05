"""add sort_order column to tasks table

Revision ID: a1b2c3d4e5f6
Revises: 3dc4cf3ae3e6
Create Date: 2026-01-03 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, None] = '3dc4cf3ae3e6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Add sort_order column to tasks table for drag-and-drop task reordering.

    Steps:
    1. Add nullable sort_order column (allows existing rows to accept NULL)
    2. Backfill existing tasks with created_at timestamp (Unix epoch milliseconds)
    3. Make column non-nullable
    4. Create composite index (user_id, sort_order) for efficient sorted queries
    """
    # Step 1: Add nullable column
    op.add_column('tasks', sa.Column('sort_order', sa.BigInteger(), nullable=True))

    # Step 2: Backfill existing tasks
    # Set sort_order = created_at timestamp in milliseconds (Unix epoch)
    # This preserves chronological order for existing tasks
    op.execute("""
        UPDATE tasks
        SET sort_order = EXTRACT(EPOCH FROM created_at) * 1000
        WHERE sort_order IS NULL
    """)

    # Step 3: Make column non-nullable and set default
    op.alter_column('tasks', 'sort_order', nullable=False)

    # Step 4: Create composite index for efficient sorted queries
    # Index on (user_id, sort_order) for "SELECT * FROM tasks WHERE user_id = ? ORDER BY sort_order"
    op.create_index('idx_tasks_user_sort_order', 'tasks', ['user_id', 'sort_order'], unique=False)


def downgrade() -> None:
    """
    Remove sort_order column and associated index.

    This restores the table to its previous state before drag-and-drop feature.
    """
    # Drop composite index first
    op.drop_index('idx_tasks_user_sort_order', table_name='tasks')

    # Drop sort_order column
    op.drop_column('tasks', 'sort_order')
