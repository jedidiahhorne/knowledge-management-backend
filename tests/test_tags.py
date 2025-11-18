"""Tests for tags API endpoints."""
from fastapi import status


def test_create_tag(client, db_session):
    """Test creating a tag."""
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

    # Create a tag
    response = client.post(
        "/api/v1/tags/",
        json={
            "name": "python",
            "color": "#3776ab",
            "description": "Python programming language",
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["name"] == "python"
    assert data["color"] == "#3776ab"
    assert data["description"] == "Python programming language"
    assert "id" in data
    assert "created_at" in data


def test_create_tag_duplicate_name(client, db_session):
    """Test creating a tag with duplicate name."""
    from app.models.tag import Tag
    from app.models.user import User

    # Create user
    user = User(email="test@example.com", username="testuser")
    user.set_password("testpassword123")
    db_session.add(user)
    db_session.commit()

    # Create existing tag
    existing_tag = Tag(name="python", color="#3776ab")
    db_session.add(existing_tag)
    db_session.commit()

    # Login
    login_response = client.post(
        "/api/v1/auth/login/json",
        json={"username": "testuser", "password": "testpassword123"},
    )
    token = login_response.json()["access_token"]

    # Try to create duplicate tag
    response = client.post(
        "/api/v1/tags/",
        json={"name": "python", "color": "#000000"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "already exists" in response.json()["detail"]


def test_list_tags(client, db_session):
    """Test listing tags."""
    from app.models.tag import Tag
    from app.models.user import User

    # Create user
    user = User(email="test@example.com", username="testuser")
    user.set_password("testpassword123")
    db_session.add(user)
    db_session.commit()

    # Create tags
    tag1 = Tag(name="python", color="#3776ab")
    tag2 = Tag(name="javascript", color="#f7df1e")
    tag3 = Tag(name="fastapi", color="#009688")
    db_session.add_all([tag1, tag2, tag3])
    db_session.commit()

    # Login
    login_response = client.post(
        "/api/v1/auth/login/json",
        json={"username": "testuser", "password": "testpassword123"},
    )
    token = login_response.json()["access_token"]

    # List tags
    response = client.get(
        "/api/v1/tags/",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == 3
    assert all("id" in tag for tag in data)
    assert all("name" in tag for tag in data)
    # Should be ordered by name
    assert data[0]["name"] == "fastapi"
    assert data[1]["name"] == "javascript"
    assert data[2]["name"] == "python"


def test_list_tags_with_search(client, db_session):
    """Test listing tags with search."""
    from app.models.tag import Tag
    from app.models.user import User

    # Create user
    user = User(email="test@example.com", username="testuser")
    user.set_password("testpassword123")
    db_session.add(user)
    db_session.commit()

    # Create tags
    tag1 = Tag(name="python", description="Python language")
    tag2 = Tag(name="javascript", description="JS language")
    tag3 = Tag(name="python-advanced", description="Advanced Python")
    db_session.add_all([tag1, tag2, tag3])
    db_session.commit()

    # Login
    login_response = client.post(
        "/api/v1/auth/login/json",
        json={"username": "testuser", "password": "testpassword123"},
    )
    token = login_response.json()["access_token"]

    # Search for "python"
    response = client.get(
        "/api/v1/tags/?search=python",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == 2
    assert all("python" in tag["name"].lower() for tag in data)


def test_get_tag(client, db_session):
    """Test getting a specific tag."""
    from app.models.tag import Tag
    from app.models.user import User

    # Create user
    user = User(email="test@example.com", username="testuser")
    user.set_password("testpassword123")
    db_session.add(user)
    db_session.commit()

    # Create tag
    tag = Tag(name="python", color="#3776ab", description="Python language")
    db_session.add(tag)
    db_session.commit()

    # Login
    login_response = client.post(
        "/api/v1/auth/login/json",
        json={"username": "testuser", "password": "testpassword123"},
    )
    token = login_response.json()["access_token"]

    # Get tag
    response = client.get(
        f"/api/v1/tags/{tag.id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == tag.id
    assert data["name"] == "python"
    assert data["color"] == "#3776ab"


def test_get_tag_not_found(client, db_session):
    """Test getting a nonexistent tag."""
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

    # Get nonexistent tag
    response = client.get(
        "/api/v1/tags/99999",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_update_tag(client, db_session):
    """Test updating a tag."""
    from app.models.tag import Tag
    from app.models.user import User

    # Create user
    user = User(email="test@example.com", username="testuser")
    user.set_password("testpassword123")
    db_session.add(user)
    db_session.commit()

    # Create tag
    tag = Tag(name="python", color="#3776ab")
    db_session.add(tag)
    db_session.commit()

    # Login
    login_response = client.post(
        "/api/v1/auth/login/json",
        json={"username": "testuser", "password": "testpassword123"},
    )
    token = login_response.json()["access_token"]

    # Update tag
    response = client.put(
        f"/api/v1/tags/{tag.id}",
        json={"name": "python3", "color": "#000000", "description": "Updated description"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["name"] == "python3"
    assert data["color"] == "#000000"
    assert data["description"] == "Updated description"


def test_update_tag_partial(client, db_session):
    """Test partial update of a tag."""
    from app.models.tag import Tag
    from app.models.user import User

    # Create user
    user = User(email="test@example.com", username="testuser")
    user.set_password("testpassword123")
    db_session.add(user)
    db_session.commit()

    # Create tag
    tag = Tag(name="python", color="#3776ab", description="Original description")
    db_session.add(tag)
    db_session.commit()

    # Login
    login_response = client.post(
        "/api/v1/auth/login/json",
        json={"username": "testuser", "password": "testpassword123"},
    )
    token = login_response.json()["access_token"]

    # Update only color
    response = client.put(
        f"/api/v1/tags/{tag.id}",
        json={"color": "#ff0000"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["name"] == "python"  # Unchanged
    assert data["color"] == "#ff0000"  # Updated
    assert data["description"] == "Original description"  # Unchanged


def test_update_tag_duplicate_name(client, db_session):
    """Test updating a tag with duplicate name."""
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

    # Login
    login_response = client.post(
        "/api/v1/auth/login/json",
        json={"username": "testuser", "password": "testpassword123"},
    )
    token = login_response.json()["access_token"]

    # Try to rename tag2 to "python"
    response = client.put(
        f"/api/v1/tags/{tag2.id}",
        json={"name": "python"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "already exists" in response.json()["detail"]


def test_delete_tag(client, db_session):
    """Test deleting a tag."""
    from app.models.tag import Tag
    from app.models.user import User

    # Create user
    user = User(email="test@example.com", username="testuser")
    user.set_password("testpassword123")
    db_session.add(user)
    db_session.commit()

    # Create tag
    tag = Tag(name="python", color="#3776ab")
    db_session.add(tag)
    db_session.commit()
    tag_id = tag.id

    # Login
    login_response = client.post(
        "/api/v1/auth/login/json",
        json={"username": "testuser", "password": "testpassword123"},
    )
    token = login_response.json()["access_token"]

    # Delete tag
    response = client.delete(
        f"/api/v1/tags/{tag_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == status.HTTP_204_NO_CONTENT

    # Verify it's deleted
    get_response = client.get(
        f"/api/v1/tags/{tag_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert get_response.status_code == status.HTTP_404_NOT_FOUND


def test_add_tag_to_note(client, db_session):
    """Test adding a tag to a note."""
    from app.models.note import Note
    from app.models.tag import Tag
    from app.models.user import User

    # Create user
    user = User(email="test@example.com", username="testuser")
    user.set_password("testpassword123")
    db_session.add(user)
    db_session.commit()

    # Create tag and note
    tag = Tag(name="python")
    note = Note(title="Test Note", user_id=user.id)
    db_session.add_all([tag, note])
    db_session.commit()

    # Login
    login_response = client.post(
        "/api/v1/auth/login/json",
        json={"username": "testuser", "password": "testpassword123"},
    )
    token = login_response.json()["access_token"]

    # Add tag to note
    response = client.post(
        f"/api/v1/tags/{tag.id}/notes/{note.id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == status.HTTP_200_OK

    # Verify tag was added
    db_session.refresh(note)
    assert tag in note.tags
    assert len(note.tags) == 1


def test_add_tag_to_note_already_has_tag(client, db_session):
    """Test adding a tag to a note that already has it."""
    from app.models.note import Note
    from app.models.tag import Tag
    from app.models.user import User

    # Create user
    user = User(email="test@example.com", username="testuser")
    user.set_password("testpassword123")
    db_session.add(user)
    db_session.commit()

    # Create tag and note with tag already attached
    tag = Tag(name="python")
    note = Note(title="Test Note", user_id=user.id)
    note.tags = [tag]
    db_session.add_all([tag, note])
    db_session.commit()

    # Login
    login_response = client.post(
        "/api/v1/auth/login/json",
        json={"username": "testuser", "password": "testpassword123"},
    )
    token = login_response.json()["access_token"]

    # Try to add tag again (should not error, just return success)
    response = client.post(
        f"/api/v1/tags/{tag.id}/notes/{note.id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == status.HTTP_200_OK

    # Verify tag is still there (only once)
    db_session.refresh(note)
    assert tag in note.tags
    assert len(note.tags) == 1


def test_add_tag_to_note_other_user(client, db_session):
    """Test adding a tag to another user's note."""
    from app.models.note import Note
    from app.models.tag import Tag
    from app.models.user import User

    # Create two users
    user1 = User(email="user1@example.com", username="user1")
    user1.set_password("password123")
    user2 = User(email="user2@example.com", username="user2")
    user2.set_password("password123")
    db_session.add_all([user1, user2])
    db_session.commit()

    # Create tag and note for user1
    tag = Tag(name="python")
    note = Note(title="User1 Note", user_id=user1.id)
    db_session.add_all([tag, note])
    db_session.commit()

    # Login as user2
    login_response = client.post(
        "/api/v1/auth/login/json",
        json={"username": "user2", "password": "password123"},
    )
    token = login_response.json()["access_token"]

    # Try to add tag to user1's note
    response = client.post(
        f"/api/v1/tags/{tag.id}/notes/{note.id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_remove_tag_from_note(client, db_session):
    """Test removing a tag from a note."""
    from app.models.note import Note
    from app.models.tag import Tag
    from app.models.user import User

    # Create user
    user = User(email="test@example.com", username="testuser")
    user.set_password("testpassword123")
    db_session.add(user)
    db_session.commit()

    # Create tag and note with tag
    tag = Tag(name="python")
    note = Note(title="Test Note", user_id=user.id)
    note.tags = [tag]
    db_session.add_all([tag, note])
    db_session.commit()

    # Login
    login_response = client.post(
        "/api/v1/auth/login/json",
        json={"username": "testuser", "password": "testpassword123"},
    )
    token = login_response.json()["access_token"]

    # Remove tag from note
    response = client.delete(
        f"/api/v1/tags/{tag.id}/notes/{note.id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == status.HTTP_204_NO_CONTENT

    # Verify tag was removed
    db_session.refresh(note)
    assert tag not in note.tags
    assert len(note.tags) == 0


def test_remove_tag_from_note_not_attached(client, db_session):
    """Test removing a tag from a note that doesn't have it."""
    from app.models.note import Note
    from app.models.tag import Tag
    from app.models.user import User

    # Create user
    user = User(email="test@example.com", username="testuser")
    user.set_password("testpassword123")
    db_session.add(user)
    db_session.commit()

    # Create tag and note without tag
    tag = Tag(name="python")
    note = Note(title="Test Note", user_id=user.id)
    db_session.add_all([tag, note])
    db_session.commit()

    # Login
    login_response = client.post(
        "/api/v1/auth/login/json",
        json={"username": "testuser", "password": "testpassword123"},
    )
    token = login_response.json()["access_token"]

    # Try to remove tag (should not error, just return success)
    response = client.delete(
        f"/api/v1/tags/{tag.id}/notes/{note.id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == status.HTTP_204_NO_CONTENT


def test_list_tags_requires_auth(client):
    """Test that listing tags requires authentication."""
    response = client.get("/api/v1/tags/")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_create_tag_requires_auth(client):
    """Test that creating a tag requires authentication."""
    response = client.post(
        "/api/v1/tags/",
        json={"name": "test"},
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

