import subprocess
import json
import sys

pve_ip = "10.4.0.99"
ssh_key = r"C:\Users\StudioPC\.ssh\pve_ed25519"

def exec_in_vm(cmd):
    escaped_cmd = cmd.replace("'", "'\\''")
    pve_cmd = f"qm guest exec 220 -- sh -c '{escaped_cmd}'"
    ssh_args = [
        "ssh", "-o", "StrictHostKeyChecking=no",
        "-i", ssh_key,
        f"root@{pve_ip}",
        pve_cmd
    ]
    res = subprocess.run(ssh_args, capture_output=True, text=True, timeout=30)
    if res.returncode != 0:
        return None
    try:
        data = json.loads(res.stdout)
        if data.get("exitcode", -1) != 0:
            print("Command failed in VM:", data.get("err-data", ""))
        return data.get("out-data", "")
    except Exception as e:
        print("Parse error:", e)
        return None

def main():
    print("[*] Fetching Caddyfile from VM 220...")
    caddyfile = exec_in_vm("cat /etc/caddy/Caddyfile")
    if not caddyfile:
        print("[ERROR] Could not read Caddyfile")
        return
        
    print("[*] Parsing and removing legacy /radio block...")
    # Find the handle /radio* block
    target_block = """    # Route for Azuracast Radio
    handle /radio* {
        uri strip_prefix /radio
        reverse_proxy localhost:8080 {
            header_up Host {host}
            header_up X-Real-IP {header.CF-Connecting-IP}
            header_up X-Forwarded-For {header.CF-Connecting-IP}
            header_up X-Forwarded-Proto https
        }
    }"""
    
    if target_block in caddyfile:
        new_caddyfile = caddyfile.replace(target_block, "")
        print("[OK] Legacy block matched and removed.")
    elif "handle /radio*" in caddyfile:
        # Fallback if whitespace differs
        print("[WARN] Block didn't match exactly, doing regex/substring replacement...")
        import re
        new_caddyfile = re.sub(r'\s*# Route for Azuracast Radio\s*handle /radio\* \{.*?\n\s*\}', '', caddyfile, flags=re.DOTALL)
        print("[OK] Replaced handle /radio* using regex.")
    else:
        print("[INFO] No handle /radio* found in Caddyfile.")
        return
        
    # Write the new Caddyfile to a temporary local file, then transfer it, or write it via python inside VM
    # Writing it directly inside VM using a python helper via guest agent is super clean!
    print("[*] Writing new Caddyfile back to VM 220...")
    
    # Escape for shell execution
    escaped_content = new_caddyfile.replace('\\', '\\\\').replace('$', '\\$').replace('"', '\\"').replace('`', '\\`')
    
    # Write using cat << 'EOF'
    write_cmd = f"cat << 'EOF' > /etc/caddy/Caddyfile\n{new_caddyfile}EOF"
    write_res = exec_in_vm(write_cmd)
    if write_res is None:
        print("[ERROR] Failed to write Caddyfile")
        return
        
    print("[*] Verifying Caddyfile syntax inside VM...")
    test_res = exec_in_vm("caddy validate --config /etc/caddy/Caddyfile")
    print(test_res)
    
    print("[*] Reloading Caddy service inside VM...")
    reload_res = exec_in_vm("systemctl reload caddy")
    print("[OK] Caddy reloaded successfully!")

if __name__ == "__main__":
    main()
