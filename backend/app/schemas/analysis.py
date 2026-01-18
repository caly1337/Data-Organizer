"""
Pydantic schemas for Analysis operations
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime


class AnalysisCreate(BaseModel):
    """Schema for creating analysis"""
    scan_id: int = Field(..., description="Scan ID to analyze")
    provider: str = Field("ollama", description="LLM provider (ollama, gemini, claude)")
    mode: str = Field("fast", description="Analysis mode (fast, deep, comparison)")
    custom_prompt: Optional[str] = Field(None, description="Custom analysis prompt (optional)")


class AnalysisResponse(BaseModel):
    """Schema for analysis response"""
    id: int
    scan_id: int
    provider: str
    model: str
    mode: str
    response: str
    tokens_used: Optional[int]
    cost: Optional[float]
    duration: Optional[float]
    status: str
    created_at: datetime
    completed_at: Optional[datetime]

    class Config:
        from_attributes = True


class RecommendationResponse(BaseModel):
    """Schema for recommendation response"""
    id: int
    analysis_id: int
    type: str
    action: str
    title: str
    description: str
    reasoning: Optional[str]
    confidence: float
    impact_score: Optional[float]
    affected_count: int
    status: str
    priority: int

    class Config:
        from_attributes = True
