#!/bin/bash
# FINAL HARDEN SMTP RESOLUTION SCRIPT (Base64 Robust)

STRATO_IP="81.169.145.133"
HOST_PVE="100.69.179.87"

# VM 220: Odoo
echo "🚀 Hardening Odoo (VM 220)..."
# Create the desired compose file locally
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

# Encode and write
OD_B64=$(base64 -w0 /tmp/odoo_compose.yml)
ssh -o StrictHostKeyChecking=no root@$HOST_PVE "qm guest exec 220 -- bash -c 'echo $OD_B64 | base64 -d > /opt/homeserver2027/stacks/odoo/docker-compose.yml && cd /opt/homeserver2027/stacks/odoo && docker-compose up -d'"

# VM 200: Nextcloud
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
ssh -o StrictHostKeyChecking=no root@$HOST_PVE "qm guest exec 200 -- bash -c 'echo $NC_B64 | base64 -d > /opt/homeserver2027/stacks/nextcloud/docker-compose.yml && cd /opt/homeserver2027/stacks/nextcloud && docker-compose up -d'"
