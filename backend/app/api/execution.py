"""
Execution API Endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
import logging
from datetime import datetime

from app.database import get_db
from app.models.recommendation import Recommendation
from app.models.execution import Execution
from app.models.scan import File
from app.schemas.execution import ExecutionCreate, ExecutionResponse, ExecutionDetailResponse
from app.services.executor import execution_service

logger = logging.getLogger(__name__)

router = APIRouter()


async def run_execution_task(
    execution_id: int,
    recommendation_id: int,
    dry_run: bool,
    batch_size: int
):
    """Background task to execute recommendation"""
    from app.database import AsyncSessionLocal

    async with AsyncSessionLocal() as db:
        try:
            # Get execution record
            exec_result = await db.execute(
                select(Execution).where(Execution.id == execution_id)
            )
            execution = exec_result.scalar_one_or_none()

            if not execution:
                logger.error(f"Execution {execution_id} not found")
                return

            # Get recommendation
            rec_result = await db.execute(
                select(Recommendation).where(Recommendation.id == recommendation_id)
            )
            recommendation = rec_result.scalar_one_or_none()

            if not recommendation:
                logger.error(f"Recommendation {recommendation_id} not found")
                execution.status = "failed"
                execution.error_message = "Recommendation not found"
                await db.commit()
                return

            # Update status
            execution.status = "running"
            execution.started_at = datetime.now()
            await db.commit()

            # Get affected files
            file_ids = recommendation.affected_files
            files_result = await db.execute(
                select(File).where(File.id.in_(file_ids))
            )
            files = files_result.scalars().all()

            # Convert to dict for executor
            files_data = [
                {
                    "path": f.path,
                    "size": f.size,
                    "id": f.id
                }
                for f in files
            ]

            recommendation_data = {
                "type": recommendation.type,
                "action": recommendation.action,
                "affected_files": files_data,
                "metadata": recommendation.metadata or {}
            }

            # Execute
            exec_result = await execution_service.execute_recommendation(
                recommendation=recommendation_data,
                dry_run=dry_run
            )

            # Update execution record
            execution.status = "completed"
            execution.completed_at = datetime.now()
            execution.total_operations = len(exec_result["operations"])
            execution.completed_operations = exec_result["successes"]
            execution.failed_operations = exec_result["failures"]
            execution.rollback_data = exec_result["rollback_data"]
            execution.can_rollback = exec_result["can_rollback"]
            execution.errors = exec_result["errors"]
            execution.execution_log = exec_result

            # Count operation types
            for op in exec_result["operations"]:
                if op.get("type") == "move":
                    execution.files_moved += 1
                elif op.get("type") == "delete":
                    execution.files_deleted += 1
                    execution.space_freed += op.get("size", 0)

            # Update recommendation status
            if not dry_run and exec_result["successes"] > 0:
                recommendation.status = "executed"

            await db.commit()

            logger.info(f"Execution {execution_id} completed: {execution.completed_operations} successes, {execution.failed_operations} failures")

        except Exception as e:
            logger.error(f"Execution {execution_id} failed: {e}", exc_info=True)

            try:
                exec_result = await db.execute(
                    select(Execution).where(Execution.id == execution_id)
                )
                execution = exec_result.scalar_one_or_none()
                if execution:
                    execution.status = "failed"
                    execution.error_message = str(e)
                    execution.completed_at = datetime.now()
                    await db.commit()
            except Exception as update_error:
                logger.error(f"Failed to update execution status: {update_error}")


@router.post("/", response_model=ExecutionResponse)
async def create_execution(
    execution_data: ExecutionCreate,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    """Create and start execution of a recommendation"""

    # Verify recommendation exists and is approved
    result = await db.execute(
        select(Recommendation).where(Recommendation.id == execution_data.recommendation_id)
    )
    recommendation = result.scalar_one_or_none()

    if not recommendation:
        raise HTTPException(status_code=404, detail="Recommendation not found")

    if not execution_data.dry_run and not recommendation.approved:
        raise HTTPException(
            status_code=400,
            detail="Recommendation must be approved before execution"
        )

    # Create execution record
    execution = Execution(
        recommendation_id=execution_data.recommendation_id,
        dry_run=execution_data.dry_run,
        batch_size=execution_data.batch_size,
        status="pending"
    )

    db.add(execution)
    await db.commit()
    await db.refresh(execution)

    # Start execution in background
    background_tasks.add_task(
        run_execution_task,
        execution.id,
        execution_data.recommendation_id,
        execution_data.dry_run,
        execution_data.batch_size
    )

    logger.info(f"Created execution {execution.id} for recommendation {execution_data.recommendation_id} (dry_run={execution_data.dry_run})")

    return execution


@router.get("/{execution_id}", response_model=ExecutionDetailResponse)
async def get_execution(execution_id: int, db: AsyncSession = Depends(get_db)):
    """Get execution details"""

    result = await db.execute(
        select(Execution).where(Execution.id == execution_id)
    )
    execution = result.scalar_one_or_none()

    if not execution:
        raise HTTPException(status_code=404, detail="Execution not found")

    return execution


@router.post("/{execution_id}/rollback")
async def rollback_execution(
    execution_id: int,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    """Rollback an execution"""

    result = await db.execute(
        select(Execution).where(Execution.id == execution_id)
    )
    execution = result.scalar_one_or_none()

    if not execution:
        raise HTTPException(status_code=404, detail="Execution not found")

    if execution.dry_run:
        raise HTTPException(status_code=400, detail="Cannot rollback dry-run execution")

    if not execution.can_rollback:
        raise HTTPException(status_code=400, detail="Execution cannot be rolled back")

    if execution.rolled_back_at:
        raise HTTPException(status_code=400, detail="Execution already rolled back")

    # Execute rollback in background
    async def rollback_task():
        from app.database import AsyncSessionLocal

        async with AsyncSessionLocal() as db_session:
            try:
                # Run rollback
                rollback_result = await execution_service.rollback_execution(
                    execution.rollback_data
                )

                # Update execution record
                exec_result = await db_session.execute(
                    select(Execution).where(Execution.id == execution_id)
                )
                exec_record = exec_result.scalar_one_or_none()

                if exec_record:
                    exec_record.rolled_back_at = datetime.now()
                    exec_record.metadata = {
                        "rollback_result": rollback_result
                    }
                    await db_session.commit()

                logger.info(f"Rolled back execution {execution_id}")

            except Exception as e:
                logger.error(f"Rollback failed for execution {execution_id}: {e}")

    background_tasks.add_task(rollback_task)

    return {"message": "Rollback started", "execution_id": execution_id}


@router.get("/recommendation/{recommendation_id}", response_model=List[ExecutionResponse])
async def get_recommendation_executions(
    recommendation_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get all executions for a recommendation"""

    # Verify recommendation exists
    rec_result = await db.execute(
        select(Recommendation).where(Recommendation.id == recommendation_id)
    )
    recommendation = rec_result.scalar_one_or_none()

    if not recommendation:
        raise HTTPException(status_code=404, detail="Recommendation not found")

    # Get executions
    result = await db.execute(
        select(Execution)
        .where(Execution.recommendation_id == recommendation_id)
        .order_by(Execution.created_at.desc())
    )
    executions = result.scalars().all()

    return executions
