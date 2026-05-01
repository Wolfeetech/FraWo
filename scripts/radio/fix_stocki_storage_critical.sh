#!/bin/bash
# FIX STOCKI STORAGE CRITICAL - NFS 100% VOLL
# Datum: 2026-04-30
# Ziel: Stocki VM 210 Music Storage entlasten

set -euo pipefail

echo "=== STOCKI STORAGE CRITICAL FIX ==="
echo "Problem: NFS 192.168.178.25:/mnt/music_hdd ist 100% voll"
echo "Library: yourparty_Libary (283GB, 23.461 Tracks)"
echo ""

# SSH zu Stocki VM 210
STOCKI_VM="192.168.178.210"
STOCKI_JUMP="stock-pve"

echo "[1/6] Storage-Status prüfen..."
ssh -J "$STOCKI_JUMP" "$STOCKI_VM" "df -h /var/azuracast/music_storage"

echo ""
echo "[2/6] Temporary Files & Logs cleanup..."
ssh -J "$STOCKI_JUMP" "$STOCKI_VM" "
  sudo find /var/azuracast/music_storage -name '.DS_Store' -delete 2>/dev/null || true
  sudo find /var/azuracast/music_storage -name 'Thumbs.db' -delete 2>/dev/null || true
  sudo find /var/azuracast/music_storage -name '*.tmp' -delete 2>/dev/null || true
  sudo find /var/azuracast/music_storage -name '*.cache' -delete 2>/dev/null || true
"

echo ""
echo "[3/6] Duplicate Detection (Top 10 größte Dateien)..."
ssh -J "$STOCKI_JUMP" "$STOCKI_VM" "
  find /var/azuracast/music_storage/yourparty_Libary -type f -exec du -h {} + |
  sort -rh | head -10
"

echo ""
echo "[4/6] NFS Server identifizieren..."
NFS_SERVER=$(ssh -J "$STOCKI_JUMP" "$STOCKI_VM" "mount | grep music_storage | awk '{print \$1}'")
echo "NFS Server: $NFS_SERVER"

echo ""
echo "[5/6] OPTIONEN für Storage-Fix:"
echo ""
echo "OPTION A: Music Library zu Anker Storage Node migrieren (EMPFOHLEN)"
echo "  - Ziel: //10.1.0.30/Media/yourparty_Libary"
echo "  - Benefit: Zentrale Library, beide Nodes nutzen gleiche Quelle"
echo "  - Action: rsync 283GB von Stocki zu Storage Node"
echo ""
echo "OPTION B: NFS Server Disk erweitern"
echo "  - Aktion: Disk am NFS Server vergrößern (+500GB)"
echo "  - Benefit: Quick fix ohne Migration"
echo "  - Risk: Problem verschoben, nicht gelöst"
echo ""
echo "OPTION C: Stocki Node dekommissionieren"
echo "  - Aktion: Library zu Anker kopieren, VM 210 herunterfahren"
echo "  - Benefit: Nur ein Production Node"
echo "  - Risk: Kein Failover, kein Dual-Site Setup"
echo ""

echo "[6/6] Nach Cleanup - Neuer Status:"
ssh -J "$STOCKI_JUMP" "$STOCKI_VM" "df -h /var/azuracast/music_storage"

echo ""
echo "=== NÄCHSTE SCHRITTE ==="
echo "1. Entscheidung treffen: Option A, B oder C"
echo "2. Wenn Option A: scripts/radio/migrate_stocki_to_storage_node.sh ausführen"
echo "3. VM 210 AzuraCast Container neu starten"
echo "4. Storage-Status verifizieren: < 80%"
