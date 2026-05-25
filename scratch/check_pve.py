import subprocess
import sys
sys.stdout.reconfigure(encoding='utf-8')

ips = {
    "PVE Tailscale": "100.91.20.116",
    "PVE local EasyBox": "192.168.2.10",
    "Odoo local IP": "10.4.0.22",
    "UCG Tailscale IP": "100.69.179.87"
}

for name, ip in ips.items():
    print(f"Pinging {name} ({ip})...")
    # ping -n 1 -w 1000 ip
    # On Windows, ping returns 0 on success, 1 on timeout/failure
    res = subprocess.run(["ping", "-n", "1", "-w", "1000", ip], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    if res.returncode == 0:
        print(f"✅ {name} ({ip}) is ONLINE!")
    else:
        print(f"❌ {name} ({ip}) is OFFLINE.")
