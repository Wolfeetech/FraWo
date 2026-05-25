import socket
import threading
import subprocess

def ping_host(ip):
    try:
        output = subprocess.run(['ping', '-n', '1', '-w', '200', ip], capture_output=True, text=True)
        if "TTL=" in output.stdout:
            print(f"[+] Found active IP: {ip}")
    except:
        pass

subnets = ['10.4.0.', '192.168.178.', '10.1.0.', '192.168.2.', '192.168.0.', '192.168.1.']

threads = []
for subnet in subnets:
    print(f"Scanning {subnet}x ...")
    for i in range(1, 255):
        ip = f"{subnet}{i}"
        t = threading.Thread(target=ping_host, args=(ip,))
        threads.append(t)
        t.start()
        
for t in threads:
    t.join()

print("Scan complete.")
