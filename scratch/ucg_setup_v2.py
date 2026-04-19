import requests
import json
import urllib3
import sys

# Suppress insecure warning for self-signed certs
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

UCG_IP = "10.1.0.1"
USERNAME = "admin"
PASSWORD = "OD-Wolf-2026!"
TOOLBOX_IP = "10.1.0.20"

session = requests.Session()
session.verify = False

def login():
    print(f"[*] Logging in to {UCG_IP}...")
    url = f"https://{UCG_IP}/api/auth/login"
    data = {"username": USERNAME, "password": PASSWORD}
    response = session.post(url, json=data)
    if response.status_code == 200:
        print("[+] Login successful.")
        # CSRF token is in 'x-csrf-token' header
        return response.headers.get("x-csrf-token")
    else:
        print(f"[-] Login failed: {response.status_code}")
        print(response.text)
        return None

def create_port_forward(csrf_token, name, fwd_port, target_ip, target_port):
    print(f"[*] Creating rule: {name} ({fwd_port} -> {target_ip}:{target_port})...")
    # UniFi REST API endpoint for port forwards
    url = f"https://{UCG_IP}/proxy/network/api/s/default/rest/portforward"
    
    headers = {
        "x-csrf-token": csrf_token,
        "Referer": f"https://{UCG_IP}/network/default/settings/firewall/port-forwarding",
        "Content-Type": "application/json"
    }
    
    payload = {
        "name": name,
        "enabled": True,
        "fwd": fwd_port,
        "fwd_port": fwd_port,
        "dst_port": target_port,
        "forward": target_ip,
        "proto": "tcp_udp",
        "src": "any",
        "log": False
    }
    
    response = session.post(url, json=payload, headers=headers)
    if response.status_code in [200, 201]:
        print(f"[+] Rule '{name}' created successfully.")
    else:
        print(f"[-] Failed to create rule '{name}': {response.status_code}")
        print(response.text)

def main():
    csrf = login()
    if not csrf:
        sys.exit(1)
        
    create_port_forward(csrf, "HTTP_PUBLIC_HS27", "80", TOOLBOX_IP, "80")
    create_port_forward(csrf, "HTTPS_PUBLIC_HS27", "443", TOOLBOX_IP, "443")

if __name__ == "__main__":
    main()
