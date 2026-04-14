#!/bin/bash
NEW_PUBKEY="ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAILto3AU9QMBUk7rMbABL9RngHMMyp679eZBuIGhgAyNp openclaw@frawo-hostinger-secure"

install_key() {
    local dest="$1"
    mkdir -p "$dest"
    chmod 700 "$dest"
    grep -qF "$NEW_PUBKEY" "$dest/authorized_keys" 2>/dev/null || echo "$NEW_PUBKEY" >> "$dest/authorized_keys"
    chmod 600 "$dest/authorized_keys"
}

echo "[*] Installing NEW SECURE key on proxmox-anker..."
install_key /root/.ssh
echo "[OK] proxmox-anker"

echo "[*] Installing on CT 100 toolbox..."
pct exec 100 -- bash -c "
  mkdir -p /root/.ssh && chmod 700 /root/.ssh
  grep -qF 'openclaw@frawo-hostinger-secure' /root/.ssh/authorized_keys 2>/dev/null || echo '$NEW_PUBKEY' >> /root/.ssh/authorized_keys
  chmod 600 /root/.ssh/authorized_keys
"
echo "[OK] CT 100 toolbox"

echo "[*] Installing on VMs..."
for vmid in 200 220 230; do
    qm guest exec $vmid -- bash -c "mkdir -p /root/.ssh && echo '$NEW_PUBKEY' >> /root/.ssh/authorized_keys && chmod 600 /root/.ssh/authorized_keys" 2>/dev/null \
      && echo "[OK] VM $vmid" || echo "[SKIP] VM $vmid (agent unreachable)"
done

echo "[DONE] New secure public key installed. The private part remains only on the local machine."
