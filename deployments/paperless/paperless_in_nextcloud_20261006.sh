#!/usr/bin/env bash
# Paperless-Dokumente lesbar benennen und schreibgeschuetzt in Nextcloud zeigen (Odoo #1927, DOCS/ABLAGEORDNUNG.md).
# Laeuft auf dem OptiPlex-Host (10.1.0.227):  ssh root@10.1.0.227 'bash -s' < paperless_in_nextcloud_20261006.sh
#
# 1. CT110: PAPERLESS_FILENAME_FORMAT nach Ablageordnung (10_Finanzen/2026/Absender/Datum Titel), Neustart,
#    vorhandene Dokumente umbenennen (document_renamer). Sicherung .env.bak-20261006-dateinamen.
# 2. CT110: Benutzer nc-lesen, nur SFTP, nur lesen (internal-sftp -R), keine Shell/Weiterleitung.
#    Passwort zufaellig, landet nur in Vaultwarden (frawo-secret) und in Nextclouds verschluesselter Konfig.
# 3. Nextcloud (VM300): externe Ablage "/Dokumente (Paperless)" fuer wolf, schreibgeschuetzt.
set -euo pipefail
FMT="{% if 'finanzen' in tag_name_list %}10_Finanzen{% elif 'vertraege' in tag_name_list %}20_Verträge{% elif 'amt_behoerden' in tag_name_list %}30_Amt_und_Behörden{% elif 'wohnen' in tag_name_list %}50_Wohnen{% elif 'arbeit' in tag_name_list %}60_Arbeit_und_Gewerbe{% elif 'projekte' in tag_name_list %}70_Projekte{% else %}00_Unsortiert{% endif %}/{{ created_year }}/{{ correspondent }}/{{ created }} {{ title }}"
ORIG=/opt/paperless/media/documents/originals

echo "== 1/3 Paperless: Dateinamen nach Ablageordnung"
printf 'PAPERLESS_FILENAME_FORMAT=%s\n' "$FMT" > /tmp/pl_fmt.txt
pct push 110 /tmp/pl_fmt.txt /tmp/pl_fmt.txt && rm -f /tmp/pl_fmt.txt
pct exec 110 -- bash -c '
  set -e; cd /opt/paperless
  [ -f .env.bak-20261006-dateinamen ] || cp -p .env .env.bak-20261006-dateinamen
  grep -v "^PAPERLESS_FILENAME_FORMAT=" .env > .env.neu; cat /tmp/pl_fmt.txt >> .env.neu
  cat .env.neu > .env; rm -f .env.neu /tmp/pl_fmt.txt
  docker compose up -d 2>&1 | tail -2
  for i in $(seq 1 60); do docker exec paperless-webserver curl -fs -o /dev/null http://localhost:8000/ 2>/dev/null && break; sleep 3; done
  docker exec paperless-webserver document_renamer 2>&1 | tail -2
  echo "Ordner jetzt: $(ls '"$ORIG"' | tr "\n" " ")"
'

echo "== 2/3 CT110: Lesezugang nc-lesen (nur SFTP, nur lesen)"
PW=$(python3 -c "import secrets,string; a=string.ascii_letters+string.digits; print(''.join(secrets.choice(a) for _ in range(32)))")
printf '%s\n' "$PW" | pct exec 110 -- bash -c '
  set -e
  id nc-lesen >/dev/null 2>&1 || useradd --system --no-create-home --home-dir '"$ORIG"' --shell /usr/sbin/nologin nc-lesen
  read -r P; echo "nc-lesen:$P" | chpasswd
  [ -f /etc/ssh/sshd_config.bak-20261006 ] || cp -p /etc/ssh/sshd_config /etc/ssh/sshd_config.bak-20261006
  grep -q "^Match User nc-lesen" /etc/ssh/sshd_config || printf "\nMatch User nc-lesen\n    ForceCommand internal-sftp -R -d '"$ORIG"'\n    PasswordAuthentication yes\n    AllowTcpForwarding no\n    X11Forwarding no\n    PermitTTY no\n" >> /etc/ssh/sshd_config
  sshd -t && systemctl reload ssh && echo "sshd neu geladen"
'
printf '%s' "$PW" | frawo-secret ablegen "Paperless CT110 SFTP nc-lesen (Nextcloud-Ansicht)" nc-lesen sftp://10.1.0.100 2>&1 | grep -E "abgelegt|aktualisiert|FEHLER"

echo "== 3/3 Nextcloud: externe Ablage /Dokumente (Paperless), nur lesen"
printf '%s\n' "$PW" | ssh -o BatchMode=yes root@10.1.0.21 '
  set -e; read -r P; OCC="docker exec -u www-data nextcloud_app_1 php occ"
  if $OCC files_external:list wolf 2>/dev/null | grep -q "Dokumente (Paperless)"; then echo "schon vorhanden"
  else
    OUT=$($OCC files_external:create --user wolf "/Dokumente (Paperless)" sftp password::password \
      -c host=10.1.0.100 -c root='"$ORIG"' -c user=nc-lesen -c password="$P")
    ID=$(echo "$OUT" | grep -o "[0-9]\+" | tail -1); echo "Ablage-ID $ID"
    $OCC files_external:option $ID readonly true
    $OCC files_external:option $ID filesystem_check_changes 1
    $OCC files_external:verify $ID | grep -i -E "status|message"
  fi
'
unset PW
echo "Fertig."
