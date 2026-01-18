# Deploy Data-Organizer to spark.lmphq.net
# Run from F:\AI-PROD\projects\Data-Organizer

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Data-Organizer Production Deployment" -ForegroundColor Cyan
Write-Host "  Target: filescan.spark.lmphq.net" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Configuration
$SERVER = "ubuntu@spark.lmphq.net"
$DEPLOY_PATH = "/opt/apps/data-organizer"
$CADDY_PATH = "/opt/ai-stack/infra/caddy"

Write-Host "Step 1: Creating deployment archive..." -ForegroundColor Yellow
tar -czf Data-Organizer-deploy.tar.gz `
    --exclude='.git' `
    --exclude='backend/venv' `
    --exclude='frontend/node_modules' `
    --exclude='backend/__pycache__' `
    --exclude='*.pyc' `
    .

Write-Host "✓ Archive created" -ForegroundColor Green

Write-Host "`nStep 2: Transferring to spark.lmphq.net..." -ForegroundColor Yellow
scp Data-Organizer-deploy.tar.gz ${SERVER}:/tmp/
Write-Host "✓ Transfer complete" -ForegroundColor Green

Write-Host "`nStep 3: Setting up on server..." -ForegroundColor Yellow
ssh $SERVER @"
set -e

echo 'Creating directory...'
sudo mkdir -p $DEPLOY_PATH
sudo chown ubuntu:ubuntu $DEPLOY_PATH

echo 'Extracting files...'
cd $DEPLOY_PATH
tar -xzf /tmp/Data-Organizer-deploy.tar.gz
rm /tmp/Data-Organizer-deploy.tar.gz

echo 'Creating data directories...'
sudo mkdir -p /opt/data/data-organizer/{postgres,redis}
sudo chown -R ubuntu:ubuntu /opt/data/data-organizer

echo '✓ Setup complete'
"@

Write-Host "✓ Server setup complete" -ForegroundColor Green

Write-Host "`nStep 4: Instructions for Caddy configuration..." -ForegroundColor Yellow
Write-Host ""
Write-Host "Manual steps required on spark.lmphq.net:" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. SSH to server:" -ForegroundColor White
Write-Host "   ssh ubuntu@spark.lmphq.net" -ForegroundColor Gray
Write-Host ""
Write-Host "2. Edit Caddy configuration:" -ForegroundColor White
Write-Host "   sudo nano $CADDY_PATH/Caddyfile" -ForegroundColor Gray
Write-Host ""
Write-Host "3. Add the Caddy block from:" -ForegroundColor White
Write-Host "   $DEPLOY_PATH/Caddyfile.snippet" -ForegroundColor Gray
Write-Host ""
Write-Host "4. Reload Caddy:" -ForegroundColor White
Write-Host "   sudo docker exec caddy caddy reload --config /etc/caddy/Caddyfile" -ForegroundColor Gray
Write-Host ""
Write-Host "5. Deploy containers:" -ForegroundColor White
Write-Host "   cd $DEPLOY_PATH" -ForegroundColor Gray
Write-Host "   docker-compose -f docker-compose.prod.yml up -d --build" -ForegroundColor Gray
Write-Host ""
Write-Host "6. Verify deployment:" -ForegroundColor White
Write-Host "   curl https://filescan.spark.lmphq.net/health" -ForegroundColor Gray
Write-Host ""

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  Files transferred successfully!" -ForegroundColor Cyan
Write-Host "  Continue deployment on server" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Clean up local archive
Remove-Item Data-Organizer-deploy.tar.gz
