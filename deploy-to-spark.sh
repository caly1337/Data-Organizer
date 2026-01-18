#!/bin/bash
# Deploy Data-Organizer to spark.lmphq.net

set -e

SERVER="ubuntu@spark.lmphq.net"
DEPLOY_PATH="/opt/apps/data-organizer"
CADDY_PATH="/opt/ai-stack/infra/caddy"

echo "========================================"
echo "  Data-Organizer Production Deployment"
echo "  Target: filescan.spark.lmphq.net"
echo "========================================"
echo ""

echo "Step 1: Creating deployment archive..."
tar -czf Data-Organizer-deploy.tar.gz \
    --exclude='.git' \
    --exclude='backend/venv' \
    --exclude='frontend/node_modules' \
    --exclude='backend/__pycache__' \
    --exclude='*.pyc' \
    .

echo "✓ Archive created"

echo ""
echo "Step 2: Transferring to spark.lmphq.net..."
scp Data-Organizer-deploy.tar.gz ${SERVER}:/tmp/
echo "✓ Transfer complete"

echo ""
echo "Step 3: Setting up on server..."
ssh $SERVER <<'ENDSSH'
set -e

echo 'Creating directory...'
sudo mkdir -p /opt/apps/data-organizer
sudo chown ubuntu:ubuntu /opt/apps/data-organizer

echo 'Extracting files...'
cd /opt/apps/data-organizer
tar -xzf /tmp/Data-Organizer-deploy.tar.gz
rm /tmp/Data-Organizer-deploy.tar.gz

echo 'Creating data directories...'
sudo mkdir -p /opt/data/data-organizer/{postgres,redis}
sudo chown -R ubuntu:ubuntu /opt/data/data-organizer

echo '✓ Setup complete'
ENDSSH

echo "✓ Server setup complete"

echo ""
echo "========================================"
echo "Manual steps required on spark.lmphq.net:"
echo "========================================"
echo ""
echo "1. SSH to server:"
echo "   ssh ubuntu@spark.lmphq.net"
echo ""
echo "2. Edit Caddy configuration:"
echo "   sudo nano $CADDY_PATH/Caddyfile"
echo ""
echo "3. Add the Caddy block from:"
echo "   cat $DEPLOY_PATH/Caddyfile.snippet"
echo ""
echo "4. Reload Caddy:"
echo "   sudo docker exec caddy caddy reload --config /etc/caddy/Caddyfile"
echo ""
echo "5. Configure environment:"
echo "   cd $DEPLOY_PATH"
echo "   cp backend/.env.example backend/.env.prod"
echo "   # Edit backend/.env.prod with production values"
echo ""
echo "6. Deploy containers:"
echo "   docker-compose -f docker-compose.prod.yml up -d --build"
echo ""
echo "7. Verify deployment:"
echo "   curl https://filescan.spark.lmphq.net/health"
echo ""
echo "========================================"
echo "  Files transferred successfully!"
echo "  Continue deployment on server"
echo "========================================"
echo ""

# Clean up
rm Data-Organizer-deploy.tar.gz
