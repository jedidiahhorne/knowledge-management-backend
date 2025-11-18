"""Notes API routes."""
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_active_user
from app.db import get_db
from app.models.note import Note
from app.models.tag import Tag
from app.models.user import User
from app.schemas.note import NoteCreate, NoteResponse, NoteUpdate

router = APIRouter(prefix="/notes", tags=["notes"])


@router.post("/", response_model=NoteResponse, status_code=status.HTTP_201_CREATED)
def create_note(
    note_data: NoteCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Create a new note."""
    # Create the note
    note = Note(
        title=note_data.title,
        content=note_data.content,
        is_pinned=note_data.is_pinned,
        is_archived=note_data.is_archived,
        user_id=current_user.id,
    )

    # Add tags if provided
    if note_data.tag_ids:
        tags = db.query(Tag).filter(Tag.id.in_(note_data.tag_ids)).all()
        if len(tags) != len(note_data.tag_ids):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="One or more tag IDs are invalid",
            )
        note.tags = tags

    db.add(note)
    db.commit()
    db.refresh(note)
    return note


@router.get("/", response_model=list[NoteResponse])
def list_notes(
    skip: int = Query(0, ge=0, description="Number of notes to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of notes to return"),
    tag_ids: list[int] = Query(default=[], description="Filter by tag IDs (comma-separated)"),
    search: str | None = Query(None, description="Search in title and content"),
    is_pinned: bool | None = Query(None, description="Filter by pinned status"),
    is_archived: bool | None = Query(None, description="Filter by archived status"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """List notes with optional filtering and search."""
    # Start with query for current user's notes
    query = db.query(Note).filter(Note.user_id == current_user.id)

    # Filter by tags
    if tag_ids:
        query = query.join(Note.tags).filter(Tag.id.in_(tag_ids)).distinct()

    # Search in title and content
    if search:
        search_pattern = f"%{search}%"
        query = query.filter(
            or_(
                Note.title.ilike(search_pattern),
                Note.content.ilike(search_pattern),
            )
        )

    # Filter by pinned status
    if is_pinned is not None:
        query = query.filter(Note.is_pinned == is_pinned)

    # Filter by archived status
    if is_archived is not None:
        query = query.filter(Note.is_archived == is_archived)

    # Order by pinned first, then by updated_at descending
    query = query.order_by(Note.is_pinned.desc(), Note.updated_at.desc())

    # Apply pagination
    notes = query.offset(skip).limit(limit).all()
    return notes


@router.get("/{note_id}", response_model=NoteResponse)
def get_note(
    note_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Get a specific note by ID."""
    note = db.query(Note).filter(Note.id == note_id, Note.user_id == current_user.id).first()
    if not note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Note with id {note_id} not found",
        )
    return note


@router.put("/{note_id}", response_model=NoteResponse)
def update_note(
    note_id: int,
    note_update: NoteUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Update a note."""
    note = db.query(Note).filter(Note.id == note_id, Note.user_id == current_user.id).first()
    if not note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Note with id {note_id} not found",
        )

    # Update basic fields
    update_data = note_update.model_dump(exclude_unset=True, exclude={"tag_ids"})
    for field, value in update_data.items():
        setattr(note, field, value)

    # Update tags if provided
    if note_update.tag_ids is not None:
        tags = db.query(Tag).filter(Tag.id.in_(note_update.tag_ids)).all()
        if len(tags) != len(note_update.tag_ids):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="One or more tag IDs are invalid",
            )
        note.tags = tags

    db.commit()
    db.refresh(note)
    return note


@router.delete("/{note_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_note(
    note_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Delete a note."""
    note = db.query(Note).filter(Note.id == note_id, Note.user_id == current_user.id).first()
    if not note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Note with id {note_id} not found",
        )
    db.delete(note)
    db.commit()
    return None


@router.post("/{note_id}/pin", response_model=NoteResponse)
def pin_note(
    note_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Pin a note."""
    note = db.query(Note).filter(Note.id == note_id, Note.user_id == current_user.id).first()
    if not note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Note with id {note_id} not found",
        )
    note.pin()
    db.commit()
    db.refresh(note)
    return note


@router.post("/{note_id}/unpin", response_model=NoteResponse)
def unpin_note(
    note_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Unpin a note."""
    note = db.query(Note).filter(Note.id == note_id, Note.user_id == current_user.id).first()
    if not note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Note with id {note_id} not found",
        )
    note.unpin()
    db.commit()
    db.refresh(note)
    return note


@router.post("/{note_id}/archive", response_model=NoteResponse)
def archive_note(
    note_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Archive a note."""
    note = db.query(Note).filter(Note.id == note_id, Note.user_id == current_user.id).first()
    if not note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Note with id {note_id} not found",
        )
    note.archive()
    db.commit()
    db.refresh(note)
    return note


@router.post("/{note_id}/unarchive", response_model=NoteResponse)
def unarchive_note(
    note_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Unarchive a note."""
    note = db.query(Note).filter(Note.id == note_id, Note.user_id == current_user.id).first()
    if not note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Note with id {note_id} not found",
        )
    note.unarchive()
    db.commit()
    db.refresh(note)
    return note

