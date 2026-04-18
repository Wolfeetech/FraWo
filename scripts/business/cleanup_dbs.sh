#!/usr/bin/env bash
# cleanup_dbs.sh
# Final cleanup of legacy Odoo databases after confirmed migration & backup

for db in "FraWo_Live" "Recovery_DB" "FraWo_GbR_Backup"; do
    echo "Dropping database $db..."
    psql -U odoo -d postgres -c "DROP DATABASE \"$db\";"
done

echo "Deleting temporary migration files..."
rm -f /tmp/consolidate_odoo.sh /tmp/export_legacy_odoo.py /tmp/import_to_odoo.py /tmp/odoo_migration_data.json /tmp/check_schema.sql
