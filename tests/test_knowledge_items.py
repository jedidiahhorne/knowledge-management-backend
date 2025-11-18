"""Tests for knowledge items API."""
import pytest
from fastapi import status


def test_create_knowledge_item(client):
    """Test creating a knowledge item."""
    response = client.post(
        "/api/v1/knowledge-items/",
        json={
            "title": "Test Item",
            "content": "This is a test content",
            "tags": "test, example",
            "category": "testing",
        },
    )
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["title"] == "Test Item"
    assert data["content"] == "This is a test content"
    assert data["tags"] == "test, example"
    assert data["category"] == "testing"
    assert "id" in data
    assert "created_at" in data
    assert "updated_at" in data


def test_create_knowledge_item_minimal(client):
    """Test creating a knowledge item with only title."""
    response = client.post(
        "/api/v1/knowledge-items/",
        json={"title": "Minimal Item"},
    )
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["title"] == "Minimal Item"
    assert data["content"] is None


def test_get_knowledge_item(client):
    """Test getting a knowledge item by ID."""
    # Create an item first
    create_response = client.post(
        "/api/v1/knowledge-items/",
        json={"title": "Get Test Item", "content": "Content for get test"},
    )
    item_id = create_response.json()["id"]

    # Get the item
    response = client.get(f"/api/v1/knowledge-items/{item_id}")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == item_id
    assert data["title"] == "Get Test Item"
    assert data["content"] == "Content for get test"


def test_get_nonexistent_knowledge_item(client):
    """Test getting a nonexistent knowledge item."""
    response = client.get("/api/v1/knowledge-items/99999")
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_list_knowledge_items(client):
    """Test listing knowledge items."""
    # Create multiple items
    for i in range(3):
        client.post(
            "/api/v1/knowledge-items/",
            json={"title": f"Item {i+1}", "content": f"Content {i+1}"},
        )

    # List all items
    response = client.get("/api/v1/knowledge-items/")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == 3
    assert all("id" in item for item in data)
    assert all("title" in item for item in data)


def test_list_knowledge_items_with_category_filter(client):
    """Test listing knowledge items with category filter."""
    # Create items with different categories
    client.post(
        "/api/v1/knowledge-items/",
        json={"title": "Category A Item", "category": "A"},
    )
    client.post(
        "/api/v1/knowledge-items/",
        json={"title": "Category B Item", "category": "B"},
    )
    client.post(
        "/api/v1/knowledge-items/",
        json={"title": "Another Category A Item", "category": "A"},
    )

    # Filter by category
    response = client.get("/api/v1/knowledge-items/?category=A")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == 2
    assert all(item["category"] == "A" for item in data)


def test_update_knowledge_item(client):
    """Test updating a knowledge item."""
    # Create an item
    create_response = client.post(
        "/api/v1/knowledge-items/",
        json={"title": "Original Title", "content": "Original content"},
    )
    item_id = create_response.json()["id"]

    # Update the item
    response = client.put(
        f"/api/v1/knowledge-items/{item_id}",
        json={"title": "Updated Title", "content": "Updated content"},
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["title"] == "Updated Title"
    assert data["content"] == "Updated content"
    assert data["id"] == item_id


def test_update_knowledge_item_partial(client):
    """Test partial update of a knowledge item."""
    # Create an item
    create_response = client.post(
        "/api/v1/knowledge-items/",
        json={"title": "Original Title", "content": "Original content", "category": "old"},
    )
    item_id = create_response.json()["id"]

    # Update only title
    response = client.put(
        f"/api/v1/knowledge-items/{item_id}",
        json={"title": "Updated Title"},
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["title"] == "Updated Title"
    assert data["content"] == "Original content"  # Should remain unchanged
    assert data["category"] == "old"  # Should remain unchanged


def test_update_nonexistent_knowledge_item(client):
    """Test updating a nonexistent knowledge item."""
    response = client.put(
        "/api/v1/knowledge-items/99999",
        json={"title": "Updated Title"},
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_delete_knowledge_item(client):
    """Test deleting a knowledge item."""
    # Create an item
    create_response = client.post(
        "/api/v1/knowledge-items/",
        json={"title": "Item to Delete", "content": "This will be deleted"},
    )
    item_id = create_response.json()["id"]

    # Delete the item
    response = client.delete(f"/api/v1/knowledge-items/{item_id}")
    assert response.status_code == status.HTTP_204_NO_CONTENT

    # Verify it's deleted
    get_response = client.get(f"/api/v1/knowledge-items/{item_id}")
    assert get_response.status_code == status.HTTP_404_NOT_FOUND


def test_delete_nonexistent_knowledge_item(client):
    """Test deleting a nonexistent knowledge item."""
    response = client.delete("/api/v1/knowledge-items/99999")
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_create_knowledge_item_validation(client):
    """Test validation when creating a knowledge item."""
    # Missing required field (title)
    response = client.post(
        "/api/v1/knowledge-items/",
        json={"content": "Content without title"},
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    # Empty title
    response = client.post(
        "/api/v1/knowledge-items/",
        json={"title": ""},
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

