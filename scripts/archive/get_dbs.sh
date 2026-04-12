qm guest exec 220 -- docker exec odoo_db_1 psql -U odoo -d postgres -t -c "SELECT datname FROM pg_database WHERE datistemplate = false;"
