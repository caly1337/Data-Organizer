# Production Deployment to spark.lmphq.net

**Domain:** filescan.spark.lmphq.net
**Date:** 2026-01-18
**Status:** Ready to Deploy

## Prerequisites

- SSH access to spark.lmphq.net
- Caddy running at /opt/ai-stack/infra/caddy
- Docker network: ai-net

## Deployment Steps

### 1. Transfer Files to Server

From brani-pc:

```powershell
# Create tar archive
cd F:\AI-PROD\projects
tar -czf Data-Organizer.tar.gz Data-Organizer/

# Transfer to server
scp Data-Organizer.tar.gz ubuntu@spark.lmphq.net:/tmp/

# Or use rsync
rsync -avz Data-Organizer/ ubuntu@spark.lmphq.net:/opt/apps/data-organizer/
```

### 2. SSH to Server and Setup

```bash
ssh ubuntu@spark.lmphq.net

# Create directory
sudo mkdir -p /opt/apps/data-organizer
sudo chown ubuntu:ubuntu /opt/apps/data-organizer

# Extract if using tar
cd /opt/apps
tar -xzf /tmp/Data-Organizer.tar.gz

# Or if using rsync, files are already there
cd /opt/apps/data-organizer
```

### 3. Configure Production Environment

```bash
cd /opt/apps/data-organizer

# Create production .env
cat > backend/.env.prod <<EOF
# Application
DEBUG=false
API_PORT=8004
API_HOST=0.0.0.0

# Database
DATABASE_URL=postgresql://data_organizer:$(openssl rand -hex 16)@data-organizer-db:5432/data_organizer

# Redis
REDIS_URL=redis://data-organizer-redis:6379/0

# Security
SECRET_KEY=$(openssl rand -hex 32)
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# LLM Providers - Ollama
OLLAMA_ENABLED=true
OLLAMA_BASE_URL=http://spark.lmphq.net:11434
OLLAMA_SECONDARY_URL=http://localhost:11434
OLLAMA_DEFAULT_MODEL=qwen2.5:latest
OLLAMA_TIMEOUT=120

# LLM Providers - Gemini
GEMINI_ENABLED=true
GEMINI_API_KEY=AIzaSyDeZz5tIiZVn1J5swKdZri8eUEGOPWmOys
GEMINI_DEFAULT_MODEL=gemini-2.5-flash
GEMINI_GROUNDING=true
GEMINI_MAX_TOKENS=8192

# LLM Providers - Claude (Optional)
CLAUDE_ENABLED=false
CLAUDE_API_KEY=your_claude_api_key_here
CLAUDE_DEFAULT_MODEL=claude-sonnet-4.5
CLAUDE_MAX_TOKENS=8192

# File Scanning
MAX_SCAN_DEPTH=10
MAX_FILES_PER_SCAN=100000
SCAN_TIMEOUT=3600
HASH_ALGORITHM=xxhash

# Analysis
DEFAULT_ANALYSIS_MODE=fast
MAX_CONCURRENT_ANALYSES=3
ANALYSIS_TIMEOUT=300

# Execution
DRY_RUN_DEFAULT=true
REQUIRE_APPROVAL=true
ENABLE_ROLLBACK=true
MAX_BATCH_SIZE=1000

# Monitoring
ENABLE_METRICS=true
PROMETHEUS_PORT=9090

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json
EOF

# Secure the file
chmod 600 backend/.env.prod

# Create frontend env
cat > frontend/.env.prod <<EOF
NEXT_PUBLIC_API_URL=https://filescan.spark.lmphq.net
NEXT_PUBLIC_APP_NAME=Data-Organizer
NEXT_PUBLIC_APP_VERSION=0.2.0
EOF
```

### 4. Create Data Directories

```bash
sudo mkdir -p /opt/data/data-organizer/{postgres,redis}
sudo chown -R ubuntu:ubuntu /opt/data/data-organizer
```

### 5. Configure Caddy Reverse Proxy

```bash
# Edit Caddy configuration
sudo nano /opt/ai-stack/infra/caddy/Caddyfile

# Add this block inside the main *.spark.lmphq.net, *.lmphq.net { } block:
```

**Add to Caddyfile:**

```caddyfile
# Inside the main wildcard block *.spark.lmphq.net, *.lmphq.net { }

# Data-Organizer
@filescan host filescan.spark.lmphq.net filescan.lmphq.net
handle @filescan {
    # API routes
    handle /api/* {
        reverse_proxy data-organizer-backend:8004
    }

    handle /ws/* {
        reverse_proxy data-organizer-backend:8004
    }

    handle /docs* {
        reverse_proxy data-organizer-backend:8004
    }

    handle /metrics {
        reverse_proxy data-organizer-backend:8004
    }

    # Frontend (Next.js)
    handle {
        reverse_proxy data-organizer-frontend:3000
    }

    header {
        Access-Control-Allow-Origin *
        Access-Control-Allow-Methods "GET, POST, PUT, DELETE, OPTIONS"
        Access-Control-Allow-Headers "Authorization, Content-Type"
    }
}
```

**Or if using standalone block style:**

```caddyfile
# Add this as a separate block (outside the wildcard)

filescan.spark.lmphq.net, filescan.lmphq.net {
    # API routes
    handle /api/* {
        reverse_proxy data-organizer-backend:8004
    }

    handle /ws/* {
        reverse_proxy data-organizer-backend:8004
    }

    handle /docs* {
        reverse_proxy data-organizer-backend:8004
    }

    handle /metrics {
        reverse_proxy data-organizer-backend:8004
    }

    # Frontend (Next.js)
    handle {
        reverse_proxy data-organizer-frontend:3000
    }

    header {
        Access-Control-Allow-Origin *
        Access-Control-Allow-Methods "GET, POST, PUT, DELETE, OPTIONS"
        Access-Control-Allow-Headers "Authorization, Content-Type"
    }

    log {
        output file /var/log/caddy/filescan.log
    }
}
```

### 6. Reload Caddy

```bash
# Test configuration
sudo docker exec caddy caddy validate --config /etc/caddy/Caddyfile

# Reload Caddy
sudo docker exec caddy caddy reload --config /etc/caddy/Caddyfile
```

### 7. Deploy Application

```bash
cd /opt/apps/data-organizer

# Use production docker-compose
docker-compose -f docker-compose.prod.yml up -d --build

# Check logs
docker-compose -f docker-compose.prod.yml logs -f
```

### 8. Verify Deployment

```bash
# Check containers
docker-compose -f docker-compose.prod.yml ps

# Test backend
curl http://localhost:8004/health

# Test through Caddy
curl https://filescan.spark.lmphq.net/api/scans/

# Check frontend
curl https://filescan.spark.lmphq.net/
```

### 9. DNS Configuration (if needed)

If filescan.spark.lmphq.net doesn't resolve:

```bash
# Add DNS record or update /etc/hosts on client machines
192.168.2.150  filescan.spark.lmphq.net
```

## Configuration Updates

### Update CORS for Production

The backend .env.prod already configured with proper CORS.

### Update Frontend API URL

Frontend .env.prod points to:
```
NEXT_PUBLIC_API_URL=https://filescan.spark.lmphq.net
```

## Post-Deployment

### Monitor Logs

```bash
# Caddy logs
sudo tail -f /var/log/caddy/filescan.log

# Application logs
docker-compose -f docker-compose.prod.yml logs -f data-organizer-backend
docker-compose -f docker-compose.prod.yml logs -f data-organizer-frontend
```

### Health Checks

```bash
# Backend health
curl https://filescan.spark.lmphq.net/api/scans/

# Frontend
curl https://filescan.spark.lmphq.net/
```

## Rollback

If deployment fails:

```bash
cd /opt/apps/data-organizer
docker-compose -f docker-compose.prod.yml down
# Fix issues
docker-compose -f docker-compose.prod.yml up -d
```

## Quick Commands

```bash
# View all Data-Organizer containers
docker ps | grep data-organizer

# Restart backend
docker-compose -f docker-compose.prod.yml restart data-organizer-backend

# View logs
docker-compose -f docker-compose.prod.yml logs -f

# Stop all
docker-compose -f docker-compose.prod.yml down

# Rebuild and restart
docker-compose -f docker-compose.prod.yml up -d --build
```

## Accessing the Application

Once deployed:

- **Frontend:** https://filescan.spark.lmphq.net
- **API Docs:** https://filescan.spark.lmphq.net/docs
- **Backend API:** https://filescan.spark.lmphq.net/api/

## Security Notes

- Database password generated securely (in .env.prod)
- Secret key generated securely
- File mounts are read-only
- HTTPS handled by Caddy
- Logs stored in /var/log/caddy/

## Maintenance

### Backup Database

```bash
docker exec data-organizer-db pg_dump -U data_organizer data_organizer > backup-$(date +%Y%m%d).sql
```

### Update Application

```bash
cd /opt/apps/data-organizer
git pull origin main
docker-compose -f docker-compose.prod.yml up -d --build
```

### Check Resource Usage

```bash
docker stats data-organizer-backend data-organizer-frontend
```
