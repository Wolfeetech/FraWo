#!/bin/bash
# Sichert die Konfiguration des OptiPlex 7050 auf den Proxmox Backup Server (PBS).
# Angelegt 18.09.2026 (Task #1470).
#
# Gesichert wird, was nicht reproduzierbar ist:
# - /etc/network (Netzwerkkonfiguration)
# - /etc/pve/firewall (Firewall-Regeln)
# - /etc/systemd/system/ollama.service.d (Service-Overrides & Tuning)
#
# Grosse Modell-Dateien (~/.ollama/models) werden bewusst NICHT gesichert.
set -euo pipefail
export PATH="/usr/sbin:/usr/bin:/sbin:/bin"

PW_FILE="/etc/pve/priv/storage/pbs-frawo.pw"
[ -f "$PW_FILE" ] || { echo "FEHLER: $PW_FILE fehlt" >&2; exit 1; }

export PBS_PASSWORD=$(cat "$PW_FILE" | tr -d '\r\n')
export PBS_FINGERPRINT="AF:77:64:AC:0F:45:1F:8E:0B:9C:3D:D2:87:FF:69:67:D8:E1:2B:D3:BC:09:97:DA:75:32:67:D9:22:29:07:96"

proxmox-backup-client backup \
    network.pxar:/etc/network \
    firewall.pxar:/etc/pve/firewall \
    ollama-config.pxar:/etc/systemd/system/ollama.service.d \
    --repository "root@pam@10.1.0.7:local-backups" \
    --ns optiplex
