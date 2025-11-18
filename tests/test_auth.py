"""Tests for authentication endpoints."""
from fastapi import status


def test_register_user(client):
    """Test user registration."""
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "test@example.com",
            "username": "testuser",
            "password": "testpassword123",
            "full_name": "Test User",
        },
    )
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["email"] == "test@example.com"
    assert data["username"] == "testuser"
    assert data["full_name"] == "Test User"
    assert "id" in data
    assert "password" not in data
    assert "hashed_password" not in data


def test_register_duplicate_email(client):
    """Test registration with duplicate email."""
    # Register first user
    client.post(
        "/api/v1/auth/register",
        json={
            "email": "test@example.com",
            "username": "testuser1",
            "password": "testpassword123",
        },
    )

    # Try to register with same email
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "test@example.com",
            "username": "testuser2",
            "password": "testpassword123",
        },
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "Email already registered" in response.json()["detail"]


def test_register_duplicate_username(client):
    """Test registration with duplicate username."""
    # Register first user
    client.post(
        "/api/v1/auth/register",
        json={
            "email": "test1@example.com",
            "username": "testuser",
            "password": "testpassword123",
        },
    )

    # Try to register with same username
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "test2@example.com",
            "username": "testuser",
            "password": "testpassword123",
        },
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "Username already taken" in response.json()["detail"]


def test_register_validation(client):
    """Test registration validation."""
    # Short password
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "test@example.com",
            "username": "testuser",
            "password": "short",
        },
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    # Invalid email
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "invalid-email",
            "username": "testuser",
            "password": "testpassword123",
        },
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_login_success(client, db_session):
    """Test successful login."""
    from app.models.user import User

    # Create a user
    user = User(
        email="test@example.com",
        username="testuser",
    )
    user.set_password("testpassword123")
    db_session.add(user)
    db_session.commit()

    # Login
    response = client.post(
        "/api/v1/auth/login/json",
        json={"username": "testuser", "password": "testpassword123"},
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"
    assert len(data["access_token"]) > 0
    assert len(data["refresh_token"]) > 0


def test_login_invalid_credentials(client, db_session):
    """Test login with invalid credentials."""
    from app.models.user import User

    # Create a user
    user = User(
        email="test@example.com",
        username="testuser",
    )
    user.set_password("testpassword123")
    db_session.add(user)
    db_session.commit()

    # Wrong password
    response = client.post(
        "/api/v1/auth/login/json",
        json={"username": "testuser", "password": "wrongpassword"},
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

    # Wrong username
    response = client.post(
        "/api/v1/auth/login/json",
        json={"username": "wronguser", "password": "testpassword123"},
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_login_inactive_user(client, db_session):
    """Test login with inactive user."""
    from app.models.user import User

    # Create inactive user
    user = User(
        email="test@example.com",
        username="testuser",
        is_active=False,
    )
    user.set_password("testpassword123")
    db_session.add(user)
    db_session.commit()

    # Try to login
    response = client.post(
        "/api/v1/auth/login/json",
        json={"username": "testuser", "password": "testpassword123"},
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "Inactive user" in response.json()["detail"]


def test_get_current_user(client, db_session):
    """Test getting current user info."""
    from app.models.user import User

    # Create and login user
    user = User(
        email="test@example.com",
        username="testuser",
    )
    user.set_password("testpassword123")
    db_session.add(user)
    db_session.commit()

    # Login to get token
    login_response = client.post(
        "/api/v1/auth/login/json",
        json={"username": "testuser", "password": "testpassword123"},
    )
    token = login_response.json()["access_token"]

    # Get current user
    response = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["username"] == "testuser"
    assert data["email"] == "test@example.com"
    assert "password" not in data


def test_get_current_user_invalid_token(client):
    """Test getting current user with invalid token."""
    response = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": "Bearer invalid_token"},
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_refresh_token(client, db_session):
    """Test token refresh."""
    from app.models.user import User

    # Create and login user
    user = User(
        email="test@example.com",
        username="testuser",
    )
    user.set_password("testpassword123")
    db_session.add(user)
    db_session.commit()

    # Login to get tokens
    login_response = client.post(
        "/api/v1/auth/login/json",
        json={"username": "testuser", "password": "testpassword123"},
    )
    refresh_token = login_response.json()["refresh_token"]

    # Refresh token
    response = client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": refresh_token},
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert len(data["access_token"]) > 0
    assert len(data["refresh_token"]) > 0


def test_refresh_token_invalid(client):
    """Test refresh with invalid token."""
    response = client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": "invalid_token"},
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_password_reset_request(client, db_session):
    """Test password reset request."""
    from app.models.user import User

    # Create user
    user = User(
        email="test@example.com",
        username="testuser",
    )
    user.set_password("testpassword123")
    db_session.add(user)
    db_session.commit()

    # Request password reset
    response = client.post(
        "/api/v1/auth/password-reset-request",
        json={"email": "test@example.com"},
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "token" in data
    assert len(data["token"]) > 0


def test_password_reset_request_nonexistent_email(client):
    """Test password reset request with nonexistent email."""
    response = client.post(
        "/api/v1/auth/password-reset-request",
        json={"email": "nonexistent@example.com"},
    )
    # Should still return 200 for security (don't reveal if email exists)
    assert response.status_code == status.HTTP_200_OK


def test_password_reset(client, db_session):
    """Test password reset."""
    from app.core.security import create_password_reset_token
    from app.models.user import User

    # Create user
    user = User(
        email="test@example.com",
        username="testuser",
    )
    user.set_password("oldpassword123")
    db_session.add(user)
    db_session.commit()

    # Generate reset token
    reset_token = create_password_reset_token(user.email)

    # Reset password
    response = client.post(
        "/api/v1/auth/password-reset",
        json={"token": reset_token, "new_password": "newpassword123"},
    )
    assert response.status_code == status.HTTP_200_OK

    # Verify new password works
    db_session.refresh(user)
    assert user.check_password("newpassword123")
    assert not user.check_password("oldpassword123")


def test_password_reset_invalid_token(client):
    """Test password reset with invalid token."""
    response = client.post(
        "/api/v1/auth/password-reset",
        json={"token": "invalid_token", "new_password": "newpassword123"},
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_password_change(client, db_session):
    """Test password change."""
    from app.models.user import User

    # Create and login user
    user = User(
        email="test@example.com",
        username="testuser",
    )
    user.set_password("oldpassword123")
    db_session.add(user)
    db_session.commit()

    # Login to get token
    login_response = client.post(
        "/api/v1/auth/login/json",
        json={"username": "testuser", "password": "oldpassword123"},
    )
    token = login_response.json()["access_token"]

    # Change password
    response = client.post(
        "/api/v1/auth/password-change",
        json={"current_password": "oldpassword123", "new_password": "newpassword123"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == status.HTTP_200_OK

    # Verify new password works
    db_session.refresh(user)
    assert user.check_password("newpassword123")
    assert not user.check_password("oldpassword123")


def test_password_change_wrong_current_password(client, db_session):
    """Test password change with wrong current password."""
    from app.models.user import User

    # Create and login user
    user = User(
        email="test@example.com",
        username="testuser",
    )
    user.set_password("oldpassword123")
    db_session.add(user)
    db_session.commit()

    # Login to get token
    login_response = client.post(
        "/api/v1/auth/login/json",
        json={"username": "testuser", "password": "oldpassword123"},
    )
    token = login_response.json()["access_token"]

    # Try to change password with wrong current password
    response = client.post(
        "/api/v1/auth/password-change",
        json={"current_password": "wrongpassword", "new_password": "newpassword123"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "Incorrect current password" in response.json()["detail"]


def test_password_change_validation(client, db_session):
    """Test password change validation."""
    from app.models.user import User

    # Create and login user
    user = User(
        email="test@example.com",
        username="testuser",
    )
    user.set_password("oldpassword123")
    db_session.add(user)
    db_session.commit()

    # Login to get token
    login_response = client.post(
        "/api/v1/auth/login/json",
        json={"username": "testuser", "password": "oldpassword123"},
    )
    token = login_response.json()["access_token"]

    # Try to change password with short new password
    response = client.post(
        "/api/v1/auth/password-change",
        json={"current_password": "oldpassword123", "new_password": "short"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

