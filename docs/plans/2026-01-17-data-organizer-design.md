# Data-Organizer Design Document

**Date:** 2026-01-17
**Version:** 1.0
**Status:** Approved

## Executive Summary

Data-Organizer is an AI-powered filesystem analysis and optimization tool that leverages multiple Large Language Model (LLM) providers to help users understand, analyze, and reorganize their file structures intelligently.

## Problem Statement

Users struggle with:
- Disorganized filesystem structures that grow organically over time
- Duplicate files consuming unnecessary storage
- Difficulty identifying obsolete or temporary files
- Lack of intelligent categorization and organization strategies
- Manual file organization is time-consuming and error-prone

## Solution Overview

A containerized application that:
1. Scans local filesystems mounted as Docker volumes
2. Analyzes file structures using multiple LLM providers
3. Generates intelligent reorganization recommendations
4. Safely executes approved changes with rollback capability
5. Tracks filesystem evolution over time

## Architecture

### High-Level Components

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│   Frontend  │────▶│   Backend    │────▶│  Database   │
│  (Next.js)  │     │  (FastAPI)   │     │(PostgreSQL) │
└─────────────┘     └──────┬───────┘     └─────────────┘
                           │
                ┌──────────┼──────────┐
                │          │          │
         ┌──────▼───┐ ┌───▼────┐ ┌──▼─────┐
         │  Ollama  │ │ Gemini │ │ Claude │
         │  (Local) │ │ (Cloud)│ │ (Cloud)│
         └──────────┘ └────────┘ └────────┘
```

### Technology Stack

**Backend:**
- FastAPI 0.109+ (async web framework)
- SQLAlchemy 2.0+ (ORM with async support)
- Alembic (database migrations)
- Pydantic (data validation)
- Redis (caching and task queue)

**Frontend:**
- Next.js 14 (React framework with App Router)
- TypeScript (type safety)
- Tailwind CSS (styling)
- TanStack Query (data fetching)
- Zustand (state management)

**Database:**
- PostgreSQL 15 (relational database)

**LLM Providers:**
- Ollama (local models: qwen2.5:7b, llama3, mistral)
- Google Gemini (cloud: gemini-2.5-flash, gemini-1.5-pro)
- Anthropic Claude (cloud: claude-sonnet-4.5) - optional

**Infrastructure:**
- Docker & Docker Compose
- Development: brani-pc (F:\AI-PROD\projects\Data-Organizer)
- Production: spark.lmphq.net

## Data Model

### Core Entities

**Scan**
- Represents a filesystem scan operation
- Tracks path, status, timing, and results
- Contains metadata about scan configuration

**File**
- Individual file record from a scan
- Includes path, size, timestamps, hash
- Categorized by type and tagged

**Analysis**
- LLM analysis result for a scan
- Links to specific provider and model
- Stores prompt, response, and metadata

**Recommendation**
- AI-generated suggestion for file organization
- Includes confidence score and impact assessment
- Tracks approval and execution status

**Execution**
- Record of applied recommendations
- Supports dry-run mode and rollback
- Tracks progress and results

**LLMProvider**
- Configuration for LLM providers
- Tracks usage, performance, and status

### Database Schema

```sql
scans (
  id, path, status, started_at, completed_at,
  max_depth, include_hidden, follow_symlinks,
  total_files, total_directories, total_size,
  error_message, errors_count, metadata
)

files (
  id, scan_id, path, name, extension,
  size, is_directory, is_symlink,
  created_at, modified_at, accessed_at,
  hash, mime_type, category, tags, metadata
)

analyses (
  id, scan_id, provider, model, mode,
  prompt, response, tokens_used, cost, duration,
  status, error_message, created_at, completed_at, metadata
)

recommendations (
  id, analysis_id, type, action,
  title, description, reasoning,
  confidence, impact_score,
  affected_files, affected_count,
  expected_space_saved, expected_duration,
  status, approved, approved_by, approved_at,
  priority, created_at, updated_at, metadata
)

executions (
  id, recommendation_id, dry_run, batch_size,
  status, started_at, completed_at,
  total_operations, completed_operations, failed_operations,
  files_modified, files_deleted, files_moved, space_freed,
  errors, error_message,
  rollback_data, can_rollback, rolled_back_at,
  executed_by, execution_log, created_at, updated_at, metadata
)

llm_providers (
  id, name, type, enabled, config,
  total_requests, total_tokens, total_cost, success_rate,
  avg_response_time, last_used_at,
  status, error_count, last_error,
  created_at, updated_at, metadata
)
```

## Multi-Model LLM Integration

### Provider Configuration

**Ollama (Local)**
```yaml
provider: ollama
instances:
  - url: http://spark.lmphq.net:11434
    model: qwen2.5:7b
  - url: http://crm.lmphq.net:11435
    model: qwen2.5:7b
timeout: 120s
```

**Gemini (Cloud)**
```yaml
provider: gemini
api_key: ${GEMINI_API_KEY}
model: gemini-2.5-flash
grounding: true
max_tokens: 8192
```

**Claude (Cloud - Optional)**
```yaml
provider: claude
api_key: ${CLAUDE_API_KEY}
model: claude-sonnet-4.5
max_tokens: 8192
```

### Analysis Modes

**Fast Mode** (Ollama)
- Quick directory structure analysis
- Basic duplicate detection
- Simple categorization
- ~10 seconds per 1000 files
- Use case: Regular scans, quick checks

**Deep Mode** (Gemini + Ollama)
- Comprehensive analysis with web research
- Context-aware recommendations
- Advanced pattern detection
- ~30 seconds per directory
- Use case: Initial analysis, major reorganization

**Comparison Mode** (Multi-Model)
- Run same analysis on multiple LLMs
- Compare recommendations
- User selects best approach
- Use case: Complex decisions, conflicting strategies

### LLM Service Layer

```python
class LLMService:
    async def analyze_scan(
        self,
        scan: Scan,
        provider: str,
        mode: str
    ) -> Analysis:
        # Route to appropriate provider
        # Generate analysis prompt
        # Execute LLM request
        # Store and return analysis

    async def compare_analyses(
        self,
        scan: Scan,
        providers: List[str]
    ) -> List[Analysis]:
        # Run parallel analyses
        # Compare results
        # Return all analyses
```

## Core Features

### 1. Filesystem Scanner

**Capabilities:**
- Recursive directory traversal
- File metadata extraction (size, timestamps, permissions)
- Content hashing (xxhash for deduplication)
- MIME type detection
- Configurable depth and filters

**Safety:**
- Read-only operations
- Sandboxed to mounted volumes
- Respects .gitignore-style exclusions
- Handles symlinks safely

### 2. LLM Analysis Engine

**Process:**
1. Prepare scan context (directory structure, file statistics)
2. Generate analysis prompt based on mode
3. Submit to selected LLM provider(s)
4. Parse and structure response
5. Generate actionable recommendations

**Prompt Engineering:**
- Context: Directory tree, file counts, sizes
- Task: Identify issues, suggest improvements
- Constraints: Safety, reversibility, impact
- Output: Structured recommendations with confidence scores

### 3. Recommendation System

**Types:**
- **Reorganize**: Move files to better structure
- **Deduplicate**: Remove or consolidate duplicates
- **Cleanup**: Delete temporary/obsolete files
- **Archive**: Compress old/unused files
- **Categorize**: Auto-tag and organize by type

**Scoring:**
- Confidence: 0.0-1.0 (LLM certainty)
- Impact: 0.0-1.0 (expected benefit)
- Priority: Integer ranking

### 4. Execution Engine

**Safety Features:**
- Dry-run mode (preview changes)
- User approval required
- Batch processing with progress tracking
- Complete rollback support
- Audit logging

**Operations:**
- Move files
- Delete files
- Create directories
- Compress files
- Update metadata/tags

## API Design

### REST Endpoints

**Scans**
```
POST   /api/scans              - Start new scan
GET    /api/scans              - List scans
GET    /api/scans/{id}         - Get scan details
DELETE /api/scans/{id}         - Delete scan
```

**Analysis**
```
POST   /api/scans/{id}/analyze    - Run analysis
GET    /api/scans/{id}/analyses   - Get analyses
GET    /api/analyses/{id}         - Get analysis details
```

**Recommendations**
```
GET    /api/scans/{id}/recommendations  - Get recommendations
PUT    /api/recommendations/{id}/approve - Approve recommendation
PUT    /api/recommendations/{id}/reject  - Reject recommendation
```

**Execution**
```
POST   /api/recommendations/{id}/execute - Execute recommendation
POST   /api/executions/{id}/rollback    - Rollback execution
GET    /api/executions/{id}             - Get execution status
```

**LLM Providers**
```
GET    /api/llm-providers       - List providers
POST   /api/llm-providers       - Add provider
PUT    /api/llm-providers/{id}  - Update provider
DELETE /api/llm-providers/{id}  - Remove provider
```

## Security Considerations

**File Operations:**
- Sandboxed to mounted Docker volumes only
- Read-only scanning by default
- Write operations require explicit approval
- No automatic deletion without confirmation

**Data Privacy:**
- Local Ollama for sensitive data
- Optional cloud providers with user consent
- No data persistence on cloud providers
- Clear privacy policy for each provider

**Authentication:**
- JWT-based authentication (future phase)
- Role-based access control
- Audit trail for all operations

## Deployment Strategy

### Development (brani-pc)

```bash
# Setup
cd F:\AI-PROD\projects\Data-Organizer
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env

# Start services
docker-compose up -d

# Access
Backend:  http://localhost:8004
Frontend: http://localhost:3004
Database: localhost:5435
```

### Production (spark.lmphq.net)

```bash
# Deploy
ssh spark.lmphq.net
cd /opt/apps/data-organizer
docker-compose -f docker-compose.prod.yml up -d

# URLs
Backend:  http://spark.lmphq.net:8004
Frontend: http://spark.lmphq.net:3004

# Monitoring
Grafana integration for metrics
Loki for log aggregation
Prometheus for metrics
```

## Performance Considerations

**Targets:**
- Scan speed: 1000+ files/second
- Analysis time: < 30 seconds per directory
- API response: < 200ms (excluding LLM calls)
- Database queries: < 100ms

**Optimization:**
- Async operations throughout
- Redis caching for repeated queries
- Batch processing for large operations
- Connection pooling for database
- Parallel LLM requests for comparison mode

## Future Enhancements

**Phase 2+:**
- Scheduled automatic scans
- Real-time filesystem monitoring
- Custom rule engine for advanced users
- Machine learning for pattern detection
- Integration with cloud storage (S3, Drive)
- CLI tool for automation
- Browser extension for quick scans
- Mobile app for monitoring

## Success Metrics

**Technical:**
- Scan performance: 1000+ files/second
- Analysis accuracy: > 80% user approval rate
- Execution safety: Zero data loss incidents
- System uptime: > 99.9%

**User:**
- Time saved: Reduce manual organization by 80%
- Space saved: Average 20% storage reclaimed
- User satisfaction: > 4.5/5 rating
- Adoption: 10+ active scans/week

## Conclusion

Data-Organizer provides an intelligent, safe, and flexible solution for filesystem analysis and optimization. By leveraging multiple LLM providers, it offers users the best of both worlds: fast local processing with Ollama and deep cloud-based analysis with Gemini/Claude. The architecture prioritizes safety, reversibility, and user control while providing powerful AI-driven insights.
