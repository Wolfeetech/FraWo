#!/bin/bash
# 🤖 [Claude] 24.09.2026 — PBS-Neuaufbau VM241 auf OptiPlex: Antwortdatei + Installationsabbild
set -euo pipefail
W=/root/pbs241-install
mkdir -p "$W"; cd "$W"

apt-get install -y -q proxmox-auto-install-assistant xorriso >/dev/null

# Zufaelliges root-Passwort, nur als Hash; Klartext wird nicht gespeichert (Zugang per SSH-Schluessel)
HASH=$(openssl rand -base64 30 | openssl passwd -6 -stdin)
# "pve-access" = der Schluessel, den der StudioPC fuer die Knoten nutzt (~/.ssh/pve_ed25519).
# Nicht "studiopc@wolfstudioPC": unter dem Namen stehen fuenf verschiedene Schluessel im Verbund.
K1=$(grep -m1 ' pve-access$' /etc/pve/priv/authorized_keys)
K2=$(grep -m1 'jarvis@frawo.tech$' /etc/pve/priv/authorized_keys)

cat > answer.toml <<EOF
[global]
keyboard = "de"
country = "de"
fqdn = "pbs-optiplex.frawo.lan"
mailto = "wolf@frawo.tech"
timezone = "Europe/Berlin"
root-password-hashed = "$HASH"  # zufaellig, Klartext nie gespeichert
root-ssh-keys = [
  "$K1",
  "$K2",
]
reboot-on-error = false
reboot-mode = "power-off"

[network]
source = "from-answer"
cidr = "10.1.0.8/24"
dns = "10.1.0.1"
gateway = "10.1.0.1"
filter.ID_NET_NAME_MAC = "*bc2411ba450a"

[disk-setup]
filesystem = "ext4"
filter.ID_SCSI_SERIAL = "PBSSYS"
EOF

proxmox-auto-install-assistant validate-answer answer.toml
proxmox-auto-install-assistant prepare-iso /var/lib/vz/template/iso/proxmox-backup-server_4.2-1.iso \
  --fetch-from iso --answer-file answer.toml \
  --output /var/lib/vz/template/iso/pbs241-auto.iso
ls -la /var/lib/vz/template/iso/pbs241-auto.iso
