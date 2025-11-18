"""Knowledge item model."""
from sqlalchemy import Column, DateTime, Integer, String, Text
from sqlalchemy.sql import func

from app.db.base import Base


class KnowledgeItem(Base):
    """Knowledge item model for storing notes, articles, and other content."""

    __tablename__ = "knowledge_items"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False, index=True)
    content = Column(Text, nullable=True)
    tags = Column(String(500), nullable=True)  # Comma-separated tags
    category = Column(String(100), nullable=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    def __repr__(self):
        return f"<KnowledgeItem(id={self.id}, title='{self.title}')>"

