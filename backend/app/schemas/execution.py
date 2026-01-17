"""
Pydantic schemas for Execution operations
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class ExecutionCreate(BaseModel):
    """Schema for creating execution"""
    recommendation_id: int = Field(..., description="Recommendation ID to execute")
    dry_run: bool = Field(True, description="Preview changes without applying")
    batch_size: int = Field(100, ge=1, le=10000, description="Batch size for operations")


class ExecutionResponse(BaseModel):
    """Schema for execution response"""
    id: int
    recommendation_id: int
    dry_run: bool
    batch_size: int
    status: str
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    total_operations: int
    completed_operations: int
    failed_operations: int
    files_modified: int
    files_deleted: int
    files_moved: int
    space_freed: int
    can_rollback: bool
    rolled_back_at: Optional[datetime]

    class Config:
        from_attributes = True


class ExecutionDetailResponse(ExecutionResponse):
    """Detailed execution response with operation log"""
    errors: Optional[List[Dict[str, Any]]]
    execution_log: Optional[Dict[str, Any]]
