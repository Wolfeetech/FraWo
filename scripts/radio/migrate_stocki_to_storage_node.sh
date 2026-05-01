#!/bin/bash
# MIGRATE STOCKI MUSIC LIBRARY TO STORAGE NODE
# Datum: 2026-04-30
# Ziel: 283GB yourparty_Libary von NFS zu Storage Node SMB

set -euo pipefail

STOCKI_VM="192.168.178.210"
STOCKI_JUMP="stock-pve"
STORAGE_NODE="10.1.0.30"
STORAGE_SHARE="Media"
STORAGE_PATH="yourparty_Libary"

echo "=== STOCKI MUSIC LIBRARY MIGRATION ==="
echo "Source: 192.168.178.25:/mnt/music_hdd/yourparty_Libary"
echo "Target: //$STORAGE_NODE/$STORAGE_SHARE/$STORAGE_PATH"
echo "Size: 283GB, 23.461 Tracks"
echo ""

# PHASE 1: Storage Node vorbereiten
echo "[PHASE 1/5] Storage Node vorbereiten..."
ssh root@$STORAGE_NODE "
  echo '=== Storage Node Check ==='
  df -h /srv/storage/media

  echo ''
  echo 'Creating directory: $STORAGE_PATH'
  mkdir -p /srv/storage/media/$STORAGE_PATH
  chown nobody:nogroup /srv/storage/media/$STORAGE_PATH
  chmod 775 /srv/storage/media/$STORAGE_PATH
"

# PHASE 2: Rsync-Test (Dry-Run)
echo ""
echo "[PHASE 2/5] Rsync Dry-Run (Test)..."
echo "ACHTUNG: Das ist nur ein Test! Keine Dateien werden kopiert."
read -p "Fortfahren? [y/N] " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
  echo "Abgebrochen."
  exit 1
fi

ssh -J "$STOCKI_JUMP" "$STOCKI_VM" "
  rsync -avzn --progress --stats \
    /var/azuracast/music_storage/yourparty_Libary/ \
    root@$STORAGE_NODE:/srv/storage/media/$STORAGE_PATH/
" | tail -20

# PHASE 3: Echte Migration
echo ""
echo "[PHASE 3/5] ECHTE MIGRATION starten..."
echo "WARNUNG: Dies wird 283GB über das Netzwerk kopieren!"
echo "Geschätzte Zeit: 1-3 Stunden (abhängig von Netzwerk)"
read -p "Wirklich fortfahren? [y/N] " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
  echo "Abgebrochen."
  exit 1
fi

ssh -J "$STOCKI_JUMP" "$STOCKI_VM" "
  rsync -avz --progress \
    /var/azuracast/music_storage/yourparty_Libary/ \
    root@$STORAGE_NODE:/srv/storage/media/$STORAGE_PATH/
"

# PHASE 4: Verification
echo ""
echo "[PHASE 4/5] Verifikation..."
STOCKI_COUNT=$(ssh -J "$STOCKI_JUMP" "$STOCKI_VM" "find /var/azuracast/music_storage/yourparty_Libary -type f | wc -l")
STORAGE_COUNT=$(ssh root@$STORAGE_NODE "find /srv/storage/media/$STORAGE_PATH -type f | wc -l")

echo "Stocki Files: $STOCKI_COUNT"
echo "Storage Files: $STORAGE_COUNT"

if [ "$STOCKI_COUNT" -eq "$STORAGE_COUNT" ]; then
  echo "✅ Migration erfolgreich! Dateianzahl stimmt überein."
else
  echo "⚠️ WARNUNG: Dateianzahl unterschiedlich!"
  exit 1
fi

# PHASE 5: VM 210 auf SMB umstellen
echo ""
echo "[PHASE 5/5] VM 210 fstab auf SMB umstellen..."
echo "ACHTUNG: Dies wird AzuraCast neu starten!"
read -p "Fortfahren? [y/N] " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
  echo "Migration abgeschlossen, aber fstab NICHT geändert."
  echo "VM 210 nutzt weiterhin NFS!"
  exit 0
fi

ssh -J "$STOCKI_JUMP" "$STOCKI_VM" "
  # Backup current fstab
  sudo cp /etc/fstab /etc/fstab.backup_\$(date +%Y%m%d_%H%M%S)

  # Credentials file erstellen
  sudo mkdir -p /etc/hs27
  sudo bash -c 'cat > /etc/hs27/storage-node-media.credentials <<EOF
username=STORAGE_USER
password=STORAGE_PASSWORD
EOF'
  sudo chmod 600 /etc/hs27/storage-node-media.credentials

  # NFS aus fstab entfernen
  sudo sed -i '/192.168.178.25/d' /etc/fstab

  # SMB hinzufügen
  echo '//$STORAGE_NODE/$STORAGE_SHARE /var/azuracast/music_storage cifs credentials=/etc/hs27/storage-node-media.credentials,uid=1000,gid=1000,file_mode=0660,dir_mode=0770,nofail 0 0' | sudo tee -a /etc/fstab

  # Unmount NFS
  sudo umount /var/azuracast/music_storage || true

  # Mount SMB
  sudo mount -a

  # Verify
  df -h /var/azuracast/music_storage
  ls -lah /var/azuracast/music_storage/$STORAGE_PATH | head -5

  # AzuraCast neu starten
  cd /var/azuracast
  docker compose restart
"

echo ""
echo "=== MIGRATION ABGESCHLOSSEN ==="
echo "✅ 283GB von NFS zu Storage Node kopiert"
echo "✅ VM 210 fstab auf SMB umgestellt"
echo "✅ AzuraCast Container neu gestartet"
echo ""
echo "NÄCHSTE SCHRITTE:"
echo "1. Verify: df -h auf VM 210 zeigt SMB Mount"
echo "2. Test: Radio Stream auf radio.yourparty.tech"
echo "3. NFS Server 192.168.178.25 kann jetzt entlastet werden"
