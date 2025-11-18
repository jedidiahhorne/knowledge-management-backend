"""Attachment model."""
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.base import Base


class Attachment(Base):
    """Attachment model for file attachments to notes."""

    __tablename__ = "attachments"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)  # Path to stored file
    file_size = Column(Integer, nullable=True)  # Size in bytes
    mime_type = Column(String(100), nullable=True)  # MIME type (e.g., image/png, application/pdf)
    note_id = Column(Integer, ForeignKey("notes.id", ondelete="CASCADE"), nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    note = relationship("Note", back_populates="attachments")

    def get_file_size_mb(self) -> float:
        """Get file size in megabytes."""
        if self.file_size:
            return round(self.file_size / (1024 * 1024), 2)
        return 0.0

    def get_file_size_kb(self) -> float:
        """Get file size in kilobytes."""
        if self.file_size:
            return round(self.file_size / 1024, 2)
        return 0.0

    def is_image(self) -> bool:
        """Check if attachment is an image."""
        return self.mime_type and self.mime_type.startswith("image/")

    def is_pdf(self) -> bool:
        """Check if attachment is a PDF."""
        return self.mime_type == "application/pdf"

    def __repr__(self):
        return f"<Attachment(id={self.id}, filename='{self.filename}', note_id={self.note_id})>"

