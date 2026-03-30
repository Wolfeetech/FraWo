#!/bin/bash
export HOMESERVER_PROXMOX_ROOT_PASSWORD='11011995'

echo "Warte auf Proxmox Server 192.168.2.10..."
while ! ping -c 1 192.168.2.10 &> /dev/null; do
    echo "Noch nicht online..."
    sleep 5
done

echo "Proxmox Server ist online. Warte zusaetzlich auf VM 200..."
while ! ./scripts/proxmox_remote_exec.sh 'qm guest exec 200 -- ping -c 1 127.0.0.1' >> /dev/null 2>&1; do
    echo "VM 200 QEMU Agent noch nicht bereit..."
    sleep 5
done

echo "VM 200 ist online. Aktiviere Nextcloud Mail..."
./scripts/proxmox_remote_exec.sh "qm guest exec 200 -- bash -c 'cd /opt/homeserver2027/stacks/nextcloud && docker-compose exec -T -u www-data app php occ app:install mail'"
echo "Nextcloud Mail erfolgreich installiert."
