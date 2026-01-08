"""
Configuration settings for Todo MCP Server.

Uses Pydantic Settings for environment variable management with validation.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Literal


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.

    All settings have sensible defaults except DATABASE_URL (required).
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Database Configuration
    database_url: str = ""  # Required: PostgreSQL connection URL

    # Server Configuration
    mcp_server_port: int = 8001  # HTTP server port (separate from backend)
    mcp_server_host: str = "0.0.0.0"  # Bind to all interfaces

    # Logging Configuration
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"

    def __init__(self, **kwargs):
        """Initialize settings and validate required fields."""
        super().__init__(**kwargs)
        if not self.database_url:
            raise ValueError(
                "DATABASE_URL environment variable is required. "
                "Please set it in .env file or environment."
            )


# Global settings instance (singleton pattern)
_settings: Settings | None = None


def get_settings() -> Settings:
    """
    Get or create global settings instance.

    Returns:
        Settings: Application settings singleton

    Example:
        >>> settings = get_settings()
        >>> print(settings.database_url)
    """
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings
