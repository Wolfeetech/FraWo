#!/bin/bash
# 🤖 [Claude] 24.09.2026 — Laeuft AUF dem neuen PBS (VM241, 10.1.0.8), Odoo #1462
# Aufruf vom StudioPC:  ssh root@10.1.0.8 'bash -s' < 2_pbs_einrichten.sh
# Ergebnis: Datenspeicher "frawo" auf der Datenplatte (Seriennr. PBSDATA), Dienstkonto nur mit
# Sicherungsrecht, Aufraeum-/Pruefauftraege. Token landet NUR in /root/pve-token.json (600),
# wird von 3_pve_anbinden.sh abgeholt und danach geloescht. Ausgabe: nur der Fingerabdruck.
set -euo pipefail

# 1) Paketquellen: Enterprise aus (kein Abo), no-subscription an
for f in /etc/apt/sources.list.d/pbs-enterprise.sources /etc/apt/sources.list.d/pbs-enterprise.list; do
  [ -f "$f" ] && mv "$f" "$f.aus-20260924"
done
. /etc/os-release
cat > /etc/apt/sources.list.d/pbs-no-subscription.sources <<EOF
Types: deb
URIs: http://download.proxmox.com/debian/pbs
Suites: ${VERSION_CODENAME}
Components: pbs-no-subscription
Signed-By: /usr/share/keyrings/proxmox-archive-keyring.gpg
EOF
apt-get update -q >/dev/null
DEBIAN_FRONTEND=noninteractive apt-get -y -q dist-upgrade >/dev/null
DEBIAN_FRONTEND=noninteractive apt-get -y -q install qemu-guest-agent >/dev/null
systemctl enable --now qemu-guest-agent >/dev/null 2>&1 || true

# 2) Datenplatte ueber Seriennummer finden, nie ueber den Buchstaben
DISK=$(lsblk -dno NAME,SERIAL | awk '$2=="PBSDATA"{print $1}')
[ -n "$DISK" ] || { echo "FEHLER: Datenplatte PBSDATA nicht gefunden"; exit 1; }
if proxmox-backup-manager datastore list --output-format json | grep -q '"name":"frawo"'; then
  echo "Datenspeicher frawo existiert schon - uebersprungen"
else
  [ -z "$(lsblk -no FSTYPE /dev/$DISK | tr -d '[:space:]')" ] || { echo "FEHLER: /dev/$DISK ist nicht leer"; exit 1; }
  proxmox-backup-manager disk fs create frawo --disk "$DISK" --filesystem ext4 --add-datastore true
fi

# 3) Dienstkonto fuer die Proxmox-Knoten: darf sichern und eigene Sicherungen lesen, NICHT loeschen
proxmox-backup-manager user list --output-format json | grep -q '"userid":"sicherung@pbs"' || \
  proxmox-backup-manager user create sicherung@pbs --comment "PVE-Knoten, nur sichern (Claude 24.09.2026, Odoo #1462)"
if ! proxmox-backup-manager user list-tokens sicherung@pbs --output-format json | grep -q "sicherung@pbs!pve"; then
  umask 077
  proxmox-backup-manager user generate-token sicherung@pbs pve > /root/pve-token.json
fi
# Token-Rechte = Schnittmenge aus Konto- und Token-Rechten -> beide brauchen den Eintrag
proxmox-backup-manager acl update /datastore/frawo DatastoreBackup --auth-id 'sicherung@pbs'
proxmox-backup-manager acl update /datastore/frawo DatastoreBackup --auth-id 'sicherung@pbs!pve'

# 4) Aufraeumen (nur der PBS selbst loescht), Speicherbereinigung, woechentliche Pruefung
proxmox-backup-manager prune-job list --output-format json | grep -q '"id":"frawo-aufraeumen"' || \
  proxmox-backup-manager prune-job create frawo-aufraeumen --store frawo --schedule '06:00' \
    --keep-daily 7 --keep-weekly 4 --keep-monthly 3
proxmox-backup-manager datastore update frawo --gc-schedule '06:30'
proxmox-backup-manager verify-job list --output-format json | grep -q '"id":"frawo-pruefen"' || \
  proxmox-backup-manager verify-job create frawo-pruefen --store frawo --schedule 'sun 07:00' \
    --ignore-verified true --outdated-after 30
proxmox-backup-manager datastore update frawo --notify-user root@pam 2>/dev/null || true

# 5) Kontrolle
df -h /mnt/datastore/frawo | tail -1
proxmox-backup-manager cert info | awk -F': ' '/Fingerprint/{print "FINGERPRINT=" $2}'
