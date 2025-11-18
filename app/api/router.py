"""Main API router."""
from fastapi import APIRouter

from app.api import knowledge_items

api_router = APIRouter()
api_router.include_router(knowledge_items.router)

