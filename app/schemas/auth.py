"""Authentication schemas."""
from datetime import datetime

from pydantic import BaseModel, EmailStr, Field, field_serializer


class UserRegister(BaseModel):
    """Schema for user registration."""

    email: EmailStr
    username: str = Field(..., min_length=3, max_length=100)
    password: str = Field(..., min_length=8, max_length=100)
    full_name: str | None = Field(None, max_length=255)


class UserLogin(BaseModel):
    """Schema for user login."""

    username: str
    password: str


class Token(BaseModel):
    """Schema for access token response."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenRefresh(BaseModel):
    """Schema for token refresh request."""

    refresh_token: str


class PasswordResetRequest(BaseModel):
    """Schema for password reset request."""

    email: EmailStr


class PasswordReset(BaseModel):
    """Schema for password reset."""

    token: str
    new_password: str = Field(..., min_length=8, max_length=100)


class PasswordChange(BaseModel):
    """Schema for password change (requires current password)."""

    current_password: str
    new_password: str = Field(..., min_length=8, max_length=100)


class UserResponse(BaseModel):
    """Schema for user response (without sensitive data)."""

    id: int
    email: str
    username: str
    full_name: str | None
    is_active: bool
    is_superuser: bool
    created_at: datetime

    @field_serializer("created_at")
    def serialize_datetime(self, dt: datetime, _info):
        """Serialize datetime to ISO format string."""
        return dt.isoformat()

    model_config = {"from_attributes": True}

