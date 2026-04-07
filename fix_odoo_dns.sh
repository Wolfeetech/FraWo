#!/bin/bash
# VM 220 Fix Script
# Run from Toolbox or Proxmox host

echo "🔧 Setting DNS on Odoo VM 220..."
ssh -o StrictHostKeyChecking=no root@100.69.179.87 "qm guest exec 220 -- bash -c 'resolvectl dns eth0 1.1.1.1 9.9.9.9 && resolvectl domain eth0 hs27.internal'"

echo "🌐 Verifying Internet Access..."
ssh -o StrictHostKeyChecking=no root@100.69.179.87 "qm guest exec 220 -- bash -c 'ping -c 3 google.com'"

echo "🐳 Checking Docker DNS..."
ssh -o StrictHostKeyChecking=no root@100.69.179.87 "qm guest exec 220 -- bash -c 'docker exec odoo_web_1 cat /etc/resolv.conf'"
