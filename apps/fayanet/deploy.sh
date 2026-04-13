#!/bin/bash
# Dieses Skript ist der "eine Knopf", um das gesamte System auf dem Server
# zu starten oder auf den neuesten Stand zu bringen.

# Beendet das Skript sofort, wenn ein Befehl fehlschlägt.
set -e

echo ">>> [1/3] Navigiere zum Projektverzeichnis..."
cd "$(dirname "$0")"

echo ">>> [2/3] Hole die neuesten Änderungen aus dem GitHub-Repository..."
git pull

echo ">>> [3/3] Starte alle Dienste mit Docker Compose im Hintergrund..."
docker-compose up -d

echo ""
echo "==============================================="
echo "✅ Deployment erfolgreich abgeschlossen."
echo "  Aktueller Status der Dienste:"
echo "==============================================="
docker-compose ps
