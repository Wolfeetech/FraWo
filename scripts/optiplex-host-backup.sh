#!/bin/bash
# Sichert die Konfiguration des OptiPlex 7050 auf den Proxmox Backup Server (PBS).
# Angelegt 18.09.2026 (Task #1470). Umgestellt 05.10.2026 (#1912) auf den aktuellen PBS
# (10.1.0.8, Datastore frawo, Token sicherung@pbs!pve aus storage.cfg) - der alte Ziel-PBS
# 10.1.0.7 mit pbs-frawo.pw existiert nicht mehr.
#
# Gesichert wird, was nicht reproduzierbar ist:
# - /etc/network (Netzwerkkonfiguration)
# - /etc/pve/firewall (Firewall-Regeln)
# - /etc/systemd/system/ollama.service.d (Service-Overrides & Tuning)
#
# Grosse Modell-Dateien (~/.ollama/models) werden bewusst NICHT gesichert.
set -euo pipefail
export PATH="/usr/sbin:/usr/bin:/sbin:/bin"

PW_FILE="/etc/pve/priv/storage/pbs.pw"
[ -f "$PW_FILE" ] || { echo "FEHLER: $PW_FILE fehlt" >&2; exit 1; }

# Server, Datastore, Benutzer und Fingerprint aus der PVE-Speicherdefinition "pbs" lesen,
# damit ein PBS-Umzug nicht wieder unbemerkt diese Sicherung bricht.
wert() { awk -v k="$1" '/^pbs: pbs$/{p=1;next} /^[a-z]+: /{p=0} p && $1==k {print $2}' /etc/pve/storage.cfg; }
SERVER=$(wert server); STORE=$(wert datastore); BENUTZER=$(wert username); FP=$(wert fingerprint)
[ -n "$SERVER" ] && [ -n "$STORE" ] && [ -n "$BENUTZER" ] || { echo "FEHLER: Speicher 'pbs' in storage.cfg unvollstaendig" >&2; exit 1; }

export PBS_PASSWORD=$(tr -d '\r\n' < "$PW_FILE")
export PBS_FINGERPRINT="$FP"

proxmox-backup-client backup \
    network.pxar:/etc/network \
    firewall.pxar:/etc/pve/firewall \
    ollama-config.pxar:/etc/systemd/system/ollama.service.d \
    --repository "${BENUTZER}@${SERVER}:${STORE}" \
    --backup-id optiplex-host

# --- 2. Unabhaengige Kopie auf dem Anker (#1912) ------------------------------------
# Der PBS (VM 241) laeuft auf diesem OptiPlex selbst. Faellt der OptiPlex aus, waeren
# Sicherung und Gesicherte zugleich weg. Daher zusaetzlich ein Archiv der Host-Konfig
# und der PBS-Systemkonfiguration (/etc/proxmox-backup) auf den Anker, wie bei
# azuracast-offsite/odoo-offsite. Enthaelt Schluessel -> Ablage 0600, nur root.
ANKER=root@10.1.0.92
ZIEL=/var/backups/optiplex-pbs-config
STEMPEL=$(date +%Y%m%d-%H%M)
TMP=$(mktemp -d); trap 'rm -rf "$TMP"' EXIT
tar czf "$TMP/optiplex-host.tar.gz" -C / etc/network etc/pve/firewall etc/systemd/system/ollama.service.d \
    etc/systemd/system/optiplex-host-backup.service etc/systemd/system/optiplex-host-backup.timer usr/local/bin/optiplex-host-backup.sh
qm guest exec 241 --timeout 60 -- bash -c 'tar czf - -C / etc/proxmox-backup | base64 -w0' \
  | python3 -c 'import sys,json,base64; d=json.load(sys.stdin); assert d.get("exitcode")==0, d.get("err-data"); sys.stdout.buffer.write(base64.b64decode(d["out-data"]))' \
  > "$TMP/pbs-config.tar.gz"
tar tzf "$TMP/pbs-config.tar.gz" | grep -q 'etc/proxmox-backup/datastore.cfg' || { echo "FEHLER: PBS-Konfig-Archiv unvollstaendig" >&2; exit 1; }
tar czf - -C "$TMP" optiplex-host.tar.gz pbs-config.tar.gz \
  | ssh -o BatchMode=yes -o ConnectTimeout=15 "$ANKER" \
      "umask 077; mkdir -p $ZIEL && cat > $ZIEL/optiplex-pbs-config-$STEMPEL.tar.gz.tmp && mv $ZIEL/optiplex-pbs-config-$STEMPEL.tar.gz.tmp $ZIEL/optiplex-pbs-config-$STEMPEL.tar.gz && ls -t $ZIEL/optiplex-pbs-config-*.tar.gz | tail -n +15 | xargs -r rm -f"
echo "Anker-Kopie: $ZIEL/optiplex-pbs-config-$STEMPEL.tar.gz"
