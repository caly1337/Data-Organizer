# Data-Organizer Quick Start Guide

Get Data-Organizer running in 5 minutes!

## Prerequisites

- Docker & Docker Compose installed
- Access to Ollama instance (default: spark.lmphq.net:11434)
- Optional: Gemini API key for cloud analysis

## 1. Setup Environment

```bash
cd F:\AI-PROD\projects\Data-Organizer

# Backend
cp backend/.env.example backend/.env

# Frontend
cp frontend/.env.example frontend/.env
```

## 2. Configure Backend

Edit `backend/.env`:

```bash
# Required - Database
DATABASE_URL=postgresql://data_organizer:dev_password@data-organizer-db:5432/data_organizer

# Required - Ollama (Local LLM)
OLLAMA_ENABLED=true
OLLAMA_BASE_URL=http://spark.lmphq.net:11434
OLLAMA_DEFAULT_MODEL=qwen2.5:7b

# Optional - Gemini (Cloud LLM)
GEMINI_ENABLED=false
GEMINI_API_KEY=your_api_key_here

# Security
SECRET_KEY=change-this-to-random-string-in-production
```

## 3. Start Services

```bash
# Start database first
docker-compose up -d data-organizer-db data-organizer-redis

# Wait 10 seconds for DB to be ready
timeout /t 10

# Start backend
docker-compose up -d data-organizer-backend

# Start frontend
docker-compose up -d data-organizer-frontend
```

## 4. Initialize Database

```bash
cd backend
pip install -r requirements.txt
alembic upgrade head
```

## 5. Verify Installation

```bash
# Check backend health
curl http://localhost:8004/health

# Check API docs
# Open browser: http://localhost:8004/docs

# Check frontend
# Open browser: http://localhost:3004
```

## 6. First Scan (Coming in Phase 2)

Via API:
```bash
curl -X POST http://localhost:8004/api/scans \
  -H "Content-Type: application/json" \
  -d '{
    "path": "/mnt/data/test",
    "analysis_mode": "fast",
    "llm_provider": "ollama"
  }'
```

Via UI:
1. Go to http://localhost:3004
2. Click "New Scan"
3. Select directory
4. Choose analysis mode
5. Review recommendations

## Common Issues

**Database connection failed:**
```bash
# Ensure PostgreSQL is running
docker-compose ps data-organizer-db

# Check logs
docker-compose logs data-organizer-db
```

**Backend won't start:**
```bash
# Check environment variables
cat backend/.env

# Check logs
docker-compose logs data-organizer-backend
```

**Ollama connection failed:**
```bash
# Test Ollama connectivity
curl http://spark.lmphq.net:11434/api/tags

# Update OLLAMA_BASE_URL in backend/.env if needed
```

## Development Mode

```bash
# Backend with hot reload
cd backend
uvicorn app.main:app --reload --port 8004

# Frontend with hot reload
cd frontend
npm install
npm run dev
```

## Next Steps

1. Read full documentation: `README.md`
2. Review design document: `docs/plans/2026-01-17-data-organizer-design.md`
3. Check project roadmap: `PROJECT-DEFINITION.md`
4. Explore API: http://localhost:8004/docs

## Production Deployment

See `README.md` section "Production Deployment" for deploying to spark.lmphq.net.

## Support

For issues or questions:
- Check `README.md` for detailed documentation
- Review `PROJECT-DEFINITION.md` for architecture details
- Examine Docker logs: `docker-compose logs -f`
