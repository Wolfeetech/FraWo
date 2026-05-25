#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Wake Anker PVE - Try all possible methods to bring it back online
"""

import socket
import subprocess
import time
import sys
import io

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def log(msg, level="INFO"):
    icons = {"INFO": "ℹ️ ", "SUCCESS": "✅", "ERROR": "❌", "WARNING": "⚠️ ", "TRY": "🔄"}
    print(f"{icons.get(level, '')} {msg}")

def try_ping(ip, name):
    """Try to ping the host"""
    log(f"Trying to ping {name} ({ip})...", "TRY")
    result = subprocess.run(['ping', '-n', '2', ip], capture_output=True, text=True, timeout=10)
    if result.returncode == 0:
        log(f"{name} is REACHABLE!", "SUCCESS")
        return True
    else:
        log(f"{name} is not responding", "ERROR")
        return False

def try_wake_on_lan(mac_address, broadcast='255.255.255.255'):
    """Send Wake-on-LAN magic packet"""
    try:
        log(f"Sending Wake-on-LAN to {mac_address}...", "TRY")
        mac_bytes = bytes.fromhex(mac_address.replace(':', '').replace('-', ''))
        magic_packet = b'\xff' * 6 + mac_bytes * 16

        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        sock.sendto(magic_packet, (broadcast, 9))
        sock.sendto(magic_packet, (broadcast, 7))
        sock.close()

        log("WOL packet sent!", "SUCCESS")
        return True
    except Exception as e:
        log(f"WOL failed: {e}", "ERROR")
        return False

def try_ssh_through_stock(command):
    """Try to reach Anker through Stock PVE"""
    log("Trying SSH through Stock PVE bridge...", "TRY")
    try:
        # Stock PVE might have route to Anker's local network
        result = subprocess.run(
            ['ssh', 'stock-pve', f'{command}'],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode == 0:
            log("Got response through Stock PVE!", "SUCCESS")
            print(result.stdout)
            return True
        else:
            log("No route through Stock PVE", "WARNING")
            return False
    except Exception as e:
        log(f"SSH bridge failed: {e}", "ERROR")
        return False

def check_tailscale_status():
    """Check if Tailscale sees Anker"""
    log("Checking Tailscale network status...", "TRY")
    try:
        result = subprocess.run(['tailscale', 'status'], capture_output=True, text=True, timeout=5)
        lines = result.stdout.split('\n')
        for line in lines:
            if 'anker' in line.lower() or '100.69.179.87' in line:
                print(f"   {line}")
                if 'offline' in line.lower():
                    log("Tailscale shows Anker as OFFLINE", "WARNING")
                    # Check last seen
                    if 'ago' in line:
                        log(f"Last seen: {line.split('ago')[0].split(',')[-1].strip()}", "INFO")
                return False
        log("Anker not found in Tailscale network", "ERROR")
        return False
    except Exception as e:
        log(f"Tailscale check failed: {e}", "ERROR")
        return False

def try_local_network_scan():
    """Scan local network for Anker"""
    log("Scanning local 10.1.0.x network (might take time)...", "TRY")
    log("Anker should be at: 10.1.0.92", "INFO")

    # Try direct ping to known local IP
    result = subprocess.run(['ping', '-n', '1', '10.1.0.92'], capture_output=True, timeout=3)
    if result.returncode == 0:
        log("Anker responds on LOCAL network 10.1.0.92!", "SUCCESS")
        return True
    else:
        log("Anker not reachable on local network", "ERROR")
        return False

def check_for_ipmi_or_remote_management():
    """Check if IPMI/iLO/iDRAC is available"""
    log("Checking for remote management interfaces...", "TRY")

    # Common IPMI ports
    ipmi_ips = [
        '10.1.0.93',  # Common IPMI convention (host +1)
        '192.168.1.93',
    ]

    for ip in ipmi_ips:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2)
            result = sock.connect_ex((ip, 623))  # IPMI port
            sock.close()
            if result == 0:
                log(f"IPMI interface found at {ip}!", "SUCCESS")
                log(f"Access via: https://{ip}/", "INFO")
                return True
        except:
            pass

    log("No IPMI interface detected", "WARNING")
    return False

def main():
    print("\n" + "="*80)
    print("🔄 WAKE ANKER PVE - All Methods Attempt")
    print("="*80 + "\n")

    log("Target: Anker PVE (Proxmox Anker)", "INFO")
    log("Hosts: Toolbox and all business services (Odoo, Nextcloud, etc.)", "INFO")
    print()

    # Method 1: Check Tailscale status
    print("\n" + "-"*80)
    log("METHOD 1: Tailscale Network Check", "INFO")
    print("-"*80)
    check_tailscale_status()

    # Method 2: Try all known IPs
    print("\n" + "-"*80)
    log("METHOD 2: Direct IP Connectivity", "INFO")
    print("-"*80)

    ips_to_try = [
        ('100.69.179.87', 'Anker PVE (Tailscale)'),
        ('10.1.0.92', 'Anker PVE (Local)'),
        ('100.82.26.53', 'Toolbox (Tailscale)'),
        ('10.1.0.20', 'Toolbox (Local)'),
    ]

    any_reachable = False
    for ip, name in ips_to_try:
        if try_ping(ip, name):
            any_reachable = True

    # Method 3: Wake-on-LAN
    print("\n" + "-"*80)
    log("METHOD 3: Wake-on-LAN", "INFO")
    print("-"*80)
    log("Need MAC address of Anker PVE to send WOL", "WARNING")
    log("MAC address unknown - skipping WOL", "WARNING")
    log("To enable WOL: Find MAC address and add it here", "INFO")
    # Uncomment when MAC is known:
    # anker_mac = "XX:XX:XX:XX:XX:XX"
    # try_wake_on_lan(anker_mac)

    # Method 4: SSH through Stock PVE
    print("\n" + "-"*80)
    log("METHOD 4: SSH Bridge through Stock PVE", "INFO")
    print("-"*80)
    try_ssh_through_stock("ping -c 2 10.1.0.92")

    # Method 5: Local network scan
    print("\n" + "-"*80)
    log("METHOD 5: Local Network Scan", "INFO")
    print("-"*80)
    try_local_network_scan()

    # Method 6: Remote management
    print("\n" + "-"*80)
    log("METHOD 6: Remote Management Interface", "INFO")
    print("-"*80)
    check_for_ipmi_or_remote_management()

    # Summary
    print("\n" + "="*80)
    log("SUMMARY", "INFO")
    print("="*80)

    if any_reachable:
        log("SUCCESS: Anker PVE or Toolbox is reachable!", "SUCCESS")
        log("You can now try to SSH and check services", "INFO")
    else:
        log("RESULT: Anker PVE is NOT reachable by any method", "ERROR")
        print()
        log("PHYSICAL INTERVENTION REQUIRED:", "WARNING")
        log("1. Travel to Rothkreuz location", "WARNING")
        log("2. Check if server is powered on", "WARNING")
        log("3. Check network cables", "WARNING")
        log("4. Press power button if needed", "WARNING")
        log("5. Wait 2-3 minutes for boot", "WARNING")
        log("6. Re-run this script to verify", "INFO")

    print("\n" + "="*80 + "\n")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Cancelled\n")
    except Exception as e:
        print(f"\n❌ Error: {e}\n")
