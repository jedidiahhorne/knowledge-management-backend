"""Tags API routes."""
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_active_user
from app.db import get_db
from app.models.note import Note
from app.models.tag import Tag
from app.models.user import User
from app.schemas.tag import TagCreate, TagResponse, TagUpdate

router = APIRouter(prefix="/tags", tags=["tags"])


@router.post("/", response_model=TagResponse, status_code=status.HTTP_201_CREATED)
def create_tag(
    tag_data: TagCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Create a new tag."""
    # Check if tag with same name already exists
    existing_tag = db.query(Tag).filter(Tag.name == tag_data.name).first()
    if existing_tag:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Tag with name '{tag_data.name}' already exists",
        )

    tag = Tag(
        name=tag_data.name,
        color=tag_data.color,
        description=tag_data.description,
    )
    db.add(tag)
    db.commit()
    db.refresh(tag)
    return tag


@router.get("/", response_model=list[TagResponse])
def list_tags(
    skip: int = Query(0, ge=0, description="Number of tags to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of tags to return"),
    search: str | None = Query(None, description="Search in tag name and description"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """List all tags with optional search."""
    query = db.query(Tag)

    # Search in name and description
    if search:
        search_pattern = f"%{search}%"
        query = query.filter(
            Tag.name.ilike(search_pattern) | Tag.description.ilike(search_pattern)
        )

    # Order by name
    query = query.order_by(Tag.name)

    # Apply pagination
    tags = query.offset(skip).limit(limit).all()
    return tags


@router.get("/{tag_id}", response_model=TagResponse)
def get_tag(
    tag_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Get a specific tag by ID."""
    tag = db.query(Tag).filter(Tag.id == tag_id).first()
    if not tag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Tag with id {tag_id} not found",
        )
    return tag


@router.put("/{tag_id}", response_model=TagResponse)
def update_tag(
    tag_id: int,
    tag_update: TagUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Update a tag."""
    tag = db.query(Tag).filter(Tag.id == tag_id).first()
    if not tag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Tag with id {tag_id} not found",
        )

    # Check if new name conflicts with existing tag
    if tag_update.name and tag_update.name != tag.name:
        existing_tag = db.query(Tag).filter(Tag.name == tag_update.name).first()
        if existing_tag:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Tag with name '{tag_update.name}' already exists",
            )

    # Update fields
    update_data = tag_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(tag, field, value)

    db.commit()
    db.refresh(tag)
    return tag


@router.delete("/{tag_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_tag(
    tag_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Delete a tag."""
    tag = db.query(Tag).filter(Tag.id == tag_id).first()
    if not tag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Tag with id {tag_id} not found",
        )
    db.delete(tag)
    db.commit()
    return None


@router.post("/{tag_id}/notes/{note_id}", response_model=TagResponse)
def add_tag_to_note(
    tag_id: int,
    note_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Add a tag to a note."""
    # Get tag
    tag = db.query(Tag).filter(Tag.id == tag_id).first()
    if not tag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Tag with id {tag_id} not found",
        )

    # Get note (must belong to current user)
    note = db.query(Note).filter(Note.id == note_id, Note.user_id == current_user.id).first()
    if not note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Note with id {note_id} not found",
        )

    # Add tag if not already present
    if tag not in note.tags:
        note.tags.append(tag)
        db.commit()

    db.refresh(tag)
    return tag


@router.delete("/{tag_id}/notes/{note_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_tag_from_note(
    tag_id: int,
    note_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Remove a tag from a note."""
    # Get tag
    tag = db.query(Tag).filter(Tag.id == tag_id).first()
    if not tag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Tag with id {tag_id} not found",
        )

    # Get note (must belong to current user)
    note = db.query(Note).filter(Note.id == note_id, Note.user_id == current_user.id).first()
    if not note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Note with id {note_id} not found",
        )

    # Remove tag if present
    if tag in note.tags:
        note.tags.remove(tag)
        db.commit()

    return None

