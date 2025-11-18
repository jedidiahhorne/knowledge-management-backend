"""Knowledge items API routes."""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db import get_db
from app.models.knowledge_item import KnowledgeItem
from app.schemas.knowledge_item import (
    KnowledgeItemCreate,
    KnowledgeItemUpdate,
    KnowledgeItemResponse,
)

router = APIRouter(prefix="/knowledge-items", tags=["knowledge-items"])


@router.post("/", response_model=KnowledgeItemResponse, status_code=status.HTTP_201_CREATED)
def create_knowledge_item(
    item: KnowledgeItemCreate,
    db: Session = Depends(get_db),
):
    """Create a new knowledge item."""
    db_item = KnowledgeItem(**item.model_dump())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


@router.get("/", response_model=List[KnowledgeItemResponse])
def list_knowledge_items(
    skip: int = 0,
    limit: int = 100,
    category: str = None,
    db: Session = Depends(get_db),
):
    """List all knowledge items with optional filtering."""
    query = db.query(KnowledgeItem)
    if category:
        query = query.filter(KnowledgeItem.category == category)
    items = query.offset(skip).limit(limit).all()
    return items


@router.get("/{item_id}", response_model=KnowledgeItemResponse)
def get_knowledge_item(
    item_id: int,
    db: Session = Depends(get_db),
):
    """Get a specific knowledge item by ID."""
    item = db.query(KnowledgeItem).filter(KnowledgeItem.id == item_id).first()
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Knowledge item with id {item_id} not found",
        )
    return item


@router.put("/{item_id}", response_model=KnowledgeItemResponse)
def update_knowledge_item(
    item_id: int,
    item_update: KnowledgeItemUpdate,
    db: Session = Depends(get_db),
):
    """Update a knowledge item."""
    db_item = db.query(KnowledgeItem).filter(KnowledgeItem.id == item_id).first()
    if not db_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Knowledge item with id {item_id} not found",
        )

    update_data = item_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_item, field, value)

    db.commit()
    db.refresh(db_item)
    return db_item


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_knowledge_item(
    item_id: int,
    db: Session = Depends(get_db),
):
    """Delete a knowledge item."""
    db_item = db.query(KnowledgeItem).filter(KnowledgeItem.id == item_id).first()
    if not db_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Knowledge item with id {item_id} not found",
        )
    db.delete(db_item)
    db.commit()
    return None

