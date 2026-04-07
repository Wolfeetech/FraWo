#!/bin/bash
# FIX DNS SCRIPT
IP_STRATO="81.169.145.133"
VM_ID=220
PVE_HOST="100.69.179.87"

echo "📍 Fixing DNS/Hosts on VM $VM_ID via PVE $PVE_HOST..."

# Add to host /etc/hosts
ssh -o StrictHostKeyChecking=no root@$PVE_HOST "qm guest exec $VM_ID -- bash -c \"grep -q smtp.strato.de /etc/hosts || echo '$IP_STRATO smtp.strato.de' >> /etc/hosts\""

# Add to Docker containers /etc/hosts
ssh -o StrictHostKeyChecking=no root@$PVE_HOST "qm guest exec $VM_ID -- bash -c \"docker ps -q | xargs -I {} docker exec {} bash -c 'grep -q smtp.strato.de /etc/hosts || echo \\\"$IP_STRATO smtp.strato.de\\\" >> /etc/hosts'\""

# Verify ping from within Odoo container
ssh -o StrictHostKeyChecking=no root@$PVE_HOST "qm guest exec $VM_ID -- bash -c \"docker exec odoo_web_1 ping -c 1 smtp.strato.de\""
