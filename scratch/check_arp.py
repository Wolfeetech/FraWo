import subprocess

print("Pinging broadcast...")
subprocess.run(['ping', '-n', '1', '10.1.0.255'])
print("Checking ARP table...")
arp_out = subprocess.run(['arp', '-a'], capture_output=True, text=True)
for line in arp_out.stdout.splitlines():
    if '10.1.0.' in line:
        print(line)
