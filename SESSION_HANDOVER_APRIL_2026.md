# Infrastructure Handover - Session 413ed0dc (2025-2026)

This document summarizes the critical infrastructure fixes and knowledge gathered during the network troubleshooting session.

## 🖥️ Server Infrastructure
- **Proxmox Host (PVE)**: 
  - Legacy IP: `192.168.178.25`
  - Tailscale Name: `stockenweiler-pve` (`100.91.20.116`)
- **Management UI**: `https://192.168.178.25:8006`

## 📦 Container Inventory (LXC)
| ID | Name | Description |
| :--- | :--- | :--- |
| **101** | AdGuard | DNS & Ad-Blocking (Fixed during session) |
| **103** | NPM | Nginx Proxy Manager (External Access) |
| **211** | Radio API | yourparty-tech backend (Port 8080) |
| **360** | Home Assistant | Home automation (Port 8123) |

## 🔐 SSL & Proxy Details
> [!IMPORTANT]
> **Expired Status**: As of April 2026, the SSL certificate for `home.prinz-stockenweiler.de` has expired.

- **Manual SSL Renewal (CLI)**:
  If the NPM Web-UI fails, use this command inside the NPM container (LXC 103):
  ```bash
  certbot certonly --webroot -w /opt/npm/data/letsencrypt-acme-challenge -d home.prinz-stockenweiler.de
  ```
- **Nginx Configuration Path**: `/opt/npm/data/nginx/proxy_host/6.conf`
- **Certificate Path (Mounted)**: `/etc/letsencrypt/live/home.prinz-stockenweiler.de/`

## 🛡️ History & Fixes
1. **DNS Fix**: Resolved an issue where AdGuard (LXC 101) was unresponsive although "Running". Restarting the container fixed internal resolution.
2. **Reverse Proxy (400 Error)**: Fixed a TLS/SSL mismatch by manually provisioning a certificate and adjusting symlinks between the LXC host and the NPM Docker container.

---
*Created by Antigravity on 2026-04-09*
