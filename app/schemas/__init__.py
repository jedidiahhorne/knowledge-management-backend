"""Pydantic schemas for request/response validation."""
from app.schemas.attachment import AttachmentResponse
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
from app.schemas.knowledge_item import (
    KnowledgeItemCreate,
    KnowledgeItemResponse,
    KnowledgeItemUpdate,
)
from app.schemas.note import NoteCreate, NoteResponse, NoteUpdate
from app.schemas.search import (
    SearchNotesRequest,
    SearchNotesResponse,
    SearchTagsRequest,
    SearchTagsResponse,
)
from app.schemas.tag import TagCreate, TagResponse, TagUpdate

__all__ = [
    "AttachmentResponse",
    "KnowledgeItemCreate",
    "KnowledgeItemResponse",
    "KnowledgeItemUpdate",
    "NoteCreate",
    "NoteResponse",
    "NoteUpdate",
    "SearchNotesRequest",
    "SearchNotesResponse",
    "SearchTagsRequest",
    "SearchTagsResponse",
    "TagCreate",
    "TagResponse",
    "TagUpdate",
    "PasswordChange",
    "PasswordReset",
    "PasswordResetRequest",
    "Token",
    "TokenRefresh",
    "UserLogin",
    "UserRegister",
    "UserResponse",
]
