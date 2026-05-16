# Deployment Guide - Anker PVE

Quick deployment guide for FraWo Radio Backend on Anker Proxmox Server.

## Resource Requirements

### Minimal Setup
- **CPU**: 2 cores
- **RAM**: 2 GB (1.5 GB for LXC, 512 MB overhead)
- **Disk**: 10 GB
- **Network**: 10.1.0.x/24 (Anker network)

### Recommended Setup
- **CPU**: 4 cores
- **RAM**: 4 GB
- **Disk**: 20 GB

## Quick Deployment

### Option 1: Automated Script (Recommended)

```bash
# From toolbox or Anker PVE host
cd /opt/frawo/apps/radio-backend/deployment
bash deploy-to-proxmox.sh
```

### Option 2: Manual Deployment

```bash
# 1. Create LXC Container on Anker PVE
pct create 105 local:vztmpl/debian-12-standard_12.2-1_amd64.tar.zst \
  --hostname radio-backend \
  --cores 2 \
  --memory 2048 \
  --rootfs local-lvm:10 \
  --net0 name=eth0,bridge=vmbr0,ip=dhcp \
  --features nesting=1 \
  --onboot 1

# 2. Start container
pct start 105

# 3. Enter container
pct enter 105

# 4. Install Docker
apt-get update
apt-get install -y curl git docker.io docker-compose
systemctl enable --now docker

# 5. Clone repository
cd /opt
git clone https://github.com/frawo-tech/frawo.git
cd frawo/apps/radio-backend

# 6. Configure environment
cp .env.example .env
nano .env  # Edit configuration

# 7. Deploy with minimal resources
docker-compose -f deployment/docker-compose.minimal.yml up -d

# 8. Run migrations
docker-compose exec backend alembic upgrade head

# 9. Check health
curl http://localhost:8000/health
```

## Post-Deployment

### 1. Configure Caddy Reverse Proxy

Add to toolbox Caddy config:

```bash
pct exec 100 -- nano /etc/caddy/Caddyfile
```

Add:
```
radio-api.hs27.internal {
    reverse_proxy http://10.1.0.105:8000
}
```

Reload:
```bash
pct exec 100 -- caddy reload --config /etc/caddy/Caddyfile
```

### 2. Test Access

```bash
curl http://radio-api.hs27.internal/health
curl http://radio-api.hs27.internal/docs
```

### 3. Configure AzuraCast Integration

Edit `.env` in container:
```bash
AZURACAST_API_URL=http://radio-anker.hs27.internal/api
AZURACAST_API_KEY=your-key-here
AZURACAST_STATION_ID=1
```

Restart:
```bash
docker-compose restart backend
```

## Management Commands

```bash
# View logs
pct exec 105 -- docker-compose logs -f backend

# Restart backend
pct exec 105 -- docker-compose restart backend

# Update code
pct exec 105 -- bash -c "cd /opt/frawo && git pull && cd apps/radio-backend && docker-compose restart backend"

# Database backup
pct exec 105 -- docker-compose exec postgres pg_dump -U radio frawo_radio > backup.sql

# Enter container
pct enter 105

# Stop services
pct exec 105 -- docker-compose down

# Remove container (full cleanup)
pct stop 105 && pct destroy 105
```

## Monitoring

- **API Health**: http://radio-api.hs27.internal/health
- **Metrics**: http://radio-api.hs27.internal/metrics
- **Docs**: http://radio-api.hs27.internal/docs
- **Logs**: `pct exec 105 -- docker-compose logs`

## Troubleshooting

### Container won't start
```bash
pct status 105
pct start 105
journalctl -xe
```

### Database connection issues
```bash
pct exec 105 -- docker-compose ps
pct exec 105 -- docker-compose logs postgres
```

### Out of memory
Use minimal compose file:
```bash
docker-compose -f deployment/docker-compose.minimal.yml up -d
```

### Network issues
Check container IP:
```bash
pct exec 105 -- hostname -I
```

## URLs

After deployment:

- **Internal API**: http://radio-api.hs27.internal
- **Direct Access**: http://10.1.0.105:8000
- **Docs**: http://radio-api.hs27.internal/docs
- **WebSocket**: ws://radio-api.hs27.internal/api/ws/{station_id}

## Integration Points

- **Frontend**: Update stream URLs to use radio-api.hs27.internal
- **AzuraCast**: Configure API credentials
- **Caddy**: Add reverse proxy rules
- **Monitoring**: Prometheus scraping on port 9090
