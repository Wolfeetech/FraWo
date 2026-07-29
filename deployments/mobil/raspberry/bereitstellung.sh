#!/bin/bash
# FraWo — Raspberry Pi einsatzbereit machen
# Angelegt 29.07.2026. Läuft auf einem frisch geflashten Raspberry Pi OS Lite.
#
# Aufruf:
#   sudo ./bereitstellung.sh <rolle> <name>
#
#   rolle:  relais | kiosk | messplatz | reserve
#   name:   Gerätename, z.B. funk-relais-1
#
# Beispiel:
#   sudo ./bereitstellung.sh relais funk-relais-1
#
# Das Skript ist mehrfach ausführbar. Es macht nichts kaputt, wenn es ein
# zweites Mal läuft — jeder Schritt prüft vorher, ob er schon erledigt ist.
#
# ---------------------------------------------------------------------------
# ARCHITEKTUR-ENTSCHEIDUNG, bewusst anders als in Odoo #243
# ---------------------------------------------------------------------------
# Die alte Aufgabenbeschreibung sah vor, dass der Pi das Signal über Tailscale
# von CT130 holt. Dagegen sprechen zwei Dinge:
#
#   1. AzuraCast läuft auf VM210 (10.1.0.38) und ist gar nicht in Tailscale.
#      Der Weg über CT130 wäre ein Umweg über einen Rechner, der mit dem
#      Sender nichts zu tun hat.
#   2. Beim Event hängt der Pi am Handy-Hotspot. Tailscale baut dann erst eine
#      Verbindung zu einem Gerät zuhause auf, um Audio zu holen, das ohnehin
#      öffentlich abrufbar ist. Mehr Teile, die kaputtgehen können.
#
# Deshalb: Der Pi holt EINEN Stream direkt von funk.frawo.tech und bedient
# davon beliebig viele Zuhörer vor Ort. Genau dafür ist ein Relais da — eine
# Mobilfunkverbindung trägt einen Stream, nicht dreissig.
#
# Tailscale ist trotzdem drauf, aber nur für Fernwartung und Überwachung.
# Fällt es aus, läuft der Ton weiter.
# ---------------------------------------------------------------------------

set -euo pipefail

ROLLE="${1:-}"
NAME="${2:-}"

QUELLE_HOST="funk.frawo.tech"
QUELLE_MOUNT="/listen/frawo_funk/radio.mp3"
LOKALER_MOUNT="/frawo.mp3"

if [ -z "$ROLLE" ] || [ -z "$NAME" ]; then
    echo "Aufruf: sudo $0 <rolle> <name>"
    echo "  rolle: relais | kiosk | messplatz | reserve"
    echo "  name:  z.B. funk-relais-1"
    exit 1
fi

if [ "$(id -u)" -ne 0 ]; then
    echo "Bitte mit sudo starten."
    exit 1
fi

schritt() { echo; echo "=== $* ==="; }

# ---------------------------------------------------------------------------
schritt "1/7  Gerätename setzen"
if [ "$(hostname)" != "$NAME" ]; then
    hostnamectl set-hostname "$NAME"
    # Ohne passenden Eintrag in /etc/hosts meckert sudo bei jedem Aufruf
    # minutenlang herum ("unable to resolve host").
    if ! grep -q "127.0.1.1.*$NAME" /etc/hosts; then
        sed -i "s/^127.0.1.1.*/127.0.1.1\t$NAME/" /etc/hosts
        grep -q '^127.0.1.1' /etc/hosts || echo -e "127.0.1.1\t$NAME" >> /etc/hosts
    fi
    echo "  gesetzt: $NAME"
else
    echo "  war schon: $NAME"
fi

# ---------------------------------------------------------------------------
schritt "2/7  Paketquellen und Grundpakete"
export DEBIAN_FRONTEND=noninteractive
apt-get update -qq
apt-get install -y -qq curl ca-certificates prometheus-node-exporter unattended-upgrades
echo "  Grundpakete vorhanden"

# ---------------------------------------------------------------------------
schritt "3/7  Schonung der Speicherkarte"
# Die SD-Karte ist beim Pi das Bauteil, das als erstes stirbt — und sie stirbt
# an Schreibvorgängen. Zwei Stellschrauben, die am meisten bringen:
#
#   Protokolle in den Arbeitsspeicher statt auf die Karte
#   Auslagerungsdatei aus (ein Relais braucht sie nicht, sie schreibt aber
#   dauernd)
mkdir -p /etc/systemd/journald.conf.d
cat > /etc/systemd/journald.conf.d/99-frawo-sdkarte.conf <<'EOF'
# Protokolle im Arbeitsspeicher halten. Sie sind nach einem Neustart weg —
# das ist der Preis dafür, dass die Speicherkarte länger lebt. Für ein
# Einsatzgerät ist das der richtige Tausch.
[Journal]
Storage=volatile
RuntimeMaxUse=32M
EOF
systemctl restart systemd-journald 2>/dev/null || true

if systemctl is-enabled dphys-swapfile >/dev/null 2>&1; then
    systemctl disable --now dphys-swapfile 2>/dev/null || true
    echo "  Auslagerungsdatei abgeschaltet"
fi
echo "  Protokolle laufen jetzt im Arbeitsspeicher"

# ---------------------------------------------------------------------------
schritt "4/7  Messwerte bereitstellen (node_exporter)"
# Standardmässig lauscht der Exporter auf allen Adressen. Auf einem Gerät, das
# beim Event in fremden WLANs hängt, hat das nichts zu suchen — er soll nur
# über Tailscale erreichbar sein.
mkdir -p /etc/systemd/system/prometheus-node-exporter.service.d
cat > /etc/systemd/system/prometheus-node-exporter.service.d/99-frawo.conf <<'EOF'
# Nur über Tailscale erreichbar, nicht im fremden WLAN beim Event.
# tailscale0 bekommt die Adresse erst nach dem Start von tailscaled, deshalb
# wartet der Dienst darauf.
[Unit]
After=tailscaled.service
Wants=tailscaled.service

[Service]
ExecStart=
ExecStart=/usr/bin/prometheus-node-exporter --web.listen-address=:9100 --collector.hwmon
EOF
systemctl daemon-reload
systemctl enable --now prometheus-node-exporter
echo "  node_exporter läuft"

# ---------------------------------------------------------------------------
schritt "5/7  Tailscale"
if ! command -v tailscale >/dev/null 2>&1; then
    curl -fsSL https://tailscale.com/install.sh | sh
fi
if ! tailscale status >/dev/null 2>&1; then
    echo
    echo "  Tailscale ist installiert, aber noch nicht angemeldet."
    echo "  Jetzt ausführen (Schlüssel steht auf dem ProDesk in"
    echo "  /root/.tailscale-mobil-key, Rechte 600):"
    echo
    echo "    sudo tailscale up --authkey=<SCHLUESSEL> --hostname=$NAME"
    echo
else
    echo "  bereits angemeldet als $(tailscale status --self --json 2>/dev/null | grep -oE '\"DNSName\":\"[^\"]*\"' | head -1 | cut -d'\"' -f4)"
fi

# ---------------------------------------------------------------------------
schritt "6/7  Rolle einrichten: $ROLLE"
case "$ROLLE" in
  relais)
    apt-get install -y -qq icecast2
    # Icecast fragt bei der Installation interaktiv nach Passwörtern. Auf
    # einem Gerät ohne Bildschirm bleibt es sonst hängen — deshalb schreiben
    # wir die Konfiguration selbst.
    QUELL_PW=$(head -c 18 /dev/urandom | base64 | tr -d '/+=' | head -c 16)
    ADMIN_PW=$(head -c 18 /dev/urandom | base64 | tr -d '/+=' | head -c 16)
    cat > /etc/icecast2/icecast.xml <<EOF
<icecast>
  <location>FraWo mobil</location>
  <admin>mail@frawo.tech</admin>

  <limits>
    <!-- 100 Zuhoerer reichen fuer jede Veranstaltung, die wir machen.
         Der Pi 3 schafft das locker - er kopiert nur Daten. -->
    <clients>100</clients>
    <sources>2</sources>
    <queue-size>524288</queue-size>
    <client-timeout>30</client-timeout>
    <header-timeout>15</header-timeout>
    <source-timeout>10</source-timeout>
    <burst-on-connect>1</burst-on-connect>
    <!-- Puffer beim Verbindungsaufbau: Der Ton startet dadurch sofort,
         statt erst nach ein paar Sekunden. -->
    <burst-size>65536</burst-size>
  </limits>

  <authentication>
    <source-password>${QUELL_PW}</source-password>
    <relay-password>${QUELL_PW}</relay-password>
    <admin-user>admin</admin-user>
    <admin-password>${ADMIN_PW}</admin-password>
  </authentication>

  <hostname>${NAME}.local</hostname>
  <listen-socket><port>8000</port></listen-socket>

  <!-- Der eigentliche Zweck: EINEN Stream aus dem Netz holen und beliebig
       viele Zuhoerer vor Ort davon bedienen. Eine Mobilfunkverbindung traegt
       einen Stream, nicht dreissig. -->
  <relay>
    <server>${QUELLE_HOST}</server>
    <port>443</port>
    <mount>${QUELLE_MOUNT}</mount>
    <local-mount>${LOKALER_MOUNT}</local-mount>
    <on-demand>0</on-demand>
    <relay-shoutcast-metadata>1</relay-shoutcast-metadata>
  </relay>

  <paths>
    <basedir>/usr/share/icecast2</basedir>
    <logdir>/var/log/icecast2</logdir>
    <webroot>/usr/share/icecast2/web</webroot>
    <adminroot>/usr/share/icecast2/admin</adminroot>
    <alias source="/" destination="${LOKALER_MOUNT}"/>
  </paths>

  <logging>
    <accesslog>access.log</accesslog>
    <errorlog>error.log</errorlog>
    <loglevel>2</loglevel>
    <logsize>2048</logsize>
  </logging>

  <security><chroot>0</chroot></security>
</icecast>
EOF
    chown icecast2:icecast /etc/icecast2/icecast.xml
    chmod 640 /etc/icecast2/icecast.xml
    sed -i 's/^ENABLE=.*/ENABLE=true/' /etc/default/icecast2 2>/dev/null || \
        echo 'ENABLE=true' >> /etc/default/icecast2
    systemctl enable --now icecast2
    systemctl restart icecast2

    # Zugangsdaten ablegen, damit man sie nicht sucht. Nur für root lesbar.
    cat > /root/icecast-zugang.txt <<EOF
Icecast auf ${NAME}
  Adresse vor Ort:  http://${NAME}.local:8000${LOKALER_MOUNT}
  Verwaltung:       http://${NAME}.local:8000/admin/
  Benutzer:         admin
  Passwort:         ${ADMIN_PW}
  Quell-Passwort:   ${QUELL_PW}

Diese Datei nach dem Aufbau nach Vaultwarden übertragen und hier löschen.
EOF
    chmod 600 /root/icecast-zugang.txt
    echo "  Icecast läuft, Zugangsdaten in /root/icecast-zugang.txt"
    ;;

  kiosk)
    apt-get install -y -qq chromium-browser unclutter
    echo "  Kiosk-Grundpakete installiert."
    echo "  Die Startseite wird beim Aufbau festgelegt (Odoo oder Anker-Tracker)."
    ;;

  messplatz|reserve)
    echo "  Keine zusätzliche Software. Gerät ist als Reserve vorbereitet."
    ;;

  *)
    echo "  Unbekannte Rolle '$ROLLE' — es wurde nur die Grundeinrichtung gemacht."
    ;;
esac

# ---------------------------------------------------------------------------
schritt "7/7  Eintrag für die Überwachung"
TS_IP=$(tailscale ip -4 2>/dev/null | head -1 || true)
if [ -n "$TS_IP" ]; then
    cat <<EOF

  Auf dem ProDesk ausführen, dann ist das Gerät in der Überwachung:

  cat > /tmp/${NAME}.yml <<'ZIEL'
- targets:
    - "${TS_IP}:9100"
  labels:
    instance: "${NAME}"
    env: "frawo"
    mobil: "ja"
    rolle: "${ROLLE}"
    geraet: "$(tr -d '\0' < /proc/device-tree/model 2>/dev/null | sed 's/Raspberry Pi/raspberry-pi/;s/ /-/g' | tr 'A-Z' 'a-z' || echo unbekannt)"
ZIEL
  pct push 150 /tmp/${NAME}.yml /etc/prometheus/ziele/mobil/${NAME}.yml --perms 0644

  Kein Neustart nötig — Prometheus liest das Verzeichnis alle 30 Sekunden neu.
EOF
else
    echo "  Tailscale-Adresse noch nicht vorhanden. Nach der Anmeldung dieses"
    echo "  Skript einfach nochmal laufen lassen, dann steht der Eintrag hier."
fi

echo
echo "=== Fertig: $NAME (Rolle: $ROLLE) ==="
