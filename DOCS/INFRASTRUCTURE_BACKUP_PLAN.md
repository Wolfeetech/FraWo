# FraWo Infrastructure - Backup & Recovery Plan

**Date**: 2026-05-15
**Critical Priority**: HIGH

---

## 🚨 **CURRENT STATUS**

**Server**: Proxmox @ 100.69.179.87 (proxmox-anker)
**Odoo VM**: VM 220 (2GB RAM, 2 CPU, 32GB disk @ 39.77% usage)
**LVM Pool**: 90.37% FULL ⚠️ **CRITICAL**
**Last Crash**: Wed May 13 08:04 (48h ago)

---

## ⚠️ **IMMEDIATE ACTIONS REQUIRED (TODAY!)**

### 1. Storage Cleanup (15 min)
```bash
ssh root@100.69.179.87
# Remove old snapshot (frees ~8GB)
lvremove -y pve/snap_vm-120-disk-0_ucg-migrate-pre-20260405

# Check if VM 200/230 can be deleted
qm status 200
qm status 230
# If stopped/unused: lvremove pve/vm-200-disk-0 && lvremove pve/vm-230-disk-0
```

### 2. Enable Monitoring (5 min)
```bash
scp C:\Users\StudioPC\OneDrive\Dokumente\GitHub\FraWo\scripts\monitoring\setup_monitoring.sh root@100.69.179.87:/tmp/
ssh root@100.69.179.87 "bash /tmp/setup_monitoring.sh"
```

### 3. Odoo Backup (10 min)
```bash
# Backup Odoo database
ssh root@100.69.179.87 "qm guest exec 220 -- pg_dump -U odoo FraWo_GbR > /backup/odoo_$(date +%Y%m%d).sql"

# Backup filestore
ssh root@100.69.179.87 "qm guest exec 220 -- tar czf /backup/filestore_$(date +%Y%m%d).tar.gz /var/lib/odoo/.local/share/Odoo/filestore"
```

---

## 🔄 **AUTOMATED BACKUP STRATEGY**

### Daily Backups (Proxmox Backup Server)
- **What**: Full VM 220 snapshot
- **When**: Daily @ 2:00 AM
- **Retention**: 7 days rolling
- **Storage**: External PBS or NFS

### Database Dumps
- **What**: PostgreSQL dump of FraWo_GbR
- **When**: Every 6 hours
- **Retention**: 30 days
- **Location**: `/backup/odoo/` on VM 220

### Website Assets
- **What**: CSS, Images, Custom Code
- **When**: On every deployment
- **Location**: Git repo + Odoo filestore backup

---

## 🎯 **MONITORING ALERTS**

### Critical Alerts (Immediate Action)
1. **Disk Space > 85%** → Email + Webhook
2. **VM 220 Down** → Auto-restart + Alert
3. **Cloudflare Tunnel Down** → Auto-restart + Alert
4. **Server Unreachable** → Email + SMS

### Warning Alerts
1. **Disk Space > 75%** → Email
2. **High Load (>80%)** → Email
3. **Memory Usage > 80%** → Email

---

## 🔧 **RECOVERY PROCEDURES**

### Scenario 1: Website Down
```bash
# Check VM status
ssh root@100.69.179.87 "qm status 220"

# If stopped
qm start 220

# Check Cloudflare Tunnel
systemctl status cloudflared
systemctl restart cloudflared

# Verify
curl https://www.frawo-tech.de/
```

### Scenario 2: Odoo Corrupted
```bash
# Stop VM
qm stop 220

# Restore from last PBS backup
pbs-restore --vm 220 --date yesterday

# Start VM
qm start 220
```

### Scenario 3: Full Disk Crash
```bash
# Emergency cleanup
lvremove pve/snap_*  # Remove all snapshots
lvremove pve/vm-200-*  # Remove unused VMs
lvremove pve/vm-230-*

# Restart affected VMs
qm start 220
```

---

## 📊 **CAPACITY PLANNING**

### Current Usage
- **Total Pool**: 156.88GB
- **Used**: 141.75GB (90.37%)
- **Free**: 15.13GB ⚠️ **CRITICAL**

### VM Breakdown
- VM 110 (storage-node): 77.73GB (100GB allocated)
- VM 220 (odoo): 12.73GB (32GB allocated, 39.77% used)
- VM 120 (vaultwarden): 1.58GB (8GB allocated)
- VM 210: 8.33GB (32GB allocated)

### Cleanup Potential
1. Remove snapshot: **+8GB** (ucg-migrate)
2. Remove VM 200: **+32GB** (if unused)
3. Remove VM 230: **+32GB** (if unused)
4. Trim VM 110: **+20GB** (if possible)
**Total Recoverable**: ~92GB

### Target
- **Safe threshold**: <80% (125GB used)
- **Critical threshold**: >90% (141GB used) ⚠️ **CURRENT**

---

## 🔐 **ACCESS & CREDENTIALS**

**Proxmox Host**:
- IP: 100.69.179.87 (Tailscale)
- SSH: `ssh root@100.69.179.87`
- Web UI: `https://100.69.179.87:8006`

**Odoo VM 220**:
- Internal IP: 10.4.0.22:8069
- SSH: `ssh root@100.69.179.87 "qm guest exec 220 -- bash"`
- Database: FraWo_GbR
- User: wolf@frawo-tech.de
- Password: [Stored in .env]

**Cloudflare**:
- Tunnel: `www.frawo-tech.de` → `10.4.0.22:8069`
- Dashboard: https://dash.cloudflare.com

---

## ✅ **NEXT STEPS (THIS WEEK)**

- [ ] Execute storage cleanup (TODAY)
- [ ] Enable automated monitoring (TODAY)
- [ ] Set up Proxmox Backup Server (THIS WEEK)
- [ ] Configure email alerts (THIS WEEK)
- [ ] Test recovery procedure (THIS WEEK)
- [ ] Document runbook (THIS WEEK)

---

**Status**: 🟥 **CRITICAL** - Immediate action required!
**Priority**: **P0** - Do today!
