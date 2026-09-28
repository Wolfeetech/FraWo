#!/bin/bash
# Holt die LEBENDEN FraWo-Dokumente ins Gedaechtnis des Agenten (CT150 auf dem Anker).
#
# Bewusst NICHT dabei: DOCS/, artifacts/, archive/.
# Das sind zusammen ueber 1,7 Mio Zeichen Ablagerung - alte Plaene, erzeugte
# Berichte, Uebergabedokumente. Eine Suche weiss nicht, was noch gilt; sie
# liefert, was passt. Ein Treffer aus Task_Archive sieht genauso ueberzeugend
# aus wie NOW.md. Genau davor schuetzt diese Auswahl.
#
# Aufruf per Cron in CT150 - das Repo-Update macht der Cron, NICHT dieses
# Skript: es wuerde sich sonst waehrend der eigenen Ausfuehrung ueberschreiben.
#
#   15 1 * * * cd /opt/frawo-repo && git fetch --depth 1 origin main -q && \
#              git reset --hard origin/main -q && \
#              bash scripts/frawo-wissen-sync.sh >> /var/log/frawo-wissen-sync.log 2>&1
set -euo pipefail

REPO=/opt/frawo-repo
VOL=$(docker volume inspect openclaw_openclaw-data --format '{{.Mountpoint}}')
ZIEL="$VOL/workspace/memory/frawo"

# Erst in einen Nebenordner bauen, dann umschwenken. So kann ein
# fehlgeschlagener Lauf das bestehende Gedaechtnis nicht leerraeumen.
TMP="${ZIEL}.neu"
rm -rf "$TMP"
mkdir -p "$TMP"

cp "$REPO/NOW.md" "$TMP/"
cp -r "$REPO/OPERATIONS" "$TMP/"
cp -r "$REPO/SSOT" "$TMP/"

ANZAHL=$(find "$TMP" -name '*.md' | wc -l)
if [ "$ANZAHL" -lt 5 ]; then
  echo "FEHLER: nur $ANZAHL Dateien gefunden - Abbruch, bestehendes Gedaechtnis bleibt unberuehrt" >&2
  rm -rf "$TMP"
  exit 1
fi

rm -rf "$ZIEL"
mv "$TMP" "$ZIEL"
echo "$(date '+%Y-%m-%d %H:%M') - $ANZAHL Dateien uebernommen"

# Seit 28.09.2026 (Odoo #1593): Die Dateien, die Jarvis direkt im Workspace
# liest, sind KOPIEN des Repos. Vorher lagen dort Staende vom 06.09./13.09.,
# waehrend Repo und StudioPC laengst weiter waren. Jede Kopie traegt einen
# Kopfvermerk, damit niemand sie fuer das Original haelt. Atomar per mv.
WS="$VOL/workspace"
kopie() {  # $1 = Datei im Repo, $2 = Zielname im Workspace
  [ -s "$REPO/$1" ] || { echo "FEHLER: $1 fehlt oder leer - Kopie uebersprungen" >&2; return 1; }
  { printf '<!-- KOPIE aus github.com/Wolfeetech/FraWo (main) %s, Stand %s. NICHT HIER BEARBEITEN - Aenderungen nur im Repo. -->\n' \
      "$1" "$(git -C "$REPO" log -1 --format=%h)"
    cat "$REPO/$1"; } > "$WS/$2.neu"
  mv "$WS/$2.neu" "$WS/$2"
}
kopie AGENTS.md AGENTS-PROTOCOL.md
kopie INFRA.md INFRA.md
kopie NOW.md NOW.md
echo "$(date '+%Y-%m-%d %H:%M') - Protokoll, INFRA.md, NOW.md in den Workspace kopiert"

docker exec openclaw openclaw memory index
