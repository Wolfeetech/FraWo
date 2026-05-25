#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Start Toolbox Container on Proxmox
Interactive authentication
"""

import requests
import urllib3
import time
import sys
import io

# Force UTF-8 on Windows
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

PVE_HOST = "100.91.20.116"
PVE_PORT = 8006
NODE_NAME = "stock-pve"  # Will auto-detect if wrong

def pve_api_call(endpoint, ticket=None, csrf_token=None, method='GET', data=None):
    """Make API call to Proxmox"""
    url = f"https://{PVE_HOST}:{PVE_PORT}/api2/json{endpoint}"
    headers = {}

    if ticket and csrf_token:
        headers['CSRFPreventionToken'] = csrf_token
        headers['Cookie'] = f'PVEAuthCookie={ticket}'

    try:
        if method == 'GET':
            response = requests.get(url, headers=headers, verify=False, timeout=10)
        elif method == 'POST':
            response = requests.post(url, headers=headers, data=data, verify=False, timeout=10)

        if response.status_code == 200:
            return response.json().get('data')
        else:
            print(f"❌ API call failed: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def authenticate(username, password):
    """Authenticate and get ticket"""
    data = {'username': username, 'password': password}
    url = f"https://{PVE_HOST}:{PVE_PORT}/api2/json/access/ticket"

    try:
        response = requests.post(url, data=data, verify=False, timeout=10)
        if response.status_code == 200:
            result = response.json()['data']
            return result['ticket'], result['CSRFPreventionToken']
        else:
            print(f"❌ Authentication failed: {response.status_code}")
            return None, None
    except Exception as e:
        print(f"❌ Connection error: {e}")
        return None, None

def find_toolbox(ticket, csrf_token):
    """Find toolbox container across all nodes"""
    print("\n🔍 Searching for Toolbox container...")

    # Get all nodes
    nodes = pve_api_call('/nodes', ticket, csrf_token)
    if not nodes:
        return None, None

    for node in nodes:
        node_name = node['node']
        print(f"  Checking node: {node_name}")

        # Check containers
        containers = pve_api_call(f'/nodes/{node_name}/lxc', ticket, csrf_token)
        if containers:
            for ct in containers:
                name = ct.get('name', '').lower()
                if 'toolbox' in name or ct['vmid'] == 100:  # Assuming CT 100 is toolbox
                    print(f"  ✅ Found: {ct['name']} (ID: {ct['vmid']}) - Status: {ct['status']}")
                    return node_name, ct['vmid']

    return None, None

def start_container(node, vmid, ticket, csrf_token):
    """Start a container"""
    print(f"\n🚀 Starting container {vmid} on {node}...")

    endpoint = f'/nodes/{node}/lxc/{vmid}/status/start'
    result = pve_api_call(endpoint, ticket, csrf_token, method='POST')

    if result:
        print(f"✅ Start command sent successfully")
        print(f"   Task ID: {result}")

        # Wait a bit and check status
        print("\n⏳ Waiting for container to start...")
        for i in range(10):
            time.sleep(2)
            status = pve_api_call(f'/nodes/{node}/lxc/{vmid}/status/current', ticket, csrf_token)
            if status and status.get('status') == 'running':
                print(f"✅ Container is now RUNNING!")
                return True
            print(f"   Status: {status.get('status', 'unknown')} ({i+1}/10)")

        print("⚠️  Container may still be starting...")
        return True
    else:
        print("❌ Failed to start container")
        return False

def main():
    print("="*80)
    print("🚀 FRAWO Ops - Toolbox Starter")
    print("="*80)

    print(f"\n📡 Connecting to Proxmox at {PVE_HOST}:{PVE_PORT}")

    # Get credentials
    username = input("Username [root@pam]: ").strip() or "root@pam"

    # Try to import getpass for password input
    try:
        from getpass import getpass
        password = getpass("Password: ")
    except:
        password = input("Password: ")

    # Authenticate
    print("\n🔐 Authenticating...")
    ticket, csrf_token = authenticate(username, password)

    if not ticket:
        print("❌ Authentication failed. Exiting.")
        return

    print("✅ Authentication successful!")

    # Find toolbox
    node, vmid = find_toolbox(ticket, csrf_token)

    if not node or not vmid:
        print("\n❌ Could not find Toolbox container!")
        print("   Please check manually or specify VMID")

        # List all containers as fallback
        print("\n📋 All containers:")
        nodes = pve_api_call('/nodes', ticket, csrf_token)
        for n in nodes:
            containers = pve_api_call(f'/nodes/{n["node"]}/lxc', ticket, csrf_token)
            if containers:
                for ct in containers:
                    print(f"   ID {ct['vmid']}: {ct['name']} - {ct['status']}")

        return

    # Check if already running
    status = pve_api_call(f'/nodes/{node}/lxc/{vmid}/status/current', ticket, csrf_token)
    if status and status.get('status') == 'running':
        print(f"\n✅ Toolbox (ID: {vmid}) is already RUNNING!")
        return

    # Start it
    start_container(node, vmid, ticket, csrf_token)

    print("\n" + "="*80)
    print("✅ Done! Services should be coming online now.")
    print("   Run pve_check.py again in 30 seconds to verify.")
    print("="*80)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Cancelled by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
