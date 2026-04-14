#!/bin/bash
# REVOCATION SCRIPT for compromised OpenClaw key
COMPROMISED_PATTERN="openclaw@frawo-hostinger"

clean_authorized_keys() {
    local target_file="$1"
    if [ -f "$target_file" ]; then
        echo "[*] Cleaning $target_file..."
        sed -i "/$COMPROMISED_PATTERN/d" "$target_file"
    fi
}

echo "[*] Cleaning proxmox-anker..."
clean_authorized_keys /root/.ssh/authorized_keys

echo "[*] Cleaning CT 100 toolbox..."
pct exec 100 -- bash -c "sed -i '/$COMPROMISED_PATTERN/d' /root/.ssh/authorized_keys"

echo "[*] Cleaning VMs..."
for vmid in 200 220 230; do
    qm guest exec $vmid -- bash -c "sed -i '/$COMPROMISED_PATTERN/d' /root/.ssh/authorized_keys" 2>/dev/null \
      && echo "[OK] VM $vmid cleaned" || echo "[SKIP] VM $vmid (agent unreachable)"
done

echo "[DONE] Compromised key revoked from all known nodes."
