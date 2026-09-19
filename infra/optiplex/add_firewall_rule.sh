#!/bin/bash
set -e

if ! grep -q "11434" /etc/pve/firewall/cluster.fw; then
    sed -i '/dport 8006.*Default-LAN/a IN ACCEPT -source 10.0.0.0/24 -p tcp -dport 11434 -log nolog   # Ollama AI API (StudioPC & LAN)' /etc/pve/firewall/cluster.fw
    sed -i '/dport 8007.*PBS/a IN ACCEPT -source 10.1.0.0/24 -p tcp -dport 11434 -log nolog   # Ollama AI API (Paperless & Server)' /etc/pve/firewall/cluster.fw
    pve-firewall compile
    pve-firewall restart
    echo "FIREWALL_UPDATED_AND_RESTARTED"
else
    echo "RULE_ALREADY_PRESENT"
fi
