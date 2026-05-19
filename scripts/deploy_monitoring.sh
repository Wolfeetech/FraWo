# Create directory for Uptime Kuma
pct exec 100 -- bash -c "mkdir -p /opt/homeserver2027/stacks/monitoring"

# Create docker-compose.yml for Uptime Kuma
pct exec 100 -- bash -c "cat << 'EOF' > /opt/homeserver2027/stacks/monitoring/docker-compose.yml
version: '3.3'

services:
  uptime-kuma:
    image: louislam/uptime-kuma:1
    container_name: uptime-kuma
    volumes:
      - ./uptime-kuma-data:/app/data
    ports:
      - 3001:3001
    restart: always
EOF"

# Start Uptime Kuma
pct exec 100 -- bash -c "cd /opt/homeserver2027/stacks/monitoring && docker compose up -d"

# Update Caddyfile to add status.frawo-tech.de and status.hs27.internal
pct exec 100 -- bash -c "grep -q 'status.frawo-tech.de' /opt/homeserver2027/stacks/toolbox-network/Caddyfile || echo -e '\nstatus.frawo-tech.de, status.hs27.internal {\n    reverse_proxy 10.4.0.20:3001\n}\n' >> /opt/homeserver2027/stacks/toolbox-network/Caddyfile"

# Reload Caddy
pct exec 100 -- bash -c "cd /opt/homeserver2027/stacks/toolbox-network && docker compose exec -T caddy caddy reload -c /etc/caddy/Caddyfile"
