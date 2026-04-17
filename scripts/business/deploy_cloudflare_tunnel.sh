#!/usr/bin/env bash
# =============================================================================
# deploy_cloudflare_tunnel.sh
# FraWo GbR – Permanenter Cloudflare-Tunnel für www.frawo-tech.de
# Target: VM 220 (Odoo) – Ubuntu/Debian
# =============================================================================
# VORAUSSETZUNGEN (manuell vor Ausführung):
#   1. In Cloudflare Dashboard:  Zero Trust → Tunnels → "Create Tunnel"
#      Name: "frawo-odoo-prod"  →  Token kopieren
#   2. DNS in Cloudflare setzen:
#      CNAME  www.frawo-tech.de  →  <tunnel-id>.cfargotunnel.com  (Proxied)
#      CNAME  frawo-tech.de      →  www.frawo-tech.de  (Redirect Rule)
#   3. Dieses Skript auf VM220 ausführen:
#      bash deploy_cloudflare_tunnel.sh <TUNNEL_TOKEN>
# =============================================================================

set -euo pipefail

TUNNEL_TOKEN="${1:-}"
ODOO_INTERNAL="http://odoo_web_1:8069"
STACKS_DIR="/opt/homeserver2027/stacks/odoo"

if [[ -z "$TUNNEL_TOKEN" ]]; then
  echo "FEHLER: Tunnel-Token fehlt."
  echo "Usage: $0 <CLOUDFLARE_TUNNEL_TOKEN>"
  echo ""
  echo "Token generieren: Cloudflare Dashboard → Zero Trust → Tunnels → 'frawo-odoo-prod' → Token"
  exit 1
fi

echo "=== FraWo GbR: Cloudflare Tunnel Deployment ==="

# ------------------------------------------------------------------
# 1. cloudflared installieren
# ------------------------------------------------------------------
echo "[1/4] Installiere cloudflared..."
if ! command -v cloudflared &> /dev/null; then
  curl -fsSL https://pkg.cloudflare.com/cloudflare-main.gpg | \
    gpg --dearmor -o /usr/share/keyrings/cloudflare-main.gpg
  echo "deb [signed-by=/usr/share/keyrings/cloudflare-main.gpg] https://pkg.cloudflare.com/cloudflared $(lsb_release -cs) main" \
    > /etc/apt/sources.list.d/cloudflared.list
  apt-get update -qq
  apt-get install -y cloudflared
  echo "  ✓ cloudflared installiert: $(cloudflared --version)"
else
  echo "  ✓ cloudflared bereits installiert: $(cloudflared --version)"
fi

# ------------------------------------------------------------------
# 2. Tunnel als systemd-Service einrichten
# ------------------------------------------------------------------
echo "[2/4] Richte cloudflared-Systemd-Service ein..."
cloudflared service install "$TUNNEL_TOKEN"
systemctl enable cloudflared
systemctl restart cloudflared
sleep 3
if systemctl is-active --quiet cloudflared; then
  echo "  ✓ cloudflared-Service läuft"
else
  echo "  ✗ cloudflared-Service FEHLER – Journal:"
  journalctl -u cloudflared -n 20 --no-pager
  exit 1
fi

# ------------------------------------------------------------------
# 3. Caddy Update: HTTP-only → Cloudflare-Proxy-aware
#    Caddy muss nur auf localhost lauschen, CF-Tunnel kümmert sich darum
# ------------------------------------------------------------------
echo "[3/4] Aktualisiere Caddyfile (Cloudflare-Proxy-Modus)..."
cat > "$STACKS_DIR/Caddyfile.public" << 'CADDYEOF'
{
  # Cloudflare Tunnel: Caddy läuft nur intern, kein ACME nötig
  auto_https off
  admin off
}

# Cloudflare-Tunnel sendet HTTP an Caddy (TLS endet bei Cloudflare)
# Caddy leitet an Odoo weiter und setzt X-Forwarded Headers
:80 {
  # Cloudflare-IP-Vertrauen (Real-IP-Header durchleiten)
  header_up X-Real-IP {remote_host}
  header_up X-Forwarded-Proto https

  # Security Headers
  header {
    Strict-Transport-Security "max-age=31536000; includeSubDomains"
    X-Content-Type-Options nosniff
    X-Frame-Options SAMEORIGIN
  }

  reverse_proxy odoo_web_1:8069 {
    header_up Host www.frawo-tech.de
    header_up X-Forwarded-For {remote_host}
    header_up X-Forwarded-Proto https
  }
}
CADDYEOF

# Caddy-Container neu laden (graceful)
docker exec caddy-edge caddy reload --config /etc/caddy/Caddyfile 2>/dev/null || \
  docker restart caddy-edge
sleep 2
echo "  ✓ Caddyfile aktualisiert und Caddy neu geladen"

# ------------------------------------------------------------------
# 4. Odoo web.base.url aktualisieren
# ------------------------------------------------------------------
echo "[4/4] Setze Odoo web.base.url auf https://www.frawo-tech.de..."
docker exec odoo_web_1 python3 - << 'PYEOF'
import xmlrpc.client, os

url = "http://localhost:8069"
db  = "FraWo_GbR"
pw   = open("/run/secrets/odoo_admin_pw", "r").read().strip() if os.path.exists("/run/secrets/odoo_admin_pw") else "OD-Wolf-2026!"

common = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/common", allow_none=True)
uid = common.authenticate(db, "admin", pw, {})
models = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/object", allow_none=True)

ids = models.execute_kw(db, uid, pw, "ir.config_parameter", "search",
                        [[["key", "=", "web.base.url"]]])
if ids:
    models.execute_kw(db, uid, pw, "ir.config_parameter", "write",
                      [ids, {"value": "https://www.frawo-tech.de"}])
    print("  ✓ web.base.url → https://www.frawo-tech.de")
else:
    models.execute_kw(db, uid, pw, "ir.config_parameter", "create",
                      [{"key": "web.base.url", "value": "https://www.frawo-tech.de"}])
    print("  ✓ web.base.url erstellt → https://www.frawo-tech.de")
PYEOF

echo ""
echo "============================================================"
echo "  FraWo GbR: Cloudflare Tunnel Deployment ABGESCHLOSSEN"
echo "============================================================"
echo ""
echo "  Tunnel-Status:  systemctl status cloudflared"
echo "  Caddy-Status:   docker logs caddy-edge --tail 20"
echo "  Odoo-Log:       docker logs odoo_web_1 --tail 20"
echo ""
echo "  Nächster Schritt: https://www.frawo-tech.de im Browser testen"
echo "  Cloudflare Dashboard: Zero Trust → Tunnels → Status prüfen"
echo ""
