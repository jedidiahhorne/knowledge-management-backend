"""Note model."""
from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Table,
    Text,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.base import Base

# Association table for many-to-many relationship between Notes and Tags
note_tags = Table(
    "note_tags",
    Base.metadata,
    Column("note_id", Integer, ForeignKey("notes.id", ondelete="CASCADE"), primary_key=True),
    Column("tag_id", Integer, ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True),
)


class Note(Base):
    """Note model for storing user notes and content."""

    __tablename__ = "notes"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False, index=True)
    content = Column(Text, nullable=True)
    is_pinned = Column(Boolean, default=False, nullable=False)
    is_archived = Column(Boolean, default=False, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    # Relationships
    owner = relationship("User", back_populates="notes")
    tags = relationship("Tag", secondary=note_tags, back_populates="notes")
    attachments = relationship("Attachment", back_populates="note", cascade="all, delete-orphan")

    def add_tag(self, tag) -> None:
        """Add a tag to the note if not already present."""
        if tag not in self.tags:
            self.tags.append(tag)

    def remove_tag(self, tag) -> None:
        """Remove a tag from the note."""
        if tag in self.tags:
            self.tags.remove(tag)

    def has_tag(self, tag_name: str) -> bool:
        """Check if note has a specific tag by name."""
        return any(tag.name == tag_name for tag in self.tags)

    def get_tag_names(self) -> list[str]:
        """Get list of tag names for the note."""
        return [tag.name for tag in self.tags]

    def pin(self) -> None:
        """Pin the note."""
        self.is_pinned = True

    def unpin(self) -> None:
        """Unpin the note."""
        self.is_pinned = False

    def archive(self) -> None:
        """Archive the note."""
        self.is_archived = True

    def unarchive(self) -> None:
        """Unarchive the note."""
        self.is_archived = False

    def __repr__(self):
        return f"<Note(id={self.id}, title='{self.title}', user_id={self.user_id})>"

