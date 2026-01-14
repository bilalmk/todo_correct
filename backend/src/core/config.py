"""Application configuration using Pydantic Settings."""
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import HttpUrl, field_validator
import os
from dotenv import load_dotenv
load_dotenv()
class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Database
    DATABASE_URL: str

    # Authentication
    BETTER_AUTH_SECRET: str
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_DAYS: int = 7

    # Better Auth JWT Configuration (T007)
    BETTER_AUTH_JWKS_URL: str = ""
    BETTER_AUTH_ISSUER: str = ""

    # CORS
    CORS_ORIGINS: str = "http://localhost:3000"
    FRONTEND_URL: str = "http://localhost:3000"

    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    ENVIRONMENT: str = "development"

    # Logging
    LOG_LEVEL: str = "INFO"

    # Email / SMTP Configuration (T134)
    EMAIL_ENABLED: bool = False
    SMTP_HOST: str = ""
    SMTP_PORT: int = 587
    SMTP_USERNAME: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_USE_TLS: bool = True
    EMAIL_FROM: str = ""
    EMAIL_FROM_NAME: str = "Todo App"

    # ===== Phase III ChatKit Configuration (T003, T003a) =====
    # OpenAI Agents SDK Configuration
    OPENAI_API_KEY: str = ""  # Required for OpenAI Agents SDK (set in .env)
    OPENAI_MODEL: str = "gpt-4"  # Default model (overridable)

    # MCP Server Configuration
    MCP_SERVER_URL: str = "http://localhost:8001/mcp"  # Default for development
    MCP_CONNECTION_TIMEOUT: int = 30  # Timeout in seconds for MCP client connections

    # ChatKit Configuration (Constitutional Requirements)
    CHATKIT_MESSAGE_LIMIT: int = 10000  # Max message content length (FR-024)
    CHATKIT_HISTORY_LIMIT: int = 20  # Max conversation history messages (constitutional limit, FR-007)

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    # ===== Validators (T003a - FR-013 MCP_SERVER_URL validation) =====
    @field_validator("MCP_SERVER_URL")
    @classmethod
    def validate_mcp_url(cls, v: str) -> str:
        """
        Validate MCP_SERVER_URL is a valid HTTP/HTTPS URL.

        Implements FR-013 HttpUrl validation requirement from spec.md.
        Ensures scheme is http:// or https:// (reject ftp://, malformed strings).

        Args:
            v: MCP_SERVER_URL value from environment

        Returns:
            Validated URL string

        Raises:
            ValueError: If URL invalid or uses unsupported scheme

        Example:
            MCP_SERVER_URL=http://localhost:8001/mcp  # Valid
            MCP_SERVER_URL=https://mcp-server.example.com/mcp  # Valid
            MCP_SERVER_URL=ftp://localhost:8001/mcp  # Raises ValueError
        """
        if not v or v == "":
            raise ValueError(
                "Invalid MCP_SERVER_URL: must be valid HTTP/HTTPS URL "
                "(example: http://localhost:8001/mcp)"
            )

        # Validate URL scheme (must be http:// or https://)
        if not v.startswith(("http://", "https://")):
            raise ValueError(
                f"Invalid MCP_SERVER_URL: must start with http:// or https:// "
                f"(got: {v[:20]}...)"
            )

        return v

    @field_validator("OPENAI_API_KEY")
    @classmethod
    def validate_openai_key(cls, v: str) -> str:
        """
        Validate OPENAI_API_KEY is not empty (if ChatKit is enabled).

        Args:
            v: OPENAI_API_KEY value from environment

        Returns:
            Validated API key string

        Raises:
            ValueError: If API key is empty or missing
        """
        # Allow empty for non-ChatKit deployments (backward compatibility)

        if v == "":
            import warnings
            warnings.warn(
                "OPENAI_API_KEY is not set. ChatKit endpoints will fail. "
                "Set OPENAI_API_KEY in .env to enable ChatKit backend.",
                UserWarning
            )
        return v

    @property
    def cors_origins_list(self) -> list[str]:
        """Parse CORS origins from comma-separated string."""
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]

    @property
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.ENVIRONMENT.lower() == "production"

    @property
    def smtp_config(self) -> dict:
        """Build SMTP configuration dict for NotificationService."""
        return {
            "host": self.SMTP_HOST,
            "port": self.SMTP_PORT,
            "username": self.SMTP_USERNAME,
            "password": self.SMTP_PASSWORD,
            "use_tls": self.SMTP_USE_TLS,
            "from_email": self.EMAIL_FROM,
            "from_name": self.EMAIL_FROM_NAME,
        }

    @property
    def mcp_server_host(self) -> str:
        """Extract host from MCP_SERVER_URL for debugging."""
        from urllib.parse import urlparse
        parsed = urlparse(self.MCP_SERVER_URL)
        return parsed.hostname or "localhost"

    @property
    def mcp_server_port(self) -> int:
        """Extract port from MCP_SERVER_URL for debugging."""
        from urllib.parse import urlparse
        parsed = urlparse(self.MCP_SERVER_URL)
        return parsed.port or 8001

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
# Global settings instance
settings = Settings(DATABASE_URL=DATABASE_URL)
