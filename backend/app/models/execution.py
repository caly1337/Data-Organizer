"""
Execution Model
Track execution of recommendations
"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, JSON, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Execution(Base):
    """Recommendation execution record"""
    __tablename__ = "executions"

    id = Column(Integer, primary_key=True, index=True)
    recommendation_id = Column(Integer, ForeignKey("recommendations.id"), nullable=False, index=True)

    # Execution configuration
    dry_run = Column(Boolean, default=True)
    batch_size = Column(Integer, default=100)

    # Execution status
    status = Column(String(50), default="pending", index=True)  # pending, running, completed, failed, rolled_back
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)

    # Progress tracking
    total_operations = Column(Integer, default=0)
    completed_operations = Column(Integer, default=0)
    failed_operations = Column(Integer, default=0)

    # Results
    files_modified = Column(Integer, default=0)
    files_deleted = Column(Integer, default=0)
    files_moved = Column(Integer, default=0)
    space_freed = Column(Integer, default=0)  # bytes

    # Error tracking
    errors = Column(JSON, nullable=True)  # List of error details
    error_message = Column(Text, nullable=True)

    # Rollback support
    rollback_data = Column(JSON, nullable=True)  # Data needed to undo changes
    can_rollback = Column(Boolean, default=True)
    rolled_back_at = Column(DateTime(timezone=True), nullable=True)

    # Audit trail
    executed_by = Column(String(100), nullable=True)
    execution_log = Column(JSON, nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Extra metadata
    extra_metadata = Column(JSON, nullable=True)

    # Relationships
    recommendation = relationship("Recommendation", back_populates="executions")

    def __repr__(self):
        return f"<Execution(id={self.id}, recommendation_id={self.recommendation_id}, status='{self.status}')>"
