#!/usr/bin/env bash
set -euo pipefail
sshpass -p 11011995 ssh -o StrictHostKeyChecking=no root@192.168.2.10 <<'SSH'
pct exec 120 -- bash -lc '
set -euo pipefail
export DEBIAN_FRONTEND=noninteractive
apt-get update
apt-get install -y docker.io docker-compose-v2 curl ca-certificates
mkdir -p /opt/homeserver2027/stacks/vaultwarden/data
cat > /opt/homeserver2027/stacks/vaultwarden/.env <<EOF
DOMAIN=http://192.168.2.26:8080
ROCKET_PORT=80
SIGNUPS_ALLOWED=true
ADMIN_TOKEN=6w3xUai9a-NzN47xo0St-1mQfhSX9kMf3BzNuUOVfu7gWEPXjSriCnHP9WtJF5jP
WEBSOCKET_ENABLED=true
LOG_FILE=/data/vaultwarden.log
EOF
chmod 600 /opt/homeserver2027/stacks/vaultwarden/.env
cat > /opt/homeserver2027/stacks/vaultwarden/docker-compose.yml <<'"'"'EOF'"'"'
services:
  vaultwarden:
    image: vaultwarden/server:latest-alpine
    container_name: vaultwarden
    restart: unless-stopped
    ports:
      - "8080:80"
    env_file:
      - .env
    volumes:
      - ./data:/data
EOF
systemctl enable --now docker
cd /opt/homeserver2027/stacks/vaultwarden
docker compose up -d
sleep 8
curl -fsS http://127.0.0.1:8080/alive
'
SSH