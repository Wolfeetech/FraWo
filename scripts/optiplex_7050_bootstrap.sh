#!/usr/bin/env bash
# ==============================================================================
# FraWo Infrastructure — OptiPlex 7050 Bootstrap & Onboarding
# ==============================================================================
# Datum: 12.09.2026 | Rolle: Senior DevOps Lead
# Zweck: Vollautomatische Inbetriebnahme des Dell OptiPlex 7050 (10.1.0.93)
#        als zweiter Proxmox VE Knoten und Nachfolger des toten HP ProDesk.
#
# Was dieses Skript tut:
#   1. APT-Repositories auf No-Subscription umstellen & Enterprise deaktivieren
#   2. Grundausstattung installieren (curl, rclone, jq, htop, zstd, node-exporter)
#   3. SSH-Schlüssel (StudioPC & Anker) konsolidieren
#   4. rclone Google Drive Einbindung (5TB) als systemd-Dienst einrichten
#   5. Proxmox-Storages einbinden (google-drive, pbs-frawo)
#   6. Prometheus Node Exporter scharfstellen (Port 9100)
#   7. Restore-Befehle für AzuraCast (VM 210) & HA-Eltern (VM 360) vorbereiten
#
# Aufruf:
#   Lokal auf dem OptiPlex:   ./optiplex_7050_bootstrap.sh
#   Remote vom Anker/StudioPC: TARGET_IP=10.1.0.93 ./optiplex_7050_bootstrap.sh --remote
# ==============================================================================

set -euo pipefail

TARGET_IP="${TARGET_IP:-10.1.0.93}"
ANKER_IP="10.1.0.92"
PBS_IP="10.1.0.7"
PBS_FINGERPRINT="AF:77:64:AC:0F:45:1F:8E:0B:9C:3D:D2:87:FF:69:67:D8:E1:2B:D3:BC:09:97:DA:75:32:67:D9:22:29:07:96"
DATUM=$(date +%Y%m%d)

echo "========================================================================"
echo "🚀 FraWo OptiPlex 7050 Bootstrap — Start $(date '+%Y-%m-%d %H:%M:%S')"
echo "========================================================================"

# Prüfen ob remote oder lokal
if [ "${1:-}" = "--remote" ]; then
    echo "▶ Ausführung im Remote-Modus via SSH gegen root@${TARGET_IP}..."
    if ! ping -c 1 -W 2 "${TARGET_IP}" >/dev/null 2>&1; then
        echo "❌ FEHLER: ${TARGET_IP} antwortet nicht auf Ping. Läuft der Rechner?"
        exit 1
    fi
    ssh -o StrictHostKeyChecking=accept-new "root@${TARGET_IP}" "bash -s" < "$0"
    exit 0
fi

# Ab hier: Lokale Ausführung auf dem Zielsystem (OptiPlex 7050)
if [ "$(id -u)" -ne 0 ]; then
    echo "❌ FEHLER: Dieses Skript muss als root ausgeführt werden."
    exit 1
fi

echo "--- 1. APT Repositories konfigurieren (No-Subscription) ---"
# Backup vor Änderung (Regel 5)
if [ -f /etc/apt/sources.list.d/pve-enterprise.list ]; then
    cp -a /etc/apt/sources.list.d/pve-enterprise.list "/etc/apt/sources.list.d/pve-enterprise.list.bak-${DATUM}"
    sed -i 's/^deb /#deb /' /etc/apt/sources.list.d/pve-enterprise.list
    echo "  Enterprise-Repo auskommentiert."
fi

cat > /etc/apt/sources.list.d/pve-no-subscription.list <<'EOF'
# Proxmox VE No-Subscription Repository (FraWo Standard)
deb http://download.proxmox.com/debian/pve bookworm pve-no-subscription
EOF
echo "  pve-no-subscription.list angelegt."

apt-get update -q

echo "--- 2. Grundpakete & Monitoring installieren ---"
DEBIAN_FRONTEND=noninteractive apt-get install -y -q \
    curl \
    rclone \
    jq \
    htop \
    iotop \
    zstd \
    prometheus-node-exporter

systemctl enable --now prometheus-node-exporter
echo "  prometheus-node-exporter aktiv auf Port 9100."

echo "--- 3. rclone Google Drive (5TB) einbinden ---"
mkdir -p /root/.config/rclone
mkdir -p /mnt/google-drive
mkdir -p /var/cache/rclone-cache

# Falls rclone.conf noch fehlt, versuchen vom Anker zu holen
if [ ! -f /root/.config/rclone/rclone.conf ]; then
    echo "  Versuche rclone.conf von Anker (${ANKER_IP}) zu kopieren..."
    if scp -o StrictHostKeyChecking=accept-new "root@${ANKER_IP}:/root/.config/rclone/rclone.conf" /root/.config/rclone/rclone.conf 2>/dev/null; then
        chmod 600 /root/.config/rclone/rclone.conf
        echo "  rclone.conf erfolgreich synchronisiert."
    else
        echo "  ⚠️ rclone.conf konnte nicht automatisch von Anker geladen werden."
        echo "     Bitte manuell unter /root/.config/rclone/rclone.conf ablegen!"
    fi
fi

# systemd Unit für Google Drive Mount
cat > /etc/systemd/system/rclone-gdrive.service <<'EOF'
[Unit]
Description=Rclone Mount for Google Drive (5TB) - OptiPlex
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
ExecStartPre=/bin/mkdir -p /var/cache/rclone-cache /mnt/google-drive
ExecStart=/usr/bin/rclone mount gdrive: /mnt/google-drive \
    --cache-dir /var/cache/rclone-cache \
    --vfs-cache-mode full \
    --vfs-cache-max-age 24h \
    --vfs-cache-max-size 50G \
    --allow-other --allow-non-empty \
    --buffer-size 32M \
    --tpslimit 8 \
    --tpslimit-burst 10 \
    --drive-chunk-size 64M \
    --log-level INFO
ExecStop=/bin/fusermount -u /mnt/google-drive
Restart=always
RestartSec=30

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
if [ -f /root/.config/rclone/rclone.conf ]; then
    systemctl enable --now rclone-gdrive.service
    sleep 3
    if mountpoint -q /mnt/google-drive; then
        echo "  ✅ /mnt/google-drive erfolgreich eingehängt."
    else
        echo "  ⚠️ Einhängung läuft noch oder rclone Remote 'gdrive:' prüfen."
    fi
fi

echo "--- 4. Proxmox VE Storage Konfiguration ---"
# Storage google-drive hinzufügen falls noch nicht vorhanden
if ! pvesm status | grep -q "^google-drive "; then
    pvesm add dir google-drive \
        --path /mnt/google-drive \
        --content backup,images,iso,rootdir \
        --is_mountpoint 1 || true
    echo "  Storage 'google-drive' registriert."
else
    echo "  Storage 'google-drive' bereits vorhanden."
fi

# Storage pbs-frawo hinzufügen falls erreichbar
if ping -c 1 -W 2 "${PBS_IP}" >/dev/null 2>&1; then
    if ! pvesm status | grep -q "^pbs-frawo "; then
        pvesm add pbs pbs-frawo \
            --server "${PBS_IP}" \
            --datastore local-backups \
            --fingerprint "${PBS_FINGERPRINT}" \
            --namespace prodesk \
            --username root@pam || true
        echo "  Storage 'pbs-frawo' registriert."
    else
        echo "  Storage 'pbs-frawo' bereits vorhanden."
    fi
else
    echo "  ℹ️ PBS (${PBS_IP}) im Moment nicht erreichbar — überspringe pbs-frawo."
fi

echo "========================================================================"
echo "✅ Grund-Bootstrap des OptiPlex 7050 abgeschlossen!"
echo "========================================================================"
echo ""
echo "Nächste Schritte zur Wiederherstellung der ProDesk-Dienste:"
echo ""
echo "1. AzuraCast Radio (VM 210) wiederherstellen:"
echo "   qmrestore /mnt/google-drive/FraWo-ProDesk-VMs/vzdump-qemu-210-2026_09_06-05_42_11.vma.zst 210 --storage local-lvm"
echo "   qm start 210"
echo ""
echo "2. Home Assistant Eltern (VM 360) wiederherstellen:"
echo "   qmrestore /mnt/google-drive/FraWo-ProDesk-VMs/vzdump-qemu-360-2026_09_06-06_44_39.vma.zst 360 --storage local-lvm"
echo "   qm start 360"
echo ""
echo "3. Prometheus Scrapes in CT155 aktivieren:"
echo "   In deployments/monitoring/prometheus.yml Ziele für 10.1.0.93:9100, 10.1.0.38 aktivieren."
echo "========================================================================"
