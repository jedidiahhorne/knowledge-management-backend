"""Tests for database models and relationships."""
from app.models import Attachment, Note, Tag, User


def test_user_model_creation(db_session):
    """Test User model creation and password hashing."""
    user = User(
        email="test@example.com",
        username="testuser",
        full_name="Test User",
    )
    user.set_password("testpassword123")
    db_session.add(user)
    db_session.commit()

    assert user.id is not None
    assert user.email == "test@example.com"
    assert user.username == "testuser"
    assert user.check_password("testpassword123")
    assert not user.check_password("wrongpassword")
    assert user.is_active is True
    assert user.is_superuser is False


def test_note_model_creation(db_session):
    """Test Note model creation."""
    # Create a user first
    user = User(email="user@example.com", username="user1")
    user.set_password("password")
    db_session.add(user)
    db_session.commit()

    # Create a note
    note = Note(
        title="Test Note",
        content="This is a test note",
        user_id=user.id,
    )
    db_session.add(note)
    db_session.commit()

    assert note.id is not None
    assert note.title == "Test Note"
    assert note.content == "This is a test note"
    assert note.user_id == user.id
    assert note.is_pinned is False
    assert note.is_archived is False
    assert note.owner == user


def test_tag_model_creation(db_session):
    """Test Tag model creation."""
    tag = Tag(
        name="python",
        color="#3776ab",
        description="Python programming language",
    )
    db_session.add(tag)
    db_session.commit()

    assert tag.id is not None
    assert tag.name == "python"
    assert tag.color == "#3776ab"
    assert tag.description == "Python programming language"


def test_note_tag_relationship(db_session):
    """Test many-to-many relationship between Notes and Tags."""
    # Create user
    user = User(email="user@example.com", username="user1")
    user.set_password("password")
    db_session.add(user)
    db_session.commit()

    # Create tags
    tag1 = Tag(name="python", color="#3776ab")
    tag2 = Tag(name="fastapi", color="#009688")
    db_session.add_all([tag1, tag2])
    db_session.commit()

    # Create note
    note = Note(title="Python FastAPI Note", content="Content", user_id=user.id)
    db_session.add(note)
    db_session.commit()

    # Add tags to note
    note.add_tag(tag1)
    note.add_tag(tag2)
    db_session.commit()

    assert len(note.tags) == 2
    assert tag1 in note.tags
    assert tag2 in note.tags
    assert note.has_tag("python")
    assert note.has_tag("fastapi")
    assert not note.has_tag("django")
    assert "python" in note.get_tag_names()
    assert "fastapi" in note.get_tag_names()

    # Remove a tag
    note.remove_tag(tag1)
    db_session.commit()
    assert len(note.tags) == 1
    assert tag1 not in note.tags
    assert tag2 in note.tags


def test_note_attachment_relationship(db_session):
    """Test one-to-many relationship between Notes and Attachments."""
    # Create user
    user = User(email="user@example.com", username="user1")
    user.set_password("password")
    db_session.add(user)
    db_session.commit()

    # Create note
    note = Note(title="Note with Attachment", content="Content", user_id=user.id)
    db_session.add(note)
    db_session.commit()

    # Create attachments
    attachment1 = Attachment(
        filename="document.pdf",
        file_path="/uploads/document.pdf",
        file_size=1024000,
        mime_type="application/pdf",
        note_id=note.id,
    )
    attachment2 = Attachment(
        filename="image.png",
        file_path="/uploads/image.png",
        file_size=512000,
        mime_type="image/png",
        note_id=note.id,
    )
    db_session.add_all([attachment1, attachment2])
    db_session.commit()

    assert len(note.attachments) == 2
    assert attachment1 in note.attachments
    assert attachment2 in note.attachments
    assert attachment1.note == note
    assert attachment2.note == note


def test_attachment_helper_methods(db_session):
    """Test Attachment helper methods."""
    # Create user and note
    user = User(email="user@example.com", username="user1")
    user.set_password("password")
    db_session.add(user)
    db_session.commit()

    note = Note(title="Test Note", user_id=user.id)
    db_session.add(note)
    db_session.commit()

    # Create attachments
    pdf_attachment = Attachment(
        filename="doc.pdf",
        file_path="/uploads/doc.pdf",
        file_size=1048576,  # 1 MB
        mime_type="application/pdf",
        note_id=note.id,
    )
    image_attachment = Attachment(
        filename="photo.png",
        file_path="/uploads/photo.png",
        file_size=524288,  # 512 KB
        mime_type="image/png",
        note_id=note.id,
    )
    db_session.add_all([pdf_attachment, image_attachment])
    db_session.commit()

    # Test file size methods
    assert pdf_attachment.get_file_size_mb() == 1.0
    assert pdf_attachment.get_file_size_kb() == 1024.0
    assert image_attachment.get_file_size_mb() == 0.5
    assert image_attachment.get_file_size_kb() == 512.0

    # Test MIME type checks
    assert pdf_attachment.is_pdf()
    assert not pdf_attachment.is_image()
    assert image_attachment.is_image()
    assert not image_attachment.is_pdf()


def test_note_helper_methods(db_session):
    """Test Note helper methods for pinning and archiving."""
    # Create user
    user = User(email="user@example.com", username="user1")
    user.set_password("password")
    db_session.add(user)
    db_session.commit()

    # Create note
    note = Note(title="Test Note", content="Content", user_id=user.id)
    db_session.add(note)
    db_session.commit()

    # Test pinning
    assert note.is_pinned is False
    note.pin()
    db_session.commit()
    assert note.is_pinned is True
    note.unpin()
    db_session.commit()
    assert note.is_pinned is False

    # Test archiving
    assert note.is_archived is False
    note.archive()
    db_session.commit()
    assert note.is_archived is True
    note.unarchive()
    db_session.commit()
    assert note.is_archived is False


def test_user_notes_relationship(db_session):
    """Test one-to-many relationship between Users and Notes."""
    # Create user
    user = User(email="user@example.com", username="user1")
    user.set_password("password")
    db_session.add(user)
    db_session.commit()

    # Create multiple notes
    note1 = Note(title="Note 1", user_id=user.id)
    note2 = Note(title="Note 2", user_id=user.id)
    note3 = Note(title="Note 3", user_id=user.id)
    db_session.add_all([note1, note2, note3])
    db_session.commit()

    # Refresh user to get relationships
    db_session.refresh(user)

    assert len(user.notes) == 3
    assert note1 in user.notes
    assert note2 in user.notes
    assert note3 in user.notes


def test_cascade_delete(db_session):
    """Test cascade delete behavior."""
    # Create user
    user = User(email="user@example.com", username="user1")
    user.set_password("password")
    db_session.add(user)
    db_session.commit()

    # Create note with tags and attachments
    tag = Tag(name="test")
    db_session.add(tag)
    db_session.commit()

    note = Note(title="Test Note", user_id=user.id)
    note.add_tag(tag)
    db_session.add(note)
    db_session.commit()

    attachment = Attachment(
        filename="test.pdf",
        file_path="/uploads/test.pdf",
        note_id=note.id,
    )
    db_session.add(attachment)
    db_session.commit()

    note_id = note.id
    attachment_id = attachment.id

    # Delete user - should cascade delete notes and attachments
    db_session.delete(user)
    db_session.commit()

    # Verify note and attachment are deleted
    deleted_note = db_session.query(Note).filter(Note.id == note_id).first()
    deleted_attachment = db_session.query(Attachment).filter(Attachment.id == attachment_id).first()
    assert deleted_note is None
    assert deleted_attachment is None

    # Tag should still exist (no cascade from note deletion)
    existing_tag = db_session.query(Tag).filter(Tag.id == tag.id).first()
    assert existing_tag is not None

