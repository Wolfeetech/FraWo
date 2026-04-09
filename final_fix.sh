#!/bin/bash
# Odoo SSOT Restoration
echo "Fixing Odoo database reference..."
qm guest exec 220 -- sed -i 's/POSTGRES_DB=postgres/POSTGRES_DB=FraWo_GbR/g' /opt/homeserver2027/stacks/odoo/docker-compose.yml
qm guest exec 220 -- bash -c "cd /opt/homeserver2027/stacks/odoo && docker-compose up -d"

echo "Verifying Odoo reachability..."
sleep 5
qm guest exec 220 -- curl -I http://localhost:8069

echo "Nextcloud Stocki Storage Audit..."
# Preliminary reachability check for Stockenweiler PVE
ping -c 2 100.91.20.116
