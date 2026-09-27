#!/bin/bash
# 🤖 [Claude] 24.09.2026 — Laeuft auf dem ANKER (Verbund-Konfig gilt fuer alle drei Knoten), Odoo #1462
# Aufruf vom StudioPC (Token geht direkt PBS -> Anker, erscheint nirgends im Klartext):
#   scp 3_pve_anbinden.sh anker-pve:/root/
#   ssh root@10.1.0.8 'cat /root/pve-token.json && shred -u /root/pve-token.json' \
#     | ssh anker-pve "bash /root/3_pve_anbinden.sh '<FINGERPRINT aus Schritt 2>'"
set -euo pipefail
FP="$1"
SECRET=$(python3 -c 'import re,sys; m=re.search(r"\"value\"\s*:\s*\"([^\"]+)\"", sys.stdin.read()); print(m.group(1) if m else "")')
[ -n "$SECRET" ] || { echo "FEHLER: kein Token auf stdin"; exit 1; }
D=$(date +%Y%m%d)
cp /etc/pve/storage.cfg /root/storage.cfg.bak-$D
cp /etc/pve/jobs.cfg /root/jobs.cfg.bak-$D

# Neues Ziel "pbs" fuer alle drei Knoten. Loeschen darf nur der PBS selbst -> keep-all hier.
pvesm status --storage pbs >/dev/null 2>&1 || \
  pvesm add pbs pbs --server 10.1.0.8 --datastore frawo --username 'sicherung@pbs!pve' \
    --password "$SECRET" --fingerprint "$FP" --content backup --prune-backups keep-all=1
# Die drei alten Eintraege zeigen auf die tote VM240 -> nur abschalten, nicht loeschen (Rueckweg)
for s in pbs-frawo pbs-prodesk pbs-optiplex; do pvesm set $s --disable 1; done

# Naechtlicher Auftrag: alle Gaeste ausser alter PBS (240), neuer PBS (241), Test-VM (990)
pvesh get /cluster/backup --output-format json | grep -q '"id":"pbs-alle-nachts"' || \
  pvesh create /cluster/backup --id pbs-alle-nachts --schedule '01:00' --storage pbs --all 1 \
    --exclude 240,241,990 --mode snapshot --compress zstd --notification-mode notification-system \
    --notes-template '{{guestname}}' \
    --comment "Alle Gaeste nachts auf PBS VM241 OptiPlex (Claude 24.09.2026, Odoo #1462)"

pvesm status --storage pbs
grep -A9 'pbs-alle-nachts' /etc/pve/jobs.cfg
