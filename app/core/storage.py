"""File storage utilities for S3/MinIO and local storage."""
import mimetypes
import secrets
from io import BytesIO
from pathlib import Path

import boto3
from botocore.client import Config
from botocore.exceptions import ClientError
from fastapi import UploadFile

from app.core.config import settings


def get_file_extension(filename: str) -> str:
    """Get file extension from filename."""
    return filename.rsplit(".", 1)[-1].lower() if "." in filename else ""


def is_allowed_file(filename: str) -> bool:
    """Check if file extension is allowed."""
    ext = get_file_extension(filename)
    return ext in settings.ALLOWED_EXTENSIONS


def generate_unique_filename(original_filename: str, note_id: int) -> str:
    """Generate a unique filename to prevent collisions."""
    ext = get_file_extension(original_filename)
    unique_id = secrets.token_urlsafe(16)
    if ext:
        return f"{note_id}/{unique_id}.{ext}"
    return f"{note_id}/{unique_id}"


def get_s3_client():
    """Get configured S3 client for MinIO or AWS S3."""
    if not settings.USE_S3_STORAGE:
        raise ValueError("S3 storage is not enabled. Set USE_S3_STORAGE=True")

    if not settings.S3_ENDPOINT_URL:
        raise ValueError("S3_ENDPOINT_URL must be set when USE_S3_STORAGE=True")

    # Support MinIO's MINIO_ROOT_USER/MINIO_ROOT_PASSWORD or standard S3_ACCESS_KEY_ID/SECRET
    access_key = settings.S3_ACCESS_KEY_ID or settings.MINIO_ROOT_USER
    secret_key = settings.S3_SECRET_ACCESS_KEY or settings.MINIO_ROOT_PASSWORD

    if not access_key or not secret_key:
        raise ValueError(
            "S3 credentials must be set. Use either S3_ACCESS_KEY_ID/S3_SECRET_ACCESS_KEY "
            "or MINIO_ROOT_USER/MINIO_ROOT_PASSWORD (for MinIO)"
        )

    # Configure boto3 for MinIO (S3-compatible)
    s3_config = Config(
        signature_version="s3v4",
        s3={"addressing_style": "path"},
    )

    # Support MinIO's MINIO_ROOT_USER/MINIO_ROOT_PASSWORD or standard S3_ACCESS_KEY_ID/SECRET
    access_key = settings.S3_ACCESS_KEY_ID or settings.MINIO_ROOT_USER
    secret_key = settings.S3_SECRET_ACCESS_KEY or settings.MINIO_ROOT_PASSWORD

    client = boto3.client(
        "s3",
        endpoint_url=settings.S3_ENDPOINT_URL,
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
        region_name=settings.S3_REGION,
        use_ssl=settings.S3_USE_SSL,
        verify=settings.S3_VERIFY_SSL,
        config=s3_config,
    )

    return client


def ensure_s3_bucket():
    """Ensure S3 bucket exists, create if it doesn't."""
    if not settings.USE_S3_STORAGE:
        return

    try:
        s3_client = get_s3_client()
        s3_client.head_bucket(Bucket=settings.S3_BUCKET_NAME)
    except ClientError as e:
        error_code = e.response.get("Error", {}).get("Code", "")
        if error_code == "404":
            # Bucket doesn't exist, create it
            try:
                s3_client = get_s3_client()
                s3_client.create_bucket(Bucket=settings.S3_BUCKET_NAME)
            except ClientError as create_error:
                raise ValueError(f"Failed to create S3 bucket: {create_error}") from create_error
        else:
            raise ValueError(f"Failed to access S3 bucket: {e}") from e


def save_uploaded_file(file: UploadFile, note_id: int) -> tuple[str, int]:
    """
    Save uploaded file to S3/MinIO or local storage.

    Returns:
        tuple: (file_path or S3 key, file_size)
    """
    # Validate file extension
    if not is_allowed_file(file.filename or ""):
        raise ValueError(
            f"File type not allowed. Allowed extensions: {', '.join(settings.ALLOWED_EXTENSIONS)}"
        )

    # Read file content and check size
    file_content = file.file.read()
    file_size = len(file_content)

    if file_size > settings.MAX_FILE_SIZE:
        raise ValueError(
            f"File size exceeds maximum allowed size of {settings.MAX_FILE_SIZE / (1024 * 1024)} MB"
        )

    # Use S3 storage if enabled
    if settings.USE_S3_STORAGE:
        ensure_s3_bucket()
        s3_client = get_s3_client()

        # Generate unique S3 key (path)
        s3_key = generate_unique_filename(file.filename or "file", note_id)

        # Get MIME type
        mime_type = get_mime_type(file.filename or "")

        # Upload to S3
        try:
            s3_client.put_object(
                Bucket=settings.S3_BUCKET_NAME,
                Key=s3_key,
                Body=BytesIO(file_content),
                ContentType=mime_type,
            )
            return s3_key, file_size
        except ClientError as e:
            raise ValueError(f"Failed to upload file to S3: {e}") from e

    # Fallback to local storage
    upload_path = Path(settings.UPLOAD_DIR)
    upload_path.mkdir(parents=True, exist_ok=True)
    note_dir = upload_path / str(note_id)
    note_dir.mkdir(parents=True, exist_ok=True)

    # Generate unique filename
    unique_filename = generate_unique_filename(file.filename or "file", note_id).split("/")[-1]
    file_path = note_dir / unique_filename

    # Save file
    with open(file_path, "wb") as f:
        f.write(file_content)

    # Return relative path from upload directory
    relative_path = str(file_path.relative_to(upload_path))
    return relative_path, file_size


def delete_file(file_path: str) -> None:
    """Delete a file from S3/MinIO or local storage."""
    if settings.USE_S3_STORAGE:
        try:
            s3_client = get_s3_client()
            s3_client.delete_object(Bucket=settings.S3_BUCKET_NAME, Key=file_path)
        except ClientError as e:
            # Log error but don't fail (file might already be deleted)
            print(f"Warning: Failed to delete file from S3: {e}")
    else:
        # Local storage
        upload_dir = Path(settings.UPLOAD_DIR)
        full_path = upload_dir / file_path

        if full_path.exists():
            full_path.unlink()

        # Try to remove empty note directory
        note_dir = full_path.parent
        if note_dir.exists() and not any(note_dir.iterdir()):
            note_dir.rmdir()


def get_file_path(file_path: str) -> Path:
    """Get full path to a stored file (local storage only)."""
    if settings.USE_S3_STORAGE:
        raise ValueError("get_file_path() is not available for S3 storage. Use get_s3_url() instead.")
    upload_dir = Path(settings.UPLOAD_DIR)
    return upload_dir / file_path


def get_s3_url(file_path: str, expires_in: int = 3600) -> str:
    """
    Generate a presigned URL for downloading a file from S3/MinIO.

    Args:
        file_path: S3 key (path) of the file
        expires_in: URL expiration time in seconds (default: 1 hour)

    Returns:
        Presigned URL string
    """
    if not settings.USE_S3_STORAGE:
        raise ValueError("S3 storage is not enabled")

    try:
        s3_client = get_s3_client()
        url = s3_client.generate_presigned_url(
            "get_object",
            Params={"Bucket": settings.S3_BUCKET_NAME, "Key": file_path},
            ExpiresIn=expires_in,
        )
        return url
    except ClientError as e:
        raise ValueError(f"Failed to generate S3 presigned URL: {e}") from e


def get_file_content(file_path: str) -> bytes:
    """
    Get file content from S3/MinIO or local storage.

    Returns:
        File content as bytes
    """
    if settings.USE_S3_STORAGE:
        try:
            s3_client = get_s3_client()
            response = s3_client.get_object(Bucket=settings.S3_BUCKET_NAME, Key=file_path)
            return response["Body"].read()
        except ClientError as e:
            raise ValueError(f"Failed to get file from S3: {e}") from e
    else:
        # Local storage
        upload_dir = Path(settings.UPLOAD_DIR)
        full_path = upload_dir / file_path
        if not full_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        with open(full_path, "rb") as f:
            return f.read()


def get_mime_type(filename: str) -> str:
    """Get MIME type from filename."""
    mime_type, _ = mimetypes.guess_type(filename)
    return mime_type or "application/octet-stream"
