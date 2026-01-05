"""Migration testing script to verify up/down migrations."""
import pytest
from alembic import command
from alembic.config import Config
import os


@pytest.fixture
def alembic_config():
    """Create Alembic configuration."""
    config_path = os.path.join(os.path.dirname(__file__), "..", "..", "alembic.ini")
    return Config(config_path)


def test_migrations_up_and_down(alembic_config):
    """Test that migrations can be applied and reversed."""
    # Downgrade to base
    command.downgrade(alembic_config, "base")

    # Upgrade to head
    command.upgrade(alembic_config, "head")

    # Downgrade one step
    command.downgrade(alembic_config, "-1")

    # Upgrade back to head
    command.upgrade(alembic_config, "head")


def test_migration_history(alembic_config):
    """Test that migration history is consistent."""
    # This will raise an error if history is broken
    command.history(alembic_config)
