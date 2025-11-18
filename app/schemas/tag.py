"""Tag schemas."""
from datetime import datetime

from pydantic import BaseModel, Field, field_serializer


class TagBase(BaseModel):
    """Base schema for tags."""

    name: str = Field(..., min_length=1, max_length=100, description="Tag name")
    color: str | None = Field(None, max_length=7, description="Hex color code (e.g., #FF5733)")
    description: str | None = Field(None, max_length=500, description="Tag description")


class TagCreate(TagBase):
    """Schema for creating a tag."""

    pass


class TagUpdate(BaseModel):
    """Schema for updating a tag."""

    name: str | None = Field(None, min_length=1, max_length=100)
    color: str | None = Field(None, max_length=7)
    description: str | None = Field(None, max_length=500)


class TagResponse(TagBase):
    """Schema for tag response."""

    id: int
    created_at: datetime

    @field_serializer("created_at")
    def serialize_datetime(self, dt: datetime, _info):
        """Serialize datetime to ISO format string."""
        return dt.isoformat()

    model_config = {"from_attributes": True}

