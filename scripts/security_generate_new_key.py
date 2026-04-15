import subprocess
import os

key_path = r"c:\Users\Admin\Documents\Private_Networking\Codex\openclaw_id_ed25519"
# Delete existing if any (unlikely but safe)
if os.path.exists(key_path):
    os.remove(key_path)
if os.path.exists(key_path + ".pub"):
    os.remove(key_path + ".pub")

# Generate key with empty passphrase
subprocess.run(["ssh-keygen", "-t", "ed25519", "-C", "openclaw@frawo-hostinger-secure", "-f", key_path, "-N", ""], check=True)

print(f"Key generated at: {key_path}")
with open(key_path + ".pub", "r") as f:
    print(f"PUBLIC_KEY: {f.read().strip()}")
