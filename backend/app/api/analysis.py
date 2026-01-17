"""
Analysis API Endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
import logging

from app.database import get_db
from app.models.scan import Scan, File
from app.models.analysis import Analysis
from app.models.recommendation import Recommendation
from app.schemas.analysis import AnalysisCreate, AnalysisResponse, RecommendationResponse
from app.services.analyzer import filesystem_analyzer

logger = logging.getLogger(__name__)

router = APIRouter()


async def run_analysis_task(analysis_id: int, scan_id: int, provider: str, mode: str):
    """Background task to run analysis"""
    from app.database import AsyncSessionLocal

    async with AsyncSessionLocal() as db:
        try:
            # Get analysis record
            result = await db.execute(select(Analysis).where(Analysis.id == analysis_id))
            analysis = result.scalar_one_or_none()

            if not analysis:
                logger.error(f"Analysis {analysis_id} not found")
                return

            # Get scan data
            scan_result = await db.execute(
                select(Scan).where(Scan.id == scan_id)
            )
            scan = scan_result.scalar_one_or_none()

            if not scan:
                logger.error(f"Scan {scan_id} not found")
                analysis.status = "failed"
                analysis.error_message = "Scan not found"
                await db.commit()
                return

            # Update status
            analysis.status = "processing"
            await db.commit()

            # Prepare scan data for analysis
            scan_data = {
                "path": scan.path,
                "total_files": scan.total_files,
                "total_directories": scan.total_directories,
                "total_size": scan.total_size,
                "duration": 0,  # TODO: Calculate from timestamps
                "files": []
            }

            # Get sample files (limit to avoid context overflow)
            files_result = await db.execute(
                select(File).where(File.scan_id == scan_id).limit(100)
            )
            files = files_result.scalars().all()

            for file in files:
                scan_data["files"].append({
                    "path": file.path,
                    "name": file.name,
                    "extension": file.extension,
                    "size": file.size,
                    "category": file.category,
                    "mime_type": file.mime_type
                })

            # Run analysis
            analysis_result = await filesystem_analyzer.analyze_scan(
                scan_data=scan_data,
                provider=provider,
                mode=mode
            )

            # Update analysis record
            analysis.response = analysis_result["response"]
            analysis.tokens_used = analysis_result.get("tokens_used")
            analysis.cost = analysis_result.get("cost")
            analysis.duration = analysis_result.get("duration")
            analysis.status = "completed"
            analysis.metadata = analysis_result.get("metadata")
            await db.commit()

            # Create recommendations
            for rec_data in analysis_result.get("recommendations", []):
                recommendation = Recommendation(
                    analysis_id=analysis_id,
                    type=rec_data.get("type", "reorganize"),
                    action=rec_data.get("action", "review"),
                    title=rec_data.get("title", "")[:500],
                    description=rec_data.get("description", ""),
                    reasoning=rec_data.get("reasoning"),
                    confidence=rec_data.get("confidence", 0.5),
                    impact_score=rec_data.get("impact_score"),
                    affected_files=rec_data.get("affected_files", []),
                    affected_count=len(rec_data.get("affected_files", [])),
                    priority=rec_data.get("priority", 5)
                )
                db.add(recommendation)

            await db.commit()

            logger.info(f"Analysis {analysis_id} completed with {len(analysis_result.get('recommendations', []))} recommendations")

        except Exception as e:
            logger.error(f"Analysis {analysis_id} failed: {e}", exc_info=True)

            # Update analysis status
            try:
                result = await db.execute(select(Analysis).where(Analysis.id == analysis_id))
                analysis = result.scalar_one_or_none()
                if analysis:
                    analysis.status = "failed"
                    analysis.error_message = str(e)
                    await db.commit()
            except Exception as update_error:
                logger.error(f"Failed to update analysis status: {update_error}")


@router.post("/", response_model=AnalysisResponse)
async def create_analysis(
    analysis_data: AnalysisCreate,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    """Create and start a new analysis"""

    # Verify scan exists and is completed
    result = await db.execute(select(Scan).where(Scan.id == analysis_data.scan_id))
    scan = result.scalar_one_or_none()

    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found")

    if scan.status != "completed":
        raise HTTPException(status_code=400, detail=f"Scan status is '{scan.status}', must be 'completed'")

    # Create analysis record
    analysis = Analysis(
        scan_id=analysis_data.scan_id,
        provider=analysis_data.provider,
        model="",  # Will be set by analyzer
        mode=analysis_data.mode,
        prompt="",  # Will be set by analyzer
        response="",
        status="pending"
    )

    db.add(analysis)
    await db.commit()
    await db.refresh(analysis)

    # Start analysis in background
    background_tasks.add_task(
        run_analysis_task,
        analysis.id,
        analysis_data.scan_id,
        analysis_data.provider,
        analysis_data.mode
    )

    logger.info(f"Created analysis {analysis.id} for scan {analysis_data.scan_id}")

    return analysis


@router.get("/{analysis_id}", response_model=AnalysisResponse)
async def get_analysis(analysis_id: int, db: AsyncSession = Depends(get_db)):
    """Get analysis details"""

    result = await db.execute(select(Analysis).where(Analysis.id == analysis_id))
    analysis = result.scalar_one_or_none()

    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")

    return analysis


@router.get("/{analysis_id}/recommendations", response_model=List[RecommendationResponse])
async def get_recommendations(
    analysis_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get recommendations from analysis"""

    # Verify analysis exists
    result = await db.execute(select(Analysis).where(Analysis.id == analysis_id))
    analysis = result.scalar_one_or_none()

    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")

    # Get recommendations
    recs_result = await db.execute(
        select(Recommendation)
        .where(Recommendation.analysis_id == analysis_id)
        .order_by(Recommendation.priority.desc(), Recommendation.confidence.desc())
    )
    recommendations = recs_result.scalars().all()

    return recommendations


@router.get("/scan/{scan_id}", response_model=List[AnalysisResponse])
async def get_scan_analyses(scan_id: int, db: AsyncSession = Depends(get_db)):
    """Get all analyses for a scan"""

    # Verify scan exists
    result = await db.execute(select(Scan).where(Scan.id == scan_id))
    scan = result.scalar_one_or_none()

    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found")

    # Get analyses
    analyses_result = await db.execute(
        select(Analysis)
        .where(Analysis.scan_id == scan_id)
        .order_by(Analysis.created_at.desc())
    )
    analyses = analyses_result.scalars().all()

    return analyses
