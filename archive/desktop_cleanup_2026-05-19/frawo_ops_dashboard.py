#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FRAWO Ops - Comprehensive Infrastructure Dashboard
Shows real-time status of all servers and services
"""

import requests
import urllib3
import socket
import time
import sys
import io
from datetime import datetime

# Force UTF-8 on Windows
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Infrastructure configuration
INFRASTRUCTURE = {
    "servers": {
        "Stockenweiler PVE": {
            "ip": "100.91.20.116",
            "ports": {"SSH": 22, "PVE Web": 8006, "SPICE": 3128},
            "expected_status": "online",
            "role": "Primary Proxmox Host",
            "containers": {
                "101": "AdGuard DNS",
                "103": "NPM (Nginx Proxy Manager)",
                "106": "WireGuard VPN",
                "108": "Vaultwarden",
                "109": "PBS Backup",
                "110": "n8n Automation",
                "120": "File Server",
                "130": "Mail Relay",
                "202": "MongoDB Primary",
                "207": "Radio WordPress",
                "208": "MariaDB Server",
                "211": "Radio API"
            }
        },
        "Toolbox (Anker PVE)": {
            "ip": "100.82.26.53",
            "local_ip": "10.1.0.20",
            "ports": {"SSH": 22, "HTTP": 80, "HTTPS": 443},
            "expected_status": "online",
            "role": "Core Services Hub (Caddy, DNS, Portal)",
            "hosts": [
                "portal.hs27.internal",
                "cloud.hs27.internal",
                "odoo.hs27.internal",
                "paperless.hs27.internal",
                "vault.hs27.internal",
                "ha.hs27.internal"
            ]
        },
        "Proxmox Anker": {
            "ip": "100.69.179.87",
            "local_ip": "10.1.0.92",
            "ports": {"SSH": 22, "PVE Web": 8006},
            "expected_status": "online",
            "role": "Secondary Proxmox Host"
        }
    },
    "services": {
        "Portal": "http://portal.hs27.internal/",
        "Nextcloud": "http://cloud.hs27.internal/",
        "Odoo ERP": "http://odoo.hs27.internal/",
        "Paperless": "http://paperless.hs27.internal/",
        "Vault": "http://vault.hs27.internal/",
        "Home Assistant": "http://ha.hs27.internal/",
        "PVE Web": "https://100.91.20.116:8006/"
    }
}

def check_port(host, port, timeout=2):
    """Check if a port is open"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((host, port))
        sock.close()
        return result == 0
    except:
        return False

def check_http_service(url, timeout=3):
    """Check HTTP service and return status"""
    try:
        start = time.time()
        response = requests.get(url, timeout=timeout, verify=False, allow_redirects=True)
        elapsed = (time.time() - start) * 1000
        return {
            "status": "online",
            "code": response.status_code,
            "time_ms": round(elapsed, 0)
        }
    except requests.exceptions.Timeout:
        return {"status": "timeout", "code": None, "time_ms": None}
    except requests.exceptions.ConnectionError:
        return {"status": "offline", "code": None, "time_ms": None}
    except Exception as e:
        return {"status": "error", "code": None, "time_ms": None}

def print_header():
    """Print dashboard header"""
    print("\n" + "="*100)
    print(f"{'FRAWO OPS - INFRASTRUCTURE DASHBOARD':^100}")
    print(f"{'Generated: ' + datetime.now().strftime('%Y-%m-%d %H:%M:%S'):^100}")
    print("="*100)

def print_server_status():
    """Print status of all servers"""
    print("\n🖥️  SERVER STATUS")
    print("-"*100)

    for name, config in INFRASTRUCTURE["servers"].items():
        ip = config["ip"]
        role = config.get("role", "")

        print(f"\n📦 {name}")
        print(f"   Role: {role}")
        print(f"   IP: {ip}", end="")
        if "local_ip" in config:
            print(f" (Local: {config['local_ip']})", end="")
        print()

        # Check ports
        ports_status = []
        for port_name, port in config["ports"].items():
            is_open = check_port(ip, port)
            icon = "✅" if is_open else "❌"
            ports_status.append(f"{icon} {port_name}:{port}")

        print(f"   Ports: {' | '.join(ports_status)}")

        # Show containers if available
        if "containers" in config:
            print(f"   Containers: {len(config['containers'])} running")
            for vmid, name_ct in list(config["containers"].items())[:3]:
                print(f"      • {vmid}: {name_ct}")
            if len(config["containers"]) > 3:
                print(f"      ... and {len(config['containers']) - 3} more")

        # Show hosted domains if available
        if "hosts" in config:
            all_offline = not any(check_port(ip, port) for port in config["ports"].values())
            status_msg = "⚠️  ALL OFFLINE (Toolbox is down)" if all_offline else "Hosting services"
            print(f"   {status_msg}:")
            for host in config["hosts"][:4]:
                print(f"      • {host}")

def print_services_status():
    """Print status of all web services"""
    print("\n\n🌐 WEB SERVICES")
    print("-"*100)
    print(f"{'Service':<20} {'Status':<12} {'Response':<15} {'URL':<50}")
    print("-"*100)

    for name, url in INFRASTRUCTURE["services"].items():
        result = check_http_service(url)

        if result["status"] == "online":
            status = f"✅ {result['code']}"
            response = f"{result['time_ms']}ms"
        elif result["status"] == "timeout":
            status = "⏱️  TIMEOUT"
            response = "> 3s"
        elif result["status"] == "offline":
            status = "❌ OFFLINE"
            response = "No connection"
        else:
            status = "⚠️  ERROR"
            response = "Unknown"

        print(f"{name:<20} {status:<12} {response:<15} {url:<50}")

def print_diagnostics():
    """Print diagnostics and recommendations"""
    print("\n\n🔍 DIAGNOSTICS & RECOMMENDATIONS")
    print("-"*100)

    toolbox_online = check_port("100.82.26.53", 22)
    anker_pve_online = check_port("100.69.179.87", 22)
    stock_pve_online = check_port("100.91.20.116", 22)

    issues = []

    if not toolbox_online:
        issues.append({
            "severity": "🔴 CRITICAL",
            "issue": "Toolbox server is OFFLINE",
            "impact": "All hs27.internal services unavailable (Portal, Odoo, Nextcloud, etc.)",
            "action": "1. Check if Anker PVE is powered on\n" +
                     "               2. If Anker PVE is on, check Toolbox container/VM status\n" +
                     "               3. Toolbox IP: 10.1.0.20 (local) / 100.82.26.53 (Tailscale)"
        })

    if not anker_pve_online:
        issues.append({
            "severity": "🟠 HIGH",
            "issue": "Anker PVE (Proxmox host) is OFFLINE",
            "impact": "Toolbox and all services on Anker infrastructure unavailable",
            "action": "1. Check if physical server is powered on at Rothkreuz location\n" +
                     "               2. Check network connectivity (10.1.0.92 local / 100.69.179.87 Tailscale)\n" +
                     "               3. May require physical access to restart"
        })

    if stock_pve_online and not toolbox_online:
        issues.append({
            "severity": "🟡 INFO",
            "issue": "Stockenweiler PVE is online but Toolbox is not reachable",
            "impact": "Core Radio/Music services running, but business services (Odoo, etc.) offline",
            "action": "Services on Stockenweiler PVE continue to run:\n" +
                     "               • NPM (Nginx Proxy Manager)\n" +
                     "               • Radio infrastructure\n" +
                     "               • File Server\n" +
                     "               • n8n Automation"
        })

    if not issues:
        print("✅ All systems operational")
    else:
        for i, issue in enumerate(issues, 1):
            print(f"\n{i}. {issue['severity']} - {issue['issue']}")
            print(f"   Impact: {issue['impact']}")
            print(f"   Action: {issue['action']}")

def print_quick_actions():
    """Print available quick actions"""
    print("\n\n⚡ QUICK ACTIONS")
    print("-"*100)
    print("1. To access Stockenweiler PVE:")
    print("   • Web: https://100.91.20.116:8006/")
    print("   • SSH: ssh stock-pve")
    print()
    print("2. To check/start Toolbox (if Anker PVE is online):")
    print("   • SSH to Anker: ssh anker-pve")
    print("   • List containers: pct list")
    print("   • Start Toolbox: pct start <vmid>")
    print()
    print("3. To run this dashboard again:")
    print("   • python Desktop/frawo_ops_dashboard.py")
    print()
    print("4. For detailed PVE management:")
    print("   • python Desktop/pve_start_toolbox.py")

def main():
    print_header()
    print_server_status()
    print_services_status()
    print_diagnostics()
    print_quick_actions()

    print("\n" + "="*100)
    print(f"{'Dashboard complete':^100}")
    print("="*100 + "\n")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user\n")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
