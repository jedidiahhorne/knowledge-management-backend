"""Search schemas."""
from datetime import datetime

from pydantic import BaseModel, Field

from app.schemas.note import NoteResponse
from app.schemas.tag import TagResponse


class SearchNotesRequest(BaseModel):
    """Schema for note search request."""

    query: str | None = Field(None, description="Search query for title and content")
    tag_ids: list[int] | None = Field(None, description="Filter by tag IDs")
    tag_names: list[str] | None = Field(None, description="Filter by tag names")
    is_pinned: bool | None = Field(None, description="Filter by pinned status")
    is_archived: bool | None = Field(None, description="Filter by archived status")
    created_after: datetime | None = Field(None, description="Filter notes created after this date")
    created_before: datetime | None = Field(None, description="Filter notes created before this date")
    updated_after: datetime | None = Field(None, description="Filter notes updated after this date")
    updated_before: datetime | None = Field(None, description="Filter notes updated before this date")
    skip: int = Field(0, ge=0, description="Number of results to skip")
    limit: int = Field(100, ge=1, le=1000, description="Maximum number of results to return")


class SearchTagsRequest(BaseModel):
    """Schema for tag search request."""

    query: str | None = Field(None, description="Search query for tag name and description")
    skip: int = Field(0, ge=0, description="Number of results to skip")
    limit: int = Field(100, ge=1, le=1000, description="Maximum number of results to return")


class SearchNotesResponse(BaseModel):
    """Schema for note search response."""

    notes: list[NoteResponse] = Field(..., description="List of matching notes")
    total: int = Field(..., description="Total number of matching notes")
    skip: int = Field(..., description="Number of results skipped")
    limit: int = Field(..., description="Maximum number of results")


class SearchTagsResponse(BaseModel):
    """Schema for tag search response."""

    tags: list[TagResponse] = Field(..., description="List of matching tags")
    total: int = Field(..., description="Total number of matching tags")
    skip: int = Field(..., description="Number of results skipped")
    limit: int = Field(..., description="Maximum number of results")

