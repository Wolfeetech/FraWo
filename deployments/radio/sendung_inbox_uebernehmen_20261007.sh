#!/usr/bin/env bash
# #1916: Die letzten Sende-Links (aktive Sendungen 01-10), die noch in die Inbox zeigen, auf die Master_Library umhaengen.
# Entscheidung Claude 07.10.2026: Titel laufen bereits in den Sendungen (von Wolf kuratiert) -> uebernehmen.
# Aufruf auf dem ProDesk als Datei (nicht per stdin: pct exec liest stdin): bash /root/sendung_inbox_uebernehmen_20261007.sh
# Ablauf: Kopie der Inbox-Datei -> Putz-/Ablage-Strecke wie radio_neuzugang.sh -> Link umhaengen.
# Inbox-Originale bleiben unberuehrt. Rueckweg: $SICH/links_vorher.tsv (Link<TAB>altes Ziel) -> ln -sfn.
set -euo pipefail
LIVE=/anker-backup/musik-umzug-20261005
NAME=sendung-uebernahme-20261007
SICH=/var/lib/beets/$NAME
ank() { ssh -o BatchMode=yes root@10.1.0.92 "$@"; }  # mit Heredoc/Umleitung aufrufen
ct() { pct exec 120 -- "$@" < /dev/null; }
ctin() { pct exec 120 -- "$@"; }

echo "=== 1 Inbox-Links finden und Dateien kopieren"
ank "bash -s" <<EOF
set -e
cd $LIVE/Curated_Playlists
mkdir -p $LIVE/Inbox/$NAME; : > /root/$NAME.links
i=0
for d in 0[1-9]_* 10_*; do
  find "\$d" -type l | while IFS= read -r l; do
    z=\$(readlink "\$l")
    case "\$z" in */Inbox/*) ;; *) continue;; esac
    q=\$(cd "\$(dirname "\$l")" && realpath -s "\$z")   # Links sind relativ (../../Inbox/...)
    [ -s "\$q" ] || { echo "LEER (0 Byte, bleibt in Inbox): \$l" >&2; continue; }
    i=\$(wc -l < /root/$NAME.links); n=\$(printf %03d \$i)
    mkdir -p "$LIVE/Inbox/$NAME/\$n"; cp -p "\$q" "$LIVE/Inbox/$NAME/\$n/"
    printf '%s\t%s\t%s\n' "$LIVE/Curated_Playlists/\$l" "\$z" "/mnt/music/Inbox/$NAME/\$n/\$(basename "\$q")" >> /root/$NAME.links
  done
done
wc -l < /root/$NAME.links
EOF

ct mkdir -p "$SICH"
ank "cat /root/$NAME.links" | ctin sh -c "cat > $SICH/links_vorher.tsv"
echo "=== 2 Putzen"
ct python3 /var/lib/beets/radio_ape_entfernen.py --root "/mnt/music/Inbox/$NAME" --sicherung "$SICH/ape" --ausfuehren | tail -1
ct python3 /var/lib/beets/radio_titel_putzen.py --root "/mnt/music/Inbox/$NAME" --sicherung "$SICH/titel" --ausfuehren | tail -1
ct python3 /var/lib/beets/radio_cover_entfernen.py --root "/mnt/music/Inbox/$NAME" --sha1 /var/lib/beets/entfernen_sha1.txt --sicherung "$SICH/cover" --ausfuehren | tail -1
echo "=== 3 Ablegen"
ct python3 /var/lib/beets/radio_neuzugang_ablegen.py --quelle "/mnt/music/Inbox/$NAME" --sicherung "$SICH/ablage" --ausfuehren | tail -1

echo "=== 4 Links umhaengen (neu abgelegt oder vorhandene Dublette in der Bibliothek)"
ct sh -c "cat $SICH/ablage/ablage.tsv $SICH/ablage/dubletten.tsv 2>/dev/null" > /tmp/$NAME.ziele
ank "cat > /root/$NAME.ziele" < /tmp/$NAME.ziele
ank "bash -s" <<EOF
umgehaengt=0; offen=0
while IFS=\$'\t' read -r link alt kopie; do
  neu=\$(awk -F'\t' -v k="\$kopie" '\$1==k{print \$2; exit}' /root/$NAME.ziele)
  neu_a=\$(printf %s "\$neu" | sed 's#^/mnt/music#$LIVE#')
  if [ -n "\$neu" ] && [ -e "\$neu_a" ]; then
    ln -sfn "\$(realpath -s --relative-to="\$(dirname "\$link")" "\$neu_a")" "\$link"; umgehaengt=\$((umgehaengt+1))
  else
    echo "OFFEN (unklar, bleibt in Inbox): \$link"; offen=\$((offen+1))
  fi
done < /root/$NAME.links
echo "umgehaengt: \$umgehaengt | offen: \$offen"
EOF
rm -f /tmp/$NAME.ziele
