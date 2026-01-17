"""
Analysis Model
LLM analysis results
"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, JSON, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Analysis(Base):
    """LLM analysis result"""
    __tablename__ = "analyses"

    id = Column(Integer, primary_key=True, index=True)
    scan_id = Column(Integer, ForeignKey("scans.id"), nullable=False, index=True)

    # LLM configuration
    provider = Column(String(50), nullable=False, index=True)  # ollama, gemini, claude
    model = Column(String(100), nullable=False)
    mode = Column(String(50), default="fast")  # fast, deep, comparison

    # Analysis content
    prompt = Column(Text, nullable=False)
    response = Column(Text, nullable=False)

    # Metadata
    tokens_used = Column(Integer, nullable=True)
    cost = Column(Float, nullable=True)
    duration = Column(Float, nullable=True)  # seconds

    # Status
    status = Column(String(50), default="pending", index=True)  # pending, processing, completed, failed
    error_message = Column(Text, nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)

    # Additional data
    metadata = Column(JSON, nullable=True)

    # Relationships
    scan = relationship("Scan", back_populates="analyses")
    recommendations = relationship("Recommendation", back_populates="analysis", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Analysis(id={self.id}, provider='{self.provider}', model='{self.model}', status='{self.status}')>"
