# Data-Organizer

AI-powered filesystem analysis and optimization tool with multi-model LLM support.

## 🎯 What It Does

Data-Organizer analyzes your filesystems and uses AI to:
- Understand file organization patterns
- Identify duplicates, bloat, and obsolete files
- Suggest intelligent reorganization strategies
- Safely execute approved changes
- Track filesystem evolution over time

## 🏗️ Architecture

**Stack:**
- Backend: FastAPI + PostgreSQL + SQLAlchemy
- Frontend: Next.js 14 + React 18 + Tailwind CSS
- LLM: Multi-model (Ollama, Gemini, Claude)
- Deployment: Docker Compose

**Ports:**
- Backend: 8004
- Frontend: 3004
- Database: 5435
- Redis: 6380

## 🚀 Quick Start

### Prerequisites

- Docker & Docker Compose
- Access to Ollama instance (spark.lmphq.net:11434)
- Optional: Gemini API key for cloud analysis

### 1. Clone and Setup

```bash
cd F:\AI-PROD\projects\Data-Organizer
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env
```

### 2. Configure Environment

Edit `backend/.env`:
```bash
# Database
DATABASE_URL=postgresql://data_organizer:dev_password@data-organizer-db:5432/data_organizer

# LLM Providers
OLLAMA_BASE_URL=http://spark.lmphq.net:11434
OLLAMA_DEFAULT_MODEL=qwen2.5:7b

GEMINI_API_KEY=your_api_key_here
GEMINI_DEFAULT_MODEL=gemini-2.5-flash

# Application
API_PORT=8004
DEBUG=true
```

### 3. Start Services

```bash
# Start database
docker-compose up -d data-organizer-db

# Run migrations
cd backend
pip install -r requirements.txt
alembic upgrade head

# Start backend
docker-compose up -d data-organizer-backend

# Start frontend
docker-compose up -d data-organizer-frontend
```

### 4. Access

- Frontend: http://localhost:3004
- Backend API: http://localhost:8004
- API Docs: http://localhost:8004/docs

## 📖 Usage

### Web Interface

1. Navigate to http://localhost:3004
2. Click "New Scan"
3. Select directory to analyze (must be mounted in Docker)
4. Choose LLM provider (Ollama/Gemini/Multi)
5. Review recommendations
6. Approve and execute changes

### API

```python
import requests

# Start a scan
response = requests.post('http://localhost:8004/api/scans', json={
    'path': '/data/to/analyze',
    'analysis_mode': 'deep',
    'llm_provider': 'ollama'
})
scan_id = response.json()['id']

# Get recommendations
recs = requests.get(f'http://localhost:8004/api/scans/{scan_id}/recommendations')

# Execute approved changes
requests.post(f'http://localhost:8004/api/scans/{scan_id}/execute', json={
    'recommendation_ids': [1, 2, 3],
    'dry_run': False
})
```

## 🎨 Features

### Analysis Modes

**Fast Mode** (Ollama)
- Quick directory structure analysis
- Basic duplicate detection
- ~10 seconds per 1000 files

**Deep Mode** (Gemini + Ollama)
- Comprehensive analysis
- Web research for file type context
- ~30 seconds per directory

**Comparison Mode** (Multi-Model)
- Run analysis on multiple LLMs
- Compare recommendations
- Choose best approach

### Supported Operations

- **Reorganize**: Move files to suggested structure
- **Deduplicate**: Remove or consolidate duplicates
- **Cleanup**: Delete obsolete/temporary files
- **Archive**: Compress old/unused files
- **Categorize**: Auto-tag and organize by type

## 🔧 Development

### Backend

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8004
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

### Database Migrations

```bash
# Create migration
alembic revision --autogenerate -m "description"

# Apply
alembic upgrade head

# Rollback
alembic downgrade -1
```

### Testing

```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm test
```

## 🐳 Docker

### Build

```bash
docker-compose build
```

### Logs

```bash
docker-compose logs -f data-organizer-backend
docker-compose logs -f data-organizer-frontend
```

### Reset

```bash
docker-compose down -v
docker-compose up -d
```

## 📊 LLM Providers

### Ollama (Local)

**Pros:**
- Free, unlimited usage
- Privacy (data stays local)
- Fast response times
- Multiple models available

**Cons:**
- Limited reasoning for complex scenarios
- Requires GPU for best performance

**Configuration:**
```yaml
ollama:
  instances:
    - url: "http://spark.lmphq.net:11434"
      model: "qwen2.5:7b"
    - url: "http://crm.lmphq.net:11435"
      model: "qwen2.5:7b"
```

### Google Gemini (Cloud)

**Pros:**
- Excellent reasoning capabilities
- Google Search grounding
- Fast and reliable

**Cons:**
- API costs
- Internet dependency
- Data sent to Google

**Configuration:**
```yaml
gemini:
  api_key: "YOUR_API_KEY"
  model: "gemini-2.5-flash"
  grounding: true
```

## 🔐 Security

- **Sandboxed Operations**: File ops limited to mounted volumes
- **Dry-Run Default**: All destructive ops preview first
- **User Approval**: Explicit confirmation required
- **Rollback Support**: All changes can be undone
- **Audit Logging**: Complete operation history
- **No Auto-Delete**: Manual approval for deletions

## 📈 Monitoring

### Metrics

- Scan performance (files/second)
- LLM response times
- Recommendation accuracy
- User approval rates
- Execution success rates

### Integration

- Grafana dashboards
- Prometheus metrics
- Loki log aggregation

## 🚀 Production Deployment

### Target: spark.lmphq.net

```bash
# SSH to server
ssh spark.lmphq.net

# Clone repository
cd /opt/apps
git clone <repo-url> data-organizer

# Configure
cd data-organizer
cp backend/.env.example backend/.env
# Edit .env with production values

# Deploy
docker-compose -f docker-compose.prod.yml up -d

# Verify
curl http://localhost:8004/health
```

### URLs
- Backend: http://spark.lmphq.net:8004
- Frontend: http://spark.lmphq.net:3004

## 🛣️ Roadmap

- [x] Phase 1: Foundation (Project structure, Docker setup)
- [ ] Phase 2: Core Scanning (Filesystem analysis)
- [ ] Phase 3: LLM Analysis (Multi-model integration)
- [ ] Phase 4: Execution Engine (Safe file operations)
- [ ] Phase 5: Frontend (Web dashboard)
- [ ] Phase 6: Advanced (Scheduling, ML patterns)

## 📝 API Documentation

Full API documentation available at `/docs` endpoint when running.

### Key Endpoints

- `POST /api/scans` - Start new scan
- `GET /api/scans/{id}` - Get scan status
- `GET /api/scans/{id}/analysis` - Get LLM analysis
- `GET /api/scans/{id}/recommendations` - Get suggestions
- `POST /api/scans/{id}/execute` - Apply changes
- `POST /api/scans/{id}/rollback` - Undo changes

## 🤝 Contributing

This is an internal LMP HQ project.

## 📄 License

Proprietary - LMP HQ

## 🔗 Related Projects

- **LMP-CRM**: FastAPI + Next.js pattern reference
- **lmp-mcp**: Infrastructure management tools
- **Harry variants**: LLM integration examples
