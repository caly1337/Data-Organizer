"""
Recommendation Model
AI-generated suggestions for file organization
"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, JSON, Float, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Recommendation(Base):
    """AI-generated recommendation"""
    __tablename__ = "recommendations"

    id = Column(Integer, primary_key=True, index=True)
    analysis_id = Column(Integer, ForeignKey("analyses.id"), nullable=False, index=True)

    # Recommendation type
    type = Column(String(50), nullable=False, index=True)  # reorganize, deduplicate, cleanup, archive, categorize
    action = Column(String(50), nullable=False)  # move, delete, compress, tag

    # Details
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=False)
    reasoning = Column(Text, nullable=True)

    # Confidence and impact
    confidence = Column(Float, nullable=False)  # 0.0 - 1.0
    impact_score = Column(Float, nullable=True)  # 0.0 - 1.0

    # Target files
    affected_files = Column(JSON, nullable=False)  # List of file IDs
    affected_count = Column(Integer, default=0)

    # Expected results
    expected_space_saved = Column(Integer, nullable=True)  # bytes
    expected_duration = Column(Float, nullable=True)  # seconds

    # Status
    status = Column(String(50), default="pending", index=True)  # pending, approved, rejected, executed, failed
    approved = Column(Boolean, default=False)
    approved_by = Column(String(100), nullable=True)
    approved_at = Column(DateTime(timezone=True), nullable=True)

    # Priority
    priority = Column(Integer, default=0, index=True)  # Higher = more important

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Metadata
    metadata = Column(JSON, nullable=True)

    # Relationships
    analysis = relationship("Analysis", back_populates="recommendations")
    executions = relationship("Execution", back_populates="recommendation", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Recommendation(id={self.id}, type='{self.type}', status='{self.status}', confidence={self.confidence})>"
