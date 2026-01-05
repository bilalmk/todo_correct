"""Application configuration using Pydantic Settings."""
from pydantic_settings import BaseSettings, SettingsConfigDict
import os
from dotenv import load_dotenv

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

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

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

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
# Global settings instance
settings = Settings(DATABASE_URL=DATABASE_URL)
