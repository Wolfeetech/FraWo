#!/bin/bash
PUBKEY="ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIOvJ20ysxd54MhNUpl4UunmkyYi5acEjbKPwHh51iG3j openclaw@frawo-hostinger"

install_key() {
    local dest="$1"
    mkdir -p "$dest"
    chmod 700 "$dest"
    grep -qF "$PUBKEY" "$dest/authorized_keys" 2>/dev/null || echo "$PUBKEY" >> "$dest/authorized_keys"
    chmod 600 "$dest/authorized_keys"
}

echo "[*] Installing OpenClaw key on proxmox-anker..."
install_key /root/.ssh
echo "[OK] proxmox-anker"

echo "[*] Installing on CT 100 toolbox..."
pct exec 100 -- bash -c "
  mkdir -p /root/.ssh && chmod 700 /root/.ssh
  grep -qF 'openclaw' /root/.ssh/authorized_keys 2>/dev/null || echo '$PUBKEY' >> /root/.ssh/authorized_keys
  chmod 600 /root/.ssh/authorized_keys
"
echo "[OK] CT 100 toolbox"

echo "[*] Installing on VM 200 Nextcloud (via qm guest exec)..."
qm guest exec 200 --timeout 15 -- bash -c "mkdir -p /root/.ssh && echo '$PUBKEY' >> /root/.ssh/authorized_keys && chmod 600 /root/.ssh/authorized_keys" 2>/dev/null \
  && echo "[OK] VM 200 nextcloud" || echo "[SKIP] VM 200 - no guest agent"

echo "[*] Installing on VM 220 Odoo..."
qm guest exec 220 --timeout 15 -- bash -c "mkdir -p /root/.ssh && echo '$PUBKEY' >> /root/.ssh/authorized_keys && chmod 600 /root/.ssh/authorized_keys" 2>/dev/null \
  && echo "[OK] VM 220 odoo" || echo "[SKIP] VM 220 - no guest agent"

echo "[*] Installing on VM 230 Paperless..."
qm guest exec 230 --timeout 15 -- bash -c "mkdir -p /root/.ssh && echo '$PUBKEY' >> /root/.ssh/authorized_keys && chmod 600 /root/.ssh/authorized_keys" 2>/dev/null \
  && echo "[OK] VM 230 paperless" || echo "[SKIP] VM 230 - no guest agent"

echo "[SKIP] VM 210 HAOS - no root SSH available"

echo ""
echo "=== OPENCLAW PRIVATE KEY (fuer Hostinger) ==="
cat /tmp/openclaw_ed25519
echo "=== END PRIVATE KEY ==="

# Aufraumen
rm -f /tmp/openclaw_ed25519 /tmp/openclaw_ed25519.pub
echo "[*] Temp keys cleaned up from /tmp"
