#!/bin/bash
# FraWo Storage Cleanup Script
# VORSICHT: Prüfen Sie vor dem Ausführen, was gelöscht werden soll!

set -e

echo "[*] FraWo Storage Cleanup starting..."
echo ""

# 1. Show current usage
echo "[1] Current LVM Pool Usage:"
lvs pve/data -o lv_name,data_percent,meta_percent
echo ""

# 2. List snapshots (safe to delete if old)
echo "[2] Existing Snapshots:"
lvs | grep snap || echo "No snapshots found"
echo ""

# 3. Remove old snapshot
read -p "Delete snapshot 'snap_vm-120-disk-0_ucg-migrate-pre-20260405'? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    lvremove -y pve/snap_vm-120-disk-0_ucg-migrate-pre-20260405
    echo "[OK] Snapshot removed"
fi

# 4. List stopped VMs (candidates for cleanup)
echo ""
echo "[3] Stopped VMs:"
qm list | grep stopped || echo "All VMs running"
echo ""

# 5. Check for old VM disks
echo "[4] Unused VM disks:"
lvs | grep -E 'vm-200|vm-230' || echo "None found"
echo ""

# 6. Cleanup suggestions
echo ""
echo "[*] Cleanup Recommendations:"
echo "  1. Remove snapshot: ~8GB freed"
echo "  2. Remove VM 200/230 if unused: ~64GB freed"
echo "  3. Trim VM 110 if possible: ~20GB saved"
echo ""
echo "Current pool usage: 90.37% (CRITICAL)"
echo "Target: <80% (SAFE)"
