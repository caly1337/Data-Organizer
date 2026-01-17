"""
Pydantic schemas for Scan operations
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class ScanCreate(BaseModel):
    """Schema for creating a new scan"""
    path: str = Field(..., description="Directory path to scan")
    max_depth: int = Field(10, ge=1, le=50, description="Maximum directory depth")
    include_hidden: bool = Field(False, description="Include hidden files")
    follow_symlinks: bool = Field(False, description="Follow symbolic links")


class ScanResponse(BaseModel):
    """Schema for scan response"""
    id: int
    path: str
    status: str
    started_at: datetime
    completed_at: Optional[datetime]
    total_files: int
    total_directories: int
    total_size: int
    error_message: Optional[str]
    errors_count: int
    metadata: Optional[Dict[str, Any]]

    class Config:
        from_attributes = True


class FileResponse(BaseModel):
    """Schema for file response"""
    id: int
    scan_id: int
    path: str
    name: str
    extension: Optional[str]
    size: int
    is_directory: bool
    is_symlink: bool
    created_at: Optional[datetime]
    modified_at: Optional[datetime]
    hash: Optional[str]
    mime_type: Optional[str]
    category: Optional[str]

    class Config:
        from_attributes = True


class ScanDetailResponse(ScanResponse):
    """Detailed scan response with files"""
    files: List[FileResponse] = []


class ScanListResponse(BaseModel):
    """List of scans with pagination"""
    scans: List[ScanResponse]
    total: int
    page: int
    page_size: int
