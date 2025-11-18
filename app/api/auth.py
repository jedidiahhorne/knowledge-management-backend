"""Authentication API routes."""
from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.dependencies import get_current_active_user
from app.core.security import (
    create_access_token,
    create_password_reset_token,
    create_refresh_token,
    verify_password_reset_token,
)
from app.db import get_db
from app.models.user import User
from app.schemas.auth import (
    PasswordChange,
    PasswordReset,
    PasswordResetRequest,
    Token,
    TokenRefresh,
    UserLogin,
    UserRegister,
    UserResponse,
)

router = APIRouter(prefix="/auth", tags=["authentication"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user_data: UserRegister, db: Session = Depends(get_db)):
    """Register a new user."""
    # Check if user with email already exists
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    # Check if username already exists
    existing_username = db.query(User).filter(User.username == user_data.username).first()
    if existing_username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken",
        )

    # Create new user
    user = User(
        email=user_data.email,
        username=user_data.username,
        full_name=user_data.full_name,
    )
    user.set_password(user_data.password)
    db.add(user)
    db.commit()
    db.refresh(user)

    return user


@router.post("/login", response_model=Token)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    """Login and get access token."""
    # Find user by username
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or not user.check_password(form_data.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user",
        )

    # Create tokens
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id), "username": user.username},
        expires_delta=access_token_expires,
    )
    refresh_token = create_refresh_token(data={"sub": str(user.id), "username": user.username})

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


@router.post("/login/json", response_model=Token)
def login_json(user_data: UserLogin, db: Session = Depends(get_db)):
    """Login using JSON body (alternative to form data)."""
    user = db.query(User).filter(User.username == user_data.username).first()
    if not user or not user.check_password(user_data.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user",
        )

    # Create tokens
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id), "username": user.username},
        expires_delta=access_token_expires,
    )
    refresh_token = create_refresh_token(data={"sub": str(user.id), "username": user.username})

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


@router.post("/refresh", response_model=Token)
def refresh_token(token_data: TokenRefresh, db: Session = Depends(get_db)):
    """Refresh access token using refresh token."""
    from app.core.security import verify_token

    payload = verify_token(token_data.refresh_token, token_type="refresh")
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )

    user_id: int = payload.get("sub")
    user = db.query(User).filter(User.id == user_id).first()
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive",
        )

    # Create new tokens
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.id, "username": user.username},
        expires_delta=access_token_expires,
    )
    refresh_token = create_refresh_token(data={"sub": user.id, "username": user.username})

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


@router.post("/password-reset-request", status_code=status.HTTP_200_OK)
def request_password_reset(
    request: PasswordResetRequest,
    db: Session = Depends(get_db),
):
    """Request a password reset token (sends token, in production would send email)."""
    user = db.query(User).filter(User.email == request.email).first()
    if not user:
        # Don't reveal if email exists for security
        return {"message": "If the email exists, a password reset token has been generated"}

    reset_token = create_password_reset_token(email=user.email)
    # In production, send this token via email
    # For now, return it (in production, don't return it)
    return {
        "message": "Password reset token generated",
        "token": reset_token,  # Remove this in production
    }


@router.post("/password-reset", status_code=status.HTTP_200_OK)
def reset_password(
    reset_data: PasswordReset,
    db: Session = Depends(get_db),
):
    """Reset password using reset token."""
    email = verify_password_reset_token(reset_data.token)
    if email is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token",
        )

    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    user.set_password(reset_data.new_password)
    db.commit()

    return {"message": "Password reset successfully"}


@router.post("/password-change", status_code=status.HTTP_200_OK)
def change_password(
    password_data: PasswordChange,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Change password (requires current password)."""
    if not current_user.check_password(password_data.current_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect current password",
        )

    current_user.set_password(password_data.new_password)
    db.commit()

    return {"message": "Password changed successfully"}


@router.get("/me", response_model=UserResponse)
def get_current_user_info(current_user: User = Depends(get_current_active_user)):
    """Get current user information."""
    return current_user

