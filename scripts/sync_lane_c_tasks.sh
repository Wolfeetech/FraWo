#!/bin/bash
export HOMESERVER_PROXMOX_ROOT_PASSWORD='11011995'

# Task 1
./scripts/proxmox_remote_exec.sh "qm guest exec 220 -- bash -c 'cd /opt/homeserver2027/stacks/odoo && echo -e \"task = env['\\'project.task\\''].create({\\'name\\': \\'[Lane C] Tailscale Route Approval (10.1.0.0/24)\\', \\'description\\': \\'<ul><li>[ ] In login.tailscale.com/admin/machines die Route 10.1.0.0/24 bei toolbox approven.</li><li>[ ] Route springt auf active</li><li>[ ] Zuweisung an Wolfi (Operator)</li></ul>\\'})\n\" | docker-compose exec -T web odoo shell -d postgres'"

# Task 2
./scripts/proxmox_remote_exec.sh "qm guest exec 220 -- bash -c 'cd /opt/homeserver2027/stacks/odoo && echo -e \"task = env['\\'project.task\\''].create({\\'name\\': \\'[Lane C] Tailscale Split DNS Update\\', \\'description\\': \\'<ul><li>[ ] Restricted Nameserver fuer hs27.internal auf 10.1.0.20 umstellen</li><li>[ ] Zuweisung an Wolfi (Operator)</li></ul>\\'})\n\" | docker-compose exec -T web odoo shell -d postgres'"

echo "Tasks successfully dispatched to Odoo."
