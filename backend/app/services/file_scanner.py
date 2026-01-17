"""
File Scanner Service
Scans filesystems and extracts metadata
"""
import os
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime
import mimetypes
import xxhash
import asyncio
from concurrent.futures import ThreadPoolExecutor

logger = logging.getLogger(__name__)


class FileScanner:
    """Filesystem scanner with metadata extraction"""

    def __init__(
        self,
        max_depth: int = 10,
        include_hidden: bool = False,
        follow_symlinks: bool = False,
        hash_files: bool = True
    ):
        self.max_depth = max_depth
        self.include_hidden = include_hidden
        self.follow_symlinks = follow_symlinks
        self.hash_files = hash_files
        self.executor = ThreadPoolExecutor(max_workers=4)

    async def scan_directory(
        self,
        path: str,
        on_file_callback: Optional[callable] = None,
        on_progress_callback: Optional[callable] = None
    ) -> Dict[str, Any]:
        """
        Scan a directory and return metadata

        Args:
            path: Directory path to scan
            on_file_callback: Async callback for each file found
            on_progress_callback: Async callback for progress updates

        Returns:
            Dictionary with scan results
        """
        start_time = datetime.now()
        path_obj = Path(path)

        if not path_obj.exists():
            raise ValueError(f"Path does not exist: {path}")

        if not path_obj.is_dir():
            raise ValueError(f"Path is not a directory: {path}")

        # Scan results
        results = {
            "path": str(path),
            "total_files": 0,
            "total_directories": 0,
            "total_size": 0,
            "files": [],
            "errors": [],
            "started_at": start_time.isoformat(),
        }

        # Scan recursively
        try:
            await self._scan_recursive(
                path_obj,
                depth=0,
                results=results,
                on_file_callback=on_file_callback,
                on_progress_callback=on_progress_callback
            )
        except Exception as e:
            logger.error(f"Scan failed: {e}")
            results["errors"].append({
                "path": str(path),
                "error": str(e)
            })

        # Finalize results
        results["completed_at"] = datetime.now().isoformat()
        results["duration"] = (datetime.now() - start_time).total_seconds()

        return results

    async def _scan_recursive(
        self,
        path: Path,
        depth: int,
        results: Dict[str, Any],
        on_file_callback: Optional[callable],
        on_progress_callback: Optional[callable]
    ):
        """Recursively scan directory"""

        # Check depth limit
        if depth > self.max_depth:
            return

        try:
            for item in path.iterdir():
                # Skip hidden files if configured
                if not self.include_hidden and item.name.startswith('.'):
                    continue

                # Handle symlinks
                if item.is_symlink() and not self.follow_symlinks:
                    continue

                try:
                    if item.is_dir():
                        results["total_directories"] += 1

                        # Recurse into directory
                        await self._scan_recursive(
                            item,
                            depth + 1,
                            results,
                            on_file_callback,
                            on_progress_callback
                        )
                    else:
                        # Process file
                        file_metadata = await self._process_file(item)
                        results["total_files"] += 1
                        results["total_size"] += file_metadata["size"]
                        results["files"].append(file_metadata)

                        # Callback
                        if on_file_callback:
                            await on_file_callback(file_metadata)

                        # Progress callback
                        if on_progress_callback and results["total_files"] % 100 == 0:
                            await on_progress_callback({
                                "files": results["total_files"],
                                "directories": results["total_directories"],
                                "size": results["total_size"]
                            })

                except PermissionError as e:
                    logger.warning(f"Permission denied: {item}")
                    results["errors"].append({
                        "path": str(item),
                        "error": "Permission denied"
                    })
                except Exception as e:
                    logger.error(f"Error processing {item}: {e}")
                    results["errors"].append({
                        "path": str(item),
                        "error": str(e)
                    })

        except PermissionError:
            logger.warning(f"Permission denied: {path}")
            results["errors"].append({
                "path": str(path),
                "error": "Permission denied"
            })
        except Exception as e:
            logger.error(f"Error scanning {path}: {e}")
            results["errors"].append({
                "path": str(path),
                "error": str(e)
            })

    async def _process_file(self, file_path: Path) -> Dict[str, Any]:
        """Extract metadata from file"""
        loop = asyncio.get_event_loop()

        try:
            stat = file_path.stat()

            # Get MIME type
            mime_type, _ = mimetypes.guess_type(str(file_path))

            # Calculate hash if enabled
            file_hash = None
            if self.hash_files and stat.st_size < 100 * 1024 * 1024:  # Only hash files < 100MB
                file_hash = await loop.run_in_executor(
                    self.executor,
                    self._calculate_hash,
                    file_path
                )

            # Categorize file
            category = self._categorize_file(file_path, mime_type)

            return {
                "path": str(file_path),
                "name": file_path.name,
                "extension": file_path.suffix.lower() if file_path.suffix else None,
                "size": stat.st_size,
                "is_directory": False,
                "is_symlink": file_path.is_symlink(),
                "created_at": datetime.fromtimestamp(stat.st_ctime).isoformat(),
                "modified_at": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                "accessed_at": datetime.fromtimestamp(stat.st_atime).isoformat(),
                "hash": file_hash,
                "mime_type": mime_type,
                "category": category,
                "metadata": {
                    "mode": stat.st_mode,
                    "inode": stat.st_ino,
                    "device": stat.st_dev,
                    "nlink": stat.st_nlink,
                    "uid": stat.st_uid,
                    "gid": stat.st_gid,
                }
            }

        except Exception as e:
            logger.error(f"Error processing file {file_path}: {e}")
            raise

    def _calculate_hash(self, file_path: Path) -> str:
        """Calculate xxhash for file (runs in thread pool)"""
        try:
            hasher = xxhash.xxh64()
            with open(file_path, 'rb') as f:
                while chunk := f.read(8192):
                    hasher.update(chunk)
            return hasher.hexdigest()
        except Exception as e:
            logger.error(f"Hash calculation failed for {file_path}: {e}")
            return None

    def _categorize_file(self, file_path: Path, mime_type: Optional[str]) -> str:
        """Categorize file by type"""
        extension = file_path.suffix.lower()

        # Code files
        code_extensions = {'.py', '.js', '.ts', '.java', '.cpp', '.c', '.h', '.go', '.rs', '.rb', '.php'}
        if extension in code_extensions:
            return "code"

        # Documents
        doc_extensions = {'.pdf', '.doc', '.docx', '.txt', '.md', '.odt', '.rtf'}
        if extension in doc_extensions:
            return "document"

        # Images
        if mime_type and mime_type.startswith('image/'):
            return "image"

        # Videos
        if mime_type and mime_type.startswith('video/'):
            return "video"

        # Audio
        if mime_type and mime_type.startswith('audio/'):
            return "audio"

        # Archives
        archive_extensions = {'.zip', '.tar', '.gz', '.bz2', '.7z', '.rar', '.xz'}
        if extension in archive_extensions:
            return "archive"

        # Data files
        data_extensions = {'.json', '.xml', '.yaml', '.yml', '.csv', '.sql', '.db', '.sqlite'}
        if extension in data_extensions:
            return "data"

        # Build artifacts
        build_extensions = {'.o', '.pyc', '.class', '.obj', '.exe', '.dll', '.so'}
        if extension in build_extensions:
            return "build_artifact"

        # Temporary files
        if file_path.name.endswith('~') or extension in {'.tmp', '.temp', '.bak', '.swp', '.swo'}:
            return "temporary"

        return "other"

    async def get_directory_tree(self, path: str, max_depth: int = 3) -> Dict[str, Any]:
        """Get directory tree structure (lightweight, no file details)"""
        path_obj = Path(path)

        if not path_obj.exists():
            raise ValueError(f"Path does not exist: {path}")

        tree = {
            "name": path_obj.name or str(path_obj),
            "path": str(path_obj),
            "is_directory": True,
            "children": []
        }

        if max_depth > 0 and path_obj.is_dir():
            try:
                for item in path_obj.iterdir():
                    if not self.include_hidden and item.name.startswith('.'):
                        continue

                    if item.is_dir():
                        subtree = await self.get_directory_tree(str(item), max_depth - 1)
                        tree["children"].append(subtree)
                    else:
                        tree["children"].append({
                            "name": item.name,
                            "path": str(item),
                            "is_directory": False
                        })
            except PermissionError:
                tree["error"] = "Permission denied"

        return tree

    async def find_duplicates(self, files: List[Dict[str, Any]]) -> List[List[Dict[str, Any]]]:
        """Find duplicate files by hash"""
        hash_map = {}

        for file in files:
            if file.get("hash"):
                file_hash = file["hash"]
                if file_hash not in hash_map:
                    hash_map[file_hash] = []
                hash_map[file_hash].append(file)

        # Return only groups with duplicates
        duplicates = [group for group in hash_map.values() if len(group) > 1]
        return duplicates

    def cleanup(self):
        """Cleanup resources"""
        self.executor.shutdown(wait=True)
