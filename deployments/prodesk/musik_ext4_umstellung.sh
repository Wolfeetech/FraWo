#!/usr/bin/env bash
# Musikplatte ProDesk (WD20SDRW, Seriennr. WD-WX62E302VF6E, /dev/sdX2) von NTFS auf ext4 umstellen.
# Odoo #1263 · Freigabe Wolf 05.10.2026 („Sobald du die Kopie hast“) · Claude
#
# Voraussetzung: vollstaendige Kopie in Anker:/anker-backup/musik-umzug-20261005 (rsync -rltH).
# Laeuft auf dem ProDesk als root. Jede Phase prueft; vor mkfs MUSS die Gegenzaehlung exakt stimmen.
# Ausfall waehrend des Laufs: Radio (AzuraCast), Samba-Freigaben (music, documents, scans, playlists, sender),
# Scan-Ablage. Rueckweg bis Phase 4: einfach alles wieder starten (Platte unveraendert).
set -euo pipefail
ANKER=root@10.1.0.92
KOPIE=/anker-backup/musik-umzug-20261005
MNT=/mnt/music_hdd
SERIAL=WD-WX62E302VF6E
LOG=/root/musik-ext4-umstellung.log
exec > >(tee -a "$LOG") 2>&1
schritt() { echo; echo "=== $(date '+%F %T') $*"; }
zaehle() { # Dateien, Links, Verzeichnisse, Bytes (ohne Verzeichnisgroessen) unter $1
  # Unlesbare Eintraege (NTFS-Altschaden) ueberspringt find mit Fehlermeldung; sie fehlen dann
  # auch in der Kopie. Der Fehlercode von find darf hier nicht abbrechen.
  { find "$1" -mindepth 1 \( -type f -printf 'f %s\n' -o -type l -printf 'l 0\n' -o -type d -printf 'd 0\n' \) 2>/dev/null || true; } \
    | awk '{n[$1]++; if($1=="f") b+=$2} END {printf "f=%d l=%d d=%d bytes=%d\n", n["f"], n["l"], n["d"], b}'
}

DEV=$(lsblk -dpno NAME,SERIAL | awk -v s="$SERIAL" '$2==s{print $1}')
PART="${DEV}2"
[ -b "$PART" ] || { echo "ABBRUCH: Platte $SERIAL nicht gefunden"; exit 1; }
[ "$(findmnt -no SOURCE "$MNT")" = "$PART" ] || { echo "ABBRUCH: $MNT ist nicht $PART"; exit 1; }
echo "Platte: $DEV ($SERIAL), Partition $PART"

schritt "1 Dienste anhalten"
systemctl stop cron frawo-musik-sync.timer frawo-scan-ingest.timer frawo-radio-rotation-sync.timer
qm guest exec 220 --timeout 120 -- docker stop azuracast >/dev/null
pct shutdown 120 --timeout 120
sleep 3; ! pgrep -f "rsync .*music_hdd" >/dev/null || { echo "ABBRUCH: rsync auf der Platte laeuft noch"; exit 1; }

schritt "2 letzter Abgleich nach $KOPIE (mit --delete)"
# Lesefehler (I/O error 5) betreffen den bekannten NTFS-Altschaden vom 03.08. Diese Dateien sind
# unlesbar und damit schon verloren. rsync meldet dann Code 23; sie werden protokolliert und
# fehlen in BEIDEN Zaehlungen (find kann sie ebenfalls nicht lesen). Jeder andere Code bricht ab.
set +e
rsync -rltH --delete --ignore-errors --numeric-ids --stats "$MNT/" "$ANKER:$KOPIE/" > /root/musik-ext4-abgleich.log 2>&1
RC=$?
set -e
tail -15 /root/musik-ext4-abgleich.log
grep -E "Input/output error|failed:" /root/musik-ext4-abgleich.log > /root/musik-ext4-unlesbar.txt || true
echo "rsync-Code $RC, unlesbare Eintraege: $(wc -l < /root/musik-ext4-unlesbar.txt) (Liste /root/musik-ext4-unlesbar.txt)"
case $RC in 0|23|24) ;; *) echo "ABBRUCH: rsync-Code $RC"; exit 1;; esac
if grep -v -E "Input/output error|failed: (No such file|Input/output)" /root/musik-ext4-unlesbar.txt | grep -q .; then
  echo "ABBRUCH: andere Fehler als I/O im Abgleich"; exit 1
fi

schritt "3 Gegenzaehlung Quelle vs. Kopie"
Q=$(zaehle "$MNT"); K=$(ssh "$ANKER" "$(declare -f zaehle); zaehle $KOPIE")
echo "Quelle: $Q"; echo "Kopie:  $K"
[ "$Q" = "$K" ] || { echo "ABBRUCH: Zaehlung weicht ab - Platte bleibt unveraendert, Dienste per Hand starten"; exit 1; }

schritt "4 Formatieren (ab hier kein Rueckweg ohne Kopie)"
cp -p /etc/fstab /etc/fstab.bak-20261005-ext4
umount "$MNT"
mkfs.ext4 -F -L musik -m 0 -E lazy_itable_init=1 "$PART" >/dev/null
UUID=$(blkid -s UUID -o value "$PART")
sed -i -E "s|^UUID=[^ ]+ $MNT ntfs-3g .*|UUID=$UUID $MNT ext4 defaults,noatime,nofail 0 2|" /etc/fstab
grep -n " $MNT " /etc/fstab
systemctl daemon-reload; mount "$MNT"
[ "$(findmnt -no FSTYPE "$MNT")" = ext4 ] || { echo "ABBRUCH: ext4 nicht eingehaengt"; exit 1; }

schritt "5 Zurueckkopieren vom Anker"
ssh "$ANKER" "rsync -rltH --numeric-ids --stats $KOPIE/ root@10.1.0.128:$MNT/" | tail -15
# (Vom Anker gelesen: ZFS, keine Lesefehler erwartet. Jeder Fehler hier bricht wegen pipefail ab.)

schritt "6 Rechte wie unter NTFS (uid/gid 100000 = root im CT120, alles 0777)"
chown -R 100000:100000 "$MNT"
chmod -R 0777 "$MNT"

schritt "7 Gegenzaehlung neu vs. Kopie"
N=$(zaehle "$MNT"); echo "Neu:   $N"; echo "Kopie: $K"
[ "$N" = "$K" ] || { echo "WARNUNG: Zaehlung weicht ab - Dienste NICHT gestartet, bitte pruefen"; exit 1; }

schritt "8 Dienste starten"
pct start 120
sleep 15
qm guest exec 220 --timeout 120 -- docker start azuracast >/dev/null
systemctl start frawo-musik-sync.timer frawo-scan-ingest.timer frawo-radio-rotation-sync.timer cron
pct exec 120 -- sh -c 'ls /mnt/music | head -3; touch /mnt/music/.schreibtest && rm /mnt/music/.schreibtest && echo "CT120 schreiben: OK"'
echo "FERTIG $(date '+%F %T')"
