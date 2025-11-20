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

    # File Upload - S3/MinIO Storage
    USE_S3_STORAGE: bool = False  # Set to True to use S3/MinIO instead of local storage
    S3_ENDPOINT_URL: str | None = None  # MinIO endpoint (e.g., https://minio.example.com)
    # Railway MinIO uses ROOT_USER and ROOT_PASSWORD (these map to S3_ACCESS_KEY_ID and S3_SECRET_ACCESS_KEY)
    # For AWS S3, use S3_ACCESS_KEY_ID and S3_SECRET_ACCESS_KEY directly
    S3_ACCESS_KEY_ID: str | None = None  # MinIO root user (or ROOT_USER from Railway) or AWS access key
    S3_SECRET_ACCESS_KEY: str | None = None  # MinIO root password (or ROOT_PASSWORD from Railway) or AWS secret key
    # Alternative Railway MinIO variable names (will be used if S3_ACCESS_KEY_ID/SECRET not set)
    ROOT_USER: str | None = None  # Railway MinIO root user
    ROOT_PASSWORD: str | None = None  # Railway MinIO root password
    S3_BUCKET_NAME: str = "files"  # Default bucket name
    S3_REGION: str = "us-east-1"  # Not used for MinIO but required by boto3
    S3_USE_SSL: bool = True
    S3_VERIFY_SSL: bool = True  # Set to False for self-signed certificates (common with MinIO)

    # File Upload - Local Storage (fallback)
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

