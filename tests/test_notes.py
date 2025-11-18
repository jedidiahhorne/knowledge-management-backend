"""Tests for notes API endpoints."""
from fastapi import status


def test_create_note(client, db_session):
    """Test creating a note."""
    from app.models.user import User

    # Create and login user
    user = User(email="test@example.com", username="testuser")
    user.set_password("testpassword123")
    db_session.add(user)
    db_session.commit()

    login_response = client.post(
        "/api/v1/auth/login/json",
        json={"username": "testuser", "password": "testpassword123"},
    )
    token = login_response.json()["access_token"]

    # Create a note
    response = client.post(
        "/api/v1/notes/",
        json={
            "title": "Test Note",
            "content": "This is a test note",
            "is_pinned": False,
            "is_archived": False,
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["title"] == "Test Note"
    assert data["content"] == "This is a test note"
    assert data["is_pinned"] is False
    assert data["is_archived"] is False
    assert data["user_id"] == user.id
    assert "id" in data
    assert "created_at" in data
    assert "updated_at" in data


def test_create_note_with_tags(client, db_session):
    """Test creating a note with tags."""
    from app.models.tag import Tag
    from app.models.user import User

    # Create user
    user = User(email="test@example.com", username="testuser")
    user.set_password("testpassword123")
    db_session.add(user)
    db_session.commit()

    # Create tags
    tag1 = Tag(name="python", color="#3776ab")
    tag2 = Tag(name="fastapi", color="#009688")
    db_session.add_all([tag1, tag2])
    db_session.commit()

    # Login
    login_response = client.post(
        "/api/v1/auth/login/json",
        json={"username": "testuser", "password": "testpassword123"},
    )
    token = login_response.json()["access_token"]

    # Create note with tags
    response = client.post(
        "/api/v1/notes/",
        json={
            "title": "Python Note",
            "content": "Content about Python",
            "tag_ids": [tag1.id, tag2.id],
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert len(data["tags"]) == 2
    assert any(tag["name"] == "python" for tag in data["tags"])
    assert any(tag["name"] == "fastapi" for tag in data["tags"])


def test_create_note_invalid_tags(client, db_session):
    """Test creating a note with invalid tag IDs."""
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

    # Try to create note with invalid tag ID
    response = client.post(
        "/api/v1/notes/",
        json={
            "title": "Test Note",
            "tag_ids": [99999],
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_list_notes(client, db_session):
    """Test listing notes."""
    from app.models.note import Note
    from app.models.user import User

    # Create user
    user = User(email="test@example.com", username="testuser")
    user.set_password("testpassword123")
    db_session.add(user)
    db_session.commit()

    # Create notes
    note1 = Note(title="Note 1", content="Content 1", user_id=user.id)
    note2 = Note(title="Note 2", content="Content 2", user_id=user.id)
    note3 = Note(title="Note 3", content="Content 3", user_id=user.id)
    db_session.add_all([note1, note2, note3])
    db_session.commit()

    # Login
    login_response = client.post(
        "/api/v1/auth/login/json",
        json={"username": "testuser", "password": "testpassword123"},
    )
    token = login_response.json()["access_token"]

    # List notes
    response = client.get(
        "/api/v1/notes/",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == 3
    assert all("id" in note for note in data)
    assert all("title" in note for note in data)


def test_list_notes_with_tag_filter(client, db_session):
    """Test listing notes filtered by tags."""
    from app.models.note import Note
    from app.models.tag import Tag
    from app.models.user import User

    # Create user
    user = User(email="test@example.com", username="testuser")
    user.set_password("testpassword123")
    db_session.add(user)
    db_session.commit()

    # Create tags
    tag1 = Tag(name="python")
    tag2 = Tag(name="javascript")
    db_session.add_all([tag1, tag2])
    db_session.commit()

    # Create notes with tags
    note1 = Note(title="Python Note", user_id=user.id)
    note1.tags = [tag1]
    note2 = Note(title="JS Note", user_id=user.id)
    note2.tags = [tag2]
    note3 = Note(title="Another Python Note", user_id=user.id)
    note3.tags = [tag1]
    db_session.add_all([note1, note2, note3])
    db_session.commit()

    # Login
    login_response = client.post(
        "/api/v1/auth/login/json",
        json={"username": "testuser", "password": "testpassword123"},
    )
    token = login_response.json()["access_token"]

    # Filter by tag
    response = client.get(
        f"/api/v1/notes/?tag_ids={tag1.id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == 2
    assert all("python" in [tag["name"] for tag in note["tags"]] for note in data)


def test_list_notes_with_search(client, db_session):
    """Test listing notes with search."""
    from app.models.note import Note
    from app.models.user import User

    # Create user
    user = User(email="test@example.com", username="testuser")
    user.set_password("testpassword123")
    db_session.add(user)
    db_session.commit()

    # Create notes
    note1 = Note(title="Python Tutorial", content="Learn Python", user_id=user.id)
    note2 = Note(title="JavaScript Guide", content="Learn JS", user_id=user.id)
    note3 = Note(title="Python Advanced", content="Advanced Python", user_id=user.id)
    db_session.add_all([note1, note2, note3])
    db_session.commit()

    # Login
    login_response = client.post(
        "/api/v1/auth/login/json",
        json={"username": "testuser", "password": "testpassword123"},
    )
    token = login_response.json()["access_token"]

    # Search for "Python"
    response = client.get(
        "/api/v1/notes/?search=Python",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == 2
    assert all("Python" in note["title"] for note in data)

    # Search in content
    response = client.get(
        "/api/v1/notes/?search=Learn",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == 2


def test_list_notes_with_pinned_filter(client, db_session):
    """Test listing notes filtered by pinned status."""
    from app.models.note import Note
    from app.models.user import User

    # Create user
    user = User(email="test@example.com", username="testuser")
    user.set_password("testpassword123")
    db_session.add(user)
    db_session.commit()

    # Create notes
    note1 = Note(title="Pinned Note", user_id=user.id, is_pinned=True)
    note2 = Note(title="Regular Note", user_id=user.id, is_pinned=False)
    note3 = Note(title="Another Pinned", user_id=user.id, is_pinned=True)
    db_session.add_all([note1, note2, note3])
    db_session.commit()

    # Login
    login_response = client.post(
        "/api/v1/auth/login/json",
        json={"username": "testuser", "password": "testpassword123"},
    )
    token = login_response.json()["access_token"]

    # Filter by pinned
    response = client.get(
        "/api/v1/notes/?is_pinned=true",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == 2
    assert all(note["is_pinned"] is True for note in data)


def test_get_note(client, db_session):
    """Test getting a specific note."""
    from app.models.note import Note
    from app.models.user import User

    # Create user
    user = User(email="test@example.com", username="testuser")
    user.set_password("testpassword123")
    db_session.add(user)
    db_session.commit()

    # Create note
    note = Note(title="Test Note", content="Content", user_id=user.id)
    db_session.add(note)
    db_session.commit()

    # Login
    login_response = client.post(
        "/api/v1/auth/login/json",
        json={"username": "testuser", "password": "testpassword123"},
    )
    token = login_response.json()["access_token"]

    # Get note
    response = client.get(
        f"/api/v1/notes/{note.id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == note.id
    assert data["title"] == "Test Note"
    assert data["content"] == "Content"


def test_get_note_not_found(client, db_session):
    """Test getting a nonexistent note."""
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

    # Get nonexistent note
    response = client.get(
        "/api/v1/notes/99999",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_get_note_other_user(client, db_session):
    """Test getting a note belonging to another user."""
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

    # Try to get user1's note
    response = client.get(
        f"/api/v1/notes/{note.id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_update_note(client, db_session):
    """Test updating a note."""
    from app.models.note import Note
    from app.models.user import User

    # Create user
    user = User(email="test@example.com", username="testuser")
    user.set_password("testpassword123")
    db_session.add(user)
    db_session.commit()

    # Create note
    note = Note(title="Original Title", content="Original content", user_id=user.id)
    db_session.add(note)
    db_session.commit()

    # Login
    login_response = client.post(
        "/api/v1/auth/login/json",
        json={"username": "testuser", "password": "testpassword123"},
    )
    token = login_response.json()["access_token"]

    # Update note
    response = client.put(
        f"/api/v1/notes/{note.id}",
        json={"title": "Updated Title", "content": "Updated content"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["title"] == "Updated Title"
    assert data["content"] == "Updated content"


def test_update_note_tags(client, db_session):
    """Test updating note tags."""
    from app.models.note import Note
    from app.models.tag import Tag
    from app.models.user import User

    # Create user
    user = User(email="test@example.com", username="testuser")
    user.set_password("testpassword123")
    db_session.add(user)
    db_session.commit()

    # Create tags
    tag1 = Tag(name="python")
    tag2 = Tag(name="fastapi")
    tag3 = Tag(name="django")
    db_session.add_all([tag1, tag2, tag3])
    db_session.commit()

    # Create note with tag1
    note = Note(title="Test Note", user_id=user.id)
    note.tags = [tag1]
    db_session.add(note)
    db_session.commit()

    # Login
    login_response = client.post(
        "/api/v1/auth/login/json",
        json={"username": "testuser", "password": "testpassword123"},
    )
    token = login_response.json()["access_token"]

    # Update tags
    response = client.put(
        f"/api/v1/notes/{note.id}",
        json={"tag_ids": [tag2.id, tag3.id]},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data["tags"]) == 2
    assert any(tag["name"] == "fastapi" for tag in data["tags"])
    assert any(tag["name"] == "django" for tag in data["tags"])


def test_delete_note(client, db_session):
    """Test deleting a note."""
    from app.models.note import Note
    from app.models.user import User

    # Create user
    user = User(email="test@example.com", username="testuser")
    user.set_password("testpassword123")
    db_session.add(user)
    db_session.commit()

    # Create note
    note = Note(title="Note to Delete", user_id=user.id)
    db_session.add(note)
    db_session.commit()
    note_id = note.id

    # Login
    login_response = client.post(
        "/api/v1/auth/login/json",
        json={"username": "testuser", "password": "testpassword123"},
    )
    token = login_response.json()["access_token"]

    # Delete note
    response = client.delete(
        f"/api/v1/notes/{note_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == status.HTTP_204_NO_CONTENT

    # Verify it's deleted
    get_response = client.get(
        f"/api/v1/notes/{note_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert get_response.status_code == status.HTTP_404_NOT_FOUND


def test_pin_note(client, db_session):
    """Test pinning a note."""
    from app.models.note import Note
    from app.models.user import User

    # Create user
    user = User(email="test@example.com", username="testuser")
    user.set_password("testpassword123")
    db_session.add(user)
    db_session.commit()

    # Create note
    note = Note(title="Test Note", user_id=user.id, is_pinned=False)
    db_session.add(note)
    db_session.commit()

    # Login
    login_response = client.post(
        "/api/v1/auth/login/json",
        json={"username": "testuser", "password": "testpassword123"},
    )
    token = login_response.json()["access_token"]

    # Pin note
    response = client.post(
        f"/api/v1/notes/{note.id}/pin",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["is_pinned"] is True


def test_archive_note(client, db_session):
    """Test archiving a note."""
    from app.models.note import Note
    from app.models.user import User

    # Create user
    user = User(email="test@example.com", username="testuser")
    user.set_password("testpassword123")
    db_session.add(user)
    db_session.commit()

    # Create note
    note = Note(title="Test Note", user_id=user.id, is_archived=False)
    db_session.add(note)
    db_session.commit()

    # Login
    login_response = client.post(
        "/api/v1/auth/login/json",
        json={"username": "testuser", "password": "testpassword123"},
    )
    token = login_response.json()["access_token"]

    # Archive note
    response = client.post(
        f"/api/v1/notes/{note.id}/archive",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["is_archived"] is True


def test_list_notes_requires_auth(client):
    """Test that listing notes requires authentication."""
    response = client.get("/api/v1/notes/")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_create_note_requires_auth(client):
    """Test that creating a note requires authentication."""
    response = client.post(
        "/api/v1/notes/",
        json={"title": "Test Note"},
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

