#!/usr/bin/env bash
set -euo pipefail

STACK_DIR="/opt/homeserver2027/stacks/toolbox-network"
CADDYFILE="${STACK_DIR}/Caddyfile"
ADGUARD="${STACK_DIR}/adguard/conf/AdGuardHome.yaml"
COMPOSE="${STACK_DIR}/docker-compose.yml"

python3 - <<'PY'
from pathlib import Path

caddy = Path('/opt/homeserver2027/stacks/toolbox-network/Caddyfile')
cfg = caddy.read_text()
block = """
https://vault.hs27.internal {
  tls internal
  reverse_proxy 192.168.2.26:8080
}
"""
if 'https://vault.hs27.internal' not in cfg:
    if not cfg.endswith('\n'):
        cfg += '\n'
    cfg += '\n' + block.strip() + '\n'
    caddy.write_text(cfg)

adguard = Path('/opt/homeserver2027/stacks/toolbox-network/adguard/conf/AdGuardHome.yaml')
text = adguard.read_text()
needle = "  - domain: vault.hs27.internal\n    answer: 192.168.2.20\n"
if 'domain: vault.hs27.internal' not in text:
    marker = "  - domain: radio.hs27.internal\n    answer: 192.168.2.20\n"
    if marker in text:
        text = text.replace(marker, marker + needle)
        adguard.write_text(text)

compose = Path('/opt/homeserver2027/stacks/toolbox-network/docker-compose.yml')
compose_text = compose.read_text()
port_line = '      - "443:443"\n'
marker = '      - "80:80"\n'
if port_line not in compose_text and marker in compose_text:
    compose_text = compose_text.replace(marker, marker + port_line, 1)
    compose.write_text(compose_text)
PY

systemctl restart homeserver-compose-toolbox-network.service
sleep 5
curl -kI --resolve vault.hs27.internal:443:127.0.0.1 https://vault.hs27.internal
curl -fsS http://192.168.2.26:8080/alive
