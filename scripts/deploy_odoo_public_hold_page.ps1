param(
    [string]$ApexHost = "frawo-tech.de",
    [string]$WwwHost = "www.frawo-tech.de"
)

$ErrorActionPreference = "Stop"

$proxmoxExec = Join-Path $PSScriptRoot "proxmox_windows_ssh_exec.ps1"

$indexHtml = @"
<!doctype html>
<html lang="de">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>FraWo</title>
  <meta name="robots" content="noindex,nofollow">
  <style>
    :root {
      --bg: #0f172a;
      --panel: #16213c;
      --line: #2f4a7d;
      --text: #e8eefc;
      --muted: #aebbd9;
      --accent: #d6b16f;
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      min-height: 100vh;
      font-family: "Segoe UI", Arial, sans-serif;
      background:
        radial-gradient(circle at top left, rgba(214,177,111,.18), transparent 32rem),
        linear-gradient(180deg, #10192f 0%, var(--bg) 100%);
      color: var(--text);
      display: grid;
      place-items: center;
      padding: 2rem;
    }
    main {
      width: min(100%, 46rem);
      background: rgba(22, 33, 60, 0.9);
      border: 1px solid rgba(214,177,111,.22);
      border-radius: 24px;
      padding: 2.25rem;
      box-shadow: 0 24px 70px rgba(0,0,0,.35);
    }
    .eyebrow {
      display: inline-block;
      letter-spacing: .18em;
      text-transform: uppercase;
      font-size: .78rem;
      color: var(--accent);
      margin-bottom: 1rem;
    }
    h1 {
      margin: 0 0 1rem;
      font-size: clamp(2rem, 6vw, 3.4rem);
      line-height: 1.05;
    }
    p {
      margin: 0 0 1rem;
      color: var(--muted);
      font-size: 1.06rem;
      line-height: 1.6;
    }
    .box {
      margin-top: 1.5rem;
      padding: 1rem 1.1rem;
      border-radius: 16px;
      background: rgba(9, 15, 29, 0.55);
      border: 1px solid rgba(47, 74, 125, 0.75);
    }
    .meta {
      margin-top: 1.6rem;
      font-size: .95rem;
      color: var(--muted);
    }
    strong { color: var(--text); }
  </style>
</head>
<body>
  <main>
    <div class="eyebrow">FraWo</div>
    <h1>Oeffentliche Seite in Ueberarbeitung</h1>
    <p>Der oeffentliche Auftritt wird aktuell technisch und gestalterisch ueberarbeitet.</p>
    <p>Die internen Systeme laufen weiter. Die oeffentliche Freigabe folgt erst nach sauberer Design-, Inhalts- und Infrastrukturfreigabe.</p>
    <div class="box">
      <p><strong>Stand jetzt:</strong> Der oeffentliche Zugriff bleibt bewusst reduziert, bis CI, Inhalte, TLS und der finale Release-Pfad freigegeben sind.</p>
    </div>
    <div class="meta">FraWo GbR</div>
  </main>
</body>
</html>
"@

$caddyfile = @"
{
  auto_https disable_redirects
}

http://$ApexHost, http://$WwwHost {
  root * /srv/public-site
  header {
    Cache-Control "no-store, max-age=0"
  }
  file_server
}

https://$ApexHost, https://$WwwHost {
  root * /srv/public-site
  header {
    Cache-Control "no-store, max-age=0"
  }
  file_server
}
"@

$override = @"
version: "3"
services:
  caddy:
    image: caddy:2
    restart: unless-stopped
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./Caddyfile.public:/etc/caddy/Caddyfile:ro
      - ./public-site:/srv/public-site:ro
      - caddy-data:/data
      - caddy-config:/config

volumes:
  caddy-data:
  caddy-config:
"@

$indexB64 = [Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes($indexHtml))
$caddyB64 = [Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes($caddyfile))
$overrideB64 = [Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes($override))

$remote = @"
qm guest exec 220 -- bash -lc 'python3 - <<'"'"'PY'"'"'
from pathlib import Path
import base64
base = Path("/opt/homeserver2027/stacks/odoo")
(base / "public-site").mkdir(parents=True, exist_ok=True)
(base / "public-site" / "index.html").write_bytes(base64.b64decode("$indexB64"))
(base / "Caddyfile.public").write_bytes(base64.b64decode("$caddyB64"))
(base / "docker-compose.public-edge.yml").write_bytes(base64.b64decode("$overrideB64"))
PY
cd /opt/homeserver2027/stacks/odoo
docker-compose -f docker-compose.yml -f docker-compose.public-edge.yml up -d caddy
docker-compose -f docker-compose.yml -f docker-compose.public-edge.yml exec -T caddy caddy validate --config /etc/caddy/Caddyfile'
"@

& $proxmoxExec -RemoteCommand $remote
