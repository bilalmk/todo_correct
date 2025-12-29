"""Rollback testing procedure for database migrations."""
import pytest
from alembic import command
from alembic.config import Config
import os


@pytest.fixture
def alembic_config():
    """Create Alembic configuration."""
    config_path = os.path.join(os.path.dirname(__file__), "..", "..", "alembic.ini")
    return Config(config_path)


def test_rollback_to_base_and_forward(alembic_config):
    """Test rolling back to base and migrating forward."""
    # Start from head
    command.upgrade(alembic_config, "head")

    # Rollback to base
    command.downgrade(alembic_config, "base")

    # Migrate forward again
    command.upgrade(alembic_config, "head")


def test_rollback_one_migration(alembic_config):
    """Test rolling back a single migration."""
    # Ensure we're at head
    command.upgrade(alembic_config, "head")

    # Rollback one migration
    command.downgrade(alembic_config, "-1")

    # Verify we can upgrade again
    command.upgrade(alembic_config, "head")


def test_rollback_to_specific_revision(alembic_config):
    """Test rolling back to a specific revision."""
    # Upgrade to head first
    command.upgrade(alembic_config, "head")

    # Rollback to users table creation (first migration)
    command.downgrade(alembic_config, "001")

    # Upgrade back to head
    command.upgrade(alembic_config, "head")
