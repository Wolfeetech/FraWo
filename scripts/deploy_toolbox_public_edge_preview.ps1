param(
    [string]$HaIp = "10.1.0.24",
    [string]$OdooIp = "10.1.0.22:8069",
    [string]$RadioIp = "100.64.23.77:80",
    [string]$VaultIp = "10.1.0.26:8080"
)

$ErrorActionPreference = "Stop"

if ([string]::IsNullOrWhiteSpace($HaIp)) { throw "HaIp must not be empty." }
if ([string]::IsNullOrWhiteSpace($OdooIp)) { throw "OdooIp must not be empty." }
if ([string]::IsNullOrWhiteSpace($RadioIp)) { throw "RadioIp must not be empty." }
if ([string]::IsNullOrWhiteSpace($VaultIp)) { throw "VaultIp must not be empty." }

$proxmoxExec = Join-Path $PSScriptRoot "proxmox_windows_ssh_exec.ps1"

$caddyfile = @"
{
  auto_https disable_redirects
}

:80 {
  @health path /healthz
  respond @health 200
  respond "Homeserver 2027 toolbox network foundation active.`n" 200
}

http://media.hs27.internal {
  reverse_proxy 10.1.0.20:8096
}

http://cloud.hs27.internal {
  reverse_proxy 10.1.0.21:80
}

http://odoo.hs27.internal {
  @radio_root path /radio /radio/
  redir @radio_root /radio/public/frawo-funk 308
  handle_path /radio/* {
    reverse_proxy $RadioIp
  }
  reverse_proxy $OdooIp
}

http://paperless.hs27.internal {
  reverse_proxy 10.1.0.23:8000
}

http://ha.hs27.internal {
  reverse_proxy $HaIp:8123
}

http://radio.hs27.internal {
  reverse_proxy $RadioIp
}

https://vault.hs27.internal {
  tls internal
  reverse_proxy $VaultIp
}

http://portal.hs27.internal {
  root * /srv/portal
  header {
    Cache-Control "no-store, max-age=0"
  }
  file_server
}

http://frawo-tech.de, https://frawo-tech.de {
  redir https://www.frawo-tech.de{uri} 308
}

http://www.frawo-tech.de, https://www.frawo-tech.de {
  @radio_root path /radio /radio/
  redir @radio_root /radio/public/frawo-funk 308
  handle_path /radio/* {
    reverse_proxy $RadioIp
  }
  reverse_proxy $OdooIp
}

http://:8443 {
  reverse_proxy $HaIp:8123 {
    header_up Host ha.hs27.internal
  }
}

http://:8444 {
  reverse_proxy $OdooIp {
    header_up Host odoo.hs27.internal
  }
}

http://:8445 {
  reverse_proxy 10.1.0.21:80 {
    header_up Host cloud.hs27.internal
  }
}

http://:8446 {
  reverse_proxy 10.1.0.23:8000 {
    header_up Host paperless.hs27.internal
  }
}

http://:8447 {
  reverse_proxy 127.0.0.1:80 {
    header_up Host portal.hs27.internal
  }
}

http://:8448 {
  reverse_proxy $RadioIp {
    header_up Host radio.hs27.internal
  }
}

http://:8449 {
  reverse_proxy 10.1.0.20:8096 {
    header_up Host media.hs27.internal
  }
}

http://:8442 {
  reverse_proxy $VaultIp {
    header_up Host vault.hs27.internal
  }
}
"@

$encoded = [Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes($caddyfile))

$remote = @"
pct exec 100 -- bash -lc 'python3 - <<'"'"'PY'"'"'
from pathlib import Path
import base64
payload = base64.b64decode("$encoded").decode("utf-8")
Path("/opt/homeserver2027/stacks/toolbox-network/Caddyfile").write_text(payload, encoding="utf-8")
PY
cd /opt/homeserver2027/stacks/toolbox-network
docker-compose exec -T caddy caddy validate --config /etc/caddy/Caddyfile
systemctl restart homeserver-compose-toolbox-network.service'
"@

& $proxmoxExec -RemoteCommand $remote
