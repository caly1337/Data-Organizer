"""
Scan and File Models
"""
from sqlalchemy import Column, Integer, String, DateTime, BigInteger, Boolean, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Scan(Base):
    """Filesystem scan record"""
    __tablename__ = "scans"

    id = Column(Integer, primary_key=True, index=True)
    path = Column(String(1000), nullable=False, index=True)
    status = Column(String(50), default="pending", index=True)  # pending, scanning, analyzing, completed, failed
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)

    # Scan configuration
    max_depth = Column(Integer, default=10)
    include_hidden = Column(Boolean, default=False)
    follow_symlinks = Column(Boolean, default=False)

    # Scan results
    total_files = Column(Integer, default=0)
    total_directories = Column(Integer, default=0)
    total_size = Column(BigInteger, default=0)  # bytes

    # Error tracking
    error_message = Column(Text, nullable=True)
    errors_count = Column(Integer, default=0)

    # Extra metadata
    extra_metadata = Column(JSON, nullable=True)

    # Relationships
    files = relationship("File", back_populates="scan", cascade="all, delete-orphan")
    analyses = relationship("Analysis", back_populates="scan", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Scan(id={self.id}, path='{self.path}', status='{self.status}')>"


class File(Base):
    """Individual file record"""
    __tablename__ = "files"

    id = Column(Integer, primary_key=True, index=True)
    scan_id = Column(Integer, ForeignKey("scans.id"), nullable=False, index=True)

    # File information
    path = Column(String(2000), nullable=False, index=True)
    name = Column(String(500), nullable=False)
    extension = Column(String(50), nullable=True, index=True)

    # File properties
    size = Column(BigInteger, nullable=False)  # bytes
    is_directory = Column(Boolean, default=False)
    is_symlink = Column(Boolean, default=False)

    # Timestamps
    created_at = Column(DateTime(timezone=True), nullable=True)
    modified_at = Column(DateTime(timezone=True), nullable=True)
    accessed_at = Column(DateTime(timezone=True), nullable=True)

    # Content analysis
    hash = Column(String(128), nullable=True, index=True)  # xxhash for deduplication
    mime_type = Column(String(200), nullable=True)

    # Categorization
    category = Column(String(100), nullable=True, index=True)  # document, image, video, code, etc.
    tags = Column(JSON, nullable=True)

    # Extra metadata
    extra_metadata = Column(JSON, nullable=True)

    # Relationships
    scan = relationship("Scan", back_populates="files")

    def __repr__(self):
        return f"<File(id={self.id}, path='{self.path}', size={self.size})>"
