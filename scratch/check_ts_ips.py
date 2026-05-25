import subprocess
import sys
sys.stdout.reconfigure(encoding='utf-8')

ips = {
    "PVE Tailscale": "100.91.20.116",
    "Radio Node Tailscale": "100.64.23.77"
}

for name, ip in ips.items():
    print(f"Pinging {name} ({ip})...")
    res = subprocess.run(["ping", "-n", "1", "-w", "1000", ip], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    if res.returncode == 0:
        print(f"✅ {name} ({ip}) is ONLINE!")
    else:
        print(f"❌ {name} ({ip}) is OFFLINE.")
