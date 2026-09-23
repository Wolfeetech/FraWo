#!/bin/bash
# Richtet einen frisch installierten Surface als Kiosk ein. Wiederholbar.
# Erwartet deployments/surface als /root/frawo-surface. Aufruf als root:
#   bash /root/frawo-surface/os/frawo-surface-setup.sh [--vm]
# Im VM-Modus bleiben Tailscale und AnyDesk-Konfigurationsrueckspielung aus.
set -euo pipefail

VM=0
[ "${1:-}" = "--vm" ] && VM=1
OS=$(cd "$(dirname "$0")" && pwd)
D="$OS/dateien"
PORTAL_SRC=$(dirname "$OS")
export DEBIAN_FRONTEND=noninteractive

echo "== Pakete"
apt-get update -q
apt-get install -y -q ubuntu-desktop-minimal prometheus-node-exporter unattended-upgrades python3 curl
snap list chromium >/dev/null 2>&1 || snap install chromium

echo "== Benutzer anzeige"
id anzeige >/dev/null 2>&1 || useradd -m -s /bin/bash -c "Anzeige" anzeige
passwd -l anzeige >/dev/null
gpasswd -d anzeige sudo >/dev/null 2>&1 || true
passwd -l frawo >/dev/null

echo "== GDM, udev, dconf"
install -m 644 "$D/gdm-custom.conf" /etc/gdm3/custom.conf
install -m 644 "$D/99-frawo-phantom-tastatur.rules" /etc/udev/rules.d/99-frawo-phantom-tastatur.rules
udevadm control --reload
install -D -m 644 "$D/dconf-profile-user" /etc/dconf/profile/user
install -D -m 644 "$D/00-frawo" /etc/dconf/db/local.d/00-frawo
dconf update

echo "== Starter"
for starter in frawo-home-control frawo-radio-control frawo-monitor; do
  install -m 644 "$D/$starter.desktop" "/usr/share/applications/$starter.desktop"
done
install -D -m 644 "$D/frawo-home-control-autostart.desktop" /etc/xdg/autostart/frawo-home-control.desktop

echo "== Portal"
install -d -m 755 /opt/frawo-portal
install -m 644 "$PORTAL_SRC/server.py" /opt/frawo-portal/server.py
install -m 644 "$PORTAL_SRC/frawo_anker_hub.html" /opt/frawo-portal/frawo_anker_hub.html
install -m 644 "$PORTAL_SRC/frawo_anker_hub.html" /opt/frawo-portal/index.html
install -m 644 "$D/frawo-portal.service" /etc/systemd/system/frawo-portal.service
systemctl daemon-reload
systemctl enable --now frawo-portal.service
systemctl restart frawo-portal.service

echo "== Updates und node_exporter"
install -m 644 "$D/52frawo-updates" /etc/apt/apt.conf.d/52frawo-updates
systemctl enable --now prometheus-node-exporter

echo "== AnyDesk"
if ! command -v anydesk >/dev/null; then
  install -d -m 755 /etc/apt/keyrings
  curl -fsSL https://keys.anydesk.com/repos/DEB-GPG-KEY -o /etc/apt/keyrings/anydesk.asc
  echo "deb [signed-by=/etc/apt/keyrings/anydesk.asc] https://deb.anydesk.com all main" > /etc/apt/sources.list.d/anydesk.list
  apt-get update -q
  apt-get install -y -q anydesk
fi
if [ "$VM" = 0 ] && [ -f /root/anydesk-sicherung/service.conf ]; then
  systemctl stop anydesk
  install -m 600 /root/anydesk-sicherung/service.conf /etc/anydesk/service.conf
  install -m 600 /root/anydesk-sicherung/system.conf /etc/anydesk/system.conf
  systemctl start anydesk
fi

if [ "$VM" = 0 ]; then
  echo "== Tailscale"
  command -v tailscale >/dev/null || curl -fsSL https://tailscale.com/install.sh | sh
  if ! tailscale status >/dev/null 2>&1; then
    tailscale up --accept-routes=false --hostname=surface-go ${TS_AUTHKEY:+--auth-key="$TS_AUTHKEY"}
  fi
  tailscale set --accept-routes=false
fi

echo "== fertig – Neustart notwendig, damit Autologin, udev und dconf greifen"
