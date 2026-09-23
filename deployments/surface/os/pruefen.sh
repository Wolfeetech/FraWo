#!/bin/bash
# Abnahme Surface-Neuaufbau. Laeuft auf dem Geraet als root.
# Ausgabe: PASS/FAIL je Punkt. Exit-Code = Anzahl FAIL. --vm ueberspringt Hardware-Netztests.
set -u
VM=0
[ "${1:-}" = "--vm" ] && VM=1
FEHLER=0
ok() { echo "PASS $1"; }
nein() { echo "FAIL $1"; FEHLER=$((FEHLER + 1)); }
pruefe() {
  if bash -c "$2" >/dev/null 2>&1; then ok "$1"; else nein "$1"; fi
}

pruefe "sshd: Passwort-Anmeldung aus" "sshd -T | grep -qx 'passwordauthentication no'"
pruefe "frawo: Passwort gesperrt" "passwd -S frawo | grep -q ' L '"
pruefe "frawo: sudo ohne Passwort" "runuser -u frawo -- sudo -n true"
pruefe "anzeige: existiert" "id anzeige"
pruefe "anzeige: kein sudo" "! id -nG anzeige | grep -qw sudo"
pruefe "anzeige: Passwort gesperrt" "passwd -S anzeige | grep -q ' L '"
pruefe "GDM: Autologin anzeige" "grep -qx 'AutomaticLogin=anzeige' /etc/gdm3/custom.conf"
pruefe "Sitzung anzeige laeuft" "loginctl list-sessions --no-legend | grep -qw anzeige"
pruefe "Home Control laeuft" "pgrep -u anzeige -f 'chromium.*--app=http://127.0.0.1:17827/'"
pruefe "Portal antwortet" "curl -fsS -o /dev/null -m 5 http://127.0.0.1:17827/"
pruefe "dconf: Bildschirmtastatur an" "grep -q 'screen-keyboard-enabled=true' /etc/dconf/db/local.d/00-frawo"
pruefe "dconf: kein Ruhezustand" "grep -q \"sleep-inactive-ac-type='nothing'\" /etc/dconf/db/local.d/00-frawo"
pruefe "dconf: Bildschirm aus nach 600 s" "grep -q 'idle-delay=uint32 600' /etc/dconf/db/local.d/00-frawo"
pruefe "Starter: drei vorhanden" "[ \$(find /usr/share/applications -maxdepth 1 -name 'frawo-*.desktop' | wc -l) -eq 3 ]"
pruefe "Updates: Neustart 04:00" "grep -q 'Automatic-Reboot-Time \"04:00\"' /etc/apt/apt.conf.d/52frawo-updates"
pruefe "node_exporter antwortet" "curl -fsS -o /dev/null -m 5 http://127.0.0.1:9100/metrics"
pruefe "Odoo erreichbar :8069" "timeout 4 bash -c '</dev/tcp/10.1.0.112/8069'"
pruefe "Home Assistant erreichbar :8123" "timeout 4 bash -c '</dev/tcp/10.1.0.40/8123'"
pruefe "Grafana erreichbar :3000" "timeout 4 bash -c '</dev/tcp/10.1.0.35/3000'"
pruefe "Kein Installationsrest /frawo-install" "[ ! -e /frawo-install ]"

if [ "$VM" = 0 ]; then
  pruefe "Route Server-Netz ueber Gateway" "ip route get 10.1.0.112 | grep -q 'via 10.4.0.1 dev wlp1s0'"
  pruefe "Tailscale: RouteAll aus" "tailscale debug prefs | grep -q '\"RouteAll\": false'"
  pruefe "AnyDesk-Dienst aktiv" "systemctl is-active --quiet anydesk"
  pruefe "udev: Phantom-Tastatur ignoriert" "[ -f /etc/udev/rules.d/99-frawo-phantom-tastatur.rules ]"
fi

echo "--- $FEHLER Fehler"
exit "$FEHLER"
