#!/bin/bash
# FraWo Infrastructure Monitoring Setup
# Run this on Proxmox host: bash setup_monitoring.sh

set -e

echo "[*] Setting up FraWo monitoring..."

# 1. Disk Space Alert
cat > /usr/local/bin/frawo-disk-check.sh <<'EOF'
#!/bin/bash
THRESHOLD=85
USAGE=$(lvs --noheadings -o data_percent pve/data | tr -d ' %')

if [ "${USAGE%.*}" -gt "$THRESHOLD" ]; then
    echo "CRITICAL: LVM Pool at ${USAGE}% - Cleanup needed!"
    # TODO: Add email/webhook notification
fi
EOF

chmod +x /usr/local/bin/frawo-disk-check.sh

# 2. Cron job - check every 6 hours
(crontab -l 2>/dev/null; echo "0 */6 * * * /usr/local/bin/frawo-disk-check.sh") | crontab -

# 3. Odoo VM uptime check
cat > /usr/local/bin/frawo-vm-check.sh <<'EOF'
#!/bin/bash
VM_ID=220
STATUS=$(qm status $VM_ID | awk '{print $2}')

if [ "$STATUS" != "running" ]; then
    echo "CRITICAL: Odoo VM 220 is $STATUS - Starting..."
    qm start $VM_ID
fi
EOF

chmod +x /usr/local/bin/frawo-vm-check.sh

# 4. Cron job - check every 5 minutes
(crontab -l 2>/dev/null; echo "*/5 * * * * /usr/local/bin/frawo-vm-check.sh") | crontab -

# 5. Cloudflare Tunnel watchdog
cat > /usr/local/bin/frawo-tunnel-check.sh <<'EOF'
#!/bin/bash
if ! pgrep -f "cloudflared.*tunnel" > /dev/null; then
    echo "CRITICAL: Cloudflare Tunnel down - Restarting..."
    systemctl restart cloudflared
fi
EOF

chmod +x /usr/local/bin/frawo-tunnel-check.sh

# 6. Cron job - check every 5 minutes
(crontab -l 2>/dev/null; echo "*/5 * * * * /usr/local/bin/frawo-tunnel-check.sh") | crontab -

echo "[OK] Monitoring setup complete!"
echo ""
echo "Configured checks:"
echo "  - Disk space: Every 6 hours (85% threshold)"
echo "  - Odoo VM: Every 5 minutes"
echo "  - Cloudflare Tunnel: Every 5 minutes"
