# Development Guide

## Development Environment Setup

### Prerequisites

- Python 3.11+
- Node.js 20+
- Docker & Docker Compose
- Git

### Initial Setup

```bash
# Clone (if from remote) or navigate to project
cd F:\AI-PROD\projects\Data-Organizer

# Run setup script
# Windows:
.\setup.ps1

# Linux/Mac:
chmod +x setup.sh
./setup.sh
```

## Backend Development

### Local Development (without Docker)

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate
# Windows:
.\venv\Scripts\Activate.ps1
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Setup database (ensure PostgreSQL is running)
# Update .env with local DATABASE_URL
alembic upgrade head

# Run development server
uvicorn app.main:app --reload --port 8004
```

### Database Migrations

```bash
cd backend

# Create new migration
alembic revision --autogenerate -m "Add new table"

# Review migration file in alembic/versions/

# Apply migration
alembic upgrade head

# Rollback one migration
alembic downgrade -1

# View current version
alembic current

# View history
alembic history
```

### Testing

```bash
cd backend

# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_scanner.py

# Run with verbose output
pytest -v
```

### Code Quality

```bash
# Format code
black app/

# Lint code
flake8 app/

# Type checking
mypy app/
```

## Frontend Development

### Local Development

```bash
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev

# Access at http://localhost:3004
```

### Building

```bash
# Production build
npm run build

# Start production server
npm start

# Type check
npm run type-check

# Lint
npm run lint
```

## Docker Development

### Building Images

```bash
# Build all services
docker-compose build

# Build specific service
docker-compose build data-organizer-backend

# Rebuild without cache
docker-compose build --no-cache
```

### Managing Services

```bash
# Start all services
docker-compose up -d

# Start specific service
docker-compose up -d data-organizer-backend

# View logs
docker-compose logs -f
docker-compose logs -f data-organizer-backend

# Restart service
docker-compose restart data-organizer-backend

# Stop all services
docker-compose down

# Stop and remove volumes
docker-compose down -v
```

### Debugging in Docker

```bash
# Execute command in running container
docker exec -it data-organizer-backend bash

# View real-time logs
docker-compose logs -f data-organizer-backend

# Inspect container
docker inspect data-organizer-backend

# Check resource usage
docker stats data-organizer-backend
```

## Project Structure

```
Data-Organizer/
├── backend/                    # FastAPI backend
│   ├── alembic/               # Database migrations
│   │   ├── versions/          # Migration files
│   │   └── env.py             # Migration environment
│   ├── app/
│   │   ├── api/               # API endpoints
│   │   │   ├── scans.py       # Scan endpoints
│   │   │   └── analysis.py    # Analysis endpoints
│   │   ├── core/              # Core configuration
│   │   │   └── config.py      # Settings management
│   │   ├── models/            # SQLAlchemy models
│   │   │   ├── scan.py        # Scan & File models
│   │   │   ├── analysis.py    # Analysis model
│   │   │   ├── recommendation.py
│   │   │   ├── execution.py
│   │   │   └── llm_provider.py
│   │   ├── schemas/           # Pydantic schemas
│   │   │   ├── scan.py
│   │   │   └── analysis.py
│   │   ├── services/          # Business logic
│   │   │   ├── llm_service.py      # Multi-provider LLM
│   │   │   ├── file_scanner.py     # Filesystem scanning
│   │   │   └── analyzer.py         # LLM analysis
│   │   ├── database.py        # Database setup
│   │   └── main.py            # FastAPI app
│   ├── tests/                 # Test suite
│   ├── .env.example           # Environment template
│   ├── Dockerfile             # Docker image
│   └── requirements.txt       # Python dependencies
├── frontend/                   # Next.js frontend
│   ├── src/
│   │   ├── app/               # Next.js 14 app directory
│   │   ├── components/        # React components
│   │   └── lib/               # Utilities
│   ├── .env.example
│   ├── Dockerfile
│   ├── package.json
│   └── tsconfig.json
├── docs/                       # Documentation
│   ├── plans/                 # Design documents
│   ├── API.md                 # API documentation
│   └── DEVELOPMENT.md         # This file
├── docker-compose.yml          # Docker Compose config
├── setup.ps1                   # Windows setup script
├── setup.sh                    # Linux/Mac setup script
├── README.md                   # Main documentation
├── QUICKSTART.md              # Quick start guide
└── PROJECT-DEFINITION.md       # Project overview
```

## Adding New Features

### 1. Add Database Model

```python
# backend/app/models/new_model.py
from sqlalchemy import Column, Integer, String
from app.database import Base

class NewModel(Base):
    __tablename__ = "new_table"
    id = Column(Integer, primary_key=True)
    name = Column(String(100))
```

### 2. Create Migration

```bash
cd backend
alembic revision --autogenerate -m "Add new_table"
alembic upgrade head
```

### 3. Add Pydantic Schema

```python
# backend/app/schemas/new_schema.py
from pydantic import BaseModel

class NewModelCreate(BaseModel):
    name: str

class NewModelResponse(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True
```

### 4. Create API Endpoint

```python
# backend/app/api/new_endpoint.py
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db

router = APIRouter()

@router.post("/")
async def create_item(db: AsyncSession = Depends(get_db)):
    # Implementation
    pass
```

### 5. Register Router

```python
# backend/app/main.py
from app.api import new_endpoint
app.include_router(new_endpoint.router, prefix="/api/items", tags=["items"])
```

## LLM Provider Development

### Adding New Provider

```python
# backend/app/services/llm_service.py
class NewProvider(BaseLLMProvider):
    def __init__(self):
        super().__init__()
        self.provider_name = "new_provider"

    async def generate(self, prompt: str, **kwargs) -> Dict[str, Any]:
        # Implementation
        return {
            "response": "...",
            "model": "model-name",
            "provider": self.provider_name,
            "duration": 0.0,
            "tokens_used": 0,
            "cost": 0.0
        }
```

Register in `LLMService.__init__()`:
```python
if settings.NEW_PROVIDER_ENABLED:
    self.providers["new_provider"] = NewProvider()
```

## Troubleshooting

### Database Issues

```bash
# Reset database
docker-compose down -v
docker-compose up -d data-organizer-db
cd backend
alembic upgrade head
```

### Backend Won't Start

```bash
# Check logs
docker-compose logs data-organizer-backend

# Check environment
cat backend/.env

# Verify database connection
docker exec -it data-organizer-db psql -U data_organizer -d data_organizer
```

### Frontend Build Errors

```bash
# Clear cache
cd frontend
rm -rf .next node_modules
npm install
npm run build
```

### Port Conflicts

```bash
# Check what's using the port
# Windows:
netstat -ano | findstr :8004

# Linux:
lsof -i :8004

# Change port in .env and docker-compose.yml
```

## Performance Optimization

### Database

- Add indexes for frequently queried columns
- Use connection pooling (configured in config.py)
- Batch insert for large datasets
- Use EXPLAIN ANALYZE for slow queries

### File Scanning

- Adjust `max_depth` to limit recursion
- Use `include_hidden=false` to skip hidden files
- Enable hashing only for files < 100MB
- Increase `ThreadPoolExecutor` workers for faster hashing

### LLM Calls

- Use Ollama for fast, frequent analyses
- Reserve Gemini for complex, deep analyses
- Cache analysis results
- Batch similar analyses together

## Contributing Guidelines

1. Create feature branch from `master`
2. Follow existing code style (Black, Flake8)
3. Add tests for new features
4. Update documentation
5. Submit PR with clear description

## Useful Commands

```bash
# Full restart
docker-compose down && docker-compose up -d

# Rebuild and restart
docker-compose up -d --build

# View all logs
docker-compose logs -f

# Database console
docker exec -it data-organizer-db psql -U data_organizer -d data_organizer

# Redis console
docker exec -it data-organizer-redis redis-cli

# Backend shell
docker exec -it data-organizer-backend bash

# Check disk usage
docker system df
```
