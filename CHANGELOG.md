# Changelog

All notable changes to Data-Organizer will be documented in this file.

## [0.2.0] - 2026-01-18

### Added
- **Settings Page**: Comprehensive configuration UI at /settings
  - LLM provider selection with dropdown
  - Model selection for Ollama and Gemini
  - Analysis mode defaults
  - Scan preference configuration
  - UI preferences (WebSocket, refresh interval)
  - Provider testing with live results

- **Custom Prompts**: Users can write custom analysis instructions
  - Checkbox to enable custom prompts
  - Large textarea for custom instructions
  - 4 pre-built prompt templates (duplicates, large files, reorganization, cleanup)
  - Expandable examples section with one-click insertion

- **Delete Functionality**:
  - Delete individual scans from scan cards
  - Delete button on scan detail page
  - Bulk delete dropdown menu:
    - Delete failed scans
    - Delete completed scans
    - Delete ALL scans
  - Confirmation dialogs for all destructive operations

- **Navigation**:
  - Navbar component on all pages
  - Active route highlighting
  - Quick access to Scans, Providers, Settings

- **Production Deployment**:
  - Caddyfile.snippet for reverse proxy
  - PRODUCTION-DEPLOYMENT.md guide
  - deploy-to-spark.ps1 and deploy-to-spark.sh scripts
  - Domain: filescan.spark.lmphq.net

### Fixed
- **Dark Mode**: Comprehensive dark mode support
  - Input fields with white text on dark backgrounds
  - All panels (white, gray, colored) with dark variants
  - Proper text contrast throughout
  - Readable placeholders
  - Visible borders and checkboxes

- **Gemini Provider**: Handle missing usage_metadata gracefully
- **Ollama Configuration**: Use HTTP with correct port (11434)
- **Model Name**: qwen2.5:latest (was qwen2.5:7b)
- **API Imports**: Fixed File model import in analysis.py
- **SQLAlchemy**: Renamed metadata columns to extra_metadata (reserved word)
- **Schema Validation**: Fixed Pydantic validation errors
- **WebSocket**: Graceful fallback to polling with no console errors
- **CORS**: Explicit origins for localhost:3004

### Changed
- Simplified scan endpoint (removed include_files parameter)
- WebSocket errors suppressed (silent polling fallback)
- Configuration now stored in localStorage
- Scan/analysis forms use configured defaults

## [0.1.0] - 2026-01-17

### Added
- **Core Backend** (FastAPI):
  - 25+ REST API endpoints
  - 6 database models (Scan, File, Analysis, Recommendation, Execution, LLMProvider)
  - 4 core services (LLMService, FileScanner, FilesystemAnalyzer, ExecutionService)
  - WebSocket support for real-time updates
  - Prometheus metrics endpoint

- **Multi-Model LLM Integration**:
  - Ollama provider (local, free)
  - Gemini provider (cloud, API-based)
  - Claude provider (optional)
  - Provider abstraction layer
  - Token and cost tracking

- **Filesystem Scanner**:
  - Async recursive scanning
  - File metadata extraction
  - xxhash-based deduplication
  - Category-based classification
  - Configurable depth and filters

- **AI Analysis Engine**:
  - Prompt engineering for different modes
  - Fast mode (~10s with Ollama)
  - Deep mode (~30s with Gemini)
  - Comparison mode (multi-model)
  - Recommendation generation

- **Execution Engine**:
  - Safe file operations (move, delete, compress, tag)
  - Dry-run preview mode
  - Complete rollback capability
  - Batch processing
  - Operation logging

- **Frontend** (Next.js 14):
  - 5 pages: home, scans list, scan detail, analysis detail, providers
  - 2 components: ScanCard, RecommendationCard
  - TypeScript API client with WebSocket support
  - Real-time updates via polling fallback
  - Tailwind CSS styling

- **Infrastructure**:
  - Docker Compose for development
  - Docker Compose for production (ai-net)
  - PostgreSQL 15 database
  - Redis 7 cache
  - Environment templates
  - Setup scripts (Windows & Linux)

- **Documentation**:
  - Complete README with architecture
  - QUICKSTART guide
  - API documentation
  - Development guide
  - Usage examples
  - Contributing guidelines
  - Design document

### Technical Details
- Language: Python 3.11, TypeScript
- Framework: FastAPI, Next.js 14
- Database: PostgreSQL 15, Redis 7
- LLM: Ollama (qwen2.5:latest), Gemini (gemini-2.5-flash)
- Ports: Backend 8004, Frontend 3004, DB 5435, Redis 6380

### Known Issues
- WebSocket connections fail (fallback to polling works)
