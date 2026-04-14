#!/bin/bash
# repair_stacks.sh - Robustly Repair Odoo and Nextcloud Stacks on Guest VMs

STRATO_IP="81.169.145.133"

# --- ODOO (VM 220) ---
echo "🛠️ Repairing Odoo (VM 220)..."
cat <<EOF > /tmp/odoo.yml
services:
  db:
    image: postgres:15
    volumes:
      - db-data:/var/lib/postgresql/data
    environment:
      - POSTGRES_DB=postgres
      - POSTGRES_PASSWORD=odoo
      - POSTGRES_USER=odoo
  web:
    image: odoo:17
    depends_on:
      - db
    ports:
      - "8069:8069"
    environment:
      - HOST=db
      - USER=odoo
      - PASSWORD=odoo
    volumes:
      - odoo-data:/var/lib/odoo
    extra_hosts:
      - "smtp.strato.de:$STRATO_IP"

volumes:
  odoo-data:
  db-data:
EOF

B64_ODOO=$(base64 -w0 /tmp/odoo.yml)
qm guest exec 220 -- bash -c "echo $B64_ODOO | base64 -d > /opt/homeserver2027/stacks/odoo/docker-compose.yml"
qm guest exec 220 -- bash -c "cd /opt/homeserver2027/stacks/odoo && docker-compose build && docker-compose up -d"

# --- NEXTCLOUD (VM 200) ---
echo "🛠️ Repairing Nextcloud (VM 200)..."
cat <<EOF > /tmp/nextcloud.yml
services:
  db:
    image: mariadb:10.11
    command: --transaction-isolation=READ-COMMITTED --binlog-format=ROW
    volumes:
      - db:/var/lib/mysql
    environment:
      - MYSQL_ROOT_PASSWORD=nextcloud
      - MYSQL_PASSWORD=nextcloud
      - MYSQL_DATABASE=nextcloud
      - MYSQL_USER=nextcloud
  redis:
    image: redis:alpine
  nextcloud:
    image: nextcloud:latest
    depends_on:
      - db
      - redis
    ports:
      - "8080:80"
    environment:
      - MYSQL_PASSWORD=nextcloud
      - MYSQL_DATABASE=nextcloud
      - MYSQL_USER=nextcloud
      - MYSQL_HOST=db
      - REDIS_HOST=redis
    volumes:
      - nextcloud:/var/www/html
    extra_hosts:
      - "smtp.strato.de:$STRATO_IP"

volumes:
  nextcloud:
  db:
EOF

B64_NC=$(base64 -w0 /tmp/nextcloud.yml)
qm guest exec 200 -- bash -c "echo $B64_NC | base64 -d > /opt/homeserver2027/stacks/nextcloud/docker-compose.yml"
qm guest exec 200 -- bash -c "cd /opt/homeserver2027/stacks/nextcloud && docker-compose build && docker-compose up -d"

echo "✅ Repair finished."
