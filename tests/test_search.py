"""Tests for search API endpoints."""
from datetime import datetime, timedelta

from fastapi import status


def test_search_notes_full_text(client, db_session):
    """Test full-text search in notes."""
    from app.models.note import Note
    from app.models.user import User

    # Create user
    user = User(email="test@example.com", username="testuser")
    user.set_password("testpassword123")
    db_session.add(user)
    db_session.commit()

    # Create notes
    note1 = Note(title="Python Tutorial", content="Learn Python programming", user_id=user.id)
    note2 = Note(title="JavaScript Guide", content="Learn JavaScript", user_id=user.id)
    note3 = Note(title="Python Advanced", content="Advanced Python concepts", user_id=user.id)
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
        "/api/v1/search/notes?query=Python",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["total"] == 2
    assert len(data["notes"]) == 2
    assert all("Python" in note["title"] for note in data["notes"])


def test_search_notes_by_tag_ids(client, db_session):
    """Test searching notes by tag IDs."""
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

    # Search by tag ID
    response = client.get(
        f"/api/v1/search/notes?tag_ids={tag1.id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["total"] == 2
    assert all(tag1.id in [tag["id"] for tag in note["tags"]] for note in data["notes"])


def test_search_notes_by_tag_names(client, db_session):
    """Test searching notes by tag names."""
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
    db_session.add_all([note1, note2])
    db_session.commit()

    # Login
    login_response = client.post(
        "/api/v1/auth/login/json",
        json={"username": "testuser", "password": "testpassword123"},
    )
    token = login_response.json()["access_token"]

    # Search by tag name
    response = client.get(
        "/api/v1/search/notes?tag_names=python",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["total"] == 1
    assert "python" in [tag["name"] for tag in data["notes"][0]["tags"]]


def test_search_notes_by_pinned_status(client, db_session):
    """Test searching notes by pinned status."""
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

    # Search pinned notes
    response = client.get(
        "/api/v1/search/notes?is_pinned=true",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["total"] == 2
    assert all(note["is_pinned"] is True for note in data["notes"])


def test_search_notes_by_date_range(client, db_session):
    """Test searching notes by date range."""
    from app.models.note import Note
    from app.models.user import User

    # Create user
    user = User(email="test@example.com", username="testuser")
    user.set_password("testpassword123")
    db_session.add(user)
    db_session.commit()

    # Create notes with different dates
    now = datetime.utcnow()
    note1 = Note(title="Old Note", user_id=user.id)
    note1.created_at = now - timedelta(days=10)
    note2 = Note(title="Recent Note", user_id=user.id)
    note2.created_at = now - timedelta(days=2)
    note3 = Note(title="New Note", user_id=user.id)
    note3.created_at = now
    db_session.add_all([note1, note2, note3])
    db_session.commit()

    # Login
    login_response = client.post(
        "/api/v1/auth/login/json",
        json={"username": "testuser", "password": "testpassword123"},
    )
    token = login_response.json()["access_token"]

    # Search notes created in last 5 days
    created_after = (now - timedelta(days=5)).isoformat()
    response = client.get(
        f"/api/v1/search/notes?created_after={created_after}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["total"] == 2


def test_search_notes_combined_filters(client, db_session):
    """Test searching notes with multiple filters combined."""
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
    tag2 = Tag(name="tutorial")
    db_session.add_all([tag1, tag2])
    db_session.commit()

    # Create notes
    note1 = Note(title="Python Tutorial", content="Learn Python", user_id=user.id, is_pinned=True)
    note1.tags = [tag1, tag2]
    note2 = Note(title="JavaScript Tutorial", content="Learn JS", user_id=user.id, is_pinned=False)
    note2.tags = [tag2]
    note3 = Note(title="Python Advanced", user_id=user.id, is_pinned=True)
    note3.tags = [tag1]
    db_session.add_all([note1, note2, note3])
    db_session.commit()

    # Login
    login_response = client.post(
        "/api/v1/auth/login/json",
        json={"username": "testuser", "password": "testpassword123"},
    )
    token = login_response.json()["access_token"]

    # Search with multiple filters
    response = client.get(
        f"/api/v1/search/notes?query=Python&tag_ids={tag1.id}&is_pinned=true",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    # Both note1 and note3 match: Python + tag1 + pinned
    assert data["total"] == 2
    assert all("Python" in note["title"] for note in data["notes"])
    assert all(note["is_pinned"] is True for note in data["notes"])
    assert all(tag1.id in [tag["id"] for tag in note["tags"]] for note in data["notes"])


def test_search_notes_pagination(client, db_session):
    """Test search notes with pagination."""
    from app.models.note import Note
    from app.models.user import User

    # Create user
    user = User(email="test@example.com", username="testuser")
    user.set_password("testpassword123")
    db_session.add(user)
    db_session.commit()

    # Create multiple notes
    notes = [
        Note(title=f"Note {i}", user_id=user.id) for i in range(15)
    ]
    db_session.add_all(notes)
    db_session.commit()

    # Login
    login_response = client.post(
        "/api/v1/auth/login/json",
        json={"username": "testuser", "password": "testpassword123"},
    )
    token = login_response.json()["access_token"]

    # First page
    response = client.get(
        "/api/v1/search/notes?skip=0&limit=10",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["total"] == 15
    assert len(data["notes"]) == 10
    assert data["skip"] == 0
    assert data["limit"] == 10

    # Second page
    response = client.get(
        "/api/v1/search/notes?skip=10&limit=10",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data["notes"]) == 5
    assert data["skip"] == 10


def test_search_notes_post_endpoint(client, db_session):
    """Test search notes using POST endpoint."""
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
    db_session.add_all([note1, note2])
    db_session.commit()

    # Login
    login_response = client.post(
        "/api/v1/auth/login/json",
        json={"username": "testuser", "password": "testpassword123"},
    )
    token = login_response.json()["access_token"]

    # Search using POST
    response = client.post(
        "/api/v1/search/notes",
        json={"query": "Python", "limit": 10},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["total"] == 1
    assert data["notes"][0]["title"] == "Python Tutorial"


def test_search_tags(client, db_session):
    """Test searching tags."""
    from app.models.tag import Tag
    from app.models.user import User

    # Create user
    user = User(email="test@example.com", username="testuser")
    user.set_password("testpassword123")
    db_session.add(user)
    db_session.commit()

    # Create tags
    tag1 = Tag(name="python", description="Python programming language")
    tag2 = Tag(name="javascript", description="JavaScript language")
    tag3 = Tag(name="python-advanced", description="Advanced Python")
    db_session.add_all([tag1, tag2, tag3])
    db_session.commit()

    # Login
    login_response = client.post(
        "/api/v1/auth/login/json",
        json={"username": "testuser", "password": "testpassword123"},
    )
    token = login_response.json()["access_token"]

    # Search tags
    response = client.get(
        "/api/v1/search/tags?query=python",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["total"] == 2
    assert all("python" in tag["name"].lower() for tag in data["tags"])


def test_search_tags_post_endpoint(client, db_session):
    """Test search tags using POST endpoint."""
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
    db_session.add_all([tag1, tag2])
    db_session.commit()

    # Login
    login_response = client.post(
        "/api/v1/auth/login/json",
        json={"username": "testuser", "password": "testpassword123"},
    )
    token = login_response.json()["access_token"]

    # Search using POST
    response = client.post(
        "/api/v1/search/tags",
        json={"query": "python"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["total"] == 1
    assert data["tags"][0]["name"] == "python"


def test_search_notes_user_isolation(client, db_session):
    """Test that search only returns notes for the authenticated user."""
    from app.models.note import Note
    from app.models.user import User

    # Create two users
    user1 = User(email="user1@example.com", username="user1")
    user1.set_password("password123")
    user2 = User(email="user2@example.com", username="user2")
    user2.set_password("password123")
    db_session.add_all([user1, user2])
    db_session.commit()

    # Create notes for both users
    note1 = Note(title="User1 Note", content="Content", user_id=user1.id)
    note2 = Note(title="User2 Note", content="Content", user_id=user2.id)
    db_session.add_all([note1, note2])
    db_session.commit()

    # Login as user1
    login_response = client.post(
        "/api/v1/auth/login/json",
        json={"username": "user1", "password": "password123"},
    )
    token = login_response.json()["access_token"]

    # Search - should only return user1's notes
    response = client.get(
        "/api/v1/search/notes?query=Content",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["total"] == 1
    assert data["notes"][0]["title"] == "User1 Note"


def test_search_notes_empty_results(client, db_session):
    """Test search with no matching results."""
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

    # Search with no matches
    response = client.get(
        "/api/v1/search/notes?query=NonexistentTerm",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["total"] == 0
    assert len(data["notes"]) == 0


def test_search_requires_auth(client):
    """Test that search requires authentication."""
    response = client.get("/api/v1/search/notes?query=test")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

    response = client.get("/api/v1/search/tags?query=test")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

