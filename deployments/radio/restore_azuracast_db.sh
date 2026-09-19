#!/bin/bash
set -e

echo "Starting MariaDB restore from yesterday's backup..."
sudo docker exec azuracast bash -c '
  unzip -p /var/azuracast/backups/automatic_backup_20260918_040201.zip tmp/azuracast_backup_mariadb/db.sql | /usr/bin/mariadb -u"$MYSQL_USER" -p"$MYSQL_PASSWORD" "$MYSQL_DATABASE"
'
echo "Restore finished! Restarting radio station..."
sudo docker exec azuracast azuracast_cli azuracast:radio:restart 1
echo "RADIO_RESTORED_AND_RESTARTED"
