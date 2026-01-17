"""
WebSocket API for Real-time Updates
"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Dict, List
import logging
import asyncio
import json

from app.database import get_db, AsyncSessionLocal
from app.models.scan import Scan
from app.models.analysis import Analysis
from app.models.execution import Execution

logger = logging.getLogger(__name__)

router = APIRouter()


class ConnectionManager:
    """Manage WebSocket connections"""

    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {}

    async def connect(self, channel: str, websocket: WebSocket):
        """Connect to a channel"""
        await websocket.accept()
        if channel not in self.active_connections:
            self.active_connections[channel] = []
        self.active_connections[channel].append(websocket)
        logger.info(f"WebSocket connected to channel: {channel}")

    def disconnect(self, channel: str, websocket: WebSocket):
        """Disconnect from channel"""
        if channel in self.active_connections:
            if websocket in self.active_connections[channel]:
                self.active_connections[channel].remove(websocket)
            if not self.active_connections[channel]:
                del self.active_connections[channel]
        logger.info(f"WebSocket disconnected from channel: {channel}")

    async def broadcast(self, channel: str, message: dict):
        """Broadcast message to all connections in channel"""
        if channel not in self.active_connections:
            return

        dead_connections = []
        for connection in self.active_connections[channel]:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"Error sending to websocket: {e}")
                dead_connections.append(connection)

        # Remove dead connections
        for conn in dead_connections:
            self.disconnect(channel, conn)


manager = ConnectionManager()


@router.websocket("/scans/{scan_id}")
async def websocket_scan(websocket: WebSocket, scan_id: int):
    """WebSocket endpoint for scan progress updates"""

    channel = f"scan_{scan_id}"
    await manager.connect(channel, websocket)

    try:
        # Send initial scan status
        async with AsyncSessionLocal() as db:
            result = await db.execute(select(Scan).where(Scan.id == scan_id))
            scan = result.scalar_one_or_none()

            if scan:
                await websocket.send_json({
                    "type": "scan_status",
                    "data": {
                        "id": scan.id,
                        "status": scan.status,
                        "total_files": scan.total_files,
                        "total_directories": scan.total_directories,
                        "total_size": scan.total_size
                    }
                })

        # Keep connection alive and send updates
        while True:
            # Wait for messages from client (ping/pong)
            try:
                data = await asyncio.wait_for(
                    websocket.receive_text(),
                    timeout=5.0
                )

                # Echo ping
                if data == "ping":
                    await websocket.send_text("pong")

            except asyncio.TimeoutError:
                # Send periodic updates
                async with AsyncSessionLocal() as db:
                    result = await db.execute(select(Scan).where(Scan.id == scan_id))
                    scan = result.scalar_one_or_none()

                    if scan:
                        await websocket.send_json({
                            "type": "scan_update",
                            "data": {
                                "id": scan.id,
                                "status": scan.status,
                                "total_files": scan.total_files,
                                "total_directories": scan.total_directories,
                                "total_size": scan.total_size
                            }
                        })

                        # Close connection if scan is done
                        if scan.status in ["completed", "failed"]:
                            await websocket.send_json({
                                "type": "scan_complete",
                                "data": {
                                    "id": scan.id,
                                    "status": scan.status
                                }
                            })
                            break

    except WebSocketDisconnect:
        manager.disconnect(channel, websocket)
        logger.info(f"Client disconnected from scan {scan_id}")
    except Exception as e:
        logger.error(f"WebSocket error for scan {scan_id}: {e}")
        manager.disconnect(channel, websocket)


@router.websocket("/analysis/{analysis_id}")
async def websocket_analysis(websocket: WebSocket, analysis_id: int):
    """WebSocket endpoint for analysis progress updates"""

    channel = f"analysis_{analysis_id}"
    await manager.connect(channel, websocket)

    try:
        # Send initial status
        async with AsyncSessionLocal() as db:
            result = await db.execute(select(Analysis).where(Analysis.id == analysis_id))
            analysis = result.scalar_one_or_none()

            if analysis:
                await websocket.send_json({
                    "type": "analysis_status",
                    "data": {
                        "id": analysis.id,
                        "status": analysis.status,
                        "provider": analysis.provider,
                        "model": analysis.model
                    }
                })

        # Keep connection alive
        while True:
            try:
                data = await asyncio.wait_for(
                    websocket.receive_text(),
                    timeout=5.0
                )

                if data == "ping":
                    await websocket.send_text("pong")

            except asyncio.TimeoutError:
                # Send updates
                async with AsyncSessionLocal() as db:
                    result = await db.execute(select(Analysis).where(Analysis.id == analysis_id))
                    analysis = result.scalar_one_or_none()

                    if analysis:
                        await websocket.send_json({
                            "type": "analysis_update",
                            "data": {
                                "id": analysis.id,
                                "status": analysis.status,
                                "duration": analysis.duration
                            }
                        })

                        if analysis.status in ["completed", "failed"]:
                            await websocket.send_json({
                                "type": "analysis_complete",
                                "data": {
                                    "id": analysis.id,
                                    "status": analysis.status
                                }
                            })
                            break

    except WebSocketDisconnect:
        manager.disconnect(channel, websocket)
        logger.info(f"Client disconnected from analysis {analysis_id}")
    except Exception as e:
        logger.error(f"WebSocket error for analysis {analysis_id}: {e}")
        manager.disconnect(channel, websocket)


@router.websocket("/execution/{execution_id}")
async def websocket_execution(websocket: WebSocket, execution_id: int):
    """WebSocket endpoint for execution progress updates"""

    channel = f"execution_{execution_id}"
    await manager.connect(channel, websocket)

    try:
        while True:
            try:
                data = await asyncio.wait_for(
                    websocket.receive_text(),
                    timeout=2.0
                )

                if data == "ping":
                    await websocket.send_text("pong")

            except asyncio.TimeoutError:
                # Send execution updates
                async with AsyncSessionLocal() as db:
                    result = await db.execute(select(Execution).where(Execution.id == execution_id))
                    execution = result.scalar_one_or_none()

                    if execution:
                        await websocket.send_json({
                            "type": "execution_update",
                            "data": {
                                "id": execution.id,
                                "status": execution.status,
                                "total_operations": execution.total_operations,
                                "completed_operations": execution.completed_operations,
                                "failed_operations": execution.failed_operations,
                                "files_modified": execution.files_modified,
                                "files_deleted": execution.files_deleted,
                                "files_moved": execution.files_moved,
                                "space_freed": execution.space_freed
                            }
                        })

                        if execution.status in ["completed", "failed", "rolled_back"]:
                            await websocket.send_json({
                                "type": "execution_complete",
                                "data": {
                                    "id": execution.id,
                                    "status": execution.status
                                }
                            })
                            break

    except WebSocketDisconnect:
        manager.disconnect(channel, websocket)
        logger.info(f"Client disconnected from execution {execution_id}")
    except Exception as e:
        logger.error(f"WebSocket error for execution {execution_id}: {e}")
        manager.disconnect(channel, websocket)


# Export manager for use in services
__all__ = ["router", "manager"]
