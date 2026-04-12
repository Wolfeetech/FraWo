#!/bin/bash
# Toolbox-based Hardening Script for Anker VMs
# Run this from the Toolbox (100.99.206.128)

STRATO_IP="81.169.145.133"
PVE_HOST="100.69.179.87"

echo "📍 Starting Base Hardening (SMTP DNS) for Anker..."

# --- Odoo (VM 220) ---
echo "🚀 Hardening Odoo (VM 220)..."
cat <<EOF > /tmp/odoo_compose.yml
version: '3'
services:
  web:
    image: odoo:16.0
    depends_on:
      - db
    ports:
      - "8069:8069"
    volumes:
      - odoo-data:/var/lib/odoo
      - ./config:/etc/odoo
    extra_hosts:
      - "smtp.strato.de:$STRATO_IP"
  db:
    image: postgres:15
    environment:
      - POSTGRES_DB=postgres
      - POSTGRES_PASSWORD=odoo
      - POSTGRES_USER=odoo
    volumes:
      - db-data:/var/lib/postgresql/data

volumes:
  odoo-data:
  db-data:
EOF

OD_B64=$(base64 -w0 /tmp/odoo_compose.yml)
ssh -o StrictHostKeyChecking=no root@$PVE_HOST "qm guest exec 220 -- bash -c 'echo \"$OD_B64\" | base64 -d > /opt/homeserver2027/stacks/odoo/docker-compose.yml && cd /opt/homeserver2027/stacks/odoo && docker-compose up -d'"

# --- Nextcloud (VM 200) ---
echo "🚀 Hardening Nextcloud (VM 200)..."
cat <<EOF > /tmp/nextcloud_compose.yml
version: '3'
services:
  db:
    image: mariadb:10.6
    restart: always
    command: --transaction-isolation=READ-COMMITTED --binlog-format=ROW
    volumes:
      - db:/var/lib/mysql
    environment:
      - MYSQL_ROOT_PASSWORD=nextcloud
      - MYSQL_PASSWORD=nextcloud
      - MYSQL_DATABASE=nextcloud
      - MYSQL_USER=nextcloud

  nextcloud:
    image: nextcloud:latest
    restart: always
    ports:
      - 8080:80
    links:
      - db
    volumes:
      - nextcloud:/var/www/html
    environment:
      - MYSQL_PASSWORD=nextcloud
      - MYSQL_DATABASE=nextcloud
      - MYSQL_USER=nextcloud
      - MYSQL_HOST=db
    extra_hosts:
      - "smtp.strato.de:$STRATO_IP"
    depends_on:
      - db
      - redis

  redis:
    image: redis:alpine
    restart: always

volumes:
  nextcloud:
  db:
EOF

NC_B64=$(base64 -w0 /tmp/nextcloud_compose.yml)
ssh -o StrictHostKeyChecking=no root@$PVE_HOST "qm guest exec 200 -- bash -c 'echo \"$NC_B64\" | base64 -d > /opt/homeserver2027/stacks/nextcloud/docker-compose.yml && cd /opt/homeserver2027/stacks/nextcloud && docker-compose up -d'"

echo "✅ Hardening Complete."
