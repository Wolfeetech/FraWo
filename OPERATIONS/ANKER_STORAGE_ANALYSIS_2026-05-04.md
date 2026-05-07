# Anker Storage Analysis & Remediation Plan - 2026-05-04

**Zeitstempel:** 2026-05-04 10:00 Europe/Berlin
**Status:** ROOT CAUSE IDENTIFIED - Broken snapshots + local-lvm oversized
**Priority:** CRITICAL - Blocks deployments, causes instability

---

## Executive Summary

Anker host instability is **directly caused by storage pressure** on `local-lvm` thin pool (89.39% used). Investigation revealed:

1. **Broken VM 200 snapshots** consuming space but not deletable
2. **local-lvm thin pool** is too small for current workload (156.88 GB for 5 VMs)
3. **ssd2tb storage** has 1.82 TB free (only 2.91% used)

**Recommended Action:** Migrate VMs from `local-lvm` to `ssd2tb` storage

---

## Detailed Findings

### Storage Status

```
local-lvm (lvmthin):  156.88 GB total, 89.39% used, 17.45 GB free
ssd2tb (dir):        1.82 TB total, 2.91% used, 1.77 TB free
```

**Problem:** 5 VMs with 32 GB boot disks each = 160 GB needed, but pool is only 156.88 GB.
This leaves NO room for:
- Snapshots
- Thin provisioning overhead
- Write operations
- System operations

### VM Inventory on Anker

| VMID | Name | Status | RAM | Boot Disk | Storage |
|------|------|--------|-----|-----------|---------|
| 200 | nextcloud | running | 3GB | 32GB | local-lvm (96.26% full!) |
| 210 | haos | running | 3GB | 32GB | local-lvm |
| 220 | odoo | running | 3GB | 32GB | local-lvm |
| 230 | paperless | running | 3GB | 32GB | local-lvm |
| 240 | PBS-FraWo | running | 2GB | 32GB | local-lvm |

**Total:** 160 GB allocated on a 156.88 GB pool → Overcommitted!

### VM 200 (Nextcloud) Issues

**Broken Snapshots:**
```
pre_update_260329           2026-03-29 16:46:59
ucg-migrate-pre-20260405    2026-04-05 01:33:56
```

**Problems:**
1. VM was locked: `lock: snapshot-delete` (previous delete attempt failed)
2. Config references snapshots: `parent: ucg-migrate-pre-20260405`
3. Snapshot files don't exist in `/etc/pve/nodes/.../qemu-server/`
4. Proxmox tries to delete from qcow2 path (wrong format)
5. Actual disk is LVM-raw: `local-lvm:vm-200-disk-0`

**Error:**
```
qemu-img: Could not open '/var/lib/vz/images/200/vm-200-disk-0.qcow2': No such file or directory
```

**Root Cause:** Storage migration from qcow2 to LVM left orphaned snapshot metadata

**VM 200 Disk Usage:**
```
vm-200-disk-0: 96.26% full (of 32 GB)
```
This is VERY high and contributes to thin pool pressure.

### Additional VM 200 Disks (not on local-lvm)

```
scsi1: stockenweiler-data:200/vm-200-disk-data.qcow2,size=20G
scsi2: stockenweiler-data:200/vm-200-disk-2.qcow2,size=100G
```

These are on NFS mount from Stockenweiler - not part of the local-lvm problem.

---

## Root Cause Analysis

### Why Anker is Unstable

1. **LVM Thin Pool at 89.39%:**
   - Triggers I/O slowdowns
   - May cause kernel delays
   - SSH daemon affected by slow I/O
   - Network stack delayed → packet loss, timeouts

2. **Overcommitted Storage:**
   - 160 GB allocated on 156.88 GB pool
   - Thin provisioning allows this, but it's dangerous
   - No headroom for writes, snapshots, or overhead

3. **VM 200 at 96.26% disk full:**
   - Constant write pressure
   - Triggers thin pool expansion attempts
   - No space to expand → failures → instability

### Why SSH is Intermittent

- I/O wait causes ssh daemon delays
- Connection attempts timeout during high I/O
- Explains: "Connection timed out during banner exchange"
- Explains: 50% packet loss in ping tests

### Why local-lvm Cleanup Attempts Failed

- Broken snapshot metadata prevents normal deletion
- Manual config edit required (blocked by SSH instability)
- Catch-22: Need SSH to fix, but SSH fails due to storage pressure

---

## Remediation Strategy

### OPTION A: Fix Snapshots (BLOCKED)

**Steps:**
1. ✅ SSH to Anker (intermittent success)
2. ✅ Unlock VM 200
3. ❌ Edit `/etc/pve/qemu-server/200.conf` (SSH timeout)
4. ❌ Remove snapshot metadata manually
5. ❌ Reclaim space

**Status:** BLOCKED by Anker SSH instability (Catch-22)

### OPTION B: Migrate to ssd2tb (RECOMMENDED)

**Advantages:**
- ssd2tb has 1.77 TB free (plenty of space)
- Can be done incrementally (one VM at a time)
- Reduces local-lvm pressure immediately
- Doesn't require fixing broken snapshots first

**Steps:**
1. When Anker SSH is stable: Migrate VM 240 (PBS) first (least critical)
2. Test stability improvement
3. Migrate remaining VMs one by one
4. Keep VM 200 for last (most complex due to broken snapshots)

**Migration Command (example for VM 240):**
```bash
qm move-disk 240 scsi0 ssd2tb --delete
```

### OPTION C: Emergency Manual Fix (if SSH becomes stable)

If we get a stable SSH window:

```bash
# 1. Backup config
cp /etc/pve/qemu-server/200.conf /root/200.conf.backup

# 2. Remove broken snapshot references
cat > /tmp/fix_vm200.sh <<'EOF'
#!/bin/bash
CONFIG=/etc/pve/qemu-server/200.conf
cp $CONFIG ${CONFIG}.pre_snapfix
sed -i '/^\[pre_update_260329\]/,/^\$/d' $CONFIG
sed -i '/^\[ucg-migrate-pre-20260405\]/,/^\$/d' $CONFIG
sed -i '/^parent:/d' $CONFIG
sed -i '/^snaptime:/d' $CONFIG
echo "Snapshots removed from config"
cat $CONFIG
EOF

chmod +x /tmp/fix_vm200.sh
/tmp/fix_vm200.sh

# 3. Verify snapshots gone
qm listsnapshot 200

# 4. Check storage
lvs | grep vm-200
pvesm status | grep local-lvm
```

---

## Immediate Actions Taken

### Session 2026-05-04 09:00-10:00

1. ✅ Connected to Anker (intermittent success)
2. ✅ Identified LVM thin pool at 89.39%
3. ✅ Listed VMs: 5 VMs on oversized pool
4. ✅ Found broken snapshots on VM 200
5. ✅ Unlocked VM 200 (`qm unlock 200`)
6. ❌ Attempted snapshot delete (failed - wrong path)
7. ❌ Attempted manual config fix (SSH timeout)
8. ✅ Identified ssd2tb as migration target

### What Works Now

✅ Frontdoor access via Tailscale/toolbox/Caddy
✅ Odoo, Portal, HA, Nextcloud web interfaces
✅ Stockenweiler is stable (swap at 47%, monitoring fixed)

### What's Still Blocked

❌ Direct SSH to Anker (intermittent, unreliable)
❌ VM 200 snapshot cleanup (needs stable SSH)
❌ VM200 agent intake deployment (needs qm guest exec via SSH)
❌ Odoo RPC scripts (10.1.0.22 unreachable)

---

## Recommended Next Steps

### PRIO 1: Wait for stable SSH window, then migrate ONE VM

**Target:** VM 240 (PBS-FraWo) - least critical, clean (no snapshots)

**Command:**
```bash
# When SSH is stable:
ssh root@100.69.179.87 "
  qm stop 240 && \
  qm move-disk 240 scsi0 ssd2tb --delete && \
  qm start 240 && \
  pvesm status | grep local-lvm
"
```

**Expected Result:** local-lvm usage drops from 89.39% to ~75%

### PRIO 2: Monitor stability improvement

- Check SSH reliability after VM migration
- Monitor local-lvm usage trend
- Test packet loss improvement

### PRIO 3: Migrate remaining VMs incrementally

**Order:**
1. VM 240 (PBS) - done
2. VM 230 (Paperless)
3. VM 210 (Home Assistant)
4. VM 220 (Odoo)
5. VM 200 (Nextcloud) - LAST (most complex)

### PRIO 4: Fix VM 200 snapshots when stable

Only after all other VMs migrated and Anker is stable.

---

## Alternative: Emergency Maintenance Window

If situation doesn't improve:

1. Schedule downtime window
2. Stop all VMs on Anker
3. Boot from rescue/LiveCD
4. Manually fix LVM thin pool
5. Fix VM 200 snapshot metadata
6. Restart VMs

**Risk:** Requires physical access or IPMI/KVM-over-IP

---

## Monitoring Plan

### Continuous (automated if possible)

- [ ] Anker SSH reachability (every 5 min)
- [ ] local-lvm usage percentage
- [ ] Packet loss to 100.69.179.87
- [ ] VM 200 disk usage (vm-200-disk-0)

### Manual checks

- [ ] Hourly: Try SSH, record success/failure
- [ ] When SSH works: Check `pvesm status`
- [ ] When stable window: Execute VM migration

### Alert Thresholds

- **local-lvm > 92%:** EMERGENCY (risk of complete failure)
- **SSH success rate < 20%:** CRITICAL
- **VM 200 disk > 98%:** CRITICAL (VM may fail)

---

## Technical Details

### LVM Commands for Reference

```bash
# Check thin pool usage
lvs -a -o lv_name,data_percent,metadata_percent | grep data

# Check physical volumes
pvs

# Check volume groups
vgs

# List all VM volumes
lvs | grep vm-

# Check Proxmox storage
pvesm status

# List VM disks
qm config VMID | grep scsi

# Move disk to different storage
qm move-disk VMID DISK TARGET_STORAGE --delete
```

### VM 200 Config Snippet (Before Fix)

```
lock: snapshot-delete
parent: ucg-migrate-pre-20260405
scsi0: local-lvm:vm-200-disk-0,size=32G
scsi1: stockenweiler-data:200/vm-200-disk-data.qcow2,size=20G
scsi2: stockenweiler-data:200/vm-200-disk-2.qcow2,size=100G
```

### Expected After Snapshot Fix

```
scsi0: local-lvm:vm-200-disk-0,size=32G
scsi1: stockenweiler-data:200/vm-200-disk-data.qcow2,size=20G
scsi2: stockenweiler-data:200/vm-200-disk-2.qcow2,size=100G
```

(No lock, no parent, no snapshot sections)

---

## Long-term Strategy

### Prevent Recurrence

1. **Set local-lvm size limit:** Reserve 20% free space minimum
2. **Regular snapshot cleanup:** Auto-delete snapshots > 30 days
3. **Migration to ssd2tb:** Use directory-based storage (more flexible)
4. **Monitoring alerts:** Alert at 80% storage, critical at 85%
5. **Snapshot policy:** Document when/why to create, retention policy

### Storage Architecture Review

**Current (Problem):**
- local-lvm (thin): Small, inflexible, overcommitted
- Boot disks on constrained storage

**Proposed:**
- ssd2tb (dir): Large, flexible, plenty of headroom
- Boot disks + data disks on same ample storage
- local-lvm reserved for CT/LXC only (smaller overhead)

---

**Status:** Analysis complete, strategy defined, awaiting stable SSH window for execution
**Next Review:** When Anker SSH becomes stable (monitor hourly)
**Ultimate Goal:** All VMs on ssd2tb, local-lvm freed up or repurposed
