#!/bin/bash
PUBKEY="ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAILjI7rqUniSmuSxs7G0eVq6iD6WaebDfNxZDWVtkbDeH Admin@Surface-Work"

echo "[*] Installing SSH key on CT 100 (toolbox)..."
pct exec 100 -- bash -c "mkdir -p /root/.ssh && chmod 700 /root/.ssh"
pct exec 100 -- bash -c "grep -qF '${PUBKEY}' /root/.ssh/authorized_keys 2>/dev/null || echo '${PUBKEY}' >> /root/.ssh/authorized_keys"
pct exec 100 -- chmod 600 /root/.ssh/authorized_keys
echo "[OK] Key installed on CT 100"

echo ""
echo "[*] Verifying..."
pct exec 100 -- cat /root/.ssh/authorized_keys
