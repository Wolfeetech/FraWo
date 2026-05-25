#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FRAWO Ops - Automatic Recovery System
Attempts to automatically recover offline services
"""

import requests
import urllib3
import socket
import time
import sys
import io
import subprocess
from datetime import datetime

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def log(message, level="INFO"):
    """Log message with timestamp"""
    timestamp = datetime.now().strftime('%H:%M:%S')
    icon = {"INFO": "ℹ️ ", "SUCCESS": "✅", "ERROR": "❌", "WARNING": "⚠️ "}.get(level, "")
    print(f"[{timestamp}] {icon} {message}")

def check_port(host, port, timeout=2):
    """Check if port is open"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((host, port))
        sock.close()
        return result == 0
    except:
        return False

def wake_on_lan(mac_address, broadcast="255.255.255.255"):
    """Send WOL magic packet"""
    try:
        import socket
        mac_bytes = bytes.fromhex(mac_address.replace(':', '').replace('-', ''))
        magic_packet = b'\xff' * 6 + mac_bytes * 16

        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        sock.sendto(magic_packet, (broadcast, 9))
        sock.close()
        return True
    except Exception as e:
        log(f"WOL failed: {e}", "ERROR")
        return False

def attempt_ssh_command(host, command, timeout=10):
    """Try to execute SSH command"""
    try:
        result = subprocess.run(
            ['ssh', host, command],
            capture_output=True,
            text=True,
            timeout=timeout
        )
        return result.returncode == 0, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return False, "", "Timeout"
    except Exception as e:
        return False, "", str(e)

def check_and_recover_anker_pve():
    """Try to recover Anker PVE"""
    log("Checking Anker PVE status...")

    if check_port("100.69.179.87", 22):
        log("Anker PVE is online!", "SUCCESS")
        return True

    log("Anker PVE is offline", "WARNING")
    log("Attempting recovery...")

    # Try WOL if MAC address known
    # anker_mac = "XX:XX:XX:XX:XX:XX"  # Add actual MAC if known
    # log(f"Sending Wake-on-LAN to {anker_mac}...")
    # wake_on_lan(anker_mac)

    log("Physical intervention may be required at Rothkreuz location", "WARNING")
    log("Actions needed:", "WARNING")
    log("  1. Check if server is powered on", "WARNING")
    log("  2. Check network cables", "WARNING")
    log("  3. Try accessing via local network: 10.1.0.92", "WARNING")

    return False

def check_and_recover_toolbox():
    """Try to recover Toolbox"""
    log("Checking Toolbox status...")

    if check_port("100.82.26.53", 22):
        log("Toolbox is online!", "SUCCESS")
        return True

    log("Toolbox is offline", "WARNING")

    # Check if Anker PVE is online first
    if not check_port("100.69.179.87", 22):
        log("Cannot recover Toolbox: Anker PVE (host) is offline", "ERROR")
        return False

    log("Anker PVE is online, attempting to start Toolbox container...")

    # Try to start via SSH
    success, stdout, stderr = attempt_ssh_command(
        "anker-pve",
        "pct list && pct start 100 || qm start 100"  # Try common IDs
    )

    if success:
        log("Start command sent, waiting for Toolbox to come online...", "INFO")
        for i in range(30):
            time.sleep(2)
            if check_port("100.82.26.53", 22):
                log(f"Toolbox is now online after {i*2}s!", "SUCCESS")
                return True
            if i % 5 == 0:
                log(f"Still waiting... ({i*2}s)", "INFO")

        log("Toolbox did not come online in time", "WARNING")
        return False
    else:
        log(f"Failed to send start command: {stderr}", "ERROR")
        return False

def verify_services():
    """Verify all services are accessible"""
    log("Verifying services...")

    services = {
        "Portal": "http://portal.hs27.internal/",
        "Odoo": "http://odoo.hs27.internal/",
        "Nextcloud": "http://cloud.hs27.internal/"
    }

    all_ok = True
    for name, url in services.items():
        try:
            response = requests.get(url, timeout=5, verify=False)
            if response.status_code < 500:
                log(f"{name}: OK ({response.status_code})", "SUCCESS")
            else:
                log(f"{name}: Error {response.status_code}", "WARNING")
                all_ok = False
        except:
            log(f"{name}: Offline", "ERROR")
            all_ok = False

    return all_ok

def main():
    print("\n" + "="*80)
    print("🔧 FRAWO OPS - AUTO RECOVERY SYSTEM")
    print("="*80 + "\n")

    log("Starting automated recovery sequence...")

    # Step 1: Check and recover Anker PVE
    anker_ok = check_and_recover_anker_pve()
    print()

    # Step 2: Check and recover Toolbox
    if anker_ok:
        toolbox_ok = check_and_recover_toolbox()
    else:
        toolbox_ok = False
        log("Skipping Toolbox recovery (Anker PVE offline)", "WARNING")

    print()

    # Step 3: Verify services
    if toolbox_ok:
        log("Waiting 10 seconds for services to initialize...")
        time.sleep(10)
        services_ok = verify_services()
    else:
        services_ok = False
        log("Skipping service verification (Toolbox offline)", "WARNING")

    # Summary
    print("\n" + "="*80)
    print("RECOVERY SUMMARY")
    print("="*80)
    print(f"Anker PVE:  {'✅ Online' if anker_ok else '❌ Offline'}")
    print(f"Toolbox:    {'✅ Online' if toolbox_ok else '❌ Offline'}")
    print(f"Services:   {'✅ Running' if services_ok else '❌ Not Available'}")
    print("="*80)

    if not anker_ok:
        print("\n🔴 Manual intervention required:")
        print("   • Anker PVE server needs to be powered on physically")
        print("   • Location: Rothkreuz")
        print("   • Contact on-site personnel")

    print()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Recovery cancelled by user\n")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}\n")
        import traceback
        traceback.print_exc()
