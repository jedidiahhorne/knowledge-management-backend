"""Knowledge item schemas."""
from datetime import datetime

from pydantic import BaseModel, Field


class KnowledgeItemBase(BaseModel):
    """Base schema for knowledge items."""

    title: str = Field(..., min_length=1, max_length=255, description="Title of the knowledge item")
    content: str | None = Field(None, description="Content of the knowledge item")
    tags: str | None = Field(None, max_length=500, description="Comma-separated tags")
    category: str | None = Field(None, max_length=100, description="Category of the knowledge item")


class KnowledgeItemCreate(KnowledgeItemBase):
    """Schema for creating a knowledge item."""

    pass


class KnowledgeItemUpdate(BaseModel):
    """Schema for updating a knowledge item."""

    title: str | None = Field(None, min_length=1, max_length=255)
    content: str | None = None
    tags: str | None = Field(None, max_length=500)
    category: str | None = Field(None, max_length=100)


class KnowledgeItemResponse(KnowledgeItemBase):
    """Schema for knowledge item response."""

    id: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}

