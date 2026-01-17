"""
Tests for FileScanner service
"""
import pytest
from pathlib import Path
from app.services.file_scanner import FileScanner


@pytest.mark.asyncio
async def test_scanner_initialization():
    """Test scanner can be initialized"""
    scanner = FileScanner(max_depth=5)
    assert scanner.max_depth == 5
    assert scanner.include_hidden == False
    scanner.cleanup()


@pytest.mark.asyncio
async def test_categorize_file():
    """Test file categorization"""
    scanner = FileScanner()

    # Test code file
    category = scanner._categorize_file(Path("test.py"), "text/x-python")
    assert category == "code"

    # Test document
    category = scanner._categorize_file(Path("doc.pdf"), "application/pdf")
    assert category == "document"

    # Test image
    category = scanner._categorize_file(Path("image.jpg"), "image/jpeg")
    assert category == "image"

    scanner.cleanup()


@pytest.mark.asyncio
async def test_format_size():
    """Test size formatting"""
    scanner = FileScanner()

    assert "1.00 KB" in scanner._format_size(1024)
    assert "1.00 MB" in scanner._format_size(1024 * 1024)
    assert "1.00 GB" in scanner._format_size(1024 * 1024 * 1024)

    scanner.cleanup()
