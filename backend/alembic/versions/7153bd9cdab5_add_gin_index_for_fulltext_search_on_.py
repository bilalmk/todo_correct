"""add gin index for fulltext search on tasks

Revision ID: 7153bd9cdab5
Revises: 60b6220ba320
Create Date: 2025-12-29 21:17:28.637610

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = '7153bd9cdab5'
down_revision: Union[str, None] = '60b6220ba320'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add GIN index for full-text search on tasks table."""
    # Create GIN index using to_tsvector for full-text search
    # This index combines title and description fields for search
    # Uses English language configuration for stemming
    op.execute("""
        CREATE INDEX idx_tasks_fulltext_search ON tasks
        USING gin(to_tsvector('english', coalesce(title, '') || ' ' || coalesce(description, '')))
    """)


def downgrade() -> None:
    """Remove GIN index for full-text search."""
    # Drop the GIN index
    op.execute("DROP INDEX IF EXISTS idx_tasks_fulltext_search")
