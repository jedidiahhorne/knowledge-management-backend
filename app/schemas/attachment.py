"""Attachment schemas."""
from datetime import datetime

from pydantic import BaseModel, field_serializer


class AttachmentResponse(BaseModel):
    """Schema for attachment response."""

    id: int
    filename: str
    file_path: str
    file_size: int | None
    mime_type: str | None
    note_id: int
    created_at: datetime

    @field_serializer("created_at")
    def serialize_datetime(self, dt: datetime, _info):
        """Serialize datetime to ISO format string."""
        return dt.isoformat()

    model_config = {"from_attributes": True}

