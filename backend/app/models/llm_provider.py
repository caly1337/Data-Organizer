"""
LLM Provider Model
Configuration for LLM providers
"""
from sqlalchemy import Column, Integer, String, DateTime, Boolean, JSON, Float
from sqlalchemy.sql import func
from app.database import Base


class LLMProvider(Base):
    """LLM provider configuration"""
    __tablename__ = "llm_providers"

    id = Column(Integer, primary_key=True, index=True)

    # Provider details
    name = Column(String(100), unique=True, nullable=False, index=True)
    type = Column(String(50), nullable=False)  # ollama, gemini, claude
    enabled = Column(Boolean, default=True, index=True)

    # Configuration
    config = Column(JSON, nullable=False)  # Provider-specific configuration
    # Example: {"base_url": "...", "model": "...", "timeout": 120}

    # Usage tracking
    total_requests = Column(Integer, default=0)
    total_tokens = Column(Integer, default=0)
    total_cost = Column(Float, default=0.0)
    success_rate = Column(Float, default=0.0)

    # Performance metrics
    avg_response_time = Column(Float, default=0.0)  # seconds
    last_used_at = Column(DateTime(timezone=True), nullable=True)

    # Status
    status = Column(String(50), default="active")  # active, inactive, error
    error_count = Column(Integer, default=0)
    last_error = Column(String(500), nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Extra metadata
    extra_metadata = Column(JSON, nullable=True)

    def __repr__(self):
        return f"<LLMProvider(id={self.id}, name='{self.name}', type='{self.type}', enabled={self.enabled})>"
