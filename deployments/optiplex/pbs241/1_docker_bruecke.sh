#!/bin/bash
# 🤖 [Claude] 24.09.2026 — Docker-FORWARD-DROP: Ausnahme nur fuer die Firewall-Bruecke von VM241 (PBS). Freigabe Wolf 24.09.2026
set -euo pipefail
U=/etc/systemd/system/frawo-docker-bruecke.service
cp "$U" "$U.bak-20260924"
cat > "$U" <<'EOF'
[Unit]
Description=FraWo: Docker soll durchgereichten Verkehr auf vmbr0 (CT102 AdGuard) und fwbr241i0 (VM241 PBS) nicht verwerfen - Freigabe Wolf 22.09./24.09.2026, Claude
After=docker.service
PartOf=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
ExecStart=/bin/sh -c 'iptables -C DOCKER-USER -i vmbr0 -o vmbr0 -j ACCEPT 2>/dev/null || iptables -I DOCKER-USER -i vmbr0 -o vmbr0 -j ACCEPT'
ExecStart=/bin/sh -c 'iptables -C DOCKER-USER -i fwbr241i0 -o fwbr241i0 -j ACCEPT 2>/dev/null || iptables -I DOCKER-USER -i fwbr241i0 -o fwbr241i0 -j ACCEPT'
ExecStop=/bin/sh -c 'iptables -D DOCKER-USER -i vmbr0 -o vmbr0 -j ACCEPT 2>/dev/null || true'
ExecStop=/bin/sh -c 'iptables -D DOCKER-USER -i fwbr241i0 -o fwbr241i0 -j ACCEPT 2>/dev/null || true'

[Install]
WantedBy=multi-user.target docker.service
EOF
systemctl daemon-reload
systemctl restart frawo-docker-bruecke.service
iptables -S DOCKER-USER
