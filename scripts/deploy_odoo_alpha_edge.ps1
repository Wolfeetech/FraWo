param(
    [string]$ApexHost = "frawo-tech.de",
    [string]$WwwHost = "www.frawo-tech.de",
    [int]$VMID = 220
)

$ErrorActionPreference = "Stop"

$proxmoxExec = Join-Path $PSScriptRoot "proxmox_windows_ssh_exec.ps1"

# Create internal Caddyfile
$caddyfile = @"
{
  auto_https off
}

http://$ApexHost, http://$WwwHost, http://caddy {
  reverse_proxy odoo_web_1:8069
}
"@

# Create ephemeral Docker Compose
$composeOverride = @"
version: "3"
services:
  caddy-alpha:
    image: caddy:2
    restart: unless-stopped
    ports:
      - "8080:80"
    volumes:
      - ./Caddyfile.alpha:/etc/caddy/Caddyfile:ro
    networks:
      - odoo_default

  cloudflared-alpha:
    image: cloudflare/cloudflared:latest
    restart: unless-stopped
    command: tunnel --no-autoupdate --url http://caddy-alpha:80
    networks:
      - odoo_default

networks:
  odoo_default:
    external: true
"@

$caddyB64 = [Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes($caddyfile))
$overrideB64 = [Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes($composeOverride))

$remoteScript = @"
#!/bin/bash
set -e
# This runs on the Proxmox HOST
# We wrap the VM commands in a clean heredoc to avoid escaping hell

cat << 'EOF' > /tmp/vm_deploy.sh
mkdir -p /opt/homeserver2027/stacks/odoo
cd /opt/homeserver2027/stacks/odoo
echo "$caddyB64" | tr -d '\r' | base64 -d > Caddyfile.alpha
echo "$overrideB64" | tr -d '\r' | base64 -d > docker-compose.alpha.yml
docker network inspect odoo_default > /dev/null 2>&1 || docker network create odoo_default
/usr/bin/docker-compose -f docker-compose.alpha.yml up -d
sleep 15
/usr/bin/docker-compose -f docker-compose.alpha.yml logs cloudflared-alpha | grep "trycloudflare.com"
EOF

# Transfer script to VM and execute
qm guest exec $VMID -- bash -c "cat > /tmp/vm_deploy.sh" < /tmp/vm_deploy.sh
qm guest exec $VMID -- bash /tmp/vm_deploy.sh
"@

Write-Host "Restoring Alpha Public Edge via TryCloudflare on VM $VMID..." -ForegroundColor Cyan
& $proxmoxExec -RemoteCommand $remoteScript
