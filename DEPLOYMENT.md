# Deployment Guide

## Development Deployment (brani-pc)

### Quick Start

```bash
cd F:\AI-PROD\projects\Data-Organizer

# Run setup script
.\setup.ps1

# Or manual:
docker-compose up -d
```

### Access

- Backend: http://localhost:8004
- Frontend: http://localhost:3004
- Database: localhost:5435
- Redis: localhost:6380

## Production Deployment (spark.lmphq.net)

### Prerequisites

- SSH access to spark.lmphq.net
- Docker installed on server
- `ai-net` network exists
- Ollama running on spark.lmphq.net:11434

### Deployment Steps

#### 1. Prepare Server

```bash
# SSH to server
ssh spark.lmphq.net

# Create application directory
sudo mkdir -p /opt/apps/data-organizer
sudo chown $USER:$USER /opt/apps/data-organizer
cd /opt/apps/data-organizer

# Create data directories
sudo mkdir -p /opt/data/data-organizer/{postgres,redis}
sudo chown -R $USER:$USER /opt/data/data-organizer
```

#### 2. Transfer Files

From brani-pc:

```powershell
# Option A: Git clone (if repository is hosted)
ssh spark.lmphq.net "cd /opt/apps && git clone <repo-url> data-organizer"

# Option B: SCP transfer
scp -r F:\AI-PROD\projects\Data-Organizer/* spark.lmphq.net:/opt/apps/data-organizer/
```

#### 3. Configure Production Environment

```bash
# On spark.lmphq.net
cd /opt/apps/data-organizer

# Create production environment file
cat > backend/.env.prod <<EOF
# Application
DEBUG=false
API_PORT=8004

# Database
DATABASE_URL=postgresql://data_organizer:CHANGE_THIS_PASSWORD@data-organizer-db:5432/data_organizer

# Redis
REDIS_URL=redis://data-organizer-redis:6379/0

# Security (CHANGE THESE!)
SECRET_KEY=$(openssl rand -hex 32)

# LLM - Ollama (Local)
OLLAMA_ENABLED=true
OLLAMA_BASE_URL=http://spark.lmphq.net:11434
OLLAMA_DEFAULT_MODEL=qwen2.5:7b

# LLM - Gemini (Optional)
GEMINI_ENABLED=true
GEMINI_API_KEY=your_actual_gemini_api_key

# Production settings
LOG_LEVEL=INFO
ENABLE_METRICS=true
EOF

# Set secure permissions
chmod 600 backend/.env.prod
```

#### 4. Create External Network

```bash
# Check if ai-net exists
docker network ls | grep ai-net

# Create if doesn't exist
docker network create ai-net
```

#### 5. Deploy Services

```bash
cd /opt/apps/data-organizer

# Pull latest images (if using registry)
# docker-compose -f docker-compose.prod.yml pull

# Build and start services
docker-compose -f docker-compose.prod.yml up -d --build

# View logs
docker-compose -f docker-compose.prod.yml logs -f
```

#### 6. Initialize Database

```bash
# Wait for database to be ready
sleep 10

# Run migrations
docker exec -it data-organizer-backend alembic upgrade head
```

#### 7. Verify Deployment

```bash
# Check services are running
docker-compose -f docker-compose.prod.yml ps

# Test backend
curl http://localhost:8004/health

# Test from external
curl http://spark.lmphq.net:8004/health

# View API docs
# Open browser: http://spark.lmphq.net:8004/docs
```

#### 8. Configure Reverse Proxy (Optional)

##### Using Nginx

```nginx
# /etc/nginx/sites-available/data-organizer

server {
    listen 80;
    server_name organizer.lmphq.net;

    # Frontend
    location / {
        proxy_pass http://localhost:3004;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }

    # Backend API
    location /api {
        proxy_pass http://localhost:8004;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

Enable site:
```bash
sudo ln -s /etc/nginx/sites-available/data-organizer /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

##### Using Caddy

```caddyfile
# /etc/caddy/Caddyfile

organizer.lmphq.net {
    # Frontend
    reverse_proxy localhost:3004

    # Backend API
    handle /api/* {
        reverse_proxy localhost:8004
    }

    # Metrics
    handle /metrics {
        reverse_proxy localhost:8004
    }
}
```

Reload Caddy:
```bash
sudo systemctl reload caddy
```

### Monitoring Integration

#### Grafana Dashboard

```bash
# Import dashboard from docs/monitoring/grafana-dashboard.json
# (To be created in future phase)
```

#### Prometheus Metrics

The backend exposes metrics at `/metrics`:

```bash
curl http://spark.lmphq.net:8004/metrics
```

Add to Prometheus config:
```yaml
scrape_configs:
  - job_name: 'data-organizer'
    static_configs:
      - targets: ['spark.lmphq.net:8004']
```

## Updates and Maintenance

### Update Deployment

```bash
# On spark.lmphq.net
cd /opt/apps/data-organizer

# Pull latest changes
git pull

# Rebuild and restart
docker-compose -f docker-compose.prod.yml up -d --build

# Run any new migrations
docker exec -it data-organizer-backend alembic upgrade head
```

### Backup Database

```bash
# Backup
docker exec data-organizer-db pg_dump -U data_organizer data_organizer > backup.sql

# Restore
cat backup.sql | docker exec -i data-organizer-db psql -U data_organizer -d data_organizer
```

### View Logs

```bash
# All services
docker-compose -f docker-compose.prod.yml logs -f

# Specific service
docker-compose -f docker-compose.prod.yml logs -f data-organizer-backend

# Last 100 lines
docker-compose -f docker-compose.prod.yml logs --tail=100 data-organizer-backend
```

### Restart Services

```bash
# Restart all
docker-compose -f docker-compose.prod.yml restart

# Restart specific service
docker-compose -f docker-compose.prod.yml restart data-organizer-backend
```

### Health Checks

```bash
# Check all containers
docker-compose -f docker-compose.prod.yml ps

# Check backend health
curl http://localhost:8004/health

# Check database
docker exec data-organizer-db pg_isready -U data_organizer

# Check Redis
docker exec data-organizer-redis redis-cli ping
```

## Rollback Procedure

If deployment fails:

```bash
# Stop new version
docker-compose -f docker-compose.prod.yml down

# Restore previous database backup
cat backup.sql | docker exec -i data-organizer-db psql -U data_organizer

# Revert code
git checkout <previous-commit>

# Redeploy
docker-compose -f docker-compose.prod.yml up -d
```

## Security Considerations

### Production Checklist

- [ ] Change all default passwords
- [ ] Generate new SECRET_KEY
- [ ] Configure firewall rules
- [ ] Enable HTTPS/SSL
- [ ] Set up log rotation
- [ ] Configure backup automation
- [ ] Review file mount permissions
- [ ] Enable authentication (when implemented)
- [ ] Set up monitoring alerts
- [ ] Document incident response plan

### File System Access

The application has read-only access to mounted directories:
- `/opt/data` → `/mnt/data` (read-only)
- `/home` → `/mnt/home` (read-only)

Never mount writable directories without careful consideration.

## Troubleshooting

### Service Won't Start

```bash
# Check logs
docker-compose -f docker-compose.prod.yml logs <service-name>

# Check environment variables
docker exec <container> env | grep -i <var-name>

# Verify network
docker network inspect ai-net
```

### Database Connection Issues

```bash
# Test connection from backend container
docker exec -it data-organizer-backend ping data-organizer-db

# Test database login
docker exec -it data-organizer-db psql -U data_organizer -d data_organizer
```

### High Memory Usage

```bash
# Check resource usage
docker stats

# Adjust in docker-compose.prod.yml:
deploy:
  resources:
    limits:
      memory: 2G  # Adjust as needed
```

### Port Conflicts

```bash
# Check what's using a port
netstat -tuln | grep 8004

# Change port in docker-compose.prod.yml and .env
```

## Performance Tuning

### Database

```sql
-- Add indexes for common queries
CREATE INDEX idx_scans_status ON scans(status);
CREATE INDEX idx_files_category ON files(category);
CREATE INDEX idx_files_hash ON files(hash);
```

### Application

- Adjust worker processes in uvicorn
- Tune database connection pool
- Configure Redis memory limits
- Enable query caching

### Docker

```yaml
# In docker-compose.prod.yml
deploy:
  resources:
    limits:
      cpus: '4.0'    # Increase for better performance
      memory: 8G
```
