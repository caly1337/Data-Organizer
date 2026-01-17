# Data-Organizer Project Definition

## 🎯 Project Overview

Data-Organizer is a containerized AI-powered filesystem analysis and optimization tool that helps users understand, analyze, and reorganize their file structures using multiple LLM models.

## 📋 Project Metadata

- **Project Name**: Data-Organizer
- **Repository**: F:\AI-PROD\projects\Data-Organizer
- **Status**: 🚧 In Development
- **Created**: 2026-01-17
- **Primary Developer**: Brani (via Claude Code)
- **Development Environment**: brani-pc (F:\AI-PROD\projects\Data-Organizer)
- **Production Target**: spark.lmphq.net

## 🎯 Purpose

Analyze local filesystems with LLM assistance to:
1. Understand file organization patterns
2. Identify duplicates, bloat, and obsolete files
3. Suggest intelligent reorganization strategies
4. Execute approved changes safely
5. Track filesystem evolution over time

## 🏗️ Architecture

### Technology Stack

| Component | Technology | Version | Port |
|-----------|-----------|---------|------|
| Database | PostgreSQL | 15 | 5435 |
| Backend | FastAPI | 0.109+ | 8004 |
| Frontend | Next.js | 14.x | 3004 |
| LLM (Local) | Ollama | Latest | 11434 |
| LLM (Cloud) | Gemini | 2.5 | API |
| ORM | SQLAlchemy | 2.0+ | - |
| Cache | Redis | 7 | 6379 |

### Multi-Model LLM Support

**Primary Providers:**
1. **Ollama** (spark.lmphq.net:11434, crm.lmphq.net:11435)
   - Models: qwen2.5:7b, llama3, mistral
   - Use case: Fast local analysis, privacy-sensitive scans

2. **Google Gemini** (API)
   - Models: gemini-2.5-flash, gemini-1.5-pro
   - Use case: Deep research, web-enhanced context

3. **Claude** (API - optional)
   - Models: claude-sonnet-4.5
   - Use case: Complex reasoning, detailed analysis

### Core Components

```
data-organizer/
├── backend/              # FastAPI backend
│   ├── app/
│   │   ├── api/         # API endpoints
│   │   │   ├── scan.py          # Filesystem scanning
│   │   │   ├── analysis.py      # LLM analysis
│   │   │   ├── recommendations.py # Suggestions
│   │   │   └── execution.py     # Apply changes
│   │   ├── models/      # SQLAlchemy models
│   │   │   ├── scan.py
│   │   │   ├── analysis.py
│   │   │   └── recommendation.py
│   │   ├── schemas/     # Pydantic schemas
│   │   ├── services/    # Business logic
│   │   │   ├── file_scanner.py
│   │   │   ├── llm_service.py
│   │   │   ├── analyzer.py
│   │   │   └── executor.py
│   │   ├── core/        # Configuration
│   │   │   ├── config.py
│   │   │   ├── llm_config.py
│   │   │   └── security.py
│   │   ├── database.py  # Database connection
│   │   └── main.py      # FastAPI application
│   ├── alembic/         # Database migrations
│   └── tests/           # Test suite
├── frontend/            # Next.js frontend
│   └── src/
│       ├── app/         # Next.js 14 app directory
│       ├── components/  # React components
│       └── lib/         # Utilities
└── docker-compose.yml
```

## 🎨 Features

### Phase 1: Foundation (Current)
- [x] Project structure
- [x] Docker setup
- [ ] Database schema
- [ ] Basic FastAPI skeleton
- [ ] LLM provider integration

### Phase 2: Core Scanning
- [ ] Filesystem scanner
- [ ] File metadata extraction
- [ ] Directory tree analysis
- [ ] Duplicate detection
- [ ] Size analysis

### Phase 3: LLM Analysis
- [ ] Ollama integration
- [ ] Gemini integration
- [ ] Multi-model orchestration
- [ ] Analysis prompt engineering
- [ ] Recommendation generation

### Phase 4: Execution Engine
- [ ] Safe file operations
- [ ] Dry-run mode
- [ ] Rollback capability
- [ ] Progress tracking
- [ ] Error handling

### Phase 5: Frontend
- [ ] Next.js dashboard
- [ ] Scan visualization
- [ ] Recommendation review
- [ ] Execution monitoring
- [ ] Historical analysis

### Phase 6: Advanced Features
- [ ] Scheduled scans
- [ ] Watch mode (real-time monitoring)
- [ ] Custom rules engine
- [ ] ML-based pattern detection
- [ ] API for automation

## 🔧 Development Environment

### Local Development (brani-pc)
```bash
# Location
F:\AI-PROD\projects\Data-Organizer

# Start services
docker-compose up -d

# Database
postgresql://localhost:5435/data_organizer

# Backend
http://localhost:8004

# Frontend
http://localhost:3004
```

### LLM Access
- Ollama: http://spark.lmphq.net:11434
- Gemini: API key in .env

## 🚀 Production Deployment

### Target: spark.lmphq.net

```bash
# Production URLs
Backend:  http://spark.lmphq.net:8004
Frontend: http://spark.lmphq.net:3004

# Docker Network: ai-net
# Monitoring: Grafana integration
```

## 📊 Database Schema

### Core Tables

1. **scans** - Filesystem scan records
   - id, path, started_at, completed_at, status, metadata

2. **files** - Individual file records
   - id, scan_id, path, size, modified_at, hash, metadata

3. **analyses** - LLM analysis results
   - id, scan_id, provider, model, prompt, response, created_at

4. **recommendations** - Suggested actions
   - id, analysis_id, type, description, confidence, status

5. **executions** - Applied changes
   - id, recommendation_id, executed_at, status, rollback_data

6. **llm_providers** - LLM configuration
   - id, name, type, config, enabled

## 🔐 Security Considerations

- File operations sandboxed to mounted volumes
- Dry-run default for all destructive operations
- User approval required for execution
- Rollback capability for all changes
- Audit log for all operations
- No automatic deletion of files

## 📈 Success Metrics

1. Scan performance: < 1000 files/second
2. LLM analysis: < 30 seconds per directory
3. Recommendation quality: User acceptance rate
4. Execution safety: Zero data loss incidents
5. User adoption: Active scans per week

## 🔗 Related Projects

- LMP-CRM: Pattern for FastAPI + Next.js + PostgreSQL
- lmp-mcp: Infrastructure management tools
- Harry variants: LLM integration patterns

## 📝 Notes

- Prioritize safety over speed for file operations
- Support multiple analysis modes (fast/deep/comparison)
- Make LLM provider selection user-configurable
- Store all analysis history for ML training
- Build API-first for automation potential

## 🎯 Current Sprint

**Sprint 1: Foundation** (Current)
- [x] Project structure
- [ ] Docker setup complete
- [ ] Database migrations
- [ ] Basic API endpoints
- [ ] LLM provider integration

**Next Sprint: Core Scanner**
- Filesystem scanning engine
- File metadata extraction
- Basic analysis with Ollama
