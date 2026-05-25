#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Quick Proxmox Status Check - No Auth Required
Uses public endpoints where possible
"""

import requests
import urllib3
import socket
import sys
import io

# Force UTF-8 output on Windows
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def check_port(host, port, timeout=3):
    """Check if a port is open"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((host, port))
        sock.close()
        return result == 0
    except:
        return False

def check_service_http(url, timeout=5):
    """Check if HTTP service responds"""
    try:
        response = requests.get(url, timeout=timeout, verify=False, allow_redirects=True)
        return response.status_code, response.elapsed.total_seconds()
    except requests.exceptions.Timeout:
        return None, "timeout"
    except Exception as e:
        return None, str(e)

def main():
    print("🔍 FRAWO Ops - Quick Infrastructure Check")
    print("="*80)

    servers = {
        "Stockenweiler PVE": {
            "ip": "100.91.20.116",
            "ports": {"SSH": 22, "PVE Web": 8006}
        },
        "Toolbox": {
            "ip": "100.82.26.53",
            "ports": {"SSH": 22, "HTTP": 80, "HTTPS": 443}
        },
        "Anker PVE": {
            "ip": "100.69.179.87",
            "ports": {"SSH": 22, "PVE Web": 8006}
        }
    }

    services = {
        "Portal": "http://portal.hs27.internal/",
        "Nextcloud": "http://cloud.hs27.internal/",
        "Odoo": "http://odoo.hs27.internal/",
        "Paperless": "http://paperless.hs27.internal/",
        "Vault": "http://vault.hs27.internal/",
        "PVE Web": "https://100.91.20.116:8006/"
    }

    # Check servers
    print("\n📡 SERVER CONNECTIVITY:")
    print("-"*80)
    for name, config in servers.items():
        ip = config["ip"]
        print(f"\n{name} ({ip}):")
        for port_name, port in config["ports"].items():
            status = check_port(ip, port)
            icon = "✅" if status else "❌"
            print(f"  {icon} {port_name} (port {port}): {'OPEN' if status else 'CLOSED'}")

    # Check services
    print("\n\n🌐 WEB SERVICES:")
    print("-"*80)
    for name, url in services.items():
        status_code, elapsed = check_service_http(url)
        if status_code:
            print(f"✅ {name:<15} - HTTP {status_code} ({elapsed:.2f}s) - {url}")
        else:
            print(f"❌ {name:<15} - OFFLINE ({elapsed}) - {url}")

    print("\n" + "="*80)

if __name__ == "__main__":
    main()
