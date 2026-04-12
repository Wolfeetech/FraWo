# History: Infrastructure Remediations (2026)

This document contains the chronological logs of remediations and drifts resolved during the early phases of the Homeserver 2027 project.

## April 2026

### 2026-04-09: Nextcloud Reachability Recovery
- **Issue**: `VM 200 nextcloud` was on `10.1.0.24/24` (drift) and collided with `HAOS`.
- **Fix**: Proxmox `ipconfig0` reset to `10.1.0.21/24`. VM restarted.
- **Result**: `cloud.hs27.internal` and `:8445` deliver `HTTP 200`.

### 2026-04-08: Odoo Runtime Drift
- **Issue**: Webcontainer failed with `password authentication failed for user "odoo"`.
- **Fix**: Reverted `docker-compose.yml` to use `env_file` and `odoo.conf` mount. Adjusted file rights.
- **Result**: Odoo healthy on `:8069`, `odoo.hs27.internal`, and mobile `:8444`.

### 2026-04-07: Nextcloud/MariaDB Version Drift
- **Issue**: Compose-Drift led to `mariadb:10.6` while redo-logs were `10.11`. Verwaister `latest`-Container.
- **Fix**: Pins to `mariadb:10.11` and `redis:alpine`. Recreated stack. Repair via `php occ upgrade`.
- **Result**: `cloud.hs27.internal` healthy.

## March 2026

### 2026-03-23: Nextcloud Initial Initialization
- **Issue**: Container running but Nextcloud not installed.
- **Fix**: Reset to empty data basis and re-initialized from IaC.
- **Result**: Admin `frawoadmin` and user `frontend` created.
