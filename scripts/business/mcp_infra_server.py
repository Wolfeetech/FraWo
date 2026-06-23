import os
import sys
import subprocess
import requests
import json
import urllib3
from typing import Dict, Any, List, Optional
from mcp.server.fastmcp import FastMCP

# Suppress insecure certificate warnings for self-signed certificates (Proxmox/UniFi)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Initialize FastMCP Server
mcp = FastMCP("InfraMCP")

# --- ENVIRONMENT CONFIGURATION (SSOT) ---
PVE_API_URL = os.getenv("PVE_API_URL", "https://10.1.0.128:8006/api2/json")
PVE_TOKEN_ID = os.getenv("PVE_TOKEN_ID", "")
PVE_TOKEN_SECRET = os.getenv("PVE_TOKEN_SECRET", "")

UCG_API_URL = os.getenv("UCG_API_URL", "https://10.1.0.1")
UCG_USERNAME = os.getenv("UCG_USERNAME", "admin")
UCG_PASSWORD = os.getenv("UCG_PASSWORD", "")  # May be empty if not provided yet

AZURACAST_API_KEY = os.getenv("AZURACAST_API_KEY", "")
AZURACAST_URL = os.getenv("AZURACAST_URL", "https://funk.frawo-tech.de/api")

# --- PROXMOX API CLIENT CLASS ---
class ProxmoxClient:
    def __init__(self):
        self.url = PVE_API_URL.rstrip('/')
        self.headers = {
            "Authorization": f"PVEAPIToken={PVE_TOKEN_ID}={PVE_TOKEN_SECRET}",
            "Accept": "application/json"
        }

    def request(self, method: str, path: str, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        url = f"{self.url}/{path.lstrip('/')}"
        try:
            res = requests.request(method, url, headers=self.headers, json=data, verify=False, timeout=10)
            if res.status_code in [200, 201]:
                return res.json()
            else:
                return {"error": f"HTTP {res.status_code}: {res.text}"}
        except Exception as e:
            return {"error": str(e)}

pve_client = ProxmoxClient()

# --- UNIFI API CLIENT CLASS ---
class UniFiClient:
    def __init__(self):
        self.url = UCG_API_URL.rstrip('/')
        self.username = UCG_USERNAME
        self.password = UCG_PASSWORD
        self.session = requests.Session()
        self.session.verify = False
        self.csrf_token = None
        self.logged_in = False

    def login(self) -> bool:
        if not self.password:
            self.logged_in = False
            return False
        
        try:
            url = f"{self.url}/api/auth/login"
            data = {"username": self.username, "password": self.password}
            res = self.session.post(url, json=data, timeout=5)
            if res.status_code == 200:
                self.csrf_token = res.headers.get("x-csrf-token")
                self.logged_in = True
                return True
        except Exception:
            pass
        self.logged_in = False
        return False

    def request(self, method: str, api_path: str) -> Dict[str, Any]:
        if not self.logged_in and not self.login():
            return {"error": "UniFi connection disabled or invalid credentials (UCG_PASSWORD not set or incorrect)."}

        headers = {
            "x-csrf-token": self.csrf_token,
            "Content-Type": "application/json"
        }
        url = f"{self.url}/{api_path.lstrip('/')}"
        try:
            res = self.session.request(method, url, headers=headers, timeout=10)
            if res.status_code == 200:
                return res.json()
            elif res.status_code == 401:
                # Retry login once
                if self.login():
                    headers["x-csrf-token"] = self.csrf_token
                    res = self.session.request(method, url, headers=headers, timeout=10)
                    if res.status_code == 200:
                        return res.json()
            return {"error": f"UniFi API HTTP {res.status_code}: {res.text}"}
        except Exception as e:
            return {"error": str(e)}

unifi_client = UniFiClient()

# --- PVE MCP TOOLS ---

@mcp.tool()
def pve_status() -> str:
    """
    Returns general status and resource metrics of the Proxmox VE hypervisor host.
    """
    res = pve_client.request("GET", "nodes/pve/status")
    if "error" in res:
        return f"Failed to get PVE status: {res['error']}"
    
    data = res.get("data", {})
    cpu_info = data.get("cpuinfo", {})
    mem = data.get("memory", {})
    swap = data.get("swap", {})
    rootfs = data.get("rootfs", {})
    
    status_str = (
        "=== Proxmox VE Host Status ===\n"
        f"PVE Version: {data.get('pveversion', 'Unknown')}\n"
        f"Uptime: {data.get('uptime', 0) // 3600} hours\n"
        f"CPU Model: {cpu_info.get('model', 'Unknown')} ({cpu_info.get('cpus', 0)} Cores)\n"
        f"CPU Usage: {data.get('cpu', 0.0) * 100:.2f}%\n"
        f"RAM Usage: {mem.get('used', 0) / (1024**3):.2f} GB / {mem.get('total', 0) / (1024**3):.2f} GB ({mem.get('used', 0)/mem.get('total', 1)*100:.2f}%)\n"
        f"Swap Usage: {swap.get('used', 0) / (1024**3):.2f} GB / {swap.get('total', 0) / (1024**3):.2f} GB\n"
        f"Disk Usage (rootfs): {rootfs.get('used', 0) / (1024**3):.2f} GB / {rootfs.get('total', 0) / (1024**3):.2f} GB\n"
        f"Load Average: {', '.join(map(str, data.get('loadavg', [])))}\n"
    )
    return status_str

@mcp.tool()
def pve_list_guests() -> str:
    """
    Lists all virtual machines and LXC containers on the Proxmox VE host with their VMIDs, statuses, and names.
    """
    lxc_res = pve_client.request("GET", "nodes/pve/lxc")
    qemu_res = pve_client.request("GET", "nodes/pve/qemu")
    
    if "error" in lxc_res or "error" in qemu_res:
        return f"Error fetching guest list: {lxc_res.get('error') or qemu_res.get('error')}"
    
    guests = []
    
    # Process LXC Containers
    for lxc in lxc_res.get("data", []):
        guests.append({
            "vmid": lxc.get("vmid"),
            "name": lxc.get("name"),
            "type": "LXC Container",
            "status": lxc.get("status"),
            "ip": lxc.get("ip", "DHCP/Static"),
            "cpus": lxc.get("cpus", 1),
            "mem": f"{lxc.get('maxmem', 0) / (1024**2):.0f} MB"
        })
        
    # Process Qemu VMs
    for vm in qemu_res.get("data", []):
        guests.append({
            "vmid": vm.get("vmid"),
            "name": vm.get("name"),
            "type": "KVM VM",
            "status": vm.get("status"),
            "ip": "N/A",
            "cpus": vm.get("cpus", 1),
            "mem": f"{vm.get('maxmem', 0) / (1024**2):.0f} MB"
        })
        
    guests.sort(key=lambda x: int(x["vmid"]))
    
    out = ["%-6s %-25s %-15s %-10s %-10s %-8s" % ("VMID", "Name", "Type", "Status", "Memory", "CPUs")]
    out.append("-" * 80)
    for g in guests:
        out.append("%-6s %-25s %-15s %-10s %-10s %-8s" % (
            g["vmid"], g["name"], g["type"], g["status"], g["mem"], g["cpus"]
        ))
        
    return "=== Proxmox Guests (VMs & Containers) ===\n" + "\n".join(out)

@mcp.tool()
def pve_guest_control(vmid: int, action: str) -> str:
    """
    Controls a virtual guest lifecycle.
    vmid: ID of the guest (e.g., 108)
    action: start, stop, shutdown, reboot
    """
    # Verify guest type first (VM vs LXC)
    lxc_res = pve_client.request("GET", "nodes/pve/lxc")
    is_lxc = False
    if not "error" in lxc_res:
        for l in lxc_res.get("data", []):
            if int(l.get("vmid")) == vmid:
                is_lxc = True
                break
                
    guest_type = "lxc" if is_lxc else "qemu"
    path = f"nodes/pve/{guest_type}/{vmid}/status/{action}"
    
    res = pve_client.request("POST", path)
    if "error" in res:
        return f"Failed to execute control action: {res['error']}"
    
    return f"Success: Action '{action}' sent to guest ID {vmid} ({guest_type.upper()})."

@mcp.tool()
def pve_exec_in_container(vmid: int, command: str) -> str:
    """
    Executes a shell command inside a running LXC container on the PVE host.
    vmid: ID of the LXC container (e.g. 101, 103, 108, 110, 140)
    command: The command to execute (e.g. "systemctl status docker", "df -h")
    """
    # Check if container is running
    status_res = pve_client.request("GET", f"nodes/pve/lxc/{vmid}/status/current")
    if "error" in status_res:
        return f"Failed to get container status: {status_res['error']}"
    
    status = status_res.get("data", {}).get("status")
    if status != "running":
        return f"Container {vmid} is in status '{status}'. Command execution is only possible in 'running' containers."
    
    # Run command via local SSH client using the mapped `pve` host
    ssh_cmd = ["ssh", "pve", f"pct exec {vmid} -- {command}"]
    try:
        result = subprocess.run(ssh_cmd, capture_output=True, text=True, timeout=30)
        output = result.stdout + result.stderr
        return f"Command: {command}\nExit Code: {result.returncode}\n\n=== Output ===\n{output}"
    except subprocess.TimeoutExpired:
        return f"Error: Command timed out after 30 seconds."
    except Exception as e:
        return f"Error executing SSH command: {str(e)}"

# --- UNIFI UCG MCP TOOLS ---

@mcp.tool()
def ucg_status() -> str:
    """
    Returns the device status and system statistics of the UniFi Cloud Gateway (UCG).
    """
    res = unifi_client.request("GET", "proxy/network/api/s/default/stat/device")
    if "error" in res:
        return f"UniFi Status Error: {res['error']}"
        
    devices = res.get("data", [])
    ucg_dev = None
    for d in devices:
        # Check if the device is a gateway
        if d.get("is_gateway", False) or "ucg" in d.get("model", "").lower():
            ucg_dev = d
            break
            
    if not ucg_dev:
        return "Gateway device not found in UniFi controller adoption list."
        
    status = (
        "=== UniFi Cloud Gateway Status ===\n"
        f"Model: {ucg_dev.get('model', 'Unknown')} (Name: {ucg_dev.get('name', 'Unknown')})\n"
        f"Version: {ucg_dev.get('version', 'Unknown')}\n"
        f"Uptime: {ucg_dev.get('uptime', 0) // 3600} hours\n"
        f"Status: Adopted and Active\n"
        f"CPU Usage: {float(ucg_dev.get('system-status', {}).get('cpu', 0.0)):.2f}%\n"
        f"Memory Usage: {float(ucg_dev.get('system-status', {}).get('mem', 0.0)):.2f}%\n"
        f"WAN IP: {ucg_dev.get('wan1', {}).get('ip', 'N/A')}\n"
    )
    return status

@mcp.tool()
def ucg_list_clients() -> str:
    """
    Retrieves a list of all active network client stations connected to the gateway.
    """
    res = unifi_client.request("GET", "proxy/network/api/s/default/stat/sta")
    if "error" in res:
        return f"UniFi Clients Error: {res['error']}"
        
    clients = res.get("data", [])
    out = ["%-20s %-15s %-17s %-8s %-10s" % ("Name/Hostname", "IP Address", "MAC Address", "VLAN", "Connection")]
    out.append("-" * 80)
    
    for c in clients:
        name = c.get("name") or c.get("hostname") or "Unknown"
        ip = c.get("ip", "N/A")
        mac = c.get("mac", "N/A")
        vlan = c.get("vlan", "Default")
        conn = "Wireless" if c.get("is_wired") is False else "Wired"
        out.append("%-20s %-15s %-17s %-8s %-10s" % (name[:20], ip, mac, vlan, conn))
        
    return "=== Connected UniFi Clients ===\n" + "\n".join(out)

@mcp.tool()
def ucg_list_networks() -> str:
    """
    Lists all configured VLANs, subnets, and DHCP settings on the gateway.
    """
    res = unifi_client.request("GET", "proxy/network/api/s/default/rest/networkconf")
    if "error" in res:
        return f"UniFi Networks Error: {res['error']}"
        
    networks = res.get("data", [])
    out = ["%-25s %-5s %-18s %-18s" % ("Network Name", "VLAN", "Gateway IP", "DHCP Range")]
    out.append("-" * 80)
    
    for n in networks:
        name = n.get("name", "Unknown")
        vlan = n.get("vlan", "Native")
        ip = n.get("ip", "N/A")
        netmask = n.get("netmask", "N/A")
        dhcp_start = n.get("dhcpd_start", "N/A")
        dhcp_stop = n.get("dhcpd_stop", "N/A")
        dhcp_range = f"{dhcp_start}-{dhcp_stop}" if dhcp_start != "N/A" else "Disabled"
        out.append("%-25s %-5s %-18s %-18s" % (name[:25], vlan, f"{ip}/{netmask}", dhcp_range))
        
    return "=== UniFi Network VLANs & Subnets ===\n" + "\n".join(out)

# --- OTHER SERVICE MONITORING TOOLS ---

@mcp.tool()
def vaultwarden_status() -> str:
    """
    Verifies the status of Vaultwarden (CT 108) and checks if the login endpoint is active.
    """
    url = "http://10.1.0.95:80"
    try:
        res = requests.get(url, timeout=5)
        status = "Active" if res.status_code == 200 else f"Error Code {res.status_code}"
        return f"Vaultwarden Container (CT 108): {status} (URL: {url})"
    except Exception as e:
        return f"Vaultwarden Container (CT 108): Offline/Unreachable. Error: {str(e)}"

@mcp.tool()
def adguard_status() -> str:
    """
    Checks if AdGuard Home (CT 101) is active and serving DNS queries.
    """
    import socket
    dns_ip = "10.1.0.52"
    try:
        # Check web interface
        web_res = requests.get(f"http://{dns_ip}:80", timeout=3)
        web_status = "UP" if web_res.status_code == 200 else f"HTTP {web_res.status_code}"
    except Exception:
        web_status = "DOWN"
        
    try:
        # Try a quick DNS resolution socket call to check if port 53 is listening
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.settimeout(2)
        # DNS query header + question for local host
        query = b'\xaa\xbb\x01\x00\x00\x01\x00\x00\x00\x00\x00\x00\x03pve\x00\x00\x01\x00\x01'
        s.sendto(query, (dns_ip, 53))
        data, _ = s.recvfrom(512)
        dns_status = "UP" if len(data) > 0 else "NO_RESPONSE"
    except Exception as e:
        dns_status = f"DOWN ({str(e)})"
        
    return f"AdGuard Home (CT 101 / {dns_ip}):\n- Web UI: {web_status}\n- DNS Service (Port 53): {dns_status}"

@mcp.tool()
def azuracast_status() -> str:
    """
    Checks the status of AzuraCast radio streaming stations and returns the currently playing track.
    """
    headers = {"X-API-Key": AZURACAST_API_KEY}
    try:
        res = requests.get(f"{AZURACAST_URL}/stations", headers=headers, verify=False, timeout=5)
        if res.status_code == 200:
            stations = res.json()
            out = []
            for s in stations:
                np = s.get("now_playing", {})
                song = np.get("song", {})
                out.append(
                    f"Station: {s.get('name')} (ID: {s.get('id')})\n"
                    f"  Status: {'Online' if s.get('is_enabled') else 'Disabled'}\n"
                    f"  Listeners: {np.get('listeners', {}).get('current', 0)} (Max: {np.get('listeners', {}).get('total', 0)})\n"
                    f"  Current Track: {song.get('text', 'No track info')}\n"
                )
            return "=== AzuraCast Status ===\n" + "\n".join(out)
        else:
            return f"Failed to fetch AzuraCast stations. HTTP {res.status_code}: {res.text}"
    except Exception as e:
        return f"AzuraCast offline or API unreachable: {str(e)}"

# --- MAIN INVOCATION ---
if __name__ == "__main__":
    mcp.run()
