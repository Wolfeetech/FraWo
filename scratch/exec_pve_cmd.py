import subprocess
import json
import sys

def exec_in_vm(cmd):
    # Proxmox IP and key
    pve_ip = "100.69.179.87"
    ssh_key = r"C:\Users\StudioPC\.ssh\pve_ed25519"
    
    # We wrap the command to run via qm guest exec inside VM 220
    # Escape quotes inside cmd
    escaped_cmd = cmd.replace("'", "'\\''")
    pve_cmd = f"qm guest exec 220 -- sh -c '{escaped_cmd}'"
    
    ssh_args = [
        "ssh", "-o", "StrictHostKeyChecking=no",
        "-i", ssh_key,
        f"root@{pve_ip}",
        pve_cmd
    ]
    
    try:
        res = subprocess.run(ssh_args, capture_output=True, text=True, timeout=30)
        if res.returncode != 0:
            print(f"[ERROR] SSH failed:\nSTDOUT: {res.stdout}\nSTDERR: {res.stderr}")
            return None
        
        try:
            data = json.loads(res.stdout)
            exitcode = data.get("exitcode", -1)
            err_data = data.get("err-data", "")
            out_data = data.get("out-data", "")
            
            if exitcode != 0:
                print(f"[WARN] Command exited with code {exitcode}")
                if err_data:
                    print(f"STDERR: {err_data}")
            return out_data
        except json.JSONDecodeError:
            print(f"[ERROR] Could not parse JSON from Proxmox:\n{res.stdout}")
            return None
    except Exception as e:
        print(f"[ERROR] Exception occurred: {str(e)}")
        return None

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python exec_pve_cmd.py <command>")
        sys.exit(1)
        
    cmd = " ".join(sys.argv[1:])
    out = exec_in_vm(cmd)
    if out is not None:
        print(out)
