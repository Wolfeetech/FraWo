import socket
import subprocess
import sys
sys.stdout.reconfigure(encoding='utf-8')

# Resolve stock-pve
try:
    pve_ip = socket.gethostbyname("stock-pve")
    print(f"Resolved stock-pve to: {pve_ip}")
except Exception as e:
    print(f"Could not resolve stock-pve: {e}")
    pve_ip = None

# List of potential Proxmox host IPs
candidates = [
    "10.4.0.1", "10.4.0.10", "10.1.0.112",
    "10.1.0.1", "10.1.0.10", "10.1.0.22", "10.1.0.30",
    "192.168.2.1", "192.168.2.10", "192.168.2.100"
]
if pve_ip and pve_ip not in candidates:
    candidates.append(pve_ip)

for ip in candidates:
    res = subprocess.run(["ping", "-n", "1", "-w", "500", ip], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    if res.returncode == 0:
        print(f"✅ {ip} is ONLINE!")
        # Try checking if port 22 (SSH) is open
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(0.5)
            s.connect((ip, 22))
            print(f"  -> Port 22 (SSH) is OPEN!")
            s.close()
        except:
            pass
        # Try checking if port 8006 (Proxmox) is open
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(0.5)
            s.connect((ip, 8006))
            print(f"  -> Port 8006 (Proxmox UI) is OPEN!")
            s.close()
        except:
            pass
