#!/bin/bash
# Deploy FraWo Radio Backend to Proxmox LXC Container on Anker PVE

set -e

# Configuration
PVE_HOST="100.69.179.87"
PVE_USER="root"
CT_ID="105"
CT_NAME="radio-backend"
GIT_REPO="https://github.com/Wolfeetech/FraWo.git"
DEPLOY_PATH="/opt/radio-backend"

echo "====================================="
echo "FraWo Radio Backend Deployment"
echo "====================================="
echo "Target: Anker PVE ($PVE_HOST)"
echo "Container ID: $CT_ID"
echo ""

# Check if running on correct host
if [ "$HOSTNAME" != "toolbox" ]; then
    echo "⚠️  This script should be run from toolbox CT or via SSH"
    echo "Run: ssh root@$PVE_HOST 'bash -s' < deploy-to-proxmox.sh"
    exit 1
fi

# Step 1: Create LXC Container (if not exists)
echo "📦 Step 1: Checking if container exists..."
if pct status $CT_ID >/dev/null 2>&1; then
    echo "✅ Container $CT_ID already exists"
else
    echo "🔨 Creating new LXC container..."
    pct create $CT_ID \
        local:vztmpl/debian-12-standard_12.2-1_amd64.tar.zst \
        --hostname $CT_NAME \
        --cores 2 \
        --memory 2048 \
        --swap 512 \
        --rootfs local-lvm:10 \
        --net0 name=eth0,bridge=vmbr0,ip=dhcp \
        --features nesting=1,keyctl=1 \
        --onboot 1 \
        --unprivileged 1

    echo "✅ Container created"
fi

# Step 2: Start container
echo ""
echo "🚀 Step 2: Starting container..."
pct start $CT_ID 2>/dev/null || echo "Container already running"
sleep 5

# Step 3: Install dependencies
echo ""
echo "📦 Step 3: Installing dependencies..."
pct exec $CT_ID -- bash -c "
    set -e
    apt-get update
    apt-get install -y curl git docker.io python3-pip
    systemctl enable docker
    systemctl start docker

    # Install Docker Compose v2 plugin
    DOCKER_COMPOSE_VERSION=v2.29.2
    curl -fsSL "https://github.com/docker/compose/releases/download/\${DOCKER_COMPOSE_VERSION}/docker-compose-linux-x86_64" \
        -o /usr/local/lib/docker/cli-plugins/docker-compose
    chmod +x /usr/local/lib/docker/cli-plugins/docker-compose
    ln -sf /usr/local/lib/docker/cli-plugins/docker-compose /usr/local/bin/docker-compose
"

echo "✅ Dependencies installed"

# Step 4: Clone repository
echo ""
echo "📥 Step 4: Cloning repository..."
pct exec $CT_ID -- bash -c "
    set -e
    rm -rf $DEPLOY_PATH
    git clone $GIT_REPO $DEPLOY_PATH
    cd $DEPLOY_PATH/apps/radio-backend
"

echo "✅ Repository cloned"

# Step 5: Configure environment
echo ""
echo "⚙️  Step 5: Configuring environment..."
pct exec $CT_ID -- bash -c "
    set -e
    cd $DEPLOY_PATH/apps/radio-backend

    # Copy environment file
    cp .env.example .env

    # Generate secret key
    SECRET_KEY=\$(openssl rand -hex 32)

    # Update .env with production values
    sed -i 's/^APP_ENV=.*/APP_ENV=production/' .env
    sed -i 's/^DEBUG=.*/DEBUG=false/' .env
    sed -i \"s|^SECRET_KEY=.*|SECRET_KEY=\$SECRET_KEY|\" .env
    sed -i 's|^DATABASE_URL=.*|DATABASE_URL=postgresql+asyncpg://radio:radio@postgres:5432/frawo_radio|' .env
    sed -i 's|^REDIS_URL=.*|REDIS_URL=redis://redis:6379/0|' .env

    echo '✅ Environment configured'
"

# Step 6: Build and start services
echo ""
echo "🐳 Step 6: Building and starting Docker services..."
pct exec $CT_ID -- bash -c "
    set -e
    cd $DEPLOY_PATH/apps/radio-backend

    docker-compose down 2>/dev/null || true
    docker-compose build
    docker-compose up -d

    echo 'Waiting for services to start...'
    sleep 10

    # Run migrations
    docker-compose exec -T backend alembic upgrade head
"

echo "✅ Services started"

# Step 7: Health check
echo ""
echo "🏥 Step 7: Health check..."
CT_IP=$(pct exec $CT_ID -- hostname -I | awk '{print $1}')
echo "Container IP: $CT_IP"

sleep 5

if curl -f http://$CT_IP:8000/health >/dev/null 2>&1; then
    echo "✅ Health check passed!"
else
    echo "⚠️  Health check failed. Check logs:"
    echo "   pct exec $CT_ID -- docker-compose -f $DEPLOY_PATH/apps/radio-backend/docker-compose.yml logs"
fi

# Step 8: Display info
echo ""
echo "====================================="
echo "✅ Deployment Complete!"
echo "====================================="
echo ""
echo "Container ID: $CT_ID"
echo "Container IP: $CT_IP"
echo "API Endpoint: http://$CT_IP:8000"
echo "API Docs: http://$CT_IP:8000/docs"
echo "Metrics: http://$CT_IP:9090/metrics"
echo ""
echo "Next steps:"
echo "1. Configure Caddy reverse proxy for radio-api.hs27.internal"
echo "2. Set up proper database credentials"
echo "3. Configure AzuraCast integration"
echo ""
echo "Useful commands:"
echo "  pct enter $CT_ID                                      # Enter container"
echo "  pct exec $CT_ID -- docker-compose logs -f backend     # View logs"
echo "  pct exec $CT_ID -- docker-compose restart backend     # Restart backend"
echo ""
