#!/usr/bin/env bash
# deploy_cloudflare_tunnel_pve.sh
# Deploys cloudflared on Proxmox host to proxy Odoo (VM 220)

set -e

TOKEN=$1

if [ -z "$TOKEN" ]; then
    echo "Usage: $0 <token>"
    exit 1
fi

echo "Installing cloudflared on Proxmox host..."
# Download the latest deb for amd64
wget https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb -O /tmp/cloudflared.deb
dpkg -i /tmp/cloudflared.deb

echo "Configuring cloudflared service..."
cloudflared service install "$TOKEN"

echo "Tunnel started and service installed."
