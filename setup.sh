#!/bin/bash
# Data-Organizer Setup Script for Linux/Mac

set -e

echo "========================================"
echo "  Data-Organizer Setup"
echo "========================================"
echo ""

# Check if Docker is running
echo "Checking Docker..."
if docker info > /dev/null 2>&1; then
    echo "✓ Docker is running"
else
    echo "✗ Docker is not running. Please start Docker."
    exit 1
fi

# Create environment files
echo ""
echo "Setting up environment files..."

if [ ! -f "backend/.env" ]; then
    cp backend/.env.example backend/.env
    echo "✓ Created backend/.env"
else
    echo "✓ backend/.env already exists"
fi

if [ ! -f "frontend/.env" ]; then
    cp frontend/.env.example frontend/.env
    echo "✓ Created frontend/.env"
else
    echo "✓ frontend/.env already exists"
fi

# Start database and redis
echo ""
echo "Starting database and Redis..."
docker-compose up -d data-organizer-db data-organizer-redis

echo "Waiting for database to be ready (10 seconds)..."
sleep 10

# Check Python
echo ""
echo "Checking Python dependencies..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    echo "✓ Python found: $PYTHON_VERSION"

    # Install backend dependencies
    echo ""
    echo "Installing backend dependencies..."
    cd backend

    if [ ! -d "venv" ]; then
        echo "Creating virtual environment..."
        python3 -m venv venv
        echo "✓ Virtual environment created"
    else
        echo "✓ Virtual environment exists"
    fi

    # Activate and install
    source venv/bin/activate
    pip install -r requirements.txt

    # Run migrations
    echo ""
    echo "Running database migrations..."
    alembic upgrade head

    cd ..
    echo "✓ Backend setup complete"
else
    echo "✗ Python 3 not found. Please install Python 3.11+"
fi

# Start backend and frontend
echo ""
echo "Starting backend and frontend..."
docker-compose up -d data-organizer-backend data-organizer-frontend

echo ""
echo "========================================"
echo "  Setup Complete!"
echo "========================================"
echo ""
echo "Services are starting up..."
echo ""
echo "Backend API:  http://localhost:8004"
echo "API Docs:     http://localhost:8004/docs"
echo "Frontend:     http://localhost:3004"
echo ""
echo "To view logs:"
echo "  docker-compose logs -f"
echo ""
echo "To stop services:"
echo "  docker-compose down"
echo ""
