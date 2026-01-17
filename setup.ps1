# Data-Organizer Setup Script for Windows
# Run this script to set up the project

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Data-Organizer Setup" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if Docker is running
Write-Host "Checking Docker..." -ForegroundColor Yellow
try {
    docker info | Out-Null
    Write-Host "✓ Docker is running" -ForegroundColor Green
} catch {
    Write-Host "✗ Docker is not running. Please start Docker Desktop." -ForegroundColor Red
    exit 1
}

# Create environment files if they don't exist
Write-Host "`nSetting up environment files..." -ForegroundColor Yellow

if (-not (Test-Path "backend\.env")) {
    Copy-Item "backend\.env.example" "backend\.env"
    Write-Host "✓ Created backend/.env" -ForegroundColor Green
} else {
    Write-Host "✓ backend/.env already exists" -ForegroundColor Green
}

if (-not (Test-Path "frontend\.env")) {
    Copy-Item "frontend\.env.example" "frontend\.env"
    Write-Host "✓ Created frontend/.env" -ForegroundColor Green
} else {
    Write-Host "✓ frontend/.env already exists" -ForegroundColor Green
}

# Start database and redis
Write-Host "`nStarting database and Redis..." -ForegroundColor Yellow
docker-compose up -d data-organizer-db data-organizer-redis

Write-Host "Waiting for database to be ready (10 seconds)..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

# Check if backend requirements are installed
Write-Host "`nChecking Python dependencies..." -ForegroundColor Yellow
$pythonCheck = python --version 2>&1
if ($pythonCheck -match "Python 3") {
    Write-Host "✓ Python 3 found: $pythonCheck" -ForegroundColor Green

    # Install backend dependencies
    Write-Host "`nInstalling backend dependencies..." -ForegroundColor Yellow
    Set-Location backend

    if (Test-Path "venv") {
        Write-Host "✓ Virtual environment exists" -ForegroundColor Green
    } else {
        Write-Host "Creating virtual environment..." -ForegroundColor Yellow
        python -m venv venv
        Write-Host "✓ Virtual environment created" -ForegroundColor Green
    }

    # Activate venv and install
    Write-Host "Installing dependencies..." -ForegroundColor Yellow
    & .\venv\Scripts\Activate.ps1
    pip install -r requirements.txt

    # Run migrations
    Write-Host "`nRunning database migrations..." -ForegroundColor Yellow
    alembic upgrade head

    Set-Location ..
    Write-Host "✓ Backend setup complete" -ForegroundColor Green
} else {
    Write-Host "✗ Python 3 not found. Please install Python 3.11+" -ForegroundColor Red
}

# Start backend and frontend
Write-Host "`nStarting backend and frontend..." -ForegroundColor Yellow
docker-compose up -d data-organizer-backend data-organizer-frontend

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  Setup Complete!" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Services are starting up..." -ForegroundColor Green
Write-Host ""
Write-Host "Backend API:  http://localhost:8004" -ForegroundColor White
Write-Host "API Docs:     http://localhost:8004/docs" -ForegroundColor White
Write-Host "Frontend:     http://localhost:3004" -ForegroundColor White
Write-Host ""
Write-Host "To view logs:" -ForegroundColor Yellow
Write-Host "  docker-compose logs -f" -ForegroundColor White
Write-Host ""
Write-Host "To stop services:" -ForegroundColor Yellow
Write-Host "  docker-compose down" -ForegroundColor White
Write-Host ""
