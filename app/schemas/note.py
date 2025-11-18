"""Note schemas."""
from datetime import datetime

from pydantic import BaseModel, Field, field_serializer


class TagBase(BaseModel):
    """Base schema for tags in note responses."""

    id: int
    name: str
    color: str | None = None

    model_config = {"from_attributes": True}


class NoteBase(BaseModel):
    """Base schema for notes."""

    title: str = Field(..., min_length=1, max_length=255, description="Title of the note")
    content: str | None = Field(None, description="Content of the note")
    is_pinned: bool = Field(default=False, description="Whether the note is pinned")
    is_archived: bool = Field(default=False, description="Whether the note is archived")


class NoteCreate(NoteBase):
    """Schema for creating a note."""

    tag_ids: list[int] = Field(default_factory=list, description="List of tag IDs to associate with the note")


class NoteUpdate(BaseModel):
    """Schema for updating a note."""

    title: str | None = Field(None, min_length=1, max_length=255)
    content: str | None = None
    is_pinned: bool | None = None
    is_archived: bool | None = None
    tag_ids: list[int] | None = Field(None, description="List of tag IDs to associate with the note")


class NoteResponse(NoteBase):
    """Schema for note response."""

    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime
    tags: list[TagBase] = Field(default_factory=list)

    @field_serializer("created_at", "updated_at")
    def serialize_datetime(self, dt: datetime, _info):
        """Serialize datetime to ISO format string."""
        return dt.isoformat()

    model_config = {"from_attributes": True}

