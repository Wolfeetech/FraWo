#!/bin/bash
# FraWo Pi 4 Onboarding Script
# Run as root on fresh Raspberry Pi OS (64-bit Bookworm)
# Usage: curl -s https://... | sudo bash
# Or: sudo bash pi_onboard.sh

set -e

NODE_NAME="${1:-pi-4}"
TS_AUTHKEY="${2:-}"  # Optional Tailscale auth key

echo "=== FraWo Raspberry Pi 4 Onboarding ==="
echo "Node name: $NODE_NAME"

# 1. System update
apt-get update -qq && apt-get upgrade -y -qq

# 2. Install Tailscale
if ! command -v tailscale &>/dev/null; then
    echo "Installing Tailscale..."
    curl -fsSL https://tailscale.com/install.sh | sh
fi

if [ -n "$TS_AUTHKEY" ]; then
    tailscale up --authkey="$TS_AUTHKEY" --ssh --hostname="$NODE_NAME"
else
    echo "No auth key provided. Run manually: tailscale up --ssh --hostname=$NODE_NAME"
fi

# 3. Install Node Exporter (ARM64)
NODE_EXPORTER_VERSION="1.8.2"
ARCH="arm64"
NODE_URL="https://github.com/prometheus/node_exporter/releases/download/v${NODE_EXPORTER_VERSION}/node_exporter-${NODE_EXPORTER_VERSION}.linux-${ARCH}.tar.gz"

echo "Installing Node Exporter v${NODE_EXPORTER_VERSION} (${ARCH})..."
cd /tmp
wget -q "$NODE_URL" -O node_exporter.tar.gz
tar xzf node_exporter.tar.gz
cp "node_exporter-${NODE_EXPORTER_VERSION}.linux-${ARCH}/node_exporter" /usr/local/bin/
chmod +x /usr/local/bin/node_exporter

# Create systemd service
cat > /etc/systemd/system/node_exporter.service << 'EOF'
[Unit]
Description=Node Exporter
After=network.target

[Service]
User=nobody
ExecStart=/usr/local/bin/node_exporter \
  --collector.thermal_zone \
  --collector.hwmon \
  --collector.systemd
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable --now node_exporter
echo "Node Exporter: $(systemctl is-active node_exporter)"

# 4. Check Pi temperature
PI_TEMP=$(cat /sys/class/thermal/thermal_zone0/temp 2>/dev/null || echo "0")
echo "Pi CPU Temp: $(echo "scale=1; $PI_TEMP/1000" | bc)°C"

# 5. Print Tailscale IP
TS_IP=$(tailscale ip -4 2>/dev/null || echo "not connected")
echo ""
echo "=== FERTIG ==="
echo "Tailscale IP: $TS_IP"
echo "Node Exporter: http://${TS_IP}:9100/metrics"
echo ""
echo "Naechste Schritte:"
echo "  1. Prometheus target eintragen: ${TS_IP}:9100 (instance=$NODE_NAME)"
echo "  2. Grafana Dashboard aktualisieren"
echo "  3. Odoo Task #254 auf Erledigt setzen"
