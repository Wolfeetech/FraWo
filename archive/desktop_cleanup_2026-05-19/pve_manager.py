#!/usr/bin/env python3
"""
Proxmox VE Manager - FRAWO Ops
Manages containers and VMs on Proxmox without SSH
"""

import requests
import urllib3
import json
import sys
from getpass import getpass

# Disable SSL warnings for self-signed certs
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class ProxmoxManager:
    def __init__(self, host, user="root@pam", password=None):
        self.host = host
        self.user = user
        self.password = password
        self.base_url = f"https://{host}:8006/api2/json"
        self.ticket = None
        self.csrf_token = None

    def authenticate(self):
        """Get authentication ticket and CSRF token"""
        if not self.password:
            self.password = getpass(f"Password for {self.user}@{self.host}: ")

        url = f"{self.base_url}/access/ticket"
        data = {
            'username': self.user,
            'password': self.password
        }

        try:
            response = requests.post(url, data=data, verify=False, timeout=10)
            if response.status_code == 200:
                result = response.json()['data']
                self.ticket = result['ticket']
                self.csrf_token = result['CSRFPreventionToken']
                print(f"✅ Authenticated to {self.host}")
                return True
            else:
                print(f"❌ Authentication failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Connection error: {e}")
            return False

    def _get_headers(self):
        """Get headers with authentication"""
        return {
            'CSRFPreventionToken': self.csrf_token,
            'Cookie': f'PVEAuthCookie={self.ticket}'
        }

    def get_nodes(self):
        """List all nodes in the cluster"""
        url = f"{self.base_url}/nodes"
        response = requests.get(url, headers=self._get_headers(), verify=False)
        if response.status_code == 200:
            return response.json()['data']
        return []

    def list_containers(self, node):
        """List all LXC containers on a node"""
        url = f"{self.base_url}/nodes/{node}/lxc"
        response = requests.get(url, headers=self._get_headers(), verify=False)
        if response.status_code == 200:
            return response.json()['data']
        return []

    def list_vms(self, node):
        """List all VMs on a node"""
        url = f"{self.base_url}/nodes/{node}/qemu"
        response = requests.get(url, headers=self._get_headers(), verify=False)
        if response.status_code == 200:
            return response.json()['data']
        return []

    def get_container_status(self, node, vmid):
        """Get detailed status of a container"""
        url = f"{self.base_url}/nodes/{node}/lxc/{vmid}/status/current"
        response = requests.get(url, headers=self._get_headers(), verify=False)
        if response.status_code == 200:
            return response.json()['data']
        return {}

    def start_container(self, node, vmid):
        """Start a container"""
        url = f"{self.base_url}/nodes/{node}/lxc/{vmid}/status/start"
        response = requests.post(url, headers=self._get_headers(), verify=False)
        if response.status_code == 200:
            return True
        return False

    def stop_container(self, node, vmid):
        """Stop a container"""
        url = f"{self.base_url}/nodes/{node}/lxc/{vmid}/status/stop"
        response = requests.post(url, headers=self._get_headers(), verify=False)
        if response.status_code == 200:
            return True
        return False

    def start_vm(self, node, vmid):
        """Start a VM"""
        url = f"{self.base_url}/nodes/{node}/qemu/{vmid}/status/start"
        response = requests.post(url, headers=self._get_headers(), verify=False)
        if response.status_code == 200:
            return True
        return False

    def display_status(self):
        """Display comprehensive status of all resources"""
        nodes = self.get_nodes()

        print("\n" + "="*80)
        print("PROXMOX CLUSTER STATUS")
        print("="*80)

        for node in nodes:
            node_name = node['node']
            status = node['status']
            print(f"\n📦 Node: {node_name} - Status: {status.upper()}")
            print("-"*80)

            # List containers
            containers = self.list_containers(node_name)
            if containers:
                print("\n🗃️  LXC CONTAINERS:")
                print(f"{'ID':<6} {'Name':<20} {'Status':<10} {'CPU':<8} {'Memory':<15}")
                print("-"*80)
                for ct in containers:
                    vmid = ct['vmid']
                    name = ct['name']
                    status = ct['status']
                    cpu = f"{ct.get('cpu', 0):.1%}"
                    mem = f"{ct.get('mem', 0)/(1024**3):.1f}GB" if 'mem' in ct else 'N/A'

                    status_icon = "✅" if status == "running" else "❌"
                    print(f"{vmid:<6} {name:<20} {status_icon} {status:<8} {cpu:<8} {mem:<15}")

            # List VMs
            vms = self.list_vms(node_name)
            if vms:
                print("\n🖥️  VIRTUAL MACHINES:")
                print(f"{'ID':<6} {'Name':<20} {'Status':<10} {'CPU':<8} {'Memory':<15}")
                print("-"*80)
                for vm in vms:
                    vmid = vm['vmid']
                    name = vm['name']
                    status = vm['status']
                    cpu = f"{vm.get('cpu', 0):.1%}"
                    mem = f"{vm.get('mem', 0)/(1024**3):.1f}GB" if 'mem' in vm else 'N/A'

                    status_icon = "✅" if status == "running" else "❌"
                    print(f"{vmid:<6} {name:<20} {status_icon} {status:<8} {cpu:<8} {mem:<15}")

        print("\n" + "="*80)

def main():
    # Stockenweiler PVE
    host = "100.91.20.116"

    print("🚀 FRAWO Ops - Proxmox Manager")
    print("="*80)

    manager = ProxmoxManager(host)

    if manager.authenticate():
        manager.display_status()

        # Interactive menu
        print("\n\n🔧 ACTIONS:")
        print("1. Start a container")
        print("2. Stop a container")
        print("3. Refresh status")
        print("4. Exit")

        choice = input("\nSelect action (1-4): ").strip()

        if choice == "1":
            vmid = input("Enter container ID to start: ").strip()
            nodes = manager.get_nodes()
            if nodes:
                node_name = nodes[0]['node']
                if manager.start_container(node_name, vmid):
                    print(f"✅ Started container {vmid}")
                else:
                    print(f"❌ Failed to start container {vmid}")
        elif choice == "3":
            manager.display_status()

if __name__ == "__main__":
    main()
