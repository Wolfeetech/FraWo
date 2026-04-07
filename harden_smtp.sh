#!/bin/bash
# HARDEN SMTP RESOLUTION SCRIPT
# To be run on the PVE Host (Anker) or Toolbox

STRATO_IP="81.169.145.133"

# VM 220: Odoo
echo "🚀 Hardening Odoo (VM 220)..."
ssh -o StrictHostKeyChecking=no root@100.69.179.87 "qm guest exec 220 -- bash -c 'cd /opt/homeserver2027/stacks/odoo && sed -i \"/services:/a \ \ web:\n    extra_hosts:\n      - \\\"smtp.strato.de:$STRATO_IP\\\"\" docker-compose.yml && docker-compose up -d'"

# VM 200: Nextcloud
echo "🚀 Hardening Nextcloud (VM 200)..."
ssh -o StrictHostKeyChecking=no root@100.69.179.87 "qm guest exec 200 -- bash -c 'cd /opt/homeserver2027/stacks/nextcloud && sed -i \"/services:/a \ \ nextcloud:\n    extra_hosts:\n      - \\\"smtp.strato.de:$STRATO_IP\\\"\" docker-compose.yml && docker-compose up -d'"
