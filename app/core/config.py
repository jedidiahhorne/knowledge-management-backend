"""Application configuration using Pydantic settings."""
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings with environment variable support."""

    # Environment
    ENVIRONMENT: Literal["development", "production"] = "development"
    DEBUG: bool = True

    # API
    API_V1_PREFIX: str = "/api/v1"
    PROJECT_NAME: str = "Knowledge Management API"

    # Database
    DATABASE_URL: str = "sqlite:///./knowledge_management.db"
    # For PostgreSQL: "postgresql://user:password@localhost/dbname"
    # For MySQL: "mysql+pymysql://user:password@localhost/dbname"

    # CORS
    CORS_ORIGINS: list[str] = ["http://localhost:3000", "http://localhost:8000"]

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )


settings = Settings()

