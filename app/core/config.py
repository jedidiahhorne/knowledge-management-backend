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

    # JWT Authentication
    SECRET_KEY: str = "your-secret-key-change-this-in-production-use-env-variable"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Password Reset
    PASSWORD_RESET_TOKEN_EXPIRE_HOURS: int = 1

    # File Upload
    UPLOAD_DIR: str = "./uploads"
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10 MB in bytes
    ALLOWED_EXTENSIONS: set[str] = {
        # Images
        "jpg", "jpeg", "png", "gif", "webp", "svg",
        # Documents
        "pdf", "doc", "docx", "xls", "xlsx", "ppt", "pptx",
        # Text
        "txt", "md", "csv",
        # Archives
        "zip", "rar", "7z",
    }

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )


settings = Settings()

