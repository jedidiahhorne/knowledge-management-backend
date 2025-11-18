"""Search API routes."""
from datetime import datetime

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_active_user
from app.db import get_db
from app.models.user import User
from app.schemas.search import (
    SearchNotesRequest,
    SearchNotesResponse,
    SearchTagsRequest,
    SearchTagsResponse,
)
from app.services.search import SearchService

router = APIRouter(prefix="/search", tags=["search"])


@router.post("/notes", response_model=SearchNotesResponse)
def search_notes(
    search_request: SearchNotesRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Search notes with full-text search and filtering."""
    notes, total = SearchService.search_notes(
        db=db,
        user_id=current_user.id,
        query=search_request.query,
        tag_ids=search_request.tag_ids,
        tag_names=search_request.tag_names,
        is_pinned=search_request.is_pinned,
        is_archived=search_request.is_archived,
        created_after=search_request.created_after,
        created_before=search_request.created_before,
        updated_after=search_request.updated_after,
        updated_before=search_request.updated_before,
        skip=search_request.skip,
        limit=search_request.limit,
    )

    return SearchNotesResponse(
        notes=notes,
        total=total,
        skip=search_request.skip,
        limit=search_request.limit,
    )


@router.get("/notes", response_model=SearchNotesResponse)
def search_notes_get(
    query: str | None = Query(None, description="Search query for title and content"),
    tag_ids: list[int] = Query(default=[], description="Filter by tag IDs"),
    tag_names: list[str] = Query(default=[], description="Filter by tag names"),
    is_pinned: bool | None = Query(None, description="Filter by pinned status"),
    is_archived: bool | None = Query(None, description="Filter by archived status"),
    created_after: datetime | None = Query(None, description="Filter notes created after this date"),
    created_before: datetime | None = Query(None, description="Filter notes created before this date"),
    updated_after: datetime | None = Query(None, description="Filter notes updated after this date"),
    updated_before: datetime | None = Query(None, description="Filter notes updated before this date"),
    skip: int = Query(0, ge=0, description="Number of results to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of results to return"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Search notes with full-text search and filtering (GET endpoint)."""
    # Convert empty lists to None
    tag_ids_filter = tag_ids if tag_ids else None
    tag_names_filter = tag_names if tag_names else None

    notes, total = SearchService.search_notes(
        db=db,
        user_id=current_user.id,
        query=query,
        tag_ids=tag_ids_filter,
        tag_names=tag_names_filter,
        is_pinned=is_pinned,
        is_archived=is_archived,
        created_after=created_after,
        created_before=created_before,
        updated_after=updated_after,
        updated_before=updated_before,
        skip=skip,
        limit=limit,
    )

    return SearchNotesResponse(
        notes=notes,
        total=total,
        skip=skip,
        limit=limit,
    )


@router.post("/tags", response_model=SearchTagsResponse)
def search_tags(
    search_request: SearchTagsRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Search tags with full-text search."""
    tags, total = SearchService.search_tags(
        db=db,
        query=search_request.query,
        skip=search_request.skip,
        limit=search_request.limit,
    )

    return SearchTagsResponse(
        tags=tags,
        total=total,
        skip=search_request.skip,
        limit=search_request.limit,
    )


@router.get("/tags", response_model=SearchTagsResponse)
def search_tags_get(
    query: str | None = Query(None, description="Search query for tag name and description"),
    skip: int = Query(0, ge=0, description="Number of results to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of results to return"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Search tags with full-text search (GET endpoint)."""
    tags, total = SearchService.search_tags(
        db=db,
        query=query,
        skip=skip,
        limit=limit,
    )

    return SearchTagsResponse(
        tags=tags,
        total=total,
        skip=skip,
        limit=limit,
    )

