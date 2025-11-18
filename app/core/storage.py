"""File storage utilities."""
import secrets
from pathlib import Path

from fastapi import UploadFile

from app.core.config import settings


def ensure_upload_dir() -> Path:
    """Ensure upload directory exists and return its path."""
    upload_path = Path(settings.UPLOAD_DIR)
    upload_path.mkdir(parents=True, exist_ok=True)
    return upload_path


def get_file_extension(filename: str) -> str:
    """Get file extension from filename."""
    return filename.rsplit(".", 1)[-1].lower() if "." in filename else ""


def is_allowed_file(filename: str) -> bool:
    """Check if file extension is allowed."""
    ext = get_file_extension(filename)
    return ext in settings.ALLOWED_EXTENSIONS


def generate_unique_filename(original_filename: str) -> str:
    """Generate a unique filename to prevent collisions."""
    ext = get_file_extension(original_filename)
    unique_id = secrets.token_urlsafe(16)
    if ext:
        return f"{unique_id}.{ext}"
    return unique_id


def save_uploaded_file(file: UploadFile, note_id: int) -> tuple[str, int]:
    """
    Save uploaded file to disk.

    Returns:
        tuple: (file_path, file_size)
    """
    # Validate file extension
    if not is_allowed_file(file.filename or ""):
        raise ValueError(f"File type not allowed. Allowed extensions: {', '.join(settings.ALLOWED_EXTENSIONS)}")

    # Ensure upload directory exists
    upload_dir = ensure_upload_dir()
    note_dir = upload_dir / str(note_id)
    note_dir.mkdir(parents=True, exist_ok=True)

    # Generate unique filename
    unique_filename = generate_unique_filename(file.filename or "file")
    file_path = note_dir / unique_filename

    # Read file content and check size
    file_content = file.file.read()
    file_size = len(file_content)

    if file_size > settings.MAX_FILE_SIZE:
        raise ValueError(f"File size exceeds maximum allowed size of {settings.MAX_FILE_SIZE / (1024 * 1024)} MB")

    # Save file
    with open(file_path, "wb") as f:
        f.write(file_content)

    # Return relative path from upload directory
    relative_path = str(file_path.relative_to(upload_dir))
    return relative_path, file_size


def delete_file(file_path: str) -> None:
    """Delete a file from storage."""
    upload_dir = Path(settings.UPLOAD_DIR)
    full_path = upload_dir / file_path

    if full_path.exists():
        full_path.unlink()

    # Try to remove empty note directory
    note_dir = full_path.parent
    if note_dir.exists() and not any(note_dir.iterdir()):
        note_dir.rmdir()


def get_file_path(file_path: str) -> Path:
    """Get full path to a stored file."""
    upload_dir = Path(settings.UPLOAD_DIR)
    return upload_dir / file_path


def get_mime_type(filename: str) -> str:
    """Get MIME type from filename."""
    import mimetypes

    mime_type, _ = mimetypes.guess_type(filename)
    return mime_type or "application/octet-stream"

