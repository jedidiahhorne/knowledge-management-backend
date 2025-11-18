"""Search service for notes and tags."""
from datetime import datetime

from sqlalchemy import or_
from sqlalchemy.orm import Query, Session

from app.models.note import Note
from app.models.tag import Tag


class SearchService:
    """Service for searching notes and tags."""

    @staticmethod
    def search_notes(
        db: Session,
        user_id: int,
        query: str | None = None,
        tag_ids: list[int] | None = None,
        tag_names: list[str] | None = None,
        is_pinned: bool | None = None,
        is_archived: bool | None = None,
        created_after: datetime | None = None,
        created_before: datetime | None = None,
        updated_after: datetime | None = None,
        updated_before: datetime | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> tuple[list[Note], int]:
        """
        Search notes with various filters.

        Returns:
            tuple: (list of notes, total count)
        """
        # Start with base query for user's notes
        base_query = db.query(Note).filter(Note.user_id == user_id)

        # Apply filters
        query_obj = SearchService._apply_note_filters(
            base_query,
            query=query,
            tag_ids=tag_ids,
            tag_names=tag_names,
            is_pinned=is_pinned,
            is_archived=is_archived,
            created_after=created_after,
            created_before=created_before,
            updated_after=updated_after,
            updated_before=updated_before,
        )

        # Get total count before pagination
        total_count = query_obj.count()

        # Apply ordering and pagination
        query_obj = query_obj.order_by(Note.is_pinned.desc(), Note.updated_at.desc())
        notes = query_obj.offset(skip).limit(limit).all()

        return notes, total_count

    @staticmethod
    def search_tags(
        db: Session,
        query: str | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> tuple[list[Tag], int]:
        """
        Search tags.

        Returns:
            tuple: (list of tags, total count)
        """
        base_query = db.query(Tag)

        # Apply search query
        if query:
            search_pattern = f"%{query}%"
            base_query = base_query.filter(
                or_(
                    Tag.name.ilike(search_pattern),
                    Tag.description.ilike(search_pattern),
                )
            )

        # Get total count
        total_count = base_query.count()

        # Apply ordering and pagination
        tags = base_query.order_by(Tag.name).offset(skip).limit(limit).all()

        return tags, total_count

    @staticmethod
    def _apply_note_filters(
        query_obj: Query,
        query: str | None = None,
        tag_ids: list[int] | None = None,
        tag_names: list[str] | None = None,
        is_pinned: bool | None = None,
        is_archived: bool | None = None,
        created_after: datetime | None = None,
        created_before: datetime | None = None,
        updated_after: datetime | None = None,
        updated_before: datetime | None = None,
    ) -> Query:
        """Apply filters to note query."""
        # Full-text search in title and content
        if query:
            search_pattern = f"%{query}%"
            query_obj = query_obj.filter(
                or_(
                    Note.title.ilike(search_pattern),
                    Note.content.ilike(search_pattern),
                )
            )

        # Filter by tag IDs
        if tag_ids:
            query_obj = query_obj.join(Note.tags).filter(Tag.id.in_(tag_ids)).distinct()

        # Filter by tag names
        if tag_names:
            query_obj = query_obj.join(Note.tags).filter(Tag.name.in_(tag_names)).distinct()

        # Filter by pinned status
        if is_pinned is not None:
            query_obj = query_obj.filter(Note.is_pinned == is_pinned)

        # Filter by archived status
        if is_archived is not None:
            query_obj = query_obj.filter(Note.is_archived == is_archived)

        # Filter by creation date
        if created_after:
            query_obj = query_obj.filter(Note.created_at >= created_after)
        if created_before:
            query_obj = query_obj.filter(Note.created_at <= created_before)

        # Filter by update date
        if updated_after:
            query_obj = query_obj.filter(Note.updated_at >= updated_after)
        if updated_before:
            query_obj = query_obj.filter(Note.updated_at <= updated_before)

        return query_obj

