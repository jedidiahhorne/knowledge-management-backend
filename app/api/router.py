"""Main API router."""
from fastapi import APIRouter

from app.api import attachments, auth, knowledge_items, notes, search, tags

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(knowledge_items.router)
api_router.include_router(notes.router)
api_router.include_router(tags.router)
api_router.include_router(attachments.router)
api_router.include_router(search.router)

