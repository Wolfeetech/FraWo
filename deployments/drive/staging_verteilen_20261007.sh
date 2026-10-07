#!/usr/bin/env bash
# Festhaengende Dateien aus dem Staging der ALTEN Drive-Abholung (Anker, /opt/frawo-gdrive-bridge/staging)
# nach DOCS/ABLAGEORDNUNG.md verteilen (Odoo #1927). Laeuft auf dem Anker. Nur KOPIEREN, Staging bleibt
# bis zur Abnahme liegen.
#   Dokumente      -> Paperless-Consume auf CT110 (OptiPlex), direkt per pct push (nicht ueber Drive)
#   Musik          -> Radio-Eingang /anker-backup/musik-umzug-20261005/Inbox/neuzugang-20261007 (Reinigung danach)
#   Programme etc. -> Nextcloud wolf/files/80_Technik/Software/Installer_2026-10 (VM300), Dubletten per SHA-256
set -uo pipefail
ST=/opt/frawo-gdrive-bridge/staging
MUSIK=/anker-backup/musik-umzug-20261005/Inbox/neuzugang-20261007
OPTI=root@10.1.0.227
NC=/var/lib/docker/volumes/nextcloud_nextcloud/_data/data/wolf/files/80_Technik/Software/Installer_2026-10
cd "$ST" || exit 1
mkdir -p "$MUSIK"
d=0; m=0; s=0; x=0

# 1) Musik: Ordner des Uploads und lose Audiodateien/Alben-Zips
for o in Luki nikotine Bandcamp rekordbox Playlists PioneerDJ; do
  [ -d "$o" ] && cp -a --no-clobber "$o" "$MUSIK/" && m=$((m + $(find "$o" -type f | wc -l)))
done
for f in *.mp3 *.flac *.wav "Bliss Inc. - echo-chambered.zip"; do
  [ -f "$f" ] && cp -a --no-clobber "$f" "$MUSIK/" && m=$((m+1))
done

# 2) Dokumente: Belege, Noerpel-Scans, Zaehlerfoto -> Paperless (Paperless verwirft Dubletten selbst)
TMP=$(mktemp -d); trap 'rm -rf "$TMP"' EXIT
while IFS= read -r -d '' f; do
  n=$(basename "$f" | tr -d '\r')
  case "$n" in *.pdf|*.PDF|*.jpg|*.jpeg|*.docx) ;; *) n="$n.pdf";; esac
  cp -a "$f" "$TMP/$n"; d=$((d+1))
done < <(find . -maxdepth 1 -type f \( -name 'Altablage*' -o -iname '*.pdf' -o -name 'Noerpel_*' -o -name 'zaehlerstrom_*' -o -iname '*.docx' \) -print0)
find "Gehaltsnachweise Noerpel" -type f -print0 2>/dev/null | while IFS= read -r -d '' f; do cp -a "$f" "$TMP/Noerpel_$(basename "$f")"; done
tar -C "$TMP" -cf - . | ssh -o BatchMode=yes $OPTI 'Z=$(mktemp -d) && tar -C "$Z" -xf - && for f in "$Z"/*; do pct push 110 "$f" "/opt/paperless/consume/$(basename "$f")" --user 1000 --group 1000; done; n=$(ls "$Z" | wc -l); rm -rf "$Z"; echo "an Paperless uebergeben: $n"'

# 3) Programme, Firmware, Modelle, Produktbilder -> Nextcloud, ohne Dubletten
ssh -o BatchMode=yes $OPTI "ssh -o BatchMode=yes root@10.1.0.21 'mkdir -p \"$NC\"; cd /var/lib/docker/volumes/nextcloud_nextcloud/_data/data/wolf/files && find 80_Technik -type f -size +100k -exec sha256sum {} +'" > /tmp/nc_sha.txt
find . -maxdepth 2 -type f \( -iname '*.exe' -o -iname '*.zip' -o -iname '*.bin' -o -iname '*.webp' -o -iname '*.ini' \) \
     ! -name 'Bliss Inc.*' -print0 | while IFS= read -r -d '' f; do
  h=$(sha256sum "$f" | cut -d' ' -f1)
  if grep -q "^$h " /tmp/nc_sha.txt; then echo "schon in Nextcloud: $f" >&2; continue; fi
  echo "$h  x" >> /tmp/nc_sha.txt
  printf '%s\0' "$f"
done > /tmp/nc_neu.lst
tr '\0' '\n' < /tmp/nc_neu.lst | sed 's/^/  neu: /'
tar --null -T /tmp/nc_neu.lst -cf - | ssh -o BatchMode=yes $OPTI "ssh -o BatchMode=yes root@10.1.0.21 'tar -C \"$NC\" -xf - && chown -R 33:33 \"$NC\" && docker exec -u www-data nextcloud_app_1 php occ files:scan --path=wolf/files/80_Technik/Software >/dev/null && echo Nextcloud ok'"
echo "Musik kopiert: $m Dateien -> $MUSIK"
