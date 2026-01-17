"""
Executor Service
Safely executes file operations with rollback support
"""
import os
import shutil
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime
import json

logger = logging.getLogger(__name__)


class FileOperationError(Exception):
    """Exception for file operation errors"""
    pass


class ExecutionService:
    """Service for executing file operations safely"""

    def __init__(self, dry_run: bool = True):
        self.dry_run = dry_run
        self.operations_log = []

    async def execute_recommendation(
        self,
        recommendation: Dict[str, Any],
        dry_run: bool = None
    ) -> Dict[str, Any]:
        """
        Execute a recommendation

        Args:
            recommendation: Recommendation data
            dry_run: Override instance dry_run setting

        Returns:
            Execution results with rollback data
        """
        is_dry_run = dry_run if dry_run is not None else self.dry_run

        result = {
            "dry_run": is_dry_run,
            "started_at": datetime.now().isoformat(),
            "operations": [],
            "successes": 0,
            "failures": 0,
            "rollback_data": [],
            "errors": []
        }

        rec_type = recommendation.get("type")
        action = recommendation.get("action")
        affected_files = recommendation.get("affected_files", [])

        logger.info(f"Executing recommendation: {rec_type}/{action} ({len(affected_files)} files, dry_run={is_dry_run})")

        # Route to appropriate handler
        try:
            if action == "move":
                result = await self._execute_move(
                    affected_files,
                    recommendation,
                    is_dry_run,
                    result
                )
            elif action == "delete":
                result = await self._execute_delete(
                    affected_files,
                    recommendation,
                    is_dry_run,
                    result
                )
            elif action == "compress":
                result = await self._execute_compress(
                    affected_files,
                    recommendation,
                    is_dry_run,
                    result
                )
            elif action == "tag":
                result = await self._execute_tag(
                    affected_files,
                    recommendation,
                    is_dry_run,
                    result
                )
            else:
                logger.warning(f"Unknown action: {action}")
                result["errors"].append({
                    "error": f"Unknown action: {action}"
                })

        except Exception as e:
            logger.error(f"Execution failed: {e}", exc_info=True)
            result["errors"].append({
                "error": str(e)
            })

        result["completed_at"] = datetime.now().isoformat()
        result["can_rollback"] = len(result["rollback_data"]) > 0

        return result

    async def _execute_move(
        self,
        files: List[Dict[str, Any]],
        recommendation: Dict[str, Any],
        dry_run: bool,
        result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute move operation"""

        # Extract destination from recommendation
        # This is a simplified version - production would need more sophisticated parsing
        dest_dir = recommendation.get("metadata", {}).get("destination_directory", "/organized")

        for file_data in files:
            file_path = Path(file_data.get("path", ""))

            if not file_path.exists():
                result["errors"].append({
                    "file": str(file_path),
                    "error": "File not found"
                })
                result["failures"] += 1
                continue

            try:
                # Determine new path
                new_path = Path(dest_dir) / file_path.name

                if dry_run:
                    result["operations"].append({
                        "type": "move",
                        "from": str(file_path),
                        "to": str(new_path),
                        "status": "planned"
                    })
                else:
                    # Ensure destination directory exists
                    new_path.parent.mkdir(parents=True, exist_ok=True)

                    # Save rollback data
                    result["rollback_data"].append({
                        "type": "move",
                        "original_path": str(file_path),
                        "new_path": str(new_path)
                    })

                    # Move file
                    shutil.move(str(file_path), str(new_path))

                    result["operations"].append({
                        "type": "move",
                        "from": str(file_path),
                        "to": str(new_path),
                        "status": "completed"
                    })

                result["successes"] += 1

            except Exception as e:
                logger.error(f"Failed to move {file_path}: {e}")
                result["errors"].append({
                    "file": str(file_path),
                    "error": str(e)
                })
                result["failures"] += 1

        return result

    async def _execute_delete(
        self,
        files: List[Dict[str, Any]],
        recommendation: Dict[str, Any],
        dry_run: bool,
        result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute delete operation"""

        for file_data in files:
            file_path = Path(file_data.get("path", ""))

            if not file_path.exists():
                result["errors"].append({
                    "file": str(file_path),
                    "error": "File not found"
                })
                result["failures"] += 1
                continue

            try:
                if dry_run:
                    result["operations"].append({
                        "type": "delete",
                        "file": str(file_path),
                        "size": file_data.get("size", 0),
                        "status": "planned"
                    })
                else:
                    # Save rollback data (file content for small files)
                    file_size = file_path.stat().st_size

                    rollback_entry = {
                        "type": "delete",
                        "path": str(file_path),
                        "size": file_size
                    }

                    # Store content only for small files (< 1MB)
                    if file_size < 1024 * 1024:
                        with open(file_path, 'rb') as f:
                            rollback_entry["content"] = f.read().hex()

                    result["rollback_data"].append(rollback_entry)

                    # Delete file
                    file_path.unlink()

                    result["operations"].append({
                        "type": "delete",
                        "file": str(file_path),
                        "size": file_size,
                        "status": "completed"
                    })

                result["successes"] += 1

            except Exception as e:
                logger.error(f"Failed to delete {file_path}: {e}")
                result["errors"].append({
                    "file": str(file_path),
                    "error": str(e)
                })
                result["failures"] += 1

        return result

    async def _execute_compress(
        self,
        files: List[Dict[str, Any]],
        recommendation: Dict[str, Any],
        dry_run: bool,
        result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute compress operation"""

        archive_name = recommendation.get("metadata", {}).get("archive_name", "archive.zip")

        if dry_run:
            result["operations"].append({
                "type": "compress",
                "files": [f.get("path") for f in files],
                "archive": archive_name,
                "status": "planned"
            })
            result["successes"] += len(files)
        else:
            # Implementation would use zipfile or tarfile
            # For now, just log the intent
            logger.info(f"Would compress {len(files)} files to {archive_name}")
            result["operations"].append({
                "type": "compress",
                "files": [f.get("path") for f in files],
                "archive": archive_name,
                "status": "not_implemented"
            })

        return result

    async def _execute_tag(
        self,
        files: List[Dict[str, Any]],
        recommendation: Dict[str, Any],
        dry_run: bool,
        result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute tagging operation (metadata only, no file changes)"""

        tags = recommendation.get("metadata", {}).get("tags", [])

        for file_data in files:
            result["operations"].append({
                "type": "tag",
                "file": file_data.get("path"),
                "tags": tags,
                "status": "planned" if dry_run else "completed"
            })
            result["successes"] += 1

        return result

    async def rollback_execution(
        self,
        rollback_data: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Rollback executed operations

        Args:
            rollback_data: List of rollback operations

        Returns:
            Rollback results
        """
        result = {
            "started_at": datetime.now().isoformat(),
            "operations": [],
            "successes": 0,
            "failures": 0,
            "errors": []
        }

        logger.info(f"Rolling back {len(rollback_data)} operations")

        for operation in rollback_data:
            op_type = operation.get("type")

            try:
                if op_type == "move":
                    # Move file back to original location
                    original_path = Path(operation["original_path"])
                    new_path = Path(operation["new_path"])

                    if new_path.exists():
                        original_path.parent.mkdir(parents=True, exist_ok=True)
                        shutil.move(str(new_path), str(original_path))

                        result["operations"].append({
                            "type": "rollback_move",
                            "from": str(new_path),
                            "to": str(original_path),
                            "status": "completed"
                        })
                        result["successes"] += 1
                    else:
                        result["errors"].append({
                            "operation": operation,
                            "error": "File not found at new location"
                        })
                        result["failures"] += 1

                elif op_type == "delete":
                    # Restore deleted file if content was saved
                    if "content" in operation:
                        file_path = Path(operation["path"])
                        file_path.parent.mkdir(parents=True, exist_ok=True)

                        with open(file_path, 'wb') as f:
                            f.write(bytes.fromhex(operation["content"]))

                        result["operations"].append({
                            "type": "rollback_delete",
                            "file": str(file_path),
                            "status": "completed"
                        })
                        result["successes"] += 1
                    else:
                        result["errors"].append({
                            "operation": operation,
                            "error": "File content not saved, cannot restore"
                        })
                        result["failures"] += 1

                else:
                    logger.warning(f"Unknown rollback operation type: {op_type}")
                    result["failures"] += 1

            except Exception as e:
                logger.error(f"Rollback operation failed: {e}")
                result["errors"].append({
                    "operation": operation,
                    "error": str(e)
                })
                result["failures"] += 1

        result["completed_at"] = datetime.now().isoformat()

        return result


# Global executor instance
execution_service = ExecutionService(dry_run=True)
