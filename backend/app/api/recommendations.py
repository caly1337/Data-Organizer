"""
Recommendations API Endpoints
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from typing import List
import logging
from datetime import datetime

from app.database import get_db
from app.models.recommendation import Recommendation
from app.models.analysis import Analysis
from app.schemas.analysis import RecommendationResponse

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/", response_model=List[RecommendationResponse])
async def list_recommendations(
    skip: int = 0,
    limit: int = 50,
    status: str = None,
    type: str = None,
    min_confidence: float = 0.0,
    db: AsyncSession = Depends(get_db)
):
    """List all recommendations with filtering"""

    query = select(Recommendation)

    # Apply filters
    if status:
        query = query.where(Recommendation.status == status)
    if type:
        query = query.where(Recommendation.type == type)
    if min_confidence > 0:
        query = query.where(Recommendation.confidence >= min_confidence)

    # Order by priority and confidence
    query = query.order_by(
        Recommendation.priority.desc(),
        Recommendation.confidence.desc()
    )

    # Pagination
    query = query.offset(skip).limit(limit)

    result = await db.execute(query)
    recommendations = result.scalars().all()

    return recommendations


@router.get("/{recommendation_id}", response_model=RecommendationResponse)
async def get_recommendation(
    recommendation_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get recommendation details"""

    result = await db.execute(
        select(Recommendation).where(Recommendation.id == recommendation_id)
    )
    recommendation = result.scalar_one_or_none()

    if not recommendation:
        raise HTTPException(status_code=404, detail="Recommendation not found")

    return recommendation


@router.put("/{recommendation_id}/approve")
async def approve_recommendation(
    recommendation_id: int,
    approved_by: str = "user",
    db: AsyncSession = Depends(get_db)
):
    """Approve a recommendation for execution"""

    result = await db.execute(
        select(Recommendation).where(Recommendation.id == recommendation_id)
    )
    recommendation = result.scalar_one_or_none()

    if not recommendation:
        raise HTTPException(status_code=404, detail="Recommendation not found")

    # Update recommendation
    recommendation.approved = True
    recommendation.approved_by = approved_by
    recommendation.approved_at = datetime.now()
    recommendation.status = "approved"

    await db.commit()
    await db.refresh(recommendation)

    logger.info(f"Recommendation {recommendation_id} approved by {approved_by}")

    return recommendation


@router.put("/{recommendation_id}/reject")
async def reject_recommendation(
    recommendation_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Reject a recommendation"""

    result = await db.execute(
        select(Recommendation).where(Recommendation.id == recommendation_id)
    )
    recommendation = result.scalar_one_or_none()

    if not recommendation:
        raise HTTPException(status_code=404, detail="Recommendation not found")

    # Update recommendation
    recommendation.approved = False
    recommendation.status = "rejected"

    await db.commit()
    await db.refresh(recommendation)

    logger.info(f"Recommendation {recommendation_id} rejected")

    return recommendation


@router.get("/analysis/{analysis_id}", response_model=List[RecommendationResponse])
async def get_analysis_recommendations(
    analysis_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get all recommendations for an analysis"""

    # Verify analysis exists
    analysis_result = await db.execute(
        select(Analysis).where(Analysis.id == analysis_id)
    )
    analysis = analysis_result.scalar_one_or_none()

    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")

    # Get recommendations
    result = await db.execute(
        select(Recommendation)
        .where(Recommendation.analysis_id == analysis_id)
        .order_by(Recommendation.priority.desc(), Recommendation.confidence.desc())
    )
    recommendations = result.scalars().all()

    return recommendations
