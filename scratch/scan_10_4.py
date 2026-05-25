import subprocess
import threading
import sys
sys.stdout.reconfigure(encoding='utf-8')

def ping_host(ip):
    res = subprocess.run(["ping", "-n", "1", "-w", "200", ip], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    if res.returncode == 0:
        print(f"✅ {ip} is ONLINE!")

threads = []
print("Scanning 10.4.0.x ...")
for i in range(1, 255):
    t = threading.Thread(target=ping_host, args=(f"10.4.0.{i}",))
    threads.append(t)
    t.start()

for t in threads:
    t.join()

print("Scan complete.")
