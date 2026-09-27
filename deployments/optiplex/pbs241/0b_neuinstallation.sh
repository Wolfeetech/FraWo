#!/bin/bash
# 🤖 [Claude] 24.09.2026 — PBS VM241 neu installieren (nur Systemplatte PBSSYS; Datenplatte PBSDATA bleibt), Odoo #1462
# Laeuft auf dem OptiPlex, direkt nach 0_installabbild.sh (Abbild mit reboot-mode=power-off).
# Ablauf: Installer starten -> VM schaltet sich nach der Installation selbst aus -> von Platte starten.
set -euo pipefail
qm stop 241
qm set 241 --boot 'order=ide2;scsi1'
qm start 241
echo "Installer laeuft..."
for i in $(seq 1 90); do
  sleep 20
  qm status 241 | grep -q stopped && break
done
qm status 241 | grep -q stopped || { echo "FEHLER: Installation nach 30 Min nicht fertig - Konsole ansehen"; exit 1; }
qm set 241 --boot 'order=scsi1'
qm start 241
echo "Installiert, startet von der Systemplatte - in ca. 1 Minute ist https://10.1.0.8:8007 da"
