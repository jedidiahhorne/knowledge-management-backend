"""Tests for attachments API endpoints."""
import io

from fastapi import status


def test_upload_attachment(client, db_session):
    """Test uploading an attachment."""
    from app.models.note import Note
    from app.models.user import User

    # Create user
    user = User(email="test@example.com", username="testuser")
    user.set_password("testpassword123")
    db_session.add(user)
    db_session.commit()

    # Create note
    note = Note(title="Test Note", user_id=user.id)
    db_session.add(note)
    db_session.commit()

    # Login
    login_response = client.post(
        "/api/v1/auth/login/json",
        json={"username": "testuser", "password": "testpassword123"},
    )
    token = login_response.json()["access_token"]

    # Upload file
    file_content = b"Test file content"
    files = {"file": ("test.txt", io.BytesIO(file_content), "text/plain")}
    response = client.post(
        f"/api/v1/attachments/notes/{note.id}",
        files=files,
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["filename"] == "test.txt"
    assert data["file_size"] == len(file_content)
    assert data["note_id"] == note.id
    assert data["mime_type"] == "text/plain"
    assert "id" in data
    assert "file_path" in data


def test_upload_attachment_invalid_file_type(client, db_session):
    """Test uploading an attachment with invalid file type."""
    from app.models.note import Note
    from app.models.user import User

    # Create user
    user = User(email="test@example.com", username="testuser")
    user.set_password("testpassword123")
    db_session.add(user)
    db_session.commit()

    # Create note
    note = Note(title="Test Note", user_id=user.id)
    db_session.add(note)
    db_session.commit()

    # Login
    login_response = client.post(
        "/api/v1/auth/login/json",
        json={"username": "testuser", "password": "testpassword123"},
    )
    token = login_response.json()["access_token"]

    # Try to upload invalid file type
    file_content = b"Test file content"
    files = {"file": ("test.exe", io.BytesIO(file_content), "application/x-msdownload")}
    response = client.post(
        f"/api/v1/attachments/notes/{note.id}",
        files=files,
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "not allowed" in response.json()["detail"].lower()


def test_upload_attachment_note_not_found(client, db_session):
    """Test uploading attachment to nonexistent note."""
    from app.models.user import User

    # Create user
    user = User(email="test@example.com", username="testuser")
    user.set_password("testpassword123")
    db_session.add(user)
    db_session.commit()

    # Login
    login_response = client.post(
        "/api/v1/auth/login/json",
        json={"username": "testuser", "password": "testpassword123"},
    )
    token = login_response.json()["access_token"]

    # Try to upload to nonexistent note
    file_content = b"Test file content"
    files = {"file": ("test.txt", io.BytesIO(file_content), "text/plain")}
    response = client.post(
        "/api/v1/attachments/notes/99999",
        files=files,
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_upload_attachment_other_user_note(client, db_session):
    """Test uploading attachment to another user's note."""
    from app.models.note import Note
    from app.models.user import User

    # Create two users
    user1 = User(email="user1@example.com", username="user1")
    user1.set_password("password123")
    user2 = User(email="user2@example.com", username="user2")
    user2.set_password("password123")
    db_session.add_all([user1, user2])
    db_session.commit()

    # Create note for user1
    note = Note(title="User1 Note", user_id=user1.id)
    db_session.add(note)
    db_session.commit()

    # Login as user2
    login_response = client.post(
        "/api/v1/auth/login/json",
        json={"username": "user2", "password": "password123"},
    )
    token = login_response.json()["access_token"]

    # Try to upload to user1's note
    file_content = b"Test file content"
    files = {"file": ("test.txt", io.BytesIO(file_content), "text/plain")}
    response = client.post(
        f"/api/v1/attachments/notes/{note.id}",
        files=files,
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_list_note_attachments(client, db_session):
    """Test listing attachments for a note."""
    from app.models.attachment import Attachment
    from app.models.note import Note
    from app.models.user import User

    # Create user
    user = User(email="test@example.com", username="testuser")
    user.set_password("testpassword123")
    db_session.add(user)
    db_session.commit()

    # Create note
    note = Note(title="Test Note", user_id=user.id)
    db_session.add(note)
    db_session.commit()

    # Create attachments
    attachment1 = Attachment(
        filename="file1.txt",
        file_path="1/file1.txt",
        file_size=100,
        mime_type="text/plain",
        note_id=note.id,
    )
    attachment2 = Attachment(
        filename="file2.pdf",
        file_path="1/file2.pdf",
        file_size=200,
        mime_type="application/pdf",
        note_id=note.id,
    )
    db_session.add_all([attachment1, attachment2])
    db_session.commit()

    # Login
    login_response = client.post(
        "/api/v1/auth/login/json",
        json={"username": "testuser", "password": "testpassword123"},
    )
    token = login_response.json()["access_token"]

    # List attachments
    response = client.get(
        f"/api/v1/attachments/notes/{note.id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == 2
    assert all("id" in att for att in data)
    assert all("filename" in att for att in data)


def test_get_attachment(client, db_session):
    """Test getting attachment metadata."""
    from app.models.attachment import Attachment
    from app.models.note import Note
    from app.models.user import User

    # Create user
    user = User(email="test@example.com", username="testuser")
    user.set_password("testpassword123")
    db_session.add(user)
    db_session.commit()

    # Create note and attachment
    note = Note(title="Test Note", user_id=user.id)
    db_session.add(note)
    db_session.commit()

    attachment = Attachment(
        filename="test.txt",
        file_path="1/test.txt",
        file_size=100,
        mime_type="text/plain",
        note_id=note.id,
    )
    db_session.add(attachment)
    db_session.commit()

    # Login
    login_response = client.post(
        "/api/v1/auth/login/json",
        json={"username": "testuser", "password": "testpassword123"},
    )
    token = login_response.json()["access_token"]

    # Get attachment
    response = client.get(
        f"/api/v1/attachments/{attachment.id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == attachment.id
    assert data["filename"] == "test.txt"
    assert data["file_size"] == 100


def test_download_attachment(client, db_session, tmp_path):
    """Test downloading an attachment."""
    from app.core.config import settings
    from app.core.storage import ensure_upload_dir
    from app.models.attachment import Attachment
    from app.models.note import Note
    from app.models.user import User

    # Set upload directory to temp path for testing
    original_upload_dir = settings.UPLOAD_DIR
    settings.UPLOAD_DIR = str(tmp_path / "uploads")

    try:
        # Create user
        user = User(email="test@example.com", username="testuser")
        user.set_password("testpassword123")
        db_session.add(user)
        db_session.commit()

        # Create note
        note = Note(title="Test Note", user_id=user.id)
        db_session.add(note)
        db_session.commit()

        # Create file on disk
        upload_dir = ensure_upload_dir()
        note_dir = upload_dir / str(note.id)
        note_dir.mkdir(parents=True, exist_ok=True)
        file_path = note_dir / "test.txt"
        file_content = b"Test file content for download"
        file_path.write_bytes(file_content)

        # Create attachment record
        attachment = Attachment(
            filename="test.txt",
            file_path=f"{note.id}/test.txt",
            file_size=len(file_content),
            mime_type="text/plain",
            note_id=note.id,
        )
        db_session.add(attachment)
        db_session.commit()

        # Login
        login_response = client.post(
            "/api/v1/auth/login/json",
            json={"username": "testuser", "password": "testpassword123"},
        )
        token = login_response.json()["access_token"]

        # Download attachment
        response = client.get(
            f"/api/v1/attachments/{attachment.id}/download",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.content == file_content
        assert "test.txt" in response.headers.get("content-disposition", "")
    finally:
        settings.UPLOAD_DIR = original_upload_dir


def test_download_attachment_not_found(client, db_session):
    """Test downloading a nonexistent attachment."""
    from app.models.user import User

    # Create user
    user = User(email="test@example.com", username="testuser")
    user.set_password("testpassword123")
    db_session.add(user)
    db_session.commit()

    # Login
    login_response = client.post(
        "/api/v1/auth/login/json",
        json={"username": "testuser", "password": "testpassword123"},
    )
    token = login_response.json()["access_token"]

    # Try to download nonexistent attachment
    response = client.get(
        "/api/v1/attachments/99999/download",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_delete_attachment(client, db_session, tmp_path):
    """Test deleting an attachment."""
    from app.core.config import settings
    from app.core.storage import ensure_upload_dir
    from app.models.attachment import Attachment
    from app.models.note import Note
    from app.models.user import User

    # Set upload directory to temp path for testing
    original_upload_dir = settings.UPLOAD_DIR
    settings.UPLOAD_DIR = str(tmp_path / "uploads")

    try:
        # Create user
        user = User(email="test@example.com", username="testuser")
        user.set_password("testpassword123")
        db_session.add(user)
        db_session.commit()

        # Create note
        note = Note(title="Test Note", user_id=user.id)
        db_session.add(note)
        db_session.commit()

        # Create file on disk
        upload_dir = ensure_upload_dir()
        note_dir = upload_dir / str(note.id)
        note_dir.mkdir(parents=True, exist_ok=True)
        file_path = note_dir / "test.txt"
        file_path.write_bytes(b"Test content")

        # Create attachment record
        attachment = Attachment(
            filename="test.txt",
            file_path=f"{note.id}/test.txt",
            file_size=12,
            mime_type="text/plain",
            note_id=note.id,
        )
        db_session.add(attachment)
        db_session.commit()
        attachment_id = attachment.id

        # Login
        login_response = client.post(
            "/api/v1/auth/login/json",
            json={"username": "testuser", "password": "testpassword123"},
        )
        token = login_response.json()["access_token"]

        # Delete attachment
        response = client.delete(
            f"/api/v1/attachments/{attachment_id}",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == status.HTTP_204_NO_CONTENT

        # Verify attachment is deleted from database
        from app.db import get_db
        db = next(get_db())
        deleted_attachment = db.query(Attachment).filter(Attachment.id == attachment_id).first()
        assert deleted_attachment is None

        # Verify file is deleted from disk
        assert not file_path.exists()
    finally:
        settings.UPLOAD_DIR = original_upload_dir


def test_delete_attachment_other_user(client, db_session):
    """Test deleting another user's attachment."""
    from app.models.attachment import Attachment
    from app.models.note import Note
    from app.models.user import User

    # Create two users
    user1 = User(email="user1@example.com", username="user1")
    user1.set_password("password123")
    user2 = User(email="user2@example.com", username="user2")
    user2.set_password("password123")
    db_session.add_all([user1, user2])
    db_session.commit()

    # Create note and attachment for user1
    note = Note(title="User1 Note", user_id=user1.id)
    db_session.add(note)
    db_session.commit()

    attachment = Attachment(
        filename="test.txt",
        file_path="1/test.txt",
        file_size=100,
        mime_type="text/plain",
        note_id=note.id,
    )
    db_session.add(attachment)
    db_session.commit()

    # Login as user2
    login_response = client.post(
        "/api/v1/auth/login/json",
        json={"username": "user2", "password": "password123"},
    )
    token = login_response.json()["access_token"]

    # Try to delete user1's attachment
    response = client.delete(
        f"/api/v1/attachments/{attachment.id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_upload_attachment_requires_auth(client, db_session):
    """Test that uploading attachment requires authentication."""
    from app.models.note import Note
    from app.models.user import User

    # Create user and note
    user = User(email="test@example.com", username="testuser")
    user.set_password("testpassword123")
    db_session.add(user)
    db_session.commit()

    note = Note(title="Test Note", user_id=user.id)
    db_session.add(note)
    db_session.commit()

    # Try to upload without auth
    file_content = b"Test file content"
    files = {"file": ("test.txt", io.BytesIO(file_content), "text/plain")}
    response = client.post(
        f"/api/v1/attachments/notes/{note.id}",
        files=files,
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_upload_different_file_types(client, db_session):
    """Test uploading different file types."""
    from app.models.note import Note
    from app.models.user import User

    # Create user
    user = User(email="test@example.com", username="testuser")
    user.set_password("testpassword123")
    db_session.add(user)
    db_session.commit()

    # Create note
    note = Note(title="Test Note", user_id=user.id)
    db_session.add(note)
    db_session.commit()

    # Login
    login_response = client.post(
        "/api/v1/auth/login/json",
        json={"username": "testuser", "password": "testpassword123"},
    )
    token = login_response.json()["access_token"]

    # Test uploading PDF
    pdf_content = b"%PDF-1.4 fake pdf content"
    files = {"file": ("test.pdf", io.BytesIO(pdf_content), "application/pdf")}
    response = client.post(
        f"/api/v1/attachments/notes/{note.id}",
        files=files,
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()["mime_type"] == "application/pdf"

    # Test uploading image
    image_content = b"fake image content"
    files = {"file": ("test.png", io.BytesIO(image_content), "image/png")}
    response = client.post(
        f"/api/v1/attachments/notes/{note.id}",
        files=files,
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()["mime_type"] == "image/png"

