#!/bin/bash
# FraWo · Wächter für den Verbunddienst corosync
#
# Warum es diesen Wächter gibt (Vorfall 20.09.2026, Odoo #1474):
# Auf dem OptiPlex war corosync auf 1.958 MB angewachsen (üblich ~180 MB).
# In diesem Zustand EMPFING der Dienst weiter Pakete, SENDETE aber keine mehr
# — und meldete dabei durchgehend "Quorate: Yes, Nodes: 3". Auch
# `corosync-cfgtool -s` zeigte alle Knoten als "connected", weil die
# Transportschicht tatsächlich stand.
#
# Daraus die Regel: Ein Wächter darf sich nicht auf die Selbstauskunft des
# überwachten Dienstes verlassen. Er misst deshalb BEIDES:
#   - den Zustand  (Speicherverbrauch, Mitgliederzahl)
#   - die Wirkung  (gesendete und empfangene Pakete)
# Ein Verhältnis von Empfangen zu Senden, das stark auseinanderläuft, ist das
# Frühzeichen, das am 20.09. gefehlt hat.
#
# Läuft per systemd-Timer, schreibt in den Textdatei-Sammler des node_exporter.

set -u
ZIEL="/var/lib/node_exporter/textfile_collector/frawo_corosync.prom"
TMP="${ZIEL}.$$"

trap 'rm -f "$TMP"' EXIT

{
  echo "# HELP frawo_corosync_up Laeuft der Verbunddienst (1) oder nicht (0)"
  echo "# TYPE frawo_corosync_up gauge"
  if systemctl is-active --quiet corosync; then
    echo "frawo_corosync_up 1"
  else
    echo "frawo_corosync_up 0"
    # Alles Weitere ist ohne laufenden Dienst nicht messbar.
    exit 0
  fi

  # --- Zustand: Speicherverbrauch -----------------------------------------
  # Der Vorfall zeigte sich zuerst hier: 1.958 MB statt ~180 MB.
  RSS_KB=$(ps -C corosync -o rss= 2>/dev/null | head -1 | tr -d ' ')
  if [ -n "${RSS_KB}" ]; then
    echo "# HELP frawo_corosync_speicher_bytes Arbeitsspeicher des Verbunddienstes"
    echo "# TYPE frawo_corosync_speicher_bytes gauge"
    echo "frawo_corosync_speicher_bytes $(( RSS_KB * 1024 ))"
  fi

  # --- Zustand: Mitglieder -------------------------------------------------
  MITGLIEDER=$(timeout 10 corosync-cmapctl 2>/dev/null \
    | grep -cE '^runtime\.members\.[0-9]+\.status.*joined')
  echo "# HELP frawo_corosync_mitglieder Beigetretene Knoten im Verbund"
  echo "# TYPE frawo_corosync_mitglieder gauge"
  echo "frawo_corosync_mitglieder ${MITGLIEDER:-0}"

  # --- Wirkung: gesendete und empfangene Pakete ---------------------------
  # DAS ist der Kern. Empfangen ohne Senden = der Fehler vom 20.09.
  STATS=$(timeout 10 corosync-cmapctl -m stats 2>/dev/null)
  TX=$(echo "${STATS}" | awk '/handle\.tx_crypt_packets /{print $NF}')
  RX=$(echo "${STATS}" | awk '/handle\.rx_crypt_packets /{print $NF}')

  if [ -n "${TX}" ]; then
    echo "# HELP frawo_corosync_gesendete_pakete_total Vom Verbunddienst gesendete Pakete"
    echo "# TYPE frawo_corosync_gesendete_pakete_total counter"
    echo "frawo_corosync_gesendete_pakete_total ${TX}"
  fi
  if [ -n "${RX}" ]; then
    echo "# HELP frawo_corosync_empfangene_pakete_total Vom Verbunddienst empfangene Pakete"
    echo "# TYPE frawo_corosync_empfangene_pakete_total counter"
    echo "frawo_corosync_empfangene_pakete_total ${RX}"
  fi

  # --- Wirkung: Verbindungen je Gegenstelle -------------------------------
  # down_count steigt bei jedem Abriss - am 20.09. waren es 170 in 24 Stunden.
  echo "# HELP frawo_corosync_verbindung_steht Verbindung zum Knoten steht (1) oder nicht (0)"
  echo "# TYPE frawo_corosync_verbindung_steht gauge"
  echo "# HELP frawo_corosync_verbindung_abrisse_total Abrisse der Verbindung seit dem Start"
  echo "# TYPE frawo_corosync_verbindung_abrisse_total counter"
  echo "${STATS}" | awk '
    /^stats\.knet\.node[0-9]+\.link0\.connected /   { split($1,a,"."); sub("node","",a[3]); verb[a[3]]=$NF }
    /^stats\.knet\.node[0-9]+\.link0\.down_count /  { split($1,a,"."); sub("node","",a[3]); abriss[a[3]]=$NF }
    END {
      for (n in verb)   printf "frawo_corosync_verbindung_steht{knoten=\"%s\"} %s\n", n, verb[n]
      for (n in abriss) printf "frawo_corosync_verbindung_abrisse_total{knoten=\"%s\"} %s\n", n, abriss[n]
    }'

  # --- Zeitstempel ---------------------------------------------------------
  # Fehlt diese Zahl oder wird sie alt, schweigt der Waechter selbst.
  # Dagegen gibt es eine eigene absent()-Regel.
  echo "# HELP frawo_corosync_letzte_messung_zeitstempel Wann zuletzt gemessen wurde"
  echo "# TYPE frawo_corosync_letzte_messung_zeitstempel gauge"
  echo "frawo_corosync_letzte_messung_zeitstempel $(date +%s)"

} > "$TMP" 2>/dev/null

# Erst vollstaendig schreiben, dann atomar umbenennen - sonst liest der
# Sammler halbe Dateien.
chmod 644 "$TMP"
mv "$TMP" "$ZIEL"
