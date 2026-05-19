# FRAWO Ops - Infrastructure Documentation

**Generated:** 2026-05-06
**Status:** Complete Infrastructure Audit

---

## 🏗️ Infrastructure Overview

### Architecture Summary

FRAWO operates a distributed infrastructure across two primary Proxmox hosts:

1. **Stockenweiler PVE** (Primary) - Running and operational
2. **Anker PVE** (Secondary) - Currently offline, hosts critical business services

---

## 📊 Current Status (2026-05-06 23:49)

### ✅ Online Systems

#### Stockenweiler PVE
- **IP:** 100.91.20.116 (Tailscale)
- **Status:** ✅ **ONLINE** and fully operational
- **Access:**
  - Web: https://100.91.20.116:8006/
  - SSH: `ssh stock-pve`
- **Role:** Primary Proxmox host for radio/media services

**Running Containers (12 total):**
| ID  | Name | Purpose |
|-----|------|---------|
| 101 | adguard | DNS filtering and ad-blocking |
| 103 | npm | Nginx Proxy Manager (reverse proxy) |
| 106 | wireguard | VPN server |
| 108 | vaultwarden | Password manager (Bitwarden compatible) |
| 109 | pbs | Proxmox Backup Server |
| 110 | n8n | Workflow automation |
| 120 | fileserver | Network file storage |
| 130 | mail-relay | Email relay service |
| 202 | mongodb-primary | MongoDB database |
| 207 | radio-wordpress-prod | Radio WordPress site |
| 208 | mariadb-server | MariaDB database |
| 211 | radio-api | Radio API backend |

**Running VMs:**
| ID  | Name | Memory | Purpose |
|-----|------|--------|---------|
| 210 | azuracast-vm | 8GB | Radio streaming platform |
| 360 | homeassistant-eltern | 4GB | Home automation |

### ❌ Offline Systems

#### Anker PVE (Proxmox Host)
- **IP:** 100.69.179.87 (Tailscale) / 10.1.0.92 (Local)
- **Status:** ❌ **OFFLINE**
- **Last Seen:** ~18 hours ago (Tailscale)
- **Location:** Rothkreuz
- **Issue:** Complete power/network loss

#### Toolbox Container
- **IP:** 100.82.26.53 (Tailscale) / 10.1.0.20 (Local)
- **Status:** ❌ **OFFLINE** (depends on Anker PVE)
- **Role:** Core services hub - Caddy reverse proxy, DNS, business services
- **Hosted Services:**
  - Portal (portal.hs27.internal)
  - Nextcloud (cloud.hs27.internal)
  - Odoo ERP (odoo.hs27.internal)
  - Paperless DMS (paperless.hs27.internal)
  - Vault (vault.hs27.internal)
  - Home Assistant (ha.hs27.internal)

---

## 🔴 Critical Issues

### Issue #1: Anker PVE Offline
**Severity:** 🔴 CRITICAL
**Impact:** All business-critical services unavailable

**Services Affected:**
- ❌ Odoo ERP (business operations)
- ❌ Nextcloud (file sync/collaboration)
- ❌ Paperless (document management)
- ❌ Portal (internal dashboard)
- ❌ Vault (secrets management)

**Root Cause:** Anker PVE physical server is powered off or has network failure

**Resolution Steps:**
1. **Immediate:** Check physical server at Rothkreuz location
2. **Verify:** Power is connected and server is running
3. **Check:** Network connectivity (cables, switch ports)
4. **Access:** Try local network access via 10.1.0.92
5. **Restart:** If necessary, perform hard reset

**Recovery Time Estimate:**
- If physical access available: 5-15 minutes
- If remote only: Requires on-site intervention

---

## 🛠️ Recovery Procedures

### Automated Recovery
Use the provided recovery script:
```bash
python Desktop/frawo_auto_recovery.py
```

**What it does:**
1. Checks Anker PVE connectivity
2. Attempts to start Toolbox container
3. Verifies service availability
4. Provides detailed status report

### Manual Recovery

#### If Anker PVE is accessible:
```bash
# SSH to Anker PVE
ssh anker-pve

# List all containers
pct list

# Start Toolbox (find correct VMID first)
pct start <toolbox-vmid>

# Monitor startup
pct status <toolbox-vmid>
watch -n 2 'pct status <toolbox-vmid>'
```

#### If Anker PVE is offline:
**Physical intervention required:**
1. Travel to Rothkreuz location
2. Check server power LED status
3. Press power button if needed
4. Wait 2-3 minutes for boot
5. Verify network connectivity
6. Check Tailscale status
7. Verify Toolbox auto-starts

---

## 📡 Network Configuration

### Tailscale VPN
All servers accessible via Tailscale mesh VPN:
- Network: tail150400.ts.net
- Domain: `100.x.x.x` addresses

### DNS Configuration
Internal services use `.hs27.internal` domain:
- Resolved via hosts file: `C:\Windows\System32\drivers\etc\hosts`
- All `.hs27.internal` domains point to Toolbox: 100.82.26.53

### SSH Access
Configuration: `~/.ssh/config`

**Shortcuts:**
- `ssh stock-pve` → Stockenweiler PVE
- `ssh anker-pve` → Anker PVE
- `ssh toolbox` → Toolbox container

### SSH Keys
Located in `~/.ssh/`:
- `id_ed25519` - Default key
- `id_ed25519_frawo` - FraWo infrastructure
- `pve_ed25519` - Proxmox access
- `hs27_ops_ed25519` - HS27 operations

---

## 🔧 Management Tools

### Created Tools (on Desktop)

#### 1. `frawo_ops_dashboard.py`
**Purpose:** Comprehensive infrastructure status dashboard

**Usage:**
```bash
python Desktop/frawo_ops_dashboard.py
```

**Shows:**
- All server status (connectivity, ports)
- Container/VM inventory
- Web service availability
- Diagnostic recommendations
- Quick action commands

#### 2. `frawo_auto_recovery.py`
**Purpose:** Automated recovery system

**Usage:**
```bash
python Desktop/frawo_auto_recovery.py
```

**Features:**
- Attempts automatic service recovery
- Checks Anker PVE health
- Starts Toolbox if needed
- Verifies service availability
- Provides recovery summary

#### 3. `pve_start_toolbox.py`
**Purpose:** Interactive Proxmox VM/Container manager

**Usage:**
```bash
python Desktop/pve_start_toolbox.py
```

**Features:**
- Proxmox API authentication
- Container search and identification
- Start/stop controls
- Status monitoring

#### 4. `pve_check.py`
**Purpose:** Quick connectivity check

**Usage:**
```bash
python Desktop/pve_check.py
```

**Shows:**
- Port connectivity for all servers
- HTTP service response times
- Quick status overview

---

## 🔐 Security Notes

### Access Control
- All servers require SSH key authentication
- Proxmox web interface requires password auth
- Tailscale provides zero-trust network access

### Credentials Storage
- SSH keys stored in `~/.ssh/`
- Proxmox credentials not stored (manual entry required)
- Consider using password manager for API tokens

---

## 📈 Monitoring Recommendations

### Immediate Actions
1. ✅ Setup automated health checks (every 5 minutes)
2. ✅ Configure Anker PVE to auto-start on power restore
3. ✅ Ensure Toolbox container auto-starts with Anker PVE
4. ⚠️  Setup alerting for service downtime
5. ⚠️  Document Anker PVE MAC address for Wake-on-LAN

### Long-term Improvements
1. **High Availability:**
   - Migrate critical services to Stockenweiler PVE
   - Setup failover for Odoo/Nextcloud
   - Implement automatic failover scripts

2. **Monitoring:**
   - Setup Uptime Kuma or similar
   - Configure email/Telegram alerts
   - Create status page for services

3. **Backup:**
   - Verify PBS (109) backup schedule
   - Test restore procedures
   - Document recovery time objectives

4. **Documentation:**
   - Create runbook for common issues
   - Document all service dependencies
   - Maintain contact list for on-site access

---

## 🚨 Emergency Contacts

### On-site Access
- **Location:** Rothkreuz (Anker PVE)
- **Contact:** [Add contact info]
- **Remote Access:** Tailscale VPN required

### Escalation Path
1. Attempt automated recovery
2. Try manual SSH recovery
3. Contact on-site personnel
4. Physical server access if needed

---

## 📝 Change Log

### 2026-05-06
- Initial infrastructure audit completed
- Identified Anker PVE offline issue
- Created management and recovery tools
- Documented complete architecture
- Generated status dashboard

---

## 🔗 Quick Reference

### Most Common Commands

**Check overall status:**
```bash
python Desktop/frawo_ops_dashboard.py
```

**Attempt recovery:**
```bash
python Desktop/frawo_auto_recovery.py
```

**Access Proxmox:**
```bash
# Web
start https://100.91.20.116:8006/

# SSH
ssh stock-pve
ssh anker-pve
```

**Check service status:**
```bash
curl -I http://odoo.hs27.internal/
curl -I http://portal.hs27.internal/
curl -I https://100.91.20.116:8006/
```

### Service URLs

| Service | URL |
|---------|-----|
| Proxmox Web | https://100.91.20.116:8006/ |
| Portal | http://portal.hs27.internal/ |
| Odoo ERP | http://odoo.hs27.internal/ |
| Nextcloud | http://cloud.hs27.internal/ |
| Paperless | http://paperless.hs27.internal/ |
| Vault | http://vault.hs27.internal/ |

---

## ✅ Next Steps

1. **Immediate:** Restore Anker PVE and Toolbox
2. **Short-term:** Setup automated monitoring
3. **Medium-term:** Implement high availability
4. **Long-term:** Migrate critical services for redundancy

---

**End of Documentation**
