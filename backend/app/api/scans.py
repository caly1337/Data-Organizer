"""
Scan API Endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List
import logging

from app.database import get_db
from app.models.scan import Scan, File
from app.schemas.scan import ScanCreate, ScanResponse, ScanDetailResponse, ScanListResponse
from app.services.file_scanner import FileScanner
from app.core.config import settings

logger = logging.getLogger(__name__)

router = APIRouter()


async def run_scan_task(scan_id: int, path: str, max_depth: int, include_hidden: bool, follow_symlinks: bool):
    """Background task to run filesystem scan"""
    from app.database import AsyncSessionLocal

    async with AsyncSessionLocal() as db:
        try:
            # Get scan record
            result = await db.execute(select(Scan).where(Scan.id == scan_id))
            scan = result.scalar_one_or_none()

            if not scan:
                logger.error(f"Scan {scan_id} not found")
                return

            # Update status
            scan.status = "scanning"
            await db.commit()

            # Run scan
            scanner = FileScanner(
                max_depth=max_depth,
                include_hidden=include_hidden,
                follow_symlinks=follow_symlinks
            )

            # Callback to save files to database
            async def save_file(file_data: dict):
                file = File(
                    scan_id=scan_id,
                    path=file_data["path"],
                    name=file_data["name"],
                    extension=file_data.get("extension"),
                    size=file_data["size"],
                    is_directory=file_data["is_directory"],
                    is_symlink=file_data["is_symlink"],
                    hash=file_data.get("hash"),
                    mime_type=file_data.get("mime_type"),
                    category=file_data.get("category"),
                    metadata=file_data.get("metadata")
                )
                db.add(file)

                # Commit every 100 files
                if scan.total_files % 100 == 0:
                    await db.commit()

            # Execute scan
            scan_result = await scanner.scan_directory(
                path=path,
                on_file_callback=save_file
            )

            # Update scan record
            scan.status = "completed"
            scan.total_files = scan_result["total_files"]
            scan.total_directories = scan_result["total_directories"]
            scan.total_size = scan_result["total_size"]
            scan.errors_count = len(scan_result["errors"])
            scan.completed_at = db.func.now()

            if scan_result["errors"]:
                scan.extra_metadata = {"errors": scan_result["errors"]}

            await db.commit()

            logger.info(f"Scan {scan_id} completed: {scan.total_files} files, {scan.total_directories} directories")

        except Exception as e:
            logger.error(f"Scan {scan_id} failed: {e}")

            # Update scan status
            try:
                result = await db.execute(select(Scan).where(Scan.id == scan_id))
                scan = result.scalar_one_or_none()
                if scan:
                    scan.status = "failed"
                    scan.error_message = str(e)
                    await db.commit()
            except Exception as update_error:
                logger.error(f"Failed to update scan status: {update_error}")


@router.post("/", response_model=ScanResponse)
async def create_scan(
    scan_data: ScanCreate,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    """Create and start a new filesystem scan"""

    # Create scan record
    scan = Scan(
        path=scan_data.path,
        status="pending",
        max_depth=scan_data.max_depth,
        include_hidden=scan_data.include_hidden,
        follow_symlinks=scan_data.follow_symlinks
    )

    db.add(scan)
    await db.commit()
    await db.refresh(scan)

    # Start scan in background
    background_tasks.add_task(
        run_scan_task,
        scan.id,
        scan_data.path,
        scan_data.max_depth,
        scan_data.include_hidden,
        scan_data.follow_symlinks
    )

    logger.info(f"Created scan {scan.id} for path: {scan_data.path}")

    return scan


@router.get("/", response_model=ScanListResponse)
async def list_scans(
    skip: int = 0,
    limit: int = 20,
    status: str = None,
    db: AsyncSession = Depends(get_db)
):
    """List all scans with pagination"""

    # Build query
    query = select(Scan)

    if status:
        query = query.where(Scan.status == status)

    query = query.order_by(Scan.started_at.desc())

    # Get total count
    count_result = await db.execute(select(func.count()).select_from(Scan))
    total = count_result.scalar()

    # Get scans
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    scans = result.scalars().all()

    return ScanListResponse(
        scans=scans,
        total=total,
        page=skip // limit + 1,
        page_size=limit
    )


@router.get("/{scan_id}", response_model=ScanDetailResponse)
async def get_scan(scan_id: int, include_files: bool = False, db: AsyncSession = Depends(get_db)):
    """Get scan details"""

    result = await db.execute(select(Scan).where(Scan.id == scan_id))
    scan = result.scalar_one_or_none()

    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found")

    if include_files:
        # Load files
        files_result = await db.execute(
            select(File).where(File.scan_id == scan_id).limit(1000)
        )
        scan.files = files_result.scalars().all()

    return scan


@router.delete("/{scan_id}")
async def delete_scan(scan_id: int, db: AsyncSession = Depends(get_db)):
    """Delete a scan and all associated data"""

    result = await db.execute(select(Scan).where(Scan.id == scan_id))
    scan = result.scalar_one_or_none()

    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found")

    await db.delete(scan)
    await db.commit()

    logger.info(f"Deleted scan {scan_id}")

    return {"message": "Scan deleted successfully"}


@router.get("/{scan_id}/files", response_model=List[dict])
async def get_scan_files(
    scan_id: int,
    skip: int = 0,
    limit: int = 100,
    category: str = None,
    db: AsyncSession = Depends(get_db)
):
    """Get files from a scan"""

    # Verify scan exists
    result = await db.execute(select(Scan).where(Scan.id == scan_id))
    scan = result.scalar_one_or_none()

    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found")

    # Build query
    query = select(File).where(File.scan_id == scan_id)

    if category:
        query = query.where(File.category == category)

    query = query.offset(skip).limit(limit)

    # Get files
    files_result = await db.execute(query)
    files = files_result.scalars().all()

    return files
