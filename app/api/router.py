"""Main API router."""
from fastapi import APIRouter

from app.api import auth, knowledge_items, notes, tags

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(knowledge_items.router)
api_router.include_router(notes.router)
api_router.include_router(tags.router)

