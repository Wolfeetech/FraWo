param(
    [string]$ApexHost = "frawo-tech.de",
    [string]$WwwHost = "www.frawo-tech.de",
    [string]$RadioUpstream = "192.168.2.20:80",
    [string]$InternalRadioHost = "radio.hs27.internal"
)

$ErrorActionPreference = "Stop"

$proxmoxExec = Join-Path $PSScriptRoot "proxmox_windows_ssh_exec.ps1"

$caddyfile = @"
{
  auto_https disable_redirects
}

http://$ApexHost, https://$ApexHost {
  redir https://$WwwHost{uri} 308
}

http://$WwwHost, https://$WwwHost {
  @radio_root path /radio /radio/
  redir @radio_root /radio/public/frawo-funk 308

  handle_path /radio/* {
    reverse_proxy $RadioUpstream {
      header_up Host $InternalRadioHost
    }
  }

  reverse_proxy web:8069
}
"@

$override = @"
version: "3"
services:
  caddy:
    image: caddy:2
    restart: unless-stopped
    depends_on:
      - web
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./Caddyfile.public:/etc/caddy/Caddyfile:ro
      - caddy-data:/data
      - caddy-config:/config

volumes:
  caddy-data:
  caddy-config:
"@

$caddyB64 = [Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes($caddyfile))
$overrideB64 = [Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes($override))

$remote = @"
qm guest exec 220 -- bash -lc 'python3 - <<'"'"'PY'"'"'
from pathlib import Path
import base64
Path("/opt/homeserver2027/stacks/odoo/Caddyfile.public").write_bytes(base64.b64decode("$caddyB64"))
Path("/opt/homeserver2027/stacks/odoo/docker-compose.public-edge.yml").write_bytes(base64.b64decode("$overrideB64"))
PY
cd /opt/homeserver2027/stacks/odoo
docker-compose -f docker-compose.yml -f docker-compose.public-edge.yml up -d caddy
docker-compose -f docker-compose.yml -f docker-compose.public-edge.yml exec -T caddy caddy validate --config /etc/caddy/Caddyfile'
"@

& $proxmoxExec -RemoteCommand $remote
