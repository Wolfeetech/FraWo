import socket
import sys
sys.stdout.reconfigure(encoding='utf-8')

ip = "192.168.2.100"
ports = [22, 80, 443, 8006, 8443, 9000]

print(f"Scanning open ports on {ip}...")
for port in ports:
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(1.0)
        res = s.connect_ex((ip, port))
        if res == 0:
            print(f"✅ Port {port} is OPEN!")
        else:
            print(f"❌ Port {port} is closed.")
        s.close()
    except Exception as e:
        print(f"Error checking port {port}: {e}")
