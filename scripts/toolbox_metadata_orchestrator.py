import subprocess
import os
import base64
from pathlib import Path

# Paths
ROOT = Path("c:/Users/Admin/Documents/Private_Networking")
SSH_CONFIG = ROOT / "Codex/ssh_config"
HARVEST_SCRIPT_PATH = ROOT / "scripts/music_harvester_v2.py"
PEM_KEY = ROOT / "scripts/hs27_ops_ed25519"

def run_proxmox_command(command):
    # Construct the ssh command
    ssh_cmd = [
        "ssh", "-T",
        "-o", "BatchMode=yes",
        "-F", str(SSH_CONFIG),
        "proxmox-anker",
        f"bash -lc '{command}'"
    ]
    try:
        result = subprocess.run(ssh_cmd, capture_output=True, text=True, check=True)
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"Error: {e.stderr}")
        return None

def main():
    if not HARVEST_SCRIPT_PATH.exists():
        print(f"Harvester not found at {HARVEST_SCRIPT_PATH}")
        return

    script_content = HARVEST_SCRIPT_PATH.read_text(encoding="utf-8")
    
    # We want to run this python script inside the toolbox (LXC 100)
    # We'll use a bash heredoc for pct exec
    
    bash_script = f"""pct exec 100 -- python3 - <<'EOF' > /srv/media-library/music_harvest.log 2>&1 &
{script_content}
EOF
"""
    
    # Encode the bash script to base64 to cross the SSH boundary safely
    b64_payload = base64.b64encode(bash_script.encode("utf-8")).decode("ascii")
    
    # Send to Proxmox and run
    remote_cmd = f"echo {b64_payload} | base64 -d | bash"
    
    print("Sending harvest command to Proxmox...")
    output = run_proxmox_command(remote_cmd)
    
    if output is not None:
        print("Command sent successfully.")
        print("Check progress with: pct exec 100 -- cat /srv/media-library/music_harvest.log")
    else:
        print("Failed to send command.")

if __name__ == "__main__":
    main()
