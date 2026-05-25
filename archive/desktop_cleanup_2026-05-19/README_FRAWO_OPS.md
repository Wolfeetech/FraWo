# 🚀 FRAWO Ops - Quick Start Guide

## 📦 What's Included

This package contains complete infrastructure management and monitoring tools for FRAWO operations.

### Tools Overview

| Tool | Purpose | When to Use |
|------|---------|-------------|
| `frawo_ops_dashboard.py` | Complete status dashboard | Daily health check |
| `frawo_auto_recovery.py` | Automated recovery | When services are down |
| `pve_start_toolbox.py` | Interactive PVE management | Start/stop containers |
| `pve_check.py` | Quick connectivity test | Fast status check |
| `FRAWO_OPS_DOCUMENTATION.md` | Full documentation | Reference guide |

---

## ⚡ Quick Start (3 Steps)

### 1. Check Status
```bash
python Desktop/frawo_ops_dashboard.py
```

### 2. If Services Are Down
```bash
python Desktop/frawo_auto_recovery.py
```

### 3. If Recovery Fails
- Check physical server at Rothkreuz
- SSH to Anker PVE: `ssh anker-pve`
- Manually start Toolbox container

---

## 🎯 Common Tasks

### Daily Health Check
```bash
# Quick check (30 seconds)
python Desktop/pve_check.py

# Full dashboard (1 minute)
python Desktop/frawo_ops_dashboard.py
```

### When Services Are Offline
```bash
# Step 1: Run auto-recovery
python Desktop/frawo_auto_recovery.py

# Step 2: If that fails, check dashboard for details
python Desktop/frawo_ops_dashboard.py

# Step 3: Manual intervention if needed
ssh anker-pve
pct list
pct start <toolbox-id>
```

### Access Proxmox Web
```bash
# Windows
start https://100.91.20.116:8006/

# Or just visit in browser:
# https://100.91.20.116:8006/
```

---

## 🔍 Current Infrastructure Status

### ✅ Online (Stockenweiler PVE)
- Radio/Music services
- File server
- Automation (n8n)
- VPN (WireGuard)
- Nginx Proxy Manager
- **12 containers + 2 VMs running**

### ❌ Offline (Anker PVE)
- **Anker PVE server** (physical host offline)
- **Toolbox** (container on Anker PVE)
  - Odoo ERP
  - Nextcloud
  - Paperless
  - Portal
  - Vault

---

## 🛠️ Troubleshooting

### Services not responding?
1. Run dashboard: `python Desktop/frawo_ops_dashboard.py`
2. Check diagnostics section
3. Follow recommended actions

### Can't SSH to servers?
- Check Tailscale: `tailscale status`
- Verify SSH config: `cat ~/.ssh/config | grep -A 5 "anker-pve\|stock-pve"`
- Try direct IP: `ssh root@100.91.20.116`

### Anker PVE offline?
**Requires physical intervention:**
- Location: Rothkreuz
- Check power and network cables
- Press power button if needed
- Wait 2-3 minutes for boot

---

## 📊 Service Status Check

### Quick Manual Checks
```bash
# Check Proxmox
curl -k https://100.91.20.116:8006/

# Check Odoo
curl -I http://odoo.hs27.internal/

# Check Portal
curl -I http://portal.hs27.internal/

# Check Tailscale
tailscale status
```

### Port Connectivity
```bash
# Stockenweiler PVE
ping 100.91.20.116

# Toolbox
ping 100.82.26.53

# Anker PVE
ping 100.69.179.87
```

---

## 🔐 Access Information

### SSH Shortcuts
Configured in `~/.ssh/config`:
- `ssh stock-pve` → Stockenweiler PVE
- `ssh anker-pve` → Anker PVE
- `ssh toolbox` → Toolbox container

### Web Interfaces
- **Proxmox:** https://100.91.20.116:8006/
- **Odoo:** http://odoo.hs27.internal/
- **Nextcloud:** http://cloud.hs27.internal/
- **Portal:** http://portal.hs27.internal/

### Network Details
- **Tailscale Network:** tail150400.ts.net
- **Local Network (Anker):** 10.1.0.x
- **Local Network (Stock):** 192.168.178.x

---

## 📞 When to Get Help

### Automated Recovery Worked ✅
- Monitor for 10 minutes
- Verify services with dashboard
- Schedule follow-up check

### Automated Recovery Failed ❌
- Check dashboard diagnostics
- Try manual SSH recovery
- Contact on-site personnel if needed

### Critical Business Impact 🔴
- Odoo offline = business operations impacted
- Nextcloud offline = file access impacted
- Escalate immediately for physical access

---

## 🎓 Learning Resources

### Want to Learn More?
1. **Full Documentation:** `FRAWO_OPS_DOCUMENTATION.md`
2. **Proxmox Docs:** https://pve.proxmox.com/wiki/Main_Page
3. **Tailscale Docs:** https://tailscale.com/kb/

### Understanding the Scripts
All Python scripts are well-commented:
- Open in any text editor
- Read comments for explanations
- Modify as needed for your setup

---

## 💾 Backup & Safety

### Before Making Changes
1. Run dashboard to document current state
2. Take Proxmox snapshot if modifying VMs
3. Test changes on non-critical services first

### Regular Maintenance
- Run dashboard: Weekly
- Check backups (PBS): Monthly
- Update documentation: When changes occur

---

## 🚨 Emergency Procedures

### All Services Down
```bash
# 1. Quick status check
python Desktop/pve_check.py

# 2. Auto recovery attempt
python Desktop/frawo_auto_recovery.py

# 3. If failed, escalate for physical access
```

### Single Service Down
```bash
# 1. Check dashboard
python Desktop/frawo_ops_dashboard.py

# 2. SSH to relevant server
ssh stock-pve  # or anker-pve

# 3. Check container status
pct list
pct status <vmid>

# 4. Restart if needed
pct restart <vmid>
```

---

## ✅ Success Checklist

After running tools, verify:
- [ ] Stockenweiler PVE: Online
- [ ] Anker PVE: Online
- [ ] Toolbox: Running
- [ ] Odoo: Accessible
- [ ] Nextcloud: Accessible
- [ ] Portal: Accessible
- [ ] Dashboard shows all green

---

## 📝 Notes

### Python Requirements
All scripts use standard library only:
- `requests`
- `urllib3`
- No special installation needed (works with Python 3.7+)

### Windows Compatibility
- All scripts tested on Windows
- UTF-8 encoding handled automatically
- Can also run on Linux/Mac

### Updates
Tools created: 2026-05-06
Last infrastructure audit: 2026-05-06 23:49

---

## 🎯 Quick Command Reference

```bash
# Status checks
python Desktop/frawo_ops_dashboard.py
python Desktop/pve_check.py

# Recovery
python Desktop/frawo_auto_recovery.py
python Desktop/pve_start_toolbox.py

# Direct access
ssh stock-pve
ssh anker-pve
start https://100.91.20.116:8006/

# Tailscale
tailscale status
```

---

**Need Help?** Check `FRAWO_OPS_DOCUMENTATION.md` for complete details.

**Everything Working?** Run weekly health checks to keep it that way!

---

*FRAWO Ops Tools - Making infrastructure management simple* 🎉
