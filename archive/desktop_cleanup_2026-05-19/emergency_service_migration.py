#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Emergency Service Migration to Stock PVE
Deploy critical services on Stockenweiler while Anker is offline
"""

import subprocess
import sys
import io

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

MIGRATION_PLAN = """
================================================================================
EMERGENCY SERVICE MIGRATION PLAN
================================================================================

Current Situation:
   ❌ Anker PVE: Offline (physical server down)
   ❌ Toolbox: Offline (runs on Anker)
   ✅ Stock PVE: Online and has capacity

Migration Strategy:
   Deploy minimal Odoo instance on Stock PVE to restore business operations

Services to Migrate:
   1. Odoo ERP (PRIORITY 1 - Business Critical)
   2. Portal/Dashboard (can wait)
   3. Nextcloud (can use web.de temporarily)
   4. Paperless (can wait)

================================================================================
"""

def log(msg, level="INFO"):
    """Print log message"""
    icons = {"INFO": "ℹ️ ", "SUCCESS": "✅", "ERROR": "❌", "WARNING": "⚠️ "}
    print(f"{icons.get(level, '')} {msg}")

def check_stock_pve_capacity():
    """Check if Stock PVE has capacity for new services"""
    log("Checking Stock PVE capacity...")

    try:
        # Try to get storage info
        result = subprocess.run(
            ['ssh', 'stock-pve', 'pvesm status'],
            capture_output=True,
            text=True,
            timeout=10
        )

        if result.returncode == 0:
            log("Stock PVE storage status:", "INFO")
            print(result.stdout)
            return True
        else:
            log("Could not retrieve storage info", "WARNING")
            return False
    except Exception as e:
        log(f"Error checking capacity: {e}", "ERROR")
        return False

def create_minimal_odoo_plan():
    """Create deployment plan for minimal Odoo"""

    plan = """
    MINIMAL ODOO DEPLOYMENT PLAN
    ================================================================================

    Option 1: Use existing Odoo backup
    -----------------------------------
    1. SSH to Stock PVE
    2. Check PBS (container 109) for Anker/Toolbox backups
    3. Restore Odoo container from backup
    4. Reconfigure network (point odoo.hs27.internal to new IP)

    Commands:
    ssh stock-pve
    pct list  # Find free VMID (e.g., 300)
    # Check backups on PBS
    pct exec 109 -- proxmox-backup-client list

    Option 2: Deploy fresh Odoo container
    -----------------------------------
    1. Create new LXC container on Stock PVE
    2. Install Odoo from scratch (Quick setup)
    3. Import latest database backup if available
    4. Update DNS/hosts to point to new container

    Commands:
    ssh stock-pve
    # Create Ubuntu 22.04 container
    pct create 300 local:vztmpl/ubuntu-22.04-standard_22.04-1_amd64.tar.zst \\
      --hostname odoo-temp \\
      --memory 4096 \\
      --cores 2 \\
      --net0 name=eth0,bridge=vmbr0,ip=dhcp \\
      --storage local-lvm \\
      --rootfs local-lvm:32

    pct start 300
    pct enter 300

    # Inside container:
    apt update && apt install -y odoo postgresql
    systemctl enable odoo
    systemctl start odoo

    Option 3: Docker Odoo (FASTEST)
    -----------------------------------
    Deploy Odoo via Docker on existing container

    ssh stock-pve
    pct exec 103 -- docker run -d \\
      --name odoo-emergency \\
      -p 8069:8069 \\
      -e POSTGRES_USER=odoo \\
      -e POSTGRES_PASSWORD=odoo \\
      -e POSTGRES_DB=postgres \\
      odoo:17

    Then update hosts file:
    # Change from:
    100.82.26.53 odoo.hs27.internal
    # To:
    100.91.20.116 odoo.hs27.internal

    ================================================================================
    """

    print(plan)

def update_hosts_file_plan():
    """Show how to redirect services to Stock PVE"""

    plan = """
    HOSTS FILE UPDATE PLAN
    ================================================================================

    File: C:\\Windows\\System32\\drivers\\etc\\hosts

    Current (Anker/Toolbox):
    ------------------------
    100.82.26.53 portal.hs27.internal
    100.82.26.53 cloud.hs27.internal
    100.82.26.53 odoo.hs27.internal
    100.82.26.53 paperless.hs27.internal
    100.82.26.53 vault.hs27.internal

    Temporary (Stock PVE):
    ----------------------
    # Commented out Anker/Toolbox (OFFLINE)
    # 100.82.26.53 portal.hs27.internal
    # 100.82.26.53 cloud.hs27.internal
    # 100.82.26.53 odoo.hs27.internal
    # 100.82.26.53 paperless.hs27.internal
    # 100.82.26.53 vault.hs27.internal

    # Emergency redirect to Stock PVE
    100.91.20.116 odoo.hs27.internal
    # Others stay offline until Anker recovers

    ================================================================================
    """

    print(plan)

def check_npm_proxy_capabilities():
    """Check if NPM can proxy to Anker services"""
    log("Checking NPM (Nginx Proxy Manager) capabilities...")
    log("NPM is running on Stock PVE container 103", "INFO")
    log("Could potentially proxy requests to Anker when it comes back", "INFO")

def main():
    print(MIGRATION_PLAN)

    log("Starting emergency assessment...", "INFO")
    print()

    # Check Stock PVE
    log("Step 1: Check Stock PVE capacity")
    check_stock_pve_capacity()
    print()

    # Show Odoo deployment options
    log("Step 2: Odoo deployment options")
    create_minimal_odoo_plan()
    print()

    # Show hosts file changes
    log("Step 3: DNS/Hosts redirection")
    update_hosts_file_plan()
    print()

    # NPM proxy check
    log("Step 4: Reverse proxy capabilities")
    check_npm_proxy_capabilities()
    print()

    log("RECOMMENDED IMMEDIATE ACTION:", "WARNING")
    log("Deploy Docker Odoo (Option 3) - Takes 5 minutes", "WARNING")
    log("This will restore basic Odoo access while Anker is being fixed", "WARNING")
    print()

    choice = input("Deploy emergency Odoo now? (yes/no): ").strip().lower()

    if choice == 'yes':
        log("Starting emergency Odoo deployment...", "INFO")
        deploy_emergency_odoo()
    else:
        log("Deployment cancelled. Run this script again when ready.", "INFO")

def deploy_emergency_odoo():
    """Deploy Odoo on Stock PVE via Docker"""
    log("This will deploy Odoo in NPM container using Docker", "INFO")

    commands = [
        # Check Docker
        ('ssh stock-pve "pct exec 103 -- docker --version"', "Checking Docker"),

        # Deploy Odoo + Postgres
        ('''ssh stock-pve "pct exec 103 -- docker run -d --name postgres-odoo \\
            -e POSTGRES_USER=odoo \\
            -e POSTGRES_PASSWORD=odoo \\
            -e POSTGRES_DB=postgres \\
            postgres:15"''', "Deploying PostgreSQL"),

        ('''ssh stock-pve "pct exec 103 -- docker run -d --name odoo-emergency \\
            -p 8069:8069 \\
            --link postgres-odoo:db \\
            -e HOST=db \\
            -e USER=odoo \\
            -e PASSWORD=odoo \\
            odoo:17"''', "Deploying Odoo"),
    ]

    for cmd, desc in commands:
        log(desc + "...", "INFO")
        try:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=60)
            if result.returncode == 0:
                log(desc + " - SUCCESS", "SUCCESS")
            else:
                log(desc + " - FAILED: " + result.stderr, "ERROR")
                return False
        except Exception as e:
            log(f"{desc} - ERROR: {e}", "ERROR")
            return False

    log("Emergency Odoo deployed!", "SUCCESS")
    log("Access at: http://100.91.20.116:8069", "SUCCESS")
    log("Now update hosts file to redirect odoo.hs27.internal", "INFO")

    return True

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Cancelled by user\n")
    except Exception as e:
        print(f"\n❌ Error: {e}\n")
        import traceback
        traceback.print_exc()
