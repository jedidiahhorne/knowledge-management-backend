"""Attachments API routes."""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_active_user
from app.core.storage import delete_file, get_file_path, get_mime_type, save_uploaded_file
from app.db import get_db
from app.models.attachment import Attachment
from app.models.note import Note
from app.models.user import User
from app.schemas.attachment import AttachmentResponse

router = APIRouter(prefix="/attachments", tags=["attachments"])


@router.post(
    "/notes/{note_id}",
    response_model=AttachmentResponse,
    status_code=status.HTTP_201_CREATED,
)
def upload_attachment(
    note_id: int,
    file: UploadFile,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Upload an attachment to a note."""
    # Verify note exists and belongs to user
    note = db.query(Note).filter(Note.id == note_id, Note.user_id == current_user.id).first()
    if not note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Note with id {note_id} not found",
        )

    # Validate and save file
    try:
        file_path, file_size = save_uploaded_file(file, note_id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

    # Get MIME type
    mime_type = get_mime_type(file.filename or "")

    # Create attachment record
    attachment = Attachment(
        filename=file.filename or "unnamed",
        file_path=file_path,
        file_size=file_size,
        mime_type=mime_type,
        note_id=note_id,
    )
    db.add(attachment)
    db.commit()
    db.refresh(attachment)

    return attachment


@router.get("/notes/{note_id}", response_model=list[AttachmentResponse])
def list_note_attachments(
    note_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """List all attachments for a note."""
    # Verify note exists and belongs to user
    note = db.query(Note).filter(Note.id == note_id, Note.user_id == current_user.id).first()
    if not note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Note with id {note_id} not found",
        )

    # Get attachments
    attachments = db.query(Attachment).filter(Attachment.note_id == note_id).all()
    return attachments


@router.get("/{attachment_id}", response_model=AttachmentResponse)
def get_attachment(
    attachment_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Get attachment metadata."""
    attachment = db.query(Attachment).filter(Attachment.id == attachment_id).first()
    if not attachment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Attachment with id {attachment_id} not found",
        )

    # Verify note belongs to user
    note = db.query(Note).filter(Note.id == attachment.note_id, Note.user_id == current_user.id).first()
    if not note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Attachment not found",
        )

    return attachment


@router.get("/{attachment_id}/download")
def download_attachment(
    attachment_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Download an attachment file."""
    attachment = db.query(Attachment).filter(Attachment.id == attachment_id).first()
    if not attachment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Attachment with id {attachment_id} not found",
        )

    # Verify note belongs to user
    note = db.query(Note).filter(Note.id == attachment.note_id, Note.user_id == current_user.id).first()
    if not note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Attachment not found",
        )

    # Get file path
    file_path = get_file_path(attachment.file_path)
    if not file_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found on disk",
        )

    # Return file with appropriate headers
    return FileResponse(
        path=str(file_path),
        filename=attachment.filename,
        media_type=attachment.mime_type or "application/octet-stream",
    )


@router.delete("/{attachment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_attachment(
    attachment_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Delete an attachment."""
    attachment = db.query(Attachment).filter(Attachment.id == attachment_id).first()
    if not attachment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Attachment with id {attachment_id} not found",
        )

    # Verify note belongs to user
    note = db.query(Note).filter(Note.id == attachment.note_id, Note.user_id == current_user.id).first()
    if not note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Attachment not found",
        )

    # Delete file from storage
    try:
        delete_file(attachment.file_path)
    except Exception as err:
        # Log error but continue with database deletion
        # In production, you might want to log this error
        pass

    # Delete attachment record
    db.delete(attachment)
    db.commit()
    return None

