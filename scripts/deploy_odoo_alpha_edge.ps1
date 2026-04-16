param(
    [string]$ApexHost = "frawo-tech.de",
    [string]$WwwHost = "www.frawo-tech.de",
    [int]$VMID = 220
)

$ErrorActionPreference = "Stop"

$proxmoxExec = Join-Path $PSScriptRoot "proxmox_windows_ssh_exec.ps1"

# Caddyfile for internal proxying
$caddyfile = @"
{
  auto_https off
}

http://$ApexHost, http://$WwwHost, http://caddy {
  reverse_proxy odoo_web_1:8069
}
"@

# Docker Compose for the Public Edge Alpha
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

$remote = @"
# Command to run inside the VM
VM_CMD="
mkdir -p /opt/homeserver2027/stacks/odoo && \
cd /opt/homeserver2027/stacks/odoo && \
echo '$caddyB64' | base64 -d > Caddyfile.alpha && \
echo '$overrideB64' | base64 -d > docker-compose.alpha.yml && \
/usr/bin/docker-compose -f docker-compose.alpha.yml up -d && \
sleep 10 && \
/usr/bin/docker-compose -f docker-compose.alpha.yml logs cloudflared-alpha | grep 'trycloudflare.com'
"

# Execute via qm guest exec
qm guest exec $VMID -- bash -c \"\$VM_CMD\"
"@

Write-Host "Restoring Alpha Public Edge via TryCloudflare on VM $VMID..." -ForegroundColor Cyan
& $proxmoxExec -RemoteCommand $remote
