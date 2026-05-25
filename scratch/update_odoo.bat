scp -i ~/.ssh/pve_ed25519 -o StrictHostKeyChecking=no scratch\odoo_optimized.conf root@100.69.179.87:/tmp/odoo.conf
ssh -i ~/.ssh/pve_ed25519 -o StrictHostKeyChecking=no root@100.69.179.87 "qm guest exec 220 -- bash -c 'cat > /opt/homeserver2027/stacks/odoo/odoo.conf' < /tmp/odoo.conf"
ssh -i ~/.ssh/pve_ed25519 -o StrictHostKeyChecking=no root@100.69.179.87 "qm guest exec 220 -- bash -c 'cd /opt/homeserver2027/stacks/odoo && docker compose restart odoo'"
